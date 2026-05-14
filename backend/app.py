# -*- coding: utf-8 -*-
"""智慧课堂后端 Flask API - 重建版 2026-04-14"""
import os, sys, json, time, uuid, secrets, threading, subprocess, logging, zipfile, io, html
from datetime import datetime, timedelta
from functools import wraps
from decimal import Decimal
import bcrypt, pymysql, jwt
from dbutils.pooled_db import PooledDB
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
for d in ['homework','submissions','grades','forum']:
    os.makedirs(os.path.join(UPLOAD_DIR, d), exist_ok=True)

# ---- 日志配置 ----
_log_file = os.path.join(LOG_DIR, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(_log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger('smartclass')

DB_CONFIG = {
    'host':'127.0.0.1','port':3306,'user':'root','password':'Root@123456',
    'database':'smartclass','charset':'utf8mb4','autocommit':True,
    'connect_timeout': 10,       # 连接超时 10 秒
    'read_timeout': 30,          # 读超时 30 秒
    'write_timeout': 30,         # 写超时 30 秒
}

# 让所有 cursor 默认返回 dict 而非 tuple
class _DictCursorConn:
    def __init__(self, conn):
        self._c = conn
    def cursor(self, cursorclass=None):
        return self._c.cursor(pymysql.cursors.DictCursor)
    def __getattr__(self, name):
        return getattr(self._c, name)

JWT_SECRET = os.environ.get('JWT_SECRET', 'smartclass_jwt_secret_2026_fallback_dev')
JWT_ALGO = 'HS256'
JWT_EXPIRE_DAYS = 30

app = Flask(__name__)
CORS(app, resources={r"/api/*":{"origins":"*"}})
app.config['MAX_CONTENT_LENGTH'] = 100*1024*1024

# 连接池：支持 3000 并发，优化连接复用
_db_pool = PooledDB(
    creator=pymysql,
    maxconnections=32,   # 8→32，最多32个活跃连接
    mincached=4,          # 2→4，初始预建4个连接
    maxcached=16,         # 5→16，缓存最多16个连接
    maxshared=8,          # 新增：最多8个共享连接（适用于多线程）
    blocking=True,
    **DB_CONFIG
)

def get_db():
    return _DictCursorConn(_db_pool.connection())

def _ser(v):
    if v is None: return None
    if isinstance(v, datetime): return v.strftime('%Y-%m-%dT%H:%M:%S')
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, bytes): return v.decode('utf-8','replace')
    if isinstance(v, str):
        # 尝试解析 JSON 字符串
        if v.startswith('{') or v.startswith('['):
            try: return json.loads(v)
            except: pass
    return v

def _row(r): return None if r is None else {k:_ser(v) for k,v in r.items()}
def _rows(r): return [_row(x) for x in r] if r else []

def success(data=None, msg='success'):
    return jsonify({'code':200,'success':True,'data':data,'message':msg})
def fail(msg='error'):
    """返回 HTTP 200 + success:False，前端可通过 JSON 解析获取错误信息"""
    return jsonify({'code':400,'success':False,'message':msg})
def err(msg='error', code=400):
    return jsonify({'code':code,'message':msg}), code

def gen_token(uid, role, extra=None):
    p={'user_id':uid,'role':role,'exp':datetime.utcnow()+timedelta(days=JWT_EXPIRE_DAYS)}
    if extra: p.update(extra)
    return jwt.encode(p, JWT_SECRET, algorithm=JWT_ALGO)

def dec_token(t):
    try: return jwt.decode(t, JWT_SECRET, algorithms=[JWT_ALGO])
    except: return None

def get_user(req):
    auth = req.headers.get('Authorization','')
    # 优先从 Header 取，其次从 URL ?token= 参数取（用于文件下载等场景）
    if auth.startswith('Bearer '):
        token_str = auth[7:]
    else:
        token_str = req.args.get('token','')
    if not token_str: return None
    return dec_token(token_str)

def teacher_required(f):
    @wraps(f)
    def d(*a,**k):
        u=get_user(request)
        if not u or u.get('role') not in ('teacher','admin'): return err('未授权',401)
        request.teacher_id=u['user_id']
        return f(*a,**k)
    return d

def student_required(f):
    """允许 student/teacher/admin 角色，用于学生端接口"""
    @wraps(f)
    def d(*a,**k):
        u=get_user(request)
        if not u or u.get('role') not in ('student','teacher','admin'): return err('未授权',401)
        request.teacher_id=u['user_id']   # token 里存的就是学生自己的 student_id
        return f(*a,**k)
    return d

def admin_required(f):
    @wraps(f)
    def d(*a,**k):
        u=get_user(request)
        if not u or u.get('role')!='admin': return err('未授权',401)
        request.admin_id=u['user_id']
        return f(*a,**k)
    return d

def forum_required(f):
    @wraps(f)
    def d(*a,**k):
        u=get_user(request)
        if not u or u.get('role') not in ('teacher','student','admin'): return err('未授权',401)
        request.forum_uid=u['user_id']; request.forum_role=u['role']
        return f(*a,**k)
    return d

def get_token_param(req):
    a=req.headers.get('Authorization','')
    if a.startswith('Bearer '): return a[7:]
    return req.args.get('token','')

@app.route('/api/status', methods=['GET'])
def status(): return success({'status':'ok'})

# ======= 登录认证 =======
@app.route('/api/auth/login', methods=['POST'])
def login():
    d=request.get_json() or {}
    login_type=d.get('type','teacher')
    username=(d.get('username') or '').strip()
    password=d.get('password','')
    if not username or not password: return err('用户名和密码不能为空')
    db=get_db(); cur=db.cursor()
    if login_type=='admin':
        # 先查所有教师，找到 username 匹配的管理员
        cur.execute("SELECT * FROM teachers")
        all_users = cur.fetchall()
        user = None
        for u in all_users:
            if str(u.get('username','')).strip() == username:
                user = u
                break
        db.close()
        if not user or not bcrypt.checkpw(password.encode(), user['password_hash'].encode()): return fail('用户名或密码错误')
        token=gen_token(user['id'],'admin',{'username':user['username']})
        return success({'token':token,'user':{'id':user['id'],'username':user['username'],'name':user.get('real_name',user['username']),'role':'admin'}})
    elif login_type=='teacher':
        cur.execute("SELECT * FROM teachers WHERE username=%s",(username,))
        user=cur.fetchone(); db.close()
        if not user or not bcrypt.checkpw(password.encode(),user['password_hash'].encode()): return fail('用户名或密码错误')
        token=gen_token(user['id'],'teacher',{'username':user['username']})
        return success({'token':token,'user':{'id':user['id'],'username':user['username'],'name':user.get('real_name',user['username']),'role':'teacher'}})
    elif login_type=='student':
        cur.execute("SELECT sa.*,s.name,s.student_number FROM student_accounts sa JOIN students s ON sa.student_id=s.id WHERE sa.username=%s",(username,))
        user=cur.fetchone(); db.close()
        if not user or not bcrypt.checkpw(password.encode(),user['password'].encode()): return fail('学号或密码错误')
        token=gen_token(user['student_id'],'student',{'student_number':user['student_number']})
        # 记录活跃日志
        _db=get_db(); _cur=_db.cursor()
        _cur.execute("INSERT IGNORE INTO student_login_logs (student_id, login_date) VALUES (%s, CURDATE())",(user['student_id'],))
        _db.commit(); _db.close()
        return success({'token':token,'user':{'id':user['student_id'],'username':user['student_number'],'name':user.get('name',''),'role':'student'}})
    return err('无效的登录类型')

@app.route('/api/auth/me', methods=['GET'])
@teacher_required
def auth_me():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id,username,real_name FROM teachers WHERE id=%s",(request.teacher_id,))
    u=cur.fetchone(); db.close()
    return success({'id':u['id'],'username':u['username'],'name':u.get('real_name',u['username']),'role':'teacher'}) if u else err('用户不存在',404)

@app.route('/api/auth/change_password', methods=['POST'])
@teacher_required
def change_password():
    d=request.get_json() or {}
    old_p=d.get('old_password',''); new_p=d.get('new_password','')
    if not old_p or not new_p: return err('旧密码和新密码都不能为空')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT password_hash FROM teachers WHERE id=%s",(request.teacher_id,))
    u=cur.fetchone()
    if not u or not bcrypt.checkpw(old_p.encode(),u['password_hash'].encode()): db.close(); return err('旧密码错误')
    new_hash=bcrypt.hashpw(new_p.encode(),bcrypt.gensalt()).decode()
    cur.execute("UPDATE teachers SET password_hash=%s WHERE id=%s",(new_hash,request.teacher_id))
    db.close(); return success({'message':'密码修改成功'})

# ======= 班级管理 =======
@app.route('/api/classes/all', methods=['GET'])
@teacher_required
def get_all_classes():
    # 返回系统中所有班级（含学生人数），供教师开设/编辑课程时选择关联班级
    db=get_db(); cur=db.cursor()
    cur.execute("""
        SELECT c.id, c.name,
               (SELECT COUNT(*) FROM students s WHERE s.class_id=c.id) AS student_count
        FROM classes c
        ORDER BY c.name
    """)
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

@app.route('/api/classes/<class_id>/students', methods=['GET'])
@teacher_required
def get_class_students(class_id):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id,name,student_number,sort_order FROM students WHERE class_id=%s ORDER BY sort_order,name",(class_id,))
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

# ======= 课程管理 =======
@app.route('/api/courses', methods=['GET'])
@teacher_required
def get_courses():
    term_filter = request.args.get('term', '')
    db = get_db()
    cur = db.cursor()

    if term_filter:
        cur.execute(
            "SELECT * FROM courses WHERE teacher_id=%s AND term=%s ORDER BY name",
            (request.teacher_id, term_filter)
        )
    else:
        cur.execute(
            "SELECT * FROM courses WHERE teacher_id=%s ORDER BY term DESC,name",
            (request.teacher_id,)
        )
    courses = _rows(cur.fetchall())

    # 如果没传 term，返回所有学期列表
    if not term_filter:
        cur.execute(
            "SELECT DISTINCT term FROM courses WHERE teacher_id=%s AND term IS NOT NULL AND term != '' ORDER BY term DESC",
            (request.teacher_id,)
        )
        all_terms = [r['term'] for r in cur.fetchall()]
    else:
        all_terms = []

    for c in courses:
        cur.execute("""
            SELECT c.id, c.name,
                   (SELECT COUNT(*) FROM students s WHERE s.class_id=c.id) AS student_count
            FROM classes c JOIN course_classes cc ON cc.class_id=c.id
            WHERE cc.course_id=%s
        """, (c['id'],))
        c['classes'] = _rows(cur.fetchall())
        c['class_count'] = len(c['classes'])

    db.close()
    return success({'courses': courses, 'terms': all_terms})

@app.route('/api/courses', methods=['POST'])
@teacher_required
def create_course():
    d=request.get_json() or {}
    name=(d.get('name') or '').strip(); term=(d.get('term') or '').strip()
    class_ids=d.get('class_ids') or []
    if not name or not term: return err('课程名称和学期不能为空')
    course_id=str(uuid.uuid4())[:8].upper()
    db=get_db(); cur=db.cursor()
    cur.execute("INSERT INTO courses (id,name,term,teacher_id) VALUES (%s,%s,%s,%s)",(course_id,name,term,request.teacher_id))
    for cid in class_ids: cur.execute("INSERT INTO course_classes (course_id,class_id) VALUES (%s,%s)",(course_id,str(cid)))
    db.close(); return success({'id':course_id})

@app.route('/api/courses/<course_id>', methods=['PUT'])
@teacher_required
def update_course(course_id):
    d=request.get_json() or {}
    name=(d.get('name') or '').strip(); term=(d.get('term') or '').strip()
    class_ids=[str(x) for x in (d.get('class_ids') or [])]
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE courses SET name=%s,term=%s WHERE id=%s AND teacher_id=%s",(name,term,course_id,request.teacher_id))
    cur.execute("DELETE FROM course_classes WHERE course_id=%s",(course_id,))
    for cid in class_ids: cur.execute("INSERT INTO course_classes (course_id,class_id) VALUES (%s,%s)",(course_id,cid))
    db.close(); return success()

@app.route('/api/courses/<course_id>', methods=['DELETE'])
@teacher_required
def delete_course(course_id):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM course_classes WHERE course_id=%s",(course_id,))
    cur.execute("DELETE FROM courses WHERE id=%s AND teacher_id=%s",(course_id,request.teacher_id))
    db.close(); return success()

# ======= 成绩管理 =======
@app.route('/api/scores', methods=['GET'])
@teacher_required
def get_scores():
    cid=request.args.get('course_id',''); clid=request.args.get('class_id','')
    if not cid or not clid: return err('course_id 和 class_id 不能为空')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT s.* FROM scores s JOIN courses co ON co.id=s.course_id WHERE s.course_id=%s AND s.class_id=%s AND co.teacher_id=%s ORDER BY s.student_name",(cid,clid,request.teacher_id))
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

@app.route('/api/scores', methods=['POST'])
@teacher_required
def update_scores():
    items=(request.get_json() or {}).get('items') or []
    db=get_db(); cur=db.cursor()
    for it in items:
        cid=str(it.get('course_id','')); clid=str(it.get('class_id',''))
        sid=int(it.get('student_id',0)); sname=it.get('student_name','')
        att=int(it.get('att_score',0)); inter=int(it.get('interact_score',0)); hw=int(it.get('hw_score',0))
        cur.execute("INSERT INTO scores (course_id,class_id,student_id,student_name,att_score,interact_score,hw_score) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE att_score=VALUES(att_score),interact_score=VALUES(interact_score),hw_score=VALUES(hw_score)",(cid,clid,sid,sname,att,inter,hw))
    db.close(); return success()

@app.route('/api/scores/config', methods=['GET'])
@teacher_required
def get_score_config():
    cid=request.args.get('course_id','')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM score_config WHERE course_id=%s",(cid,))
    row=cur.fetchone(); db.close()
    return success(_row(row) or {'course_id':cid,'att_max':30,'interact_max':20,'hw_max':50})

@app.route('/api/scores/config', methods=['POST'])
@teacher_required
def save_score_config():
    d=request.get_json() or {}; cid=str(d.get('course_id',''))
    db=get_db(); cur=db.cursor()
    cur.execute("INSERT INTO score_config (course_id,att_max,interact_max,hw_max) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE att_max=VALUES(att_max),interact_max=VALUES(interact_max),hw_max=VALUES(hw_max)",(cid,d.get('att_max',30),d.get('interact_max',20),d.get('hw_max',50)))
    db.close(); return success()

# ======= 考勤 =======
_att_sessions={}   # 内存会话：session_key → {course_id, class_id, teacher_id, start_time, active}
                   # signed_names 从 attendance_records DB 实时查询，不再存内存

def _cleanup_expired_tokens():
    """定时清理过期的 att_tokens（每5分钟执行一次）"""
    while True:
        time.sleep(300)  # 5分钟
        try:
            db = get_db(); cur = db.cursor()
            cur.execute("DELETE FROM att_tokens WHERE expire_at < %s AND token_type='scan'", (int(time.time()),))
            affected = cur.rowcount
            db.commit(); db.close()
            if affected > 0:
                logger.info("[考勤] 清理过期 scan_token %d 条", affected)
        except Exception as e:
            logger.error("[考勤] 清理 token 失败: %s", e)

def _cleanup_expired_sessions():
    """定时清理 24 小时前非活跃的 _att_sessions（每1小时执行一次）"""
    while True:
        time.sleep(3600)  # 1小时
        try:
            cutoff = datetime.now() - timedelta(hours=24)
            expired_keys = []
            for k, v in _att_sessions.items():
                if not v.get('active') and v.get('start_time', datetime.now()) < cutoff:
                    expired_keys.append(k)
            for k in expired_keys:
                del _att_sessions[k]
            if expired_keys:
                logger.info("[考勤] 清理过期 session %d 条", len(expired_keys))
        except Exception as e:
            logger.error("[考勤] 清理 session 失败: %s", e)

# ── 启动后台清理线程 ──
threading.Thread(target=_cleanup_expired_tokens, daemon=True).start()
threading.Thread(target=_cleanup_expired_sessions, daemon=True).start()

# ── 数据库 token 表（MEMORY 引擎，所有 worker 共享）──
def _init_token_tables():
    """启动时初始化 MEMORY 表（MySQL）"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS att_tokens (
                token      VARCHAR(64) PRIMARY KEY,
                token_type ENUM('scan','sign') NOT NULL,
                course_id  VARCHAR(32),
                class_id   VARCHAR(32),
                session_key VARCHAR(256),
                device_fp  VARCHAR(128),
                expire_at  BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_key (session_key),
                INDEX idx_expire (expire_at)
            ) ENGINE=MEMORY
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS att_device_sessions (
                device_fp  VARCHAR(128) PRIMARY KEY,
                course_id  VARCHAR(32),
                class_id   VARCHAR(32),
                session_key VARCHAR(256)
            ) ENGINE=MEMORY
        """)
        db.commit()
        logger.info("[考勤] att_tokens / att_device_sessions 初始化完成")
    finally:
        cur.close(); db.close()

def _ensure_indexes():
    """确保关键索引存在（3000并发优化）"""
    db = get_db(); cur = db.cursor()
    indexes = [
        # 考勤表索引
        ("idx_att_session_sign", "attendance_records", "session_key, sign_time"),
        ("idx_att_course_class", "attendance_records", "course_id, class_id"),
        # 作业提交表索引
        ("idx_sub_hw_student", "homework_submissions", "homework_id, student_id"),
        ("idx_sub_student", "homework_submissions", "student_id"),
        # 学生表索引
        ("idx_student_class", "students", "class_id"),
        # 考勤报表索引
        ("idx_report_teacher", "attendance_reports", "teacher_id, ended_at"),
        # 考勤学生明细索引
        ("idx_stu_rec_report", "attendance_student_records", "report_id"),
        # 考勤会话索引
        ("idx_att_tokens_expire", "att_tokens", "expire_at"),
        ("idx_att_tokens_session", "att_tokens", "session_key"),
    ]
    for idx_name, tbl, cols in indexes:
        try:
            cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl} ({cols})")
            logger.debug(f"[索引] {idx_name} ON {tbl}({cols}) ✓")
        except Exception as e:
            logger.debug(f"[索引] {idx_name} 跳过: {e}")
    try:
        db.commit()
        logger.info("[索引] 关键索引检查完成")
    finally:
        cur.close(); db.close()

def _db_scan_token_create(token, cid, clid, expire_at):
    """生成扫码令牌（写入 DB + 内存备查）"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("DELETE FROM att_tokens WHERE token=%s AND token_type='scan'", (token,))
        cur.execute(
            "INSERT INTO att_tokens (token,token_type,course_id,class_id,expire_at) VALUES (%s,'scan',%s,%s,%s)",
            (token, cid, clid, expire_at)
        )
        db.commit()
    finally:
        cur.close(); db.close()

def _db_scan_token_get(token):
    """查询扫码令牌是否存在且未过期"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute(
            "SELECT course_id,class_id FROM att_tokens WHERE token=%s AND token_type='scan' AND expire_at>%s",
            (token, int(time.time()))
        )
        r = cur.fetchone()
        return r
    finally:
        cur.close(); db.close()

def _db_scan_token_del(token):
    """消耗扫码令牌"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("DELETE FROM att_tokens WHERE token=%s AND token_type='scan'", (token,))
        db.commit()
    finally:
        cur.close(); db.close()

def _db_sign_token_create(sign_token, cid, clid, sk, device_fp, expire_at):
    """生成签到令牌"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("DELETE FROM att_tokens WHERE token=%s AND token_type='sign'", (sign_token,))
        cur.execute(
            "INSERT INTO att_tokens (token,token_type,course_id,class_id,session_key,device_fp,expire_at) VALUES (%s,'sign',%s,%s,%s,%s,%s)",
            (sign_token, cid, clid, sk, device_fp, expire_at)
        )
        db.commit()
    finally:
        cur.close(); db.close()

def _db_sign_token_get(sign_token):
    """查询签到令牌"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute(
            "SELECT course_id,class_id,session_key,device_fp FROM att_tokens WHERE token=%s AND token_type='sign' AND expire_at>%s",
            (sign_token, int(time.time()))
        )
        return cur.fetchone()
    finally:
        cur.close(); db.close()

def _db_sign_token_del(sign_token):
    """消耗签到令牌"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("DELETE FROM att_tokens WHERE token=%s AND token_type='sign'", (sign_token,))
        db.commit()
    finally:
        cur.close(); db.close()

def _db_device_lock(device_fp, cid, clid, sk):
    """设备指纹加锁"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO att_device_sessions (device_fp,course_id,class_id,session_key) VALUES (%s,%s,%s,%s)",
            (device_fp, cid, clid, sk)
        )
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
    finally:
        cur.close(); db.close()

def _db_device_check(device_fp, sk):
    """检查设备是否已签到本轮次（精确匹配 session_key）"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute(
            "SELECT session_key FROM att_device_sessions WHERE device_fp=%s",
            (device_fp,)
        )
        r = cur.fetchone()
        # 必须精确匹配 session_key，防止跨会话误判
        if r and r['session_key'] == sk:
            return r
        return None
    finally:
        cur.close(); db.close()

def _db_device_unlock_course(cid, clid):
    """清除本课程+班级的所有设备锁"""
    db = get_db(); cur = db.cursor()
    try:
        # 同时清除设备锁和 sign_token（学生需要重新扫码获取新 token）
        cur.execute("DELETE FROM att_device_sessions WHERE course_id=%s AND class_id=%s", (cid, clid))
        cur.execute("DELETE FROM att_tokens WHERE course_id=%s AND class_id=%s AND token_type='sign'", (cid, clid))
        db.commit()
        logger.debug("[设备锁] 课程=%s 班级=%s 设备锁和sign_token已清除", cid, clid)
    except Exception as e:
        logger.warning("[设备锁] 清除失败: %s", e)
        db.rollback()
    finally:
        cur.close(); db.close()

def _db_signed_names(sk):
    """从数据库实时查询已签到名单（替代内存 signed_names set）"""
    db = get_db(); cur = db.cursor()
    try:
        cur.execute(
            "SELECT DISTINCT student_name FROM attendance_records WHERE session_key LIKE %s",
            (sk + '%',)
        )
        return [r['student_name'] for r in cur.fetchall()]
    finally:
        cur.close(); db.close()

@app.route('/api/attendance/start', methods=['POST'])
@teacher_required
def att_start():
    d=request.get_json() or {}
    cid=str(d.get('course_id','')); clid=str(d.get('class_id',''))
    token=secrets.token_hex(8); ts=int(time.time()//15)
    sk=f"{cid}:{clid}:{token}:{ts}"
    # 每次开启签到：清空旧 session
    for k in list(_att_sessions.keys()):
        if _att_sessions[k]['course_id']==cid and _att_sessions[k]['class_id']==clid: _att_sessions[k]['active']=False
    _att_sessions[sk]={'_sk':sk,'course_id':cid,'class_id':clid,'teacher_id':request.teacher_id,'start_time':datetime.now(),'active':True}
    # 清除本课程+班级的设备锁（教师可重新分配设备）
    _db_device_unlock_course(cid, clid)
    st=secrets.token_hex(16); _db_scan_token_create(st, cid, clid, int(time.time())+10)
    return success({'session_key':sk,'qr_url':f"/sign?cid={cid}&clid={clid}&t={int(time.time()*1000)}&token={st}"})

@app.route('/api/attendance/qr', methods=['GET'])
@teacher_required
def att_qr():
    cid=request.args.get('course_id',''); clid=request.args.get('class_id','')
    # 复用同一个 session_key（每次刷新 QR，session_key 不变）
    active_sk = None
    for sk, sv in _att_sessions.items():
        if sv['course_id']==cid and sv['class_id']==clid and sv.get('active'):
            active_sk = sk
            break
    if not active_sk:
        token=secrets.token_hex(8); ts=int(time.time()//15)
        active_sk=f"{cid}:{clid}:{token}:{ts}"
        _att_sessions[active_sk]={'course_id':cid,'class_id':clid,'teacher_id':request.teacher_id,'start_time':datetime.now(),'active':True}
    st=secrets.token_hex(16); _db_scan_token_create(st, cid, clid, int(time.time())+10)
    return success({'qr_url':f"/sign?cid={cid}&clid={clid}&t={int(time.time()*1000)}&token={st}",'token':st,'session_key':active_sk})

@app.route('/api/attendance/current_session', methods=['GET'])
@teacher_required
def att_current_session():
    """返回当前活跃会话的已签到名单（从 DB 实时查询）"""
    cid = request.args.get('course_id', ''); clid = request.args.get('class_id', '')
    if not cid or not clid: return err('course_id 和 class_id 不能为空')
    for sk, sv in _att_sessions.items():
        if sv['course_id'] == cid and sv['class_id'] == clid and sv.get('active'):
            signed_names = _db_signed_names(sk)
            return success({'session_key': sk, 'signed_names': signed_names})
    return err('无进行中的签到', 404)

@app.route('/api/attendance/reset', methods=['POST'])
@teacher_required
def att_reset():
    cid=request.args.get('cid','') or (request.get_json() or {}).get('course_id','')
    if not cid: return err('course_id 不能为空')
    for k,v in _att_sessions.items():
        if v['course_id']==cid and v['teacher_id']==request.teacher_id: v['active']=False
    return success()

@app.route('/api/attendance/list', methods=['GET'])
@teacher_required
def att_list():
    cid=request.args.get('course_id',''); clid=request.args.get('class_id','')
    db=get_db(); cur=db.cursor()
    sql="SELECT student_name as name, MAX(sign_time) as time FROM attendance_records WHERE course_id=%s"
    params=[cid]
    if clid: sql+=" AND class_id=%s"; params.append(clid)
    sql+=" GROUP BY student_name ORDER BY time DESC LIMIT 200"
    cur.execute(sql,tuple(params))
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

@app.route('/api/attendance/manual', methods=['POST'])
@teacher_required
def att_manual():
    d=request.get_json() or {}
    cid=str(d.get('course_id','')); clid=str(d.get('class_id','')); name=(d.get('student_name') or '').strip()
    if not name: return err('学生姓名不能为空')
    
    # ── P0: 验证课程归属 ──
    db_check = get_db(); cur_check = db_check.cursor()
    cur_check.execute("SELECT id FROM courses WHERE id=%s AND teacher_id=%s", (cid, request.teacher_id))
    if not cur_check.fetchone():
        db_check.close()
        return err('无权操作此课程', 403)
    db_check.close()
    
    # 优先使用前端传来的 session_key（最可靠），其次从内存查找 QR 会话
    sk=d.get('session_key','').strip() or None
    if not sk:
        for k, v in _att_sessions.items():
            if v['course_id']==cid and v['class_id']==clid and v.get('active'):
                sk=k
                break
    
    # 如果找到 QR 会话 key，直接使用它（确保手动签到计入同一会话的报表）
    # 否则才用 manual: 前缀（表示这是一个独立的手动补签会话）
    if not sk:
        sk=f"{cid}:{clid}:manual:{int(time.time())}"
    
    # 签到记录的 session_key 格式：{sk}:{name}
    # 这样用 LIKE '{sk}%' 查询时，手动签到记录也会被包含（如果 sk 是 QR 会话 key）
    record_sk=f"{sk}:{name}"
    db=get_db(); cur=db.cursor()
    cur.execute("INSERT INTO attendance_records (session_key,course_id,class_id,student_name,sign_time) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE sign_time=VALUES(sign_time)",(record_sk,cid,clid,name,datetime.now()))
    db.close()
    # signed_names 始终从 DB 实时查询，无需手动更新内存
    return success({'message':'补签成功','session_key':sk})

@app.route('/api/attendance/apply_deduction', methods=['POST'])
@teacher_required
def att_deduction():
    d=request.get_json() or {}
    cid=str(d.get('course_id','')); clid=str(d.get('class_id','')); deduct=float(d.get('deduct_per_person',0))
    if deduct<=0: return err('扣分必须大于0')
    
    # ── P0: 验证课程归属 ──
    db_chk = get_db(); cur_chk = db_chk.cursor()
    cur_chk.execute("SELECT id FROM courses WHERE id=%s AND teacher_id=%s", (cid, request.teacher_id))
    if not cur_chk.fetchone():
        db_chk.close()
        return err('无权操作此课程', 403)
    db_chk.close()
    
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id,name FROM students WHERE class_id=%s",(clid,))
    students=cur.fetchall()
    cur.execute("SELECT student_name FROM attendance_records WHERE course_id=%s AND class_id=%s",(cid,clid))
    signed=set(r['student_name'] for r in cur.fetchall())
    
    # ── P2: 排除已请假的学生的考勤扣分 ──
    # 查询当前课程+班级的考勤报表中的请假学生
    cur.execute("""
        SELECT DISTINCT asr.student_name
        FROM attendance_reports ar
        JOIN attendance_student_records asr ON asr.report_id=ar.id
        WHERE ar.course_id=%s AND ar.class_id=%s AND asr.status='leave'
    """, (cid, clid))
    leave_students = set(r['student_name'] for r in cur.fetchall())
    
    updated=0
    for s in students:
        # 排除已签到和已请假的学生，只扣真正缺勤的
        if s['name'] not in signed and s['name'] not in leave_students:
            cur.execute("INSERT INTO scores (course_id,class_id,student_id,student_name,att_score) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE att_score=VALUES(att_score)",(cid,clid,s['id'],s['name'],-deduct))
            updated+=1
    db.close(); return success({'message':f'已为{updated}名未签到且未请假学生设置考勤扣分（已排除{len(leave_students)}名请假学生）'})

@app.route('/api/attendance/save_report', methods=['POST'])
@teacher_required
def att_save_report():
    d=request.get_json() or {}
    cid=str(d.get('course_id','')); clid=str(d.get('class_id',''))
    # 传入 session_key 则只查该会话的签到记录；不传则兼容旧逻辑（查所有历史）
    session_key = d.get('session_key', '')
    logger.debug("save_report: cid=%s, clid=%s, teacher=%s, session_key=%s", cid, clid, request.teacher_id, session_key)
    try:
        db=get_db(); cur=db.cursor()

        # 按 session_key 前缀过滤（精确匹配到本次会话）
        if session_key:
            # attendance_records.session_key 格式：{cid}:{clid}:{token}:{ts}:{name}
            # 同一会话的所有记录 session_key 以 session_key 开头
            cur.execute("""
                SELECT s.id, s.name, s.student_number,
                       ar.sign_time,
                       (ar.student_name IS NOT NULL) AS is_signed
                FROM students s
                LEFT JOIN (
                    SELECT student_name, MAX(sign_time) AS sign_time
                    FROM attendance_records
                    WHERE course_id=%s AND class_id=%s AND session_key LIKE %s
                    GROUP BY student_name
                ) ar ON ar.student_name=s.name
                WHERE s.class_id=%s
                ORDER BY s.name
            """, (cid, clid, session_key + '%', clid))
        else:
            # 兼容：不传 session_key 时按课程+班级查所有历史（跨会话汇总）
            cur.execute("""
                SELECT s.id, s.name, s.student_number,
                       ar.sign_time,
                       (ar.student_name IS NOT NULL) AS is_signed
                FROM students s
                LEFT JOIN (
                    SELECT student_name, MAX(sign_time) AS sign_time
                    FROM attendance_records
                    WHERE course_id=%s AND class_id=%s
                    GROUP BY student_name
                ) ar ON ar.student_name=s.name
                WHERE s.class_id=%s
                ORDER BY s.name
            """, (cid, clid, clid))
        rows=cur.fetchall()
        logger.debug("LEFT JOIN 返回 %d 行，signed=%d", len(rows), sum(1 for r in rows if r['is_signed']))
        db.close()

        total = len(rows)
        signed_count = sum(1 for r in rows if r['is_signed'])
        absent_count = total - signed_count

        db2=get_db(); cur2=db2.cursor()
        cur2.execute("SELECT name FROM courses WHERE id=%s",(cid,))
        course_row=cur2.fetchone(); course_name=course_row['name'] if course_row else ''
        cur2.execute("SELECT name FROM classes WHERE id=%s",(clid,))
        class_row=cur2.fetchone(); class_name=class_row['name'] if class_row else ''
        logger.debug("course_name=%s, class_name=%s", course_name, class_name)

        from datetime import datetime, timezone, timedelta
        def _parse_ts(v):
            if not v: return None
            v = str(v)
            # 处理 ISO 8601 UTC 格式 (带 Z 后缀)
            if v.endswith('Z'):
                dt_utc = datetime.fromisoformat(v.replace('Z', '+00:00'))
                # 转换为服务器本地时区
                local_tz = datetime.now().astimezone().tzinfo
                dt_local = dt_utc.astimezone(local_tz)
                return dt_local.strftime('%Y-%m-%d %H:%M:%S')
            # 处理已经是本地时间的格式：将 T 替换为空格后返回
            v = v.replace('T', ' ')
            return v[:19] if len(v) >= 19 else v
        started_at = _parse_ts(d.get('started_at',''))
        ended_at   = _parse_ts(d.get('ended_at',''))

        cur2.execute("""
            INSERT INTO attendance_reports (teacher_id,course_id,class_id,course_name,class_name,
            started_at,ended_at,total_students,signed_count,absent_count)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,(request.teacher_id,cid,clid,course_name,class_name,
             started_at, ended_at,
             total,signed_count,absent_count))
        rid=cur2.lastrowid
        logger.debug("INSERT report rid=%s", rid)

        for r in rows:
            status = 'signed' if r['is_signed'] else 'absent'
            sign_time = _parse_ts(r['sign_time']) if r['is_signed'] else None
            cur2.execute("""
                INSERT INTO attendance_student_records (report_id,student_id,student_name,student_number,status,sign_time)
                VALUES (%s,%s,%s,%s,%s,%s)
            """,(rid,r['id'],r['name'],r['student_number'],status,sign_time))

        db2.close()
        logger.debug("save_report 成功 rid=%s", rid)
        return success({'report_id':rid,'signed_count':signed_count,'absent_count':absent_count})
    except Exception as e:
        logger.exception("[ERROR save_report] %s", e)
        return err(str(e))

@app.route('/api/attendance/reports', methods=['GET'])
@teacher_required
def att_reports():
    cid=request.args.get('course_id',''); clid=request.args.get('class_id','')
    page=int(request.args.get('page',1)); ps=int(request.args.get('page_size',15))
    offset=(page-1)*ps
    db=get_db(); cur=db.cursor()
    # 统计总数
    count_sql="SELECT COUNT(*) as total FROM attendance_reports WHERE teacher_id=%s"; count_params=[request.teacher_id]
    if cid: count_sql+=" AND course_id=%s"; count_params.append(cid)
    if clid: count_sql+=" AND class_id=%s"; count_params.append(clid)
    cur.execute(count_sql,count_params)
    total=cur.fetchone()['total']
    # 查询列表（带分页）
    sql="SELECT * FROM attendance_reports WHERE teacher_id=%s"; params=[request.teacher_id]
    if cid: sql+=" AND course_id=%s"; params.append(cid)
    if clid: sql+=" AND class_id=%s"; params.append(clid)
    sql+=" ORDER BY ended_at DESC LIMIT %s OFFSET %s"; params.extend([ps,offset])
    cur.execute(sql,params); rows=cur.fetchall(); db.close()
    return success({'reports':_rows(rows),'total':total,'page':page,'page_size':ps})

@app.route('/api/attendance/report/<int:rid>', methods=['GET'])
@teacher_required
def att_report_detail(rid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM attendance_reports WHERE id=%s AND teacher_id=%s",(rid,request.teacher_id))
    r=cur.fetchone()
    if not r: db.close(); return err('报告不存在',404)
    r=_row(r)
    cur.execute("SELECT * FROM attendance_student_records WHERE report_id=%s ORDER BY student_name",(rid,))
    r['students']=_rows(cur.fetchall())
    db.close(); return success(r)

@app.route('/api/attendance/student_status', methods=['PUT'])
@teacher_required
def att_update_status():
    d=request.get_json() or {}
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE attendance_student_records SET status=%s,note=%s,updated_by=%s,updated_at=NOW() WHERE id=%s",(d.get('status',''),d.get('note',''),request.teacher_id,int(d.get('record_id',0))))
    db.close(); return success()

@app.route('/api/attendance/report/<int:rid>', methods=['DELETE'])
@teacher_required
def att_delete_report(rid):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM attendance_student_records WHERE report_id=%s",(rid,))
    cur.execute("DELETE FROM attendance_reports WHERE id=%s AND teacher_id=%s",(rid,request.teacher_id))
    db.close(); return success()

# ======= 作业管理（教师端） =======
def _homework_detail(hw, cur):
    """将单个作业 dict 补全 attachments / 评分脚本 / 统计"""
    hid=hw['id']
    cur.execute("SELECT * FROM homework_attachments WHERE homework_id=%s",(hid,))
    hw['attachments']=_rows(cur.fetchall())
    cur.execute("SELECT * FROM homework_grading_scripts WHERE homework_id=%s",(hid,))
    gs=_row(cur.fetchone()); hw['grading_script_info']={}
    if gs:
        hw['grading_script_info']={'homework_id':hid,'script_name':os.path.basename(gs.get('script_path','')),'auto_grade_enabled':bool(hw.get('auto_grade_enabled')),'has_grading_script':True}
    cur.execute("SELECT COUNT(*) as total,SUM(CASE WHEN score IS NOT NULL OR auto_score IS NOT NULL THEN 1 ELSE 0 END) as graded FROM homework_submissions WHERE homework_id=%s",(hid,))
    st=cur.fetchone(); hw['total_submissions']=st['total']; hw['graded_count']=st['graded']
    return hw

@app.route('/api/homework/<int:hid>', methods=['GET'])
@teacher_required
def get_homework_detail(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT h.*,c.name as course_name,cl.name as class_name FROM homework h JOIN courses c ON c.id=h.course_id LEFT JOIN classes cl ON cl.id=h.class_id WHERE h.id=%s AND c.teacher_id=%s",(hid,request.teacher_id))
    hw=_row(cur.fetchone())
    if not hw: return err('作业不存在或无权限',404)
    hw=_homework_detail(hw,cur)
    db.close(); return success(hw)

@app.route('/api/homework', methods=['GET'])
@teacher_required
def get_homework_list():
    cid=request.args.get('course_id',''); clid=request.args.get('class_id','')
    db=get_db(); cur=db.cursor()
    sql="SELECT h.*,c.name as course_name,cl.name as class_name FROM homework h JOIN courses c ON c.id=h.course_id LEFT JOIN classes cl ON cl.id=h.class_id WHERE c.teacher_id=%s"
    params=[request.teacher_id]
    if cid: sql+=" AND h.course_id=%s"; params.append(cid)
    if clid: sql+=" AND h.class_id=%s"; params.append(clid)
    sql+=" ORDER BY h.created_at DESC"
    cur.execute(sql,params); homeworks=_rows(cur.fetchall())
    for hw in homeworks:
        hid=hw['id']
        cur.execute("SELECT * FROM homework_attachments WHERE homework_id=%s",(hid,))
        hw['attachments']=_rows(cur.fetchall())
        cur.execute("SELECT * FROM homework_grading_scripts WHERE homework_id=%s",(hid,))
        gs=_row(cur.fetchone())
        if gs:
            hw['grading_script_info']={'homework_id':hid,'script_name':os.path.basename(gs.get('script_path','')),'auto_grade_enabled':bool(hw.get('auto_grade_enabled')),'has_grading_script':True}
        else:
            hw['grading_script_info']={'homework_id':hid,'has_grading_script':False,'auto_grade_enabled':bool(hw.get('auto_grade_enabled'))}
        cur.execute("SELECT COUNT(*) as total,SUM(CASE WHEN score IS NOT NULL OR auto_score IS NOT NULL THEN 1 ELSE 0 END) as graded FROM homework_submissions WHERE homework_id=%s",(hid,))
        st=cur.fetchone(); hw['total_submissions']=st['total']; hw['graded_count']=st['graded']
    db.close(); return success(homeworks)

def _parse_deadline(dl):
    if not dl: return None
    s = str(dl).strip()
    if 'T' in s:
        # datetime-local 输入格式: 2026-04-20T23:59 (无秒) 或 2026-04-20T23:59:00 (有秒)
        # 统一补零到 19 位
        s = (s + ':00')[:19]
        try: return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
        except: pass
    else:
        for fmt in ['%Y-%m-%d','%a, %d %b %Y']:
            try: return datetime.strptime(s[:10], fmt)
            except: pass
    return None

@app.route('/api/homework', methods=['POST'])
@teacher_required
def create_homework():
    ct=request.content_type or ''
    if 'multipart' in ct:
        title=request.form.get('title','').strip(); content=request.form.get('content','').strip()
        cid=request.form.get('course_id','').strip(); clid=request.form.get('class_id','').strip()
        dl=request.form.get('deadline',''); ts=int(request.form.get('total_score',100))
    else:
        d=request.get_json() or {}; title=(d.get('title') or '').strip(); content=(d.get('content') or '').strip()
        cid=str(d.get('course_id','')); clid=str(d.get('class_id','')); dl=d.get('deadline',''); ts=int(d.get('total_score',100))
    if not title or not cid: return err('标题和课程不能为空')
    db=get_db(); cur=db.cursor()
    cur.execute("INSERT INTO homework (course_id,class_id,teacher_id,title,content,deadline,total_score,is_published) VALUES (%s,%s,%s,%s,%s,%s,%s,1)",(cid,clid,request.teacher_id,title,content,_parse_deadline(dl),ts))
    hid=cur.lastrowid
    attachments = []
    if 'multipart' in ct:
        for f in request.files.getlist('files'):
            if f.filename:
                fn=f.filename; ext=os.path.splitext(fn)[1]; sn=f"{uuid.uuid4().hex}{ext}"
                fp=os.path.join(UPLOAD_DIR,'homework',sn); f.save(fp)
                sz=os.path.getsize(fp)
                cur.execute("INSERT INTO homework_attachments (homework_id,file_name,file_path,file_size) VALUES (%s,%s,%s,%s)",(hid,fn,fp,sz))
                attachments.append({'id':cur.lastrowid,'filename':fn,'file_path':fp,'file_size':sz})
    
    # 创建作业通知，通知班级所有学生
    deadline_str = _parse_deadline(dl).strftime('%Y-%m-%d %H:%M') if _parse_deadline(dl) else '未定'
    _create_homework_notifications(hid, cid, clid, title, deadline_str)
    
    db.close()
    return success({'id':hid,'attachments':attachments,'is_published':1,'auto_grade_enabled':False})

@app.route('/api/homework/<int:hid>', methods=['PUT'])
@teacher_required
def update_homework(hid):
    ct=request.content_type or ''
    if 'multipart' in ct:
        title=request.form.get('title','').strip(); content=request.form.get('content','').strip()
        dl=request.form.get('deadline',''); ts=int(request.form.get('total_score',100))
    else:
        d=request.get_json() or {}; title=(d.get('title') or '').strip(); content=(d.get('content') or '').strip()
        dl=d.get('deadline',''); ts=int(d.get('total_score',100))
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE homework SET title=%s,content=%s,deadline=%s,total_score=%s WHERE id=%s AND teacher_id=%s",(title,content,_parse_deadline(dl),ts,hid,request.teacher_id))
    if 'multipart' in ct:
        for f in request.files.getlist('files'):
            if f.filename:
                fn=f.filename; sn=f"{uuid.uuid4().hex}{os.path.splitext(fn)[1]}"
                fp=os.path.join(UPLOAD_DIR,'homework',sn); f.save(fp)
                cur.execute("INSERT INTO homework_attachments (homework_id,file_name,file_path,file_size) VALUES (%s,%s,%s,%s)",(hid,fn,fp,os.path.getsize(fp)))
    db.close(); return success()

@app.route('/api/homework/<int:hid>', methods=['DELETE'])
@teacher_required
def delete_homework(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM homework WHERE id=%s AND teacher_id=%s",(hid,request.teacher_id))
    db.close(); return success()

@app.route('/api/homework/attachments/<int:aid>', methods=['DELETE'])
@teacher_required
def delete_hw_attachment(aid):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM homework_attachments WHERE id=%s",(aid,))
    db.close(); return success()

# ======= 课程资源管理 =======
@app.route('/api/resources', methods=['GET'])
@teacher_required
def get_resources():
    """获取课程资源列表"""
    course_id = request.args.get('course_id', '')
    term = request.args.get('term', '')
    db=get_db(); cur=db.cursor()
    sql = "SELECT * FROM course_resources WHERE teacher_id=%s"
    params = [request.teacher_id]
    if course_id:
        sql += " AND course_id=%s"
        params.append(course_id)
    if term:
        sql += " AND term=%s"
        params.append(term)
    sql += " ORDER BY created_at DESC"
    cur.execute(sql, params)
    return success(_rows(cur.fetchall()))

@app.route('/api/resources/<int:rid>', methods=['DELETE'])
@teacher_required
def delete_resource(rid):
    """删除课程资源"""
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT file_path FROM course_resources WHERE id=%s AND teacher_id=%s",(rid,request.teacher_id))
    r=cur.fetchone()
    if not r: db.close(); return err('资源不存在',404)
    # 删除物理文件
    try:
        fp=os.path.join(BASE_DIR,r['file_path'])
        if os.path.exists(fp): os.remove(fp)
    except: pass
    cur.execute("DELETE FROM course_resources WHERE id=%s",(rid,))
    db.close(); return success()

@app.route('/api/resources/upload', methods=['POST'])
@teacher_required
def upload_resource():
    """上传课程资源"""
    course_id=request.form.get('course_id','')
    course_name=request.form.get('course_name','')
    term=request.form.get('term','')
    title=request.form.get('title','')
    description=request.form.get('description','')
    if not course_id or not title: return err('课程ID和标题不能为空')
    if 'file' not in request.files: return err('请选择要上传的文件')
    f=request.files['file']
    if not f.filename: return err('请选择要上传的文件')
    # 保存文件
    ext=os.path.splitext(f.filename)[1]
    fname=f"{uuid.uuid4().hex}{ext}"
    save_dir=os.path.join(UPLOAD_DIR,'resources')
    os.makedirs(save_dir,exist_ok=True)
    fpath=os.path.join(save_dir,fname)
    f.save(fpath)
    # 写入数据库
    db=get_db(); cur=db.cursor()
    cur.execute("""INSERT INTO course_resources
        (course_id,course_name,term,teacher_id,title,description,file_name,file_path,file_size,file_type)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (course_id,course_name,term,request.teacher_id,title,description,
         f.filename,f'uploads/resources/{fname}',os.path.getsize(fpath),ext))
    db.close()
    return success({'message':'上传成功'})

@app.route('/api/resources/download/<int:rid>', methods=['GET'])
@teacher_required
def download_resource(rid):
    """下载课程资源"""
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM course_resources WHERE id=%s",(rid,))
    r=cur.fetchone()
    if not r: db.close(); return err('资源不存在',404)
    fpath=os.path.join(BASE_DIR,r['file_path'])
    if not os.path.exists(fpath): db.close(); return err('文件不存在',404)
    db.close()
    return send_file(fpath,as_attachment=True,download_name=r['file_name'])

@app.route('/api/student/resources', methods=['GET'])
@student_required
def get_student_resources():
    """学生端获取课程资源"""
    course_id=request.args.get('course_id','')
    term=request.args.get('term','')
    db=get_db(); cur=db.cursor()
    # 获取学生可选的课程
    cur.execute("SELECT DISTINCT c.id,c.name,c.term FROM courses c JOIN course_classes cc ON cc.course_id=c.id JOIN students s ON s.class_id=cc.class_id WHERE s.id=%s",(request.teacher_id,))
    courses=cur.fetchall()
    if not courses: return success([])
    course_ids=[str(c['id']) for c in courses]
    # 查询资源
    sql="SELECT * FROM course_resources WHERE course_id IN ("+",".join(["%s"]*len(course_ids))+")"
    params=course_ids
    if course_id:
        sql+=" AND course_id=%s"
        params.append(course_id)
    if term:
        sql+=" AND term=%s"
        params.append(term)
    sql+=" ORDER BY created_at DESC"
    cur.execute(sql,params)
    db.close()
    return success(_rows(cur.fetchall()))

@app.route('/api/student/resources/download/<int:rid>', methods=['GET'])
@student_required
def student_download_resource(rid):
    """学生端下载课程资源"""
    db=get_db(); cur=db.cursor()
    # 获取学生可选的课程
    cur.execute("SELECT DISTINCT c.id FROM courses c JOIN course_classes cc ON cc.course_id=c.id JOIN students s ON s.class_id=cc.class_id WHERE s.id=%s",(request.teacher_id,))
    courses=cur.fetchall()
    if not courses:
        db.close(); return err('无权限访问',403)
    course_ids=[str(c['id']) for c in courses]
    # 验证资源属于该学生的课程
    placeholders=','.join(['%s']*len(course_ids))
    cur.execute(f"SELECT * FROM course_resources WHERE id=%s AND course_id IN ({placeholders})",[rid]+course_ids)
    r=cur.fetchone()
    if not r:
        db.close(); return err('资源不存在或无权限',404)
    fpath=os.path.join(os.path.dirname(__file__),r['file_path'])
    db.close()
    if not os.path.exists(fpath): return err('文件不存在',404)
    return send_file(fpath,as_attachment=True,download_name=r['file_name'])

@app.route('/api/homework/<int:hid>/submissions', methods=['GET'])
@teacher_required
def get_hw_submissions(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT h.*,c.teacher_id FROM homework h JOIN courses c ON c.id=h.course_id WHERE h.id=%s",(hid,))
    hw=cur.fetchone()
    if not hw: db.close(); return err('作业不存在',404)
    clid=str(hw['class_id']) if hw['class_id'] else ''
    if clid:
        cur.execute("SELECT id,name FROM students WHERE class_id=%s ORDER BY name",(clid,))
        students={str(r['id']):r['name'] for r in cur.fetchall()}
        total=len(students)
    else: students={}; total=0
    cur.execute("SELECT * FROM homework_submissions WHERE homework_id=%s ORDER BY submitted_at",(hid,))
    subs=_rows(cur.fetchall())
    for s in subs:
        cur.execute("SELECT * FROM submission_attachments WHERE submission_id=%s",(s['id'],))
        s['attachments']=_rows(cur.fetchall())
        cur.execute("SELECT * FROM grade_attachments WHERE submission_id=%s",(s['id'],))
        s['grade_attachments']=_rows(cur.fetchall())
    graded=sum(1 for s in subs if s.get('score') is not None or s.get('auto_score') is not None)
    db.close(); return success({'submissions':subs,'total_students':total,'graded_count':graded})

@app.route('/api/homework/<int:hid>/grade', methods=['POST'])
@teacher_required
def grade_hw(hid):
    ct=request.content_type or ''
    if 'multipart' in ct:
        sid=int(request.form.get('student_id',0)); score=float(request.form.get('score',0)); feedback=request.form.get('feedback','').strip()
    else:
        d=request.get_json() or {}; sid=int(d.get('student_id',0)); score=float(d.get('score',0)); feedback=(d.get('feedback') or '').strip()
    # 根据分数自动生成评语（用户未填写时）
    if not feedback:
        if score >= 80:
            feedback = '优秀，继续保持！'
        elif score >= 60:
            feedback = '良好，还有进步空间！'
        else:
            feedback = '继续加油，争取更好成绩！'
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM homework_submissions WHERE homework_id=%s AND student_id=%s",(hid,sid))
    sub=cur.fetchone()
    if not sub: db.close(); return err('未找到该学生的提交记录')
    cur.execute("UPDATE homework_submissions SET score=%s,feedback=%s,graded_at=NOW() WHERE homework_id=%s AND student_id=%s",(score,feedback,hid,sid))
    # 更新排行榜（重新统计该学生每个作业的最新分数）
    cur.execute("SELECT h.class_id,hs.student_id,hs.student_name FROM homework h JOIN homework_submissions hs ON hs.homework_id=h.id WHERE hs.id=%s",(sub['id'],))
    info=cur.fetchone()
    if info and info['class_id']:
        cur.execute("""
            SELECT SUM(hs2.score) as total, COUNT(*) as cnt
            FROM (
                SELECT hs.homework_id, hs.score,
                       ROW_NUMBER() OVER (PARTITION BY hs.student_id, hs.homework_id ORDER BY hs.submitted_at DESC) as rn
                FROM homework_submissions hs
                JOIN homework h2 ON h2.id = hs.homework_id
                WHERE hs.student_id = %s AND hs.score IS NOT NULL AND h2.class_id = %s
            ) hs2
            WHERE hs2.rn = 1
        """, (info['student_id'], info['class_id']))
        stats=cur.fetchone()
        new_total=float(stats['total'] or 0); new_count=int(stats['cnt'] or 0)
        cur.execute("SELECT id FROM homework_score_ranking WHERE class_id=%s AND student_id=%s",(info['class_id'],info['student_id']))
        ex=cur.fetchone()
        if ex:
            cur.execute("UPDATE homework_score_ranking SET total_score=%s,homework_count=%s WHERE id=%s",(new_total,new_count,ex['id']))
        else:
            cur.execute("INSERT INTO homework_score_ranking (class_id,student_id,student_name,total_score,homework_count) VALUES (%s,%s,%s,%s,%s)",(info['class_id'],info['student_id'],info['student_name'],new_total,new_count))
    db.close(); return success({'message':'评分成功'})

@app.route('/api/homework/batch_update_feedback', methods=['POST'])
@admin_required
def batch_update_feedback():
    """批量为没有评语的作业根据分数添加评语"""
    db = get_db(); cur = db.cursor()
    # 查询所有没有评语但有分数的提交
    cur.execute("""
        SELECT id, score, student_name 
        FROM homework_submissions 
        WHERE score IS NOT NULL 
        AND (feedback IS NULL OR feedback = '')
    """)
    records = cur.fetchall()
    
    def gen_feedback(score):
        if score >= 80:
            return '优秀，继续保持！'
        elif score >= 60:
            return '良好，还有进步空间！'
        else:
            return '继续加油，争取更好成绩！'
    
    updated = 0
    for rec in records:
        sid, score, name = rec['id'], rec['score'], rec['student_name']
        feedback = gen_feedback(score)
        cur.execute("UPDATE homework_submissions SET feedback=%s WHERE id=%s", (feedback, sid))
        updated += 1
    
    db.commit()
    logger.info(f"[批量更新] 为 {updated} 条作业添加评语")
    db.close()
    return success({'message': f'已为 {updated} 条作业添加评语', 'updated': updated})

@app.route('/api/homework/ranking', methods=['GET'])
@teacher_required
def get_hw_ranking():
    """获取班级天梯榜，支持按 course_id 筛选（每个课程+班级各自独立排名）"""
    course_id = request.args.get('course_id', '')
    class_id = request.args.get('class_id', '')
    if not course_id or not class_id:
        return err('course_id 和 class_id 不能为空')

    db = get_db()
    cur = db.cursor()

    # 按课程+班级统计：只统计该课程下的作业分数
    cur.execute("""
        SELECT s.id as student_id, s.name as student_name, s.class_id,
               COALESCE(SUM(hs2.score), 0) as total_score,
               COUNT(DISTINCT hs2.homework_id) as homework_count
        FROM students s
        LEFT JOIN (
            SELECT hs.homework_id, hs.student_id, hs.score,
                   ROW_NUMBER() OVER (PARTITION BY hs.student_id, hs.homework_id ORDER BY hs.submitted_at DESC) as rn
            FROM homework_submissions hs
            JOIN homework h ON h.id = hs.homework_id
            WHERE h.course_id = %s AND h.class_id = %s AND hs.score IS NOT NULL
        ) hs2 ON hs2.student_id = s.id AND hs2.rn = 1
        WHERE s.class_id = %s
        GROUP BY s.id, s.name, s.class_id
        ORDER BY total_score DESC, s.id ASC
    """, (str(course_id), str(class_id), str(class_id)))

    rows = cur.fetchall()
    ranked_list = []
    for idx, r in enumerate(rows):
        item = dict(r)
        item['rank'] = idx + 1
        ranked_list.append(item)

    db.close()
    return success(_rows(ranked_list))

# ======= 评分脚本 =======
def _run_grading(script_path, files, hid, sid, total_score):
    """运行 Python 评分脚本，自动归一化分数并写回 homework_submissions"""
    try:
        db=get_db(); cur=db.cursor()
        cur.execute("UPDATE homework_submissions SET grading_status='grading' WHERE id=%s",(sid,))
        db.close()
        # 取第一个文件的绝对路径传给脚本（评分脚本规范：stdin 接收 file_path）
        # file_path 在数据库中存的是 "submissions/xxx.xlsx"（相对 uploads 目录）
        # 需要拼接 UPLOAD_DIR 转成绝对路径，避免 cwd 变化导致文件找不到
        raw = files[0]['path'] if files else ''
        if os.path.isabs(raw):
            file_path = raw
        elif os.path.exists(raw):        # 兼容已存绝对路径的老数据
            file_path = raw
        else:
            file_path = os.path.normpath(os.path.join(UPLOAD_DIR, raw))
        inp=json.dumps({'file_path': file_path, 'files': files, 'homework_id': hid, 'submission_id': sid})
        env=os.environ.copy(); env['PYTHONIOENCODING']='utf-8'; env['PYTHONUTF8']='1'
        # 用 bytes 捕获避免 Windows GBK 编码问题，手动 decode 为 utf-8
        res=subprocess.run(['python', script_path], input=inp.encode('utf-8'), capture_output=True, timeout=60, cwd=os.path.dirname(script_path), env=env)
        out=res.stdout.decode('utf-8', errors='replace').strip()
        if res.returncode!=0: raise Exception(f"Script error: {res.stderr.decode('utf-8', errors='replace')}")
        gr=json.loads(out) if out else {}
        auto_score=gr.get('score',0); max_score=gr.get('max_score',100)
        script_msg=gr.get('message',''); details=gr.get('details',{})
        norm=round(auto_score/max_score*total_score,2) if max_score>0 else 0
        # 若脚本未返回评语，或评语为空，按分数档位自动生成
        if not script_msg:
            norm_int=int(norm)
            if norm_int>=90:   msg='优秀，继续保持！'
            elif norm_int>=80: msg='优秀，再接再厉！'
            elif norm_int>=70: msg='良好，继续保持！'
            elif norm_int>=60: msg='良好，加油！'
            else:              msg=f'不及格（{norm_int}分），请认真完成下次作业！'
        else:
            msg=script_msg
        db2=get_db(); cur2=db2.cursor()
        cur2.execute("UPDATE homework_submissions SET grading_status='done',auto_score=%s,auto_grade_message=%s,auto_grade_details=%s,score=%s,graded_at=NOW() WHERE id=%s",(auto_score,msg,json.dumps(details,ensure_ascii=False),norm,sid))
        cur2.execute("SELECT h.class_id,hs.student_id,hs.student_name FROM homework h JOIN homework_submissions hs ON hs.homework_id=h.id WHERE hs.id=%s",(sid,))
        info=cur2.fetchone()
        if info and info['class_id']:
            # 重新统计该学生每个作业的最新分数（取每个 student_id+homework_id 最后一次提交的分数）
            cur2.execute("""
                SELECT SUM(hs2.score) as total, COUNT(*) as cnt
                FROM (
                    SELECT hs.homework_id, hs.score,
                           ROW_NUMBER() OVER (PARTITION BY hs.student_id, hs.homework_id ORDER BY hs.submitted_at DESC) as rn
                    FROM homework_submissions hs
                    JOIN homework h2 ON h2.id = hs.homework_id
                    WHERE hs.student_id = %s AND hs.score IS NOT NULL AND h2.class_id = %s
                ) hs2
                WHERE hs2.rn = 1
            """, (info['student_id'], info['class_id']))
            stats = cur2.fetchone()
            new_total = float(stats['total'] or 0)
            new_count = int(stats['cnt'] or 0)
            cur2.execute("SELECT id FROM homework_score_ranking WHERE class_id=%s AND student_id=%s",(info['class_id'],info['student_id']))
            ex=cur2.fetchone()
            if ex:
                cur2.execute("UPDATE homework_score_ranking SET total_score=%s, homework_count=%s WHERE id=%s",(new_total,new_count,ex['id']))
            else:
                cur2.execute("INSERT INTO homework_score_ranking (class_id,student_id,student_name,total_score,homework_count) VALUES (%s,%s,%s,%s,%s)",(info['class_id'],info['student_id'],info['student_name'],new_total,new_count))

        db2.close()
    except subprocess.TimeoutExpired:
        db3=get_db(); cur3=db3.cursor(); cur3.execute("UPDATE homework_submissions SET grading_status='failed' WHERE id=%s",(sid,)); db3.close()
    except Exception as e:
        try:
            db4=get_db(); cur4=db4.cursor(); cur4.execute("UPDATE homework_submissions SET grading_status='failed',auto_grade_message=%s WHERE id=%s",(str(e),sid)); db4.close()
        except: pass
        # 写入文件日志便于追踪
        logger.exception("[ERROR auto_grade] sub_id=%s", sid)

@app.route('/api/homework/<int:hid>/grading_script', methods=['POST'])
@teacher_required
def upload_grading_script(hid):
    if 'script' not in request.files: return err('请选择 Python 评分脚本文件')
    f=request.files['script']
    if not f.filename.endswith('.py'): return err('仅支持 .py 文件')
    regrade_all=request.form.get('regrade_all','false').lower()=='true'
    sn=f"grading_{hid}_{uuid.uuid4().hex[:8]}.py"
    fp=os.path.join(UPLOAD_DIR,'homework',sn); f.save(fp)
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id FROM homework_grading_scripts WHERE homework_id=%s",(hid,))
    ex=cur.fetchone()
    if ex: cur.execute("UPDATE homework_grading_scripts SET script_path=%s,created_at=NOW() WHERE id=%s",(fp,ex['id']))
    else: cur.execute("INSERT INTO homework_grading_scripts (homework_id,script_path,language,timeout_seconds,created_by) VALUES (%s,%s,'python',60,%s)",(hid,fp,request.teacher_id))
    cur.execute("UPDATE homework SET has_grading_script=1 WHERE id=%s",(hid,))
    enable_auto=request.form.get('enable_auto','false').lower()=='true'
    cur.execute("UPDATE homework SET auto_grade_enabled=%s WHERE id=%s",(1 if enable_auto else 0,hid))
    if regrade_all:
        cur.execute("UPDATE homework_submissions SET grading_status='none',score=NULL WHERE homework_id=%s",(hid,))
        cur.execute("SELECT total_score FROM homework WHERE id=%s",(hid,))
        ts=(cur.fetchone() or {}).get('total_score') or 100
        cur.execute("SELECT hs.id,sa.file_path,sa.file_name FROM homework_submissions hs LEFT JOIN submission_attachments sa ON sa.submission_id=hs.id WHERE hs.homework_id=%s",(hid,))
        sub_files={}
        for r in cur.fetchall():
            sid2=r['id']
            if sid2 not in sub_files: sub_files[sid2]=[]
            if r['file_path']: sub_files[sid2].append({'id':r['id'],'path':r['file_path'],'name':r['file_name'] or os.path.basename(r['file_path'])})
        db.close()
        for sid2 in sub_files:
            t=threading.Thread(target=_run_grading,args=(fp,sub_files[sid2],hid,sid2,ts),daemon=True); t.start()
    else: db.close()
    return success({'message':'评分脚本上传成功'})

@app.route('/api/homework/<int:hid>/grading_script', methods=['GET'])
@teacher_required
def get_grading_script(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("""
        SELECT gs.*, h.auto_grade_enabled
        FROM homework_grading_scripts gs
        JOIN homework h ON h.id=gs.homework_id
        WHERE gs.homework_id=%s
    """, (hid,))
    row=cur.fetchone(); db.close()
    if not row: return success(None)
    r=_row(row); r['script_name']=os.path.basename(r.get('script_path','')) if r else ''
    r['has_grading_script'] = True
    return success(r)

@app.route('/api/homework/<int:hid>/grading_script/content', methods=['GET'])
@teacher_required
def get_grading_script_content(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT script_path FROM homework_grading_scripts WHERE homework_id=%s",(hid,))
    row=cur.fetchone(); db.close()
    if not row or not row['script_path']: return err('脚本不存在',404)
    fp=row['script_path']
    if not os.path.exists(fp): return err('脚本文件丢失',404)
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            content=f.read()
        return success({'content':content,'script_name':os.path.basename(fp)})
    except Exception as e:
        return err(f'读取脚本失败: {e}',500)

@app.route('/api/homework/<int:hid>/grading_script/download', methods=['GET'])
@teacher_required
def download_grading_script(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT script_path FROM homework_grading_scripts WHERE homework_id=%s",(hid,))
    row=cur.fetchone(); db.close()
    if not row or not row['script_path']: return err('脚本不存在',404)
    fp=row['script_path']
    if not os.path.exists(fp): return err('脚本文件丢失',404)
    return send_file(fp, as_attachment=True, download_name=os.path.basename(fp))

@app.route('/api/homework/<int:hid>/grading_script/toggle_auto', methods=['POST'])
@teacher_required
def toggle_grading_auto(hid):
    d=request.get_json() or {}; enable=bool(d.get('enable',False))
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE homework SET auto_grade_enabled=%s WHERE id=%s",(1 if enable else 0,hid))
    if not enable: cur.execute("UPDATE homework_submissions SET grading_status='none',score=NULL WHERE homework_id=%s",(hid,))
    else:
        cur.execute("SELECT total_score FROM homework WHERE id=%s",(hid,))
        ts=(cur.fetchone() or {}).get('total_score') or 100
        cur.execute("SELECT id FROM homework_submissions WHERE homework_id=%s AND grading_status IN ('none','pending','failed')",(hid,))
        for r in cur.fetchall():
            cur.execute("UPDATE homework_submissions SET grading_status='pending' WHERE id=%s",(r['id'],))
    db.close(); return success({'enabled':enable})

@app.route('/api/homework/<int:hid>/grading_script', methods=['DELETE'])
@teacher_required
def delete_grading_script(hid):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM homework_grading_scripts WHERE homework_id=%s",(hid,))
    cur.execute("UPDATE homework SET has_grading_script=0,auto_grade_enabled=0 WHERE id=%s",(hid,))
    cur.execute("UPDATE homework_submissions SET grading_status='none' WHERE homework_id=%s",(hid,))
    db.close(); return success()

@app.route('/api/homework/submissions/<int:sid>/grading_status', methods=['GET'])
def get_grading_status(sid):
    token=get_token_param(request)
    if not token: return err('未授权',401)
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT grading_status,auto_score,auto_grade_message FROM homework_submissions WHERE id=%s",(sid,))
    row=cur.fetchone(); db.close()
    if not row: return err('未找到提交',404)
    return success(_row(row))

# ======= 文件下载 =======
@app.route('/api/homework/attachments/<int:aid>/download', methods=['GET'])
def dl_hw_att(aid):
    token=get_token_param(request)
    if not token: return err('未授权',401)
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT file_path,file_name FROM homework_attachments WHERE id=%s",(aid,))
    att=cur.fetchone(); db.close()
    if not att: return err('文件不存在',404)
    fp=att['file_path']
    if not os.path.isabs(fp): fp=os.path.join(UPLOAD_DIR,fp.lstrip('/'))
    if not os.path.exists(fp): return err('文件不存在',404)
    return send_file(fp,as_attachment=True,download_name=att['file_name'])

@app.route('/api/submissions/attachments/<int:aid>/download', methods=['GET'])
def dl_sub_att(aid):
    token=get_token_param(request)
    if not token: return err('未授权',401)
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT file_path,file_name FROM submission_attachments WHERE id=%s",(aid,))
    att=cur.fetchone(); db.close()
    if not att: return err('文件不存在',404)
    fp=att['file_path']
    if not os.path.isabs(fp): fp=os.path.join(UPLOAD_DIR,fp.lstrip('/'))
    if not os.path.exists(fp): return err('文件不存在',404)
    return send_file(fp,as_attachment=True,download_name=att['file_name'])

@app.route('/api/grades/attachments/<int:aid>/download', methods=['GET'])
def dl_grd_att(aid):
    token=get_token_param(request)
    if not token: return err('未授权',401)
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT file_path,file_name FROM grade_attachments WHERE id=%s",(aid,))
    att=cur.fetchone(); db.close()
    if not att: return err('文件不存在',404)
    fp=att['file_path']
    if not os.path.isabs(fp): fp=os.path.join(UPLOAD_DIR,fp.lstrip('/'))
    if not os.path.exists(fp): return err('文件不存在',404)
    return send_file(fp,as_attachment=True,download_name=att['file_name'])

# ======= 导出作业批改报告 =======
@app.route('/api/homework/<int:hid>/export', methods=['GET'])
@teacher_required
def export_homework_reports(hid):
    """导出作业批改报告，每个学生一个HTML页面，打包为ZIP"""
    db = get_db(); cur = db.cursor()
    # 验证作业存在并获取作业信息
    cur.execute("SELECT h.*, c.name as course_name FROM homework h JOIN courses c ON c.id=h.course_id WHERE h.id=%s", (hid,))
    hw = cur.fetchone()
    if not hw: db.close(); return err('作业不存在', 404)

    # 获取所有提交记录
    cur.execute("""
        SELECT s.*, st.student_number
        FROM homework_submissions s
        LEFT JOIN students st ON st.id=s.student_id
        WHERE s.homework_id=%s ORDER BY s.submitted_at
    """, (hid,))
    subs = _rows(cur.fetchall())

    # 获取作业附件
    cur.execute("SELECT * FROM homework_attachments WHERE homework_id=%s", (hid,))
    hw_attachments = _rows(cur.fetchall())

    # 获取提交附件
    for s in subs:
        cur.execute("SELECT * FROM submission_attachments WHERE submission_id=%s", (s['id'],))
        s['attachments'] = _rows(cur.fetchall())

    db.close()

    # 生成ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for sub in subs:
            html_content = _build_student_report(hw, sub, hw_attachments)
            # 文件名：学号_姓名_作业标题.html（去除非法字符）
            safe_name = _sanitize_filename(f"{sub.get('student_number','') or sub.get('student_id','')}_{sub.get('student_name','学生')}_{hw['title']}")
            zf.writestr(f"{safe_name}.html", html_content.encode('utf-8'))

    zip_buffer.seek(0)
    filename = _sanitize_filename(f"{hw['title']}_批改报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{filename}.zip"'}
    )

def _sanitize_filename(name):
    """去除文件名中的非法字符"""
    import re
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def _build_student_report(hw, sub, hw_attachments):
    """为单个学生生成精美的HTML批改报告"""
    student_name = html.escape(sub.get('student_name', '学生') or '学生')
    student_number = html.escape(str(sub.get('student_number', '') or sub.get('student_id', '')))
    score = sub.get('score')
    auto_score = sub.get('auto_score')
    final_score = score if score is not None else (auto_score if auto_score is not None else None)
    feedback = html.escape(sub.get('feedback', '') or '')
    submitted_at = sub.get('submitted_at', '')
    if submitted_at:
        try:
            dt = datetime.strptime(submitted_at, '%Y-%m-%dT%H:%M:%S')
            submitted_at = dt.strftime('%Y/%m/%d %H:%M')
        except:
            pass

    # 评分详情
    details = sub.get('auto_grade_details') or {}
    if isinstance(details, str):
        try: details = json.loads(details)
        except: details = {}
    details_html = ''
    if details:
        items = []
        for k, v in sorted(details.items()):
            key = html.escape(str(k))
            val = html.escape(str(v))
            icon = '✅' if '✅' in val or 'check' in val.lower() else ('❌' if '❌' in val or 'x' in val.lower() else '➖')
            score_match = __import__('re').search(r'\(([+-]?\d+)分?\)', val)
            pts = score_match.group(1) if score_match else ''
            items.append(f'''
            <div class="detail-item">
                <div class="detail-icon">{icon}</div>
                <div class="detail-text">
                    <div class="detail-title">{key}</div>
                    <div class="detail-desc">{val}</div>
                </div>
                <div class="detail-score">{pts}</div>
            </div>''')
        details_html = '\n'.join(items)
    else:
        details_html = '<div class="no-details">暂无详细评分数据</div>'

    # 附件列表
    attachments_html = ''
    if sub.get('attachments'):
        att_items = []
        for att in sub['attachments']:
            fname = html.escape(att.get('file_name', '附件'))
            att_items.append(f'<div class="attachment-item">📎 {fname}</div>')
        attachments_html = '\n'.join(att_items)
    else:
        attachments_html = '<div class="no-attachments">未提交附件</div>'

    # 分数颜色
    score_color = '#10b981' if final_score is not None and final_score >= 80 else ('#f59e0b' if final_score is not None and final_score >= 60 else '#ef4444')
    score_display = f'{final_score}' if final_score is not None else '未评分'
    score_label = '分' if final_score is not None else ''

    # 评语样式
    feedback_box = ''
    if feedback:
        feedback_box = f'''
        <div class="feedback-box">
            <div class="feedback-label">评语</div>
            <div class="feedback-text">{feedback}</div>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{student_name} - {html.escape(hw.get('title','作业'))} 批改报告</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 40px 20px;
}}
.container {{
    max-width: 720px;
    margin: 0 auto;
    background: #fff;
    border-radius: 24px;
    box-shadow: 0 25px 80px rgba(0,0,0,0.25);
    overflow: hidden;
}}
.header {{
    background: linear-gradient(135deg, #1e3a5f 0%, #2d6a4f 100%);
    padding: 40px 32px;
    color: #fff;
    position: relative;
}}
.header::after {{
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0; right: 0;
    height: 60px;
    background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.08));
}}
.homework-title {{
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
    opacity: 0.9;
}}
.course-name {{
    font-size: 14px;
    opacity: 0.7;
}}
.student-section {{
    padding: 32px;
    display: flex;
    align-items: center;
    gap: 20px;
    border-bottom: 1px solid #f0f0f0;
}}
.avatar {{
    width: 64px; height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2d6a4f, #40916c);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(45,106,79,0.3);
}}
.student-info {{ flex: 1; }}
.student-name {{
    font-size: 22px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 4px;
}}
.student-meta {{
    font-size: 13px;
    color: #888;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}}
.score-badge {{
    width: 90px; height: 90px;
    border-radius: 50%;
    background: linear-gradient(135deg, {score_color}, {score_color}dd);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
    box-shadow: 0 6px 20px {score_color}44;
    position: relative;
    overflow: hidden;
}}
.score-badge::before {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
}}
.score-number {{
    font-size: 28px;
    font-weight: 800;
    line-height: 1;
}}
.score-unit {{
    font-size: 12px;
    opacity: 0.85;
    margin-top: 2px;
}}
.score-label {{
    font-size: 11px;
    opacity: 0.7;
    margin-top: 2px;
}}
.content {{
    padding: 32px;
}}
.section-title {{
    font-size: 16px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-title::before {{
    content: '';
    width: 4px; height: 20px;
    background: linear-gradient(180deg, #2d6a4f, #40916c);
    border-radius: 2px;
}}
.feedback-box {{
    background: linear-gradient(135deg, #fef9e7, #fdf4d0);
    border-left: 4px solid #f0c040;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
}}
.feedback-label {{
    font-size: 12px;
    font-weight: 600;
    color: #b8860b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}}
.feedback-text {{
    font-size: 15px;
    color: #5c4a00;
    line-height: 1.7;
}}
.details-panel {{
    background: linear-gradient(180deg, #1e293b, #0f172a);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
}}
.details-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    color: #fbbf24;
    font-size: 14px;
    font-weight: 600;
}}
.detail-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.detail-item:last-child {{ border-bottom: none; }}
.detail-icon {{
    font-size: 16px;
    flex-shrink: 0;
    margin-top: 2px;
}}
.detail-text {{ flex: 1; }}
.detail-title {{
    font-size: 13px;
    font-weight: 600;
    color: #fbbf24;
    margin-bottom: 3px;
}}
.detail-desc {{
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.5;
}}
.detail-score {{
    font-size: 13px;
    font-weight: 700;
    color: #34d399;
    flex-shrink: 0;
    min-width: 40px;
    text-align: right;
}}
.attachments-section {{
    background: #f8fafc;
    border-radius: 12px;
    padding: 20px;
}}
.attachment-item {{
    font-size: 13px;
    color: #475569;
    padding: 8px 0;
    border-bottom: 1px dashed #e2e8f0;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.attachment-item:last-child {{ border-bottom: none; }}
.no-details, .no-attachments {{
    text-align: center;
    padding: 24px;
    color: #94a3b8;
    font-size: 13px;
}}
.footer {{
    padding: 20px 32px;
    text-align: center;
    border-top: 1px solid #f0f0f0;
    color: #aaa;
    font-size: 12px;
}}
.footer-logo {{
    font-weight: 700;
    color: #2d6a4f;
    margin-bottom: 4px;
}}
@media print {{
    body {{ background: #fff; padding: 0; }}
    .container {{ box-shadow: none; border-radius: 0; }}
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="homework-title">{html.escape(hw.get('title','作业'))}</div>
        <div class="course-name">{html.escape(hw.get('course_name',''))} · 总分 {hw.get('total_score',100)}分</div>
    </div>

    <div class="student-section">
        <div class="avatar">{student_name[0] if student_name else '?'}</div>
        <div class="student-info">
            <div class="student-name">{student_name}</div>
            <div class="student-meta">
                <span>学号：{student_number}</span>
                <span>提交时间：{submitted_at or '未提交'}</span>
            </div>
        </div>
        <div class="score-badge">
            <div class="score-number">{score_display}</div>
            <div class="score-unit">{score_label}</div>
            <div class="score-label">得分</div>
        </div>
    </div>

    <div class="content">
        {feedback_box}

        <div class="section-title">评分详情</div>
        <div class="details-panel">
            <div class="details-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>
                自动评分明细
            </div>
            {details_html}
        </div>

        <div class="section-title">提交附件</div>
        <div class="attachments-section">
            {attachments_html}
        </div>
    </div>

    <div class="footer">
        <div class="footer-logo">智慧课堂 SmartClass</div>
        <div>生成时间：{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</div>
    </div>
</div>
</body>
</html>'''

# ======= 学生端通知 =======
@app.route('/api/student/notifications', methods=['GET'])
@student_required
def stu_get_notifications():
    """获取学生通知列表（自动清理30天前已读消息）"""
    db = get_db()
    cur = db.cursor()
    student_id = request.teacher_id
    
    # 清理30天前已读的通知
    cur.execute("""
        DELETE FROM student_notifications 
        WHERE student_id=%s AND is_read=1 AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)
    """, (student_id,))
    
    # 获取通知列表
    cur.execute("""
        SELECT id, type, title, content, related_id, related_type, is_read, created_at
        FROM student_notifications
        WHERE student_id=%s
        ORDER BY created_at DESC
        LIMIT 50
    """, (student_id,))
    notifications = _rows(cur.fetchall())
    
    # 统计未读数
    cur.execute("SELECT COUNT(*) as cnt FROM student_notifications WHERE student_id=%s AND is_read=0", (student_id,))
    unread_count = cur.fetchone()['cnt']
    
    db.close()
    return success({'notifications': notifications, 'unread_count': unread_count})

@app.route('/api/student/notifications/<int:nid>', methods=['DELETE'])
@student_required
def stu_delete_notification(nid):
    """删除单条通知"""
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM student_notifications WHERE id=%s AND student_id=%s", (nid, request.teacher_id))
    db.close()
    return success()

@app.route('/api/student/notifications', methods=['DELETE'])
@student_required
def stu_clear_notifications():
    """清空所有已读通知"""
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM student_notifications WHERE student_id=%s AND is_read=1", (request.teacher_id,))
    deleted = cur.rowcount
    db.close()
    return success({'deleted': deleted})

@app.route('/api/student/notifications/read', methods=['PUT'])
@student_required
def stu_mark_notifications_read():
    """标记通知为已读"""
    d = request.get_json() or {}
    nid = d.get('id')  # 如果传了id则标记单条，否则标记全部
    db = get_db()
    cur = db.cursor()
    if nid:
        cur.execute("UPDATE student_notifications SET is_read=1 WHERE id=%s AND student_id=%s", (nid, request.teacher_id))
    else:
        cur.execute("UPDATE student_notifications SET is_read=1 WHERE student_id=%s", (request.teacher_id,))
    db.close()
    return success()

def _create_homework_notifications(hw_id, course_id, class_id, title, deadline):
    """创建新作业通知（通知班级所有学生）"""
    db = get_db()
    cur = db.cursor()
    
    # 获取班级所有学生
    cur.execute("SELECT id FROM students WHERE class_id=%s", (class_id,))
    students = cur.fetchall()
    
    for stu in students:
        cur.execute("""
            INSERT INTO student_notifications (student_id, type, title, content, related_id, related_type)
            VALUES (%s, 'homework_new', %s, %s, %s, 'homework')
        """, (stu['id'], f'新作业：{title}', f'课程作业已发布，截止时间：{deadline}', hw_id))
    
    db.commit()
    db.close()

def _check_deadline_reminders(student_id):
    """检查临近到期的作业，创建提醒通知"""
    db = get_db()
    cur = db.cursor()
    
    # 查找1天内即将到期的未提交作业
    cur.execute("""
        SELECT h.id, h.title, h.deadline, c.name as course_name
        FROM homework h
        JOIN courses c ON c.id = h.course_id
        WHERE h.class_id = (SELECT class_id FROM students WHERE id=%s)
        AND h.deadline BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR)
        AND h.is_published = 1
        AND NOT EXISTS (
            SELECT 1 FROM homework_submissions hs 
            WHERE hs.homework_id = h.id AND hs.student_id = %s
        )
        AND NOT EXISTS (
            SELECT 1 FROM student_notifications sn 
            WHERE sn.student_id=%s AND sn.related_id=h.id AND sn.type='homework_reminder'
        )
    """, (student_id, student_id, student_id))
    
    upcoming = cur.fetchall()
    
    for hw in upcoming:
        deadline_str = hw['deadline'].strftime('%Y-%m-%d %H:%M') if hw['deadline'] else '未定'
        cur.execute("""
            INSERT INTO student_notifications (student_id, type, title, content, related_id, related_type)
            VALUES (%s, 'homework_reminder', %s, %s, %s, 'homework')
        """, (student_id, f'⚠️ 作业即将截止', 
              f'《{hw["title"]}》（{hw["course_name"]}）将于 {deadline_str} 截止，请尽快完成！',
              hw['id']))
    
    db.commit()
    db.close()

# ======= 学生端 =======
@app.route('/api/student/profile', methods=['GET'])
@student_required
def stu_profile():
    db=get_db(); cur=db.cursor()
    cur.execute("""
        SELECT sa.*, s.name, s.student_number, s.class_id,
               cl.name AS class_name
        FROM student_accounts sa
        JOIN students s ON sa.student_id=s.id
        LEFT JOIN classes cl ON cl.id=s.class_id
        WHERE s.id=%s
    """, (request.teacher_id,))
    row=cur.fetchone()
    if not row: return err('未找到学生信息',404)
    r=_row(row); r['avatar']=r.get('avatar',''); r['bio']=r.get('bio','')
    r.pop('password', None)  # 不返回密码 hash
    db.close(); return success(r)

@app.route('/api/student/profile', methods=['POST'])
@student_required
def stu_update_profile():
    d=request.get_json() or {}
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE student_accounts SET avatar=%s,bio=%s WHERE student_id=%s",(d.get('avatar',''),d.get('bio',''),request.teacher_id))
    db.close(); return success()

@app.route('/api/student/change_password', methods=['POST'])
@student_required
def stu_change_password():
    d=request.get_json() or {}; old_p=d.get('old_password',''); new_p=d.get('new_password','')
    if not old_p or not new_p: return err('旧密码和新密码都不能为空')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT password FROM student_accounts WHERE student_id=%s",(request.teacher_id,))
    u=cur.fetchone()
    if not u or not bcrypt.checkpw(old_p.encode(),u['password'].encode()): db.close(); return err('旧密码错误')
    new_hash=bcrypt.hashpw(new_p.encode(),bcrypt.gensalt()).decode()
    cur.execute("UPDATE student_accounts SET password=%s WHERE student_id=%s",(new_hash,request.teacher_id))
    db.close(); return success()

@app.route('/api/student/homework', methods=['GET'])
@student_required
def stu_homework():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT class_id FROM students WHERE id=%s",(request.teacher_id,))
    row=cur.fetchone()
    if not row: db.close(); return err('未找到班级信息',404)
    clid=str(row['class_id'])
    cur.execute("""
        SELECT h.*,c.name as course_name FROM homework h
        JOIN courses c ON c.id=h.course_id
        WHERE (
            h.class_id=%s
            OR (h.class_id IS NULL AND EXISTS (
                SELECT 1 FROM course_classes cc WHERE cc.course_id=c.id AND cc.class_id=%s
            ))
        )
        AND h.is_published=1
        ORDER BY h.deadline DESC
    """, (clid, clid))
    hws=_rows(cur.fetchall())
    for hw in hws:
        cur.execute("SELECT * FROM homework_attachments WHERE homework_id=%s",(hw['id'],))
        hw['attachments']=_rows(cur.fetchall())
        cur.execute("SELECT * FROM homework_submissions WHERE homework_id=%s AND student_id=%s",(hw['id'],request.teacher_id))
        sub=cur.fetchone()
        if sub:
            hw['submitted']=True; hw['submission']=_row(sub)
            cur.execute("SELECT * FROM submission_attachments WHERE submission_id=%s",(sub['id'],))
            hw['submission']['attachments']=_rows(cur.fetchall())
            # 把 submission 的评分字段拍平到 hw 层（与前端模板保持一致）
            for k in ['grading_status','score','auto_score','auto_grade_message','auto_grade_details','feedback','graded_at']:
                if sub.get(k) is not None:
                    hw[k]=sub[k]
            # 解析 auto_grade_details JSON 字符串为对象，供前端展示逐项评分
            if isinstance(hw.get('auto_grade_details'), str):
                try: hw['auto_grade_details']=json.loads(hw['auto_grade_details'])
                except: pass
        else: hw['submitted']=False; hw['submission']=None
    
    # 检查临近到期的作业，创建提醒通知
    _check_deadline_reminders(request.teacher_id)
    
    db.close(); return success(hws)

@app.route('/api/student/courses', methods=['GET'])
@student_required
def stu_courses():
    db=get_db(); cur=db.cursor()
    term_filter = request.args.get('term','')
    cur.execute("SELECT class_id FROM students WHERE id=%s",(request.teacher_id,))
    row=cur.fetchone()
    if not row: db.close(); return err('未找到班级信息',404)
    clid=str(row['class_id'])
    # 获取所有学期（用于前端筛选下拉）
    cur.execute("""
        SELECT DISTINCT c.term
        FROM courses c
        JOIN course_classes cc ON cc.course_id=c.id
        WHERE cc.class_id=%s AND c.term IS NOT NULL AND c.term != ''
        ORDER BY c.term DESC
    """, (clid,))
    terms = [r['term'] for r in cur.fetchall()]
    # 查询课程（含教师名、班级名、学期）
    if term_filter:
        cur.execute("""
            SELECT DISTINCT c.id, c.name, c.term,
                   t.real_name as teacher_name,
                   cl.name as class_name
            FROM courses c
            JOIN course_classes cc ON cc.course_id=c.id
            JOIN classes cl ON cl.id=cc.class_id
            JOIN teachers t ON t.id=c.teacher_id
            WHERE cc.class_id=%s AND c.term=%s
            ORDER BY c.term DESC, c.name
        """, (clid, term_filter))
    else:
        cur.execute("""
            SELECT DISTINCT c.id, c.name, c.term,
                   t.real_name as teacher_name,
                   cl.name as class_name
            FROM courses c
            JOIN course_classes cc ON cc.course_id=c.id
            JOIN classes cl ON cl.id=cc.class_id
            JOIN teachers t ON t.id=c.teacher_id
            WHERE cc.class_id=%s
            ORDER BY c.term DESC, c.name
        """, (clid,))
    courses=_rows(cur.fetchall())
    db.close(); return success({'courses': courses, 'terms': terms})

@app.route('/api/student/homework/<int:hid>/submit', methods=['POST'])
@student_required
def stu_submit_homework(hid):
    ct=request.content_type or ''
    if 'multipart' in ct:
        content=request.form.get('content','').strip()
    else:
        content=(request.get_json() or {}).get('content','')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT name FROM students WHERE id=%s",(request.teacher_id,))
    stu=cur.fetchone()
    stu_name=stu['name'] if stu else ''
    cur.execute("SELECT id FROM homework_submissions WHERE homework_id=%s AND student_id=%s",(hid,request.teacher_id))
    existing=cur.fetchone()
    if existing:
        sub_id=existing['id']
        cur.execute("UPDATE homework_submissions SET content=%s,submitted_at=NOW(),student_name=%s,grading_status='none',score=NULL WHERE id=%s",(content,stu_name,sub_id))
        # 重新提交：删除旧附件文件及记录
        old_file_list = request.files.getlist('files') or request.files.getlist('file') or []
        if 'multipart' in ct and old_file_list and any(f.filename for f in old_file_list):
            cur.execute("SELECT file_path FROM submission_attachments WHERE submission_id=%s",(sub_id,))
            for old in cur.fetchall():
                try:
                    if old['file_path'] and os.path.exists(old['file_path']):
                        os.remove(old['file_path'])
                except: pass
            cur.execute("DELETE FROM submission_attachments WHERE submission_id=%s",(sub_id,))
    else:
        cur.execute("INSERT INTO homework_submissions (homework_id,student_id,student_name,content,submitted_at) VALUES (%s,%s,%s,%s,NOW())",(hid,request.teacher_id,stu_name,content))
        sub_id=cur.lastrowid
    if 'multipart' in ct:
        # 兼容前端 'file'（单数）和 'files'（复数）两种字段名
        file_list = request.files.getlist('files') or []
        if not file_list:
            file_list = request.files.getlist('file') or []
        for f in file_list:
            if f.filename:
                fn=f.filename; sn=f"{uuid.uuid4().hex}{os.path.splitext(fn)[1]}"
                fp=os.path.join(UPLOAD_DIR,'submissions',sn); f.save(fp)
                cur.execute("INSERT INTO submission_attachments (submission_id,file_name,file_path,file_size) VALUES (%s,%s,%s,%s)",(sub_id,fn,fp,os.path.getsize(fp)))
    # 提交成功后检查是否需要自动评分
    cur.execute("SELECT h.has_grading_script,h.auto_grade_enabled,h.total_score,gs.script_path FROM homework h LEFT JOIN homework_grading_scripts gs ON gs.homework_id=h.id WHERE h.id=%s",(hid,))
    hw=cur.fetchone()
    if hw and hw['has_grading_script'] and hw['auto_grade_enabled'] and hw['script_path']:
        cur.execute("SELECT file_path,file_name FROM submission_attachments WHERE submission_id=%s",(sub_id,))
        rows=cur.fetchall()
        if rows:
            files=[{'path':r['file_path'],'name':r['file_name'] or os.path.basename(r['file_path'])} for r in rows]
            cur.execute("UPDATE homework_submissions SET grading_status='pending' WHERE id=%s",(sub_id,))
            t=threading.Thread(target=_run_grading,args=(hw['script_path'],files,hid,sub_id,hw['total_score'] or 100),daemon=True); t.start()
    db.close(); return success({'message':'提交成功'})

@app.route('/api/student/homework/ranking', methods=['GET'])
@student_required
def stu_hw_ranking():
    """学生天梯榜：按学期+课程筛选，每个课程独立排名"""
    term = request.args.get('term', '')
    course_id = request.args.get('course_id', '')
    if not course_id:
        return err('course_id 不能为空')

    db = get_db()
    cur = db.cursor()

    # 获取学生班级
    cur.execute("SELECT class_id FROM students WHERE id=%s", (request.teacher_id,))
    row = cur.fetchone()
    if not row:
        db.close()
        return err('未找到班级', 404)
    clid = str(row['class_id'])

    # 获取班级总人数
    cur.execute("SELECT COUNT(*) as cnt FROM students WHERE class_id=%s", (clid,))
    total = cur.fetchone()['cnt']

    # 按课程统计该班学生的作业分数
    cur.execute("""
        SELECT s.id as student_id, s.name as student_name,
               COALESCE(SUM(hs2.score), 0) as total_score,
               COUNT(DISTINCT hs2.homework_id) as homework_count
        FROM students s
        LEFT JOIN (
            SELECT hs.homework_id, hs.student_id, hs.score,
                   ROW_NUMBER() OVER (PARTITION BY hs.student_id, hs.homework_id ORDER BY hs.submitted_at DESC) as rn
            FROM homework_submissions hs
            JOIN homework h ON h.id = hs.homework_id
            WHERE h.course_id = %s AND h.class_id = %s AND hs.score IS NOT NULL
        ) hs2 ON hs2.student_id = s.id AND hs2.rn = 1
        WHERE s.class_id = %s
        GROUP BY s.id, s.name
        ORDER BY total_score DESC, s.id ASC
    """, (str(course_id), clid, clid))

    rows = cur.fetchall()
    ranked_list = []
    my_rank = None
    ranked_count = 0
    for idx, r in enumerate(rows):
        item = dict(r)
        item['rank'] = idx + 1
        ranked_list.append(item)
        if r['total_score'] > 0:
            ranked_count += 1
        if r['student_id'] == request.teacher_id:
            my_rank = {
                'student_id': r['student_id'],
                'student_name': r['student_name'],
                'rank': idx + 1,
                'total_score': r['total_score'],
                'homework_count': r['homework_count']
            }

    db.close()
    return success({
        'rankings': _rows(ranked_list),
        'total_students': total,
        'ranked_students': ranked_count,
        'my_rank': my_rank
    })

# ======= 管理端 =======
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT COUNT(*) as total FROM teachers"); tc=cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM students"); sc=cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM classes"); cc=cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM courses"); coc=cur.fetchone()['total']
    db.close()
    return success({'teachers':tc,'students':sc,'classes':cc,'courses':coc})

@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    db=get_db(); cur=db.cursor()
    # 基础统计
    cur.execute("SELECT COUNT(*) as v FROM teachers"); teachers=cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) as v FROM students"); students=cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) as v FROM classes"); classes=cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) as v FROM courses"); courses=cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) as v FROM homework WHERE title NOT LIKE '%test%' AND title NOT LIKE '%测试%' AND title NOT LIKE '%E2E%' AND title NOT LIKE '%自动化%'"); hw_total=cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) as v FROM homework_submissions"); subs_total=cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) as v FROM attendance_reports"); att_total=cur.fetchone()['v']
    # 各班级学生数
    cur.execute("""
        SELECT cl.name, COUNT(s.id) cnt
        FROM classes cl LEFT JOIN students s ON s.class_id=cl.id
        GROUP BY cl.id ORDER BY cnt DESC
    """)
    class_students = [{'name': r['name'], 'count': r['cnt']} for r in cur.fetchall()]
    # 作业提交数（过滤测试）
    cur.execute("""
        SELECT h.title, COUNT(hs.id) cnt
        FROM homework h LEFT JOIN homework_submissions hs ON hs.homework_id=h.id
        WHERE h.title NOT LIKE '%test%' AND h.title NOT LIKE '%测试%'
          AND h.title NOT LIKE '%E2E%' AND h.title NOT LIKE '%自动化%'
        GROUP BY h.id ORDER BY cnt DESC
    """)
    hw_submissions = [{'name': r['title'], 'count': r['cnt']} for r in cur.fetchall()]
    # 考勤状态分布
    cur.execute("SELECT status, COUNT(*) cnt FROM attendance_student_records GROUP BY status")
    att_rows = cur.fetchall()
    status_map = {'signed':'已签到','absent':'缺勤','late':'迟到','leave':'请假','leave_sick':'病假','leave_personal':'事假','early_leave':'早退'}
    att_dist = [{'name': status_map.get(r['status'], r['status']), 'value': r['cnt']} for r in att_rows]
    # 各课程作业数
    cur.execute("""
        SELECT c.name, COUNT(h.id) cnt
        FROM courses c LEFT JOIN homework h ON h.course_id=c.id
        GROUP BY c.id
    """)
    course_hw = [{'name': r['name'], 'count': r['cnt']} for r in cur.fetchall()]
    db.close()
    return success({
        'total': {'teachers': teachers, 'students': students, 'classes': classes,
                  'courses': courses, 'homework': hw_total, 'submissions': subs_total, 'attendance': att_total},
        'class_students': class_students,
        'hw_submissions': hw_submissions,
        'att_dist': att_dist,
        'course_hw': course_hw
    })

@app.route('/api/admin/student_activity', methods=['GET'])
@admin_required
def admin_student_activity():
    db=get_db(); cur=db.cursor()
    cur.execute("""
        SELECT login_date, COUNT(*) AS count
        FROM student_login_logs
        WHERE login_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY login_date
        ORDER BY login_date ASC
    """)
    rows = cur.fetchall()
    db.close()
    return success([{'date': str(r['login_date']), 'count': r['count']} for r in rows])

@app.route('/api/admin/course_list', methods=['GET'])
@admin_required
def admin_course_list():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id, name, term FROM courses ORDER BY term DESC, name")
    rows = cur.fetchall()
    db.close()
    return success([{'id':r['id'],'name':r['name'],'term':r['term']} for r in rows])

# ===== 课程管理 =====
@app.route('/api/admin/courses', methods=['GET'])
@admin_required
def admin_get_courses():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT c.*, t.real_name AS teacher_name FROM courses c LEFT JOIN teachers t ON t.id=c.teacher_id ORDER BY c.term DESC, c.name")
    courses = []
    for r in cur.fetchall():
        cur2 = db.cursor()
        cur2.execute("SELECT cl.id, cl.name FROM course_classes cc JOIN classes cl ON cl.id=cc.class_id WHERE cc.course_id=%s ORDER BY cl.name", (r['id'],))
        classes = [{'id': cr['id'], 'name': cr['name']} for cr in cur2.fetchall()]
        courses.append({**r, 'classes': classes})
    db.close()
    return success(courses)

@app.route('/api/admin/courses', methods=['POST'])
@admin_required
def admin_create_course():
    d = request.get_json() or {}
    name = (d.get('name') or '').strip()
    term = (d.get('term') or '').strip()
    teacher_id = d.get('teacher_id')
    class_ids = d.get('class_ids', [])
    if not name: return err('课程名称不能为空')
    if not teacher_id: return err('请选择授课教师')
    # 生成 ID（支持手动指定）
    course_id = d.get('id', '').strip() or f'crs_{int(__import__("time").time()*1000)}'
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT id FROM courses WHERE id=%s", (course_id,))
    if cur.fetchone(): db.close(); return err('课程ID已存在')
    cur.execute("INSERT INTO courses (id, name, term, teacher_id, created_at) VALUES (%s,%s,%s,%s,NOW())",
                (course_id, name, term, teacher_id))
    # 批量关联班级
    for cid in class_ids:
        cur.execute("INSERT INTO course_classes (course_id, class_id, created_at) VALUES (%s,%s,NOW())",
                    (course_id, cid))
    db.commit(); db.close()
    return success({'id': course_id, 'message': f'课程创建成功，已关联 {len(class_ids)} 个班级'})

@app.route('/api/admin/courses/<course_id>', methods=['PUT'])
@admin_required
def admin_update_course(course_id):
    d = request.get_json() or {}
    name = (d.get('name') or '').strip()
    term = (d.get('term') or '').strip()
    teacher_id = d.get('teacher_id')
    class_ids = d.get('class_ids', [])
    if not name: return err('课程名称不能为空')
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE courses SET name=%s, term=%s, teacher_id=%s WHERE id=%s",
                (name, term, teacher_id, course_id))
    # 重建班级关联
    cur.execute("DELETE FROM course_classes WHERE course_id=%s", (course_id,))
    for cid in class_ids:
        cur.execute("INSERT INTO course_classes (course_id, class_id, created_at) VALUES (%s,%s,NOW())",
                    (course_id, cid))
    db.commit(); db.close()
    return success({'message': f'课程更新成功，已关联 {len(class_ids)} 个班级'})

@app.route('/api/admin/courses/<course_id>', methods=['DELETE'])
@admin_required
def admin_delete_course(course_id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM course_classes WHERE course_id=%s", (course_id,))
    cur.execute("DELETE FROM courses WHERE id=%s", (course_id,))
    db.commit(); db.close()
    return success()

@app.route('/api/admin/courses/batch', methods=['POST'])
@admin_required
def admin_batch_create_courses():
    """批量开设课程模板：一个课程名 + 多个班级，自动为每个班级创建独立课程"""
    d = request.get_json() or {}
    base_name = (d.get('name') or '').strip()
    term = (d.get('term') or '').strip()
    teacher_id = d.get('teacher_id')
    class_ids = d.get('class_ids', [])
    if not base_name: return err('课程名称不能为空')
    if not teacher_id: return err('请选择授课教师')
    if not class_ids: return err('请选择至少一个班级')
    db = get_db(); cur = db.cursor()
    created = 0
    for cid in class_ids:
        cur.execute("SELECT name FROM classes WHERE id=%s", (cid,))
        cls = cur.fetchone()
        course_id = f'crs_{int(__import__("time").time()*1000)}_{created}'
        course_name = f"{base_name}-{cls['name']}" if len(class_ids) > 1 else base_name
        try:
            cur.execute("INSERT INTO courses (id, name, term, teacher_id, created_at) VALUES (%s,%s,%s,%s,NOW())",
                        (course_id, course_name, term, teacher_id))
            cur.execute("INSERT INTO course_classes (course_id, class_id, created_at) VALUES (%s,%s,NOW())",
                        (course_id, cid))
            created += 1
        except: pass
    db.commit(); db.close()
    return success({'created': created, 'message': f'批量开设 {created} 门课程成功'})

@app.route('/api/admin/class_list', methods=['GET'])
@admin_required
def admin_class_list():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id, name FROM classes ORDER BY name")
    rows = cur.fetchall()
    db.close()
    return success([{'id':r['id'],'name':r['name']} for r in rows])

@app.route('/api/admin/homework_stats', methods=['GET'])
@admin_required
def admin_homework_stats():
    course_id = request.args.get('course_id','')
    class_id  = request.args.get('class_id','')
    db=get_db(); cur=db.cursor()
    where = ["h.title NOT LIKE %s","h.title NOT LIKE %s",
             "h.title NOT LIKE %s","h.title NOT LIKE %s"]
    params = ['%test%','%测试%','%E2E%','%自动化%']
    if course_id:
        where.append("h.course_id=%s"); params.append(course_id)
    if class_id:
        where.append("h.class_id=%s"); params.append(class_id)
    wclause = " AND ".join(where)
    sql1 = ("SELECT h.id, h.title, h.class_id, cl.name class_name,"
            " COUNT(hs.id) sub_cnt,"
            " (SELECT COUNT(*) FROM students WHERE class_id=h.class_id) total_stu,"
            " AVG(CASE WHEN hs.score IS NOT NULL THEN hs.score ELSE NULL END) avg_score,"
            " MAX(hs.score) max_score, MIN(hs.score) min_score,"
            " SUM(CASE WHEN hs.score>=90 THEN 1 ELSE 0 END) excellent,"
            " SUM(CASE WHEN hs.score>=70 AND hs.score<90 THEN 1 ELSE 0 END) good,"
            " SUM(CASE WHEN hs.score>=60 AND hs.score<70 THEN 1 ELSE 0 END) pass_cnt,"
            " SUM(CASE WHEN hs.score IS NOT NULL AND hs.score<60 THEN 1 ELSE 0 END) fail_cnt"
            " FROM homework h"
            " LEFT JOIN classes cl ON cl.id=h.class_id"
            " LEFT JOIN homework_submissions hs ON hs.homework_id=h.id"
            " WHERE " + wclause +
            " GROUP BY h.id ORDER BY h.id")
    cur.execute(sql1, params)
    rows = cur.fetchall()
    hw_list = []
    for r in rows:
        total_stu = r['total_stu'] or 0
        sub_cnt = r['sub_cnt'] or 0
        rate = round(sub_cnt/total_stu*100, 1) if total_stu > 0 else 0
        avg = round(float(r['avg_score']), 1) if r['avg_score'] is not None else None
        mx  = round(float(r['max_score']), 1) if r['max_score'] is not None else None
        mn  = round(float(r['min_score']), 1) if r['min_score'] is not None else None
        hw_list.append({
            'id': r['id'], 'title': r['title'], 'class_name': r['class_name'] or '未知班级',
            'total_stu': total_stu, 'sub_cnt': sub_cnt, 'rate': rate,
            'avg_score': avg, 'max_score': mx, 'min_score': mn,
            'dist': {'excellent': int(r['excellent'] or 0), 'good': int(r['good'] or 0),
                     'pass': int(r['pass_cnt'] or 0), 'fail': int(r['fail_cnt'] or 0)}
        })
    # 班级提交率
    sql2 = ("SELECT cl.id, cl.name,"
            " SUM((SELECT COUNT(*) FROM homework_submissions WHERE homework_id=h.id)) sub_cnt,"
            " SUM((SELECT COUNT(*) FROM students WHERE class_id=h.class_id)) total_stu"
            " FROM homework h"
            " LEFT JOIN classes cl ON cl.id=h.class_id"
            " WHERE " + wclause +
            " GROUP BY cl.id")
    cur.execute(sql2, params)
    class_rates = []
    for r in cur.fetchall():
        ts = r['total_stu'] or 0
        sc = r['sub_cnt'] or 0
        class_rates.append({'name': r['name'] or '未知', 'rate': round(sc/ts*100,1) if ts>0 else 0})
    total_hw = len(hw_list)
    total_subs = sum(r['sub_cnt'] for r in hw_list)
    rates = [r['rate'] for r in hw_list if r['total_stu']>0]
    avg_rate = round(sum(rates)/len(rates), 1) if rates else 0
    scores = [r['avg_score'] for r in hw_list if r['avg_score'] is not None]
    avg_score = round(sum(scores)/len(scores), 1) if scores else 0
    db.close()
    return success({'total_hw': total_hw, 'total_subs': total_subs,
                    'avg_rate': avg_rate, 'avg_score': avg_score,
                    'list': hw_list, 'class_rates': class_rates})

@app.route('/api/admin/attendance_stats', methods=['GET'])
@admin_required
def admin_attendance_stats():
    course_id = request.args.get('course_id','')
    class_id  = request.args.get('class_id','')
    db=get_db(); cur=db.cursor()
    where = ["1=1"]
    params = []
    if course_id:
        where.append("ar.course_id=%s"); params.append(course_id)
    if class_id:
        where.append("ar.class_id=%s"); params.append(class_id)
    wclause = " AND ".join(where)
    # 报表明细
    sql1 = ("SELECT ar.id, ar.course_name, ar.class_name, ar.total_students,"
            " SUM(CASE WHEN rec.status='signed' THEN 1 ELSE 0 END) signed,"
            " SUM(CASE WHEN rec.status='late'   THEN 1 ELSE 0 END) late,"
            " SUM(CASE WHEN rec.status='leave'  THEN 1 ELSE 0 END) leave_cnt,"
            " SUM(CASE WHEN rec.status='absent' THEN 1 ELSE 0 END) absent"
            " FROM attendance_reports ar"
            " LEFT JOIN attendance_student_records rec ON rec.report_id=ar.id"
            " WHERE " + wclause +
            " GROUP BY ar.id ORDER BY ar.id")
    cur.execute(sql1, params)
    report_rows = cur.fetchall()
    table_list = []
    report_series = []
    total_signed = total_absent = 0
    for r in report_rows:
        total = r['total_students'] or 0
        signed = int(r['signed'] or 0)
        late   = int(r['late'] or 0)
        leave  = int(r['leave_cnt'] or 0)
        absent = int(r['absent'] or 0)
        rate   = round(signed/total*100,1) if total>0 else 0
        total_signed += signed; total_absent += absent
        label = (r['class_name'] or '') + '#' + str(r['id'])
        table_list.append({'id':r['id'],'course_name':r['course_name'],'class_name':r['class_name'],
                           'total':total,'signed':signed,'late':late,'leave':leave,'absent':absent,'rate':rate})
        report_series.append({'label':label,'signed':signed,'late':late,'leave':leave,'absent':absent})
    # 状态分布
    sql2 = ("SELECT rec.status, COUNT(*) cnt"
            " FROM attendance_student_records rec"
            " JOIN attendance_reports ar ON ar.id=rec.report_id"
            " WHERE " + wclause +
            " GROUP BY rec.status")
    cur.execute(sql2, params)
    status_map = {'signed':'已签到','absent':'缺勤','late':'迟到','leave':'请假'}
    dist = [{'name':status_map.get(r['status'],r['status']),'value':r['cnt']} for r in cur.fetchall()]
    # 班级签到率
    sql3 = ("SELECT ar.class_name,"
            " SUM(CASE WHEN rec.status='signed' THEN 1 ELSE 0 END) signed,"
            " COUNT(rec.id) total"
            " FROM attendance_student_records rec"
            " JOIN attendance_reports ar ON ar.id=rec.report_id"
            " WHERE " + wclause +
            " GROUP BY ar.class_name")
    cur.execute(sql3, params)
    class_rates = []
    for r in cur.fetchall():
        rate = round(r['signed']/r['total']*100,1) if r['total']>0 else 0
        class_rates.append({'name':r['class_name'],'rate':rate})
    # 缺勤 TOP
    sql4 = ("SELECT rec.student_name, COUNT(*) cnt"
            " FROM attendance_student_records rec"
            " JOIN attendance_reports ar ON ar.id=rec.report_id"
            " WHERE rec.status='absent' AND " + wclause +
            " GROUP BY rec.student_name ORDER BY cnt DESC LIMIT 15")
    cur.execute(sql4, params)
    absent_top = [{'name':r['student_name'],'count':r['cnt']} for r in cur.fetchall()]
    total_reports = len(report_rows)
    rates = [r['rate'] for r in table_list]
    avg_rate = round(sum(rates)/len(rates),1) if rates else 0
    db.close()
    return success({'total_reports':total_reports,'total_signed':total_signed,
                    'total_absent':total_absent,'avg_rate':avg_rate,
                    'list':table_list,'dist':dist,'class_rates':class_rates,
                    'report_series':report_series,'absent_top':absent_top})




@app.route('/api/admin/teachers', methods=['GET'])
@admin_required
def admin_get_teachers():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id,username,real_name,teacher_token,created_at FROM teachers ORDER BY id")
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

@app.route('/api/admin/teachers', methods=['POST'])
@admin_required
def admin_create_teacher():
    d=request.get_json() or {}
    username=(d.get('username') or '').strip(); real_name=(d.get('real_name') or '').strip()
    password=d.get('password','123456')
    if not username or not real_name: return err('用户名和姓名不能为空')
    pw_hash=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
    token=secrets.token_urlsafe(16)
    db=get_db(); cur=db.cursor()
    try:
        cur.execute("INSERT INTO teachers (username,password_hash,real_name,teacher_token) VALUES (%s,%s,%s,%s)",(username,pw_hash,real_name,token))
        db.close(); return success({'id':cur.lastrowid})
    except Exception as e:
        db.close(); return err(f'创建失败: {e}')

@app.route('/api/admin/teachers/<int:tid>', methods=['PUT'])
@admin_required
def admin_update_teacher(tid):
    d=request.get_json() or {}
    username=(d.get('username') or '').strip(); real_name=(d.get('real_name') or '').strip()
    password=d.get('password')
    db=get_db(); cur=db.cursor()
    if password:
        pw=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
        cur.execute("UPDATE teachers SET username=%s,real_name=%s,password_hash=%s WHERE id=%s",(username,real_name,pw,tid))
    else:
        cur.execute("UPDATE teachers SET username=%s,real_name=%s WHERE id=%s",(username,real_name,tid))
    db.close(); return success()

@app.route('/api/admin/teachers/<int:tid>', methods=['DELETE'])
@admin_required
def admin_delete_teacher(tid):
    if tid==1: return err('不能删除超级管理员')
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM teachers WHERE id=%s",(tid,))
    db.close(); return success()

@app.route('/api/admin/teachers/<int:tid>/reset_token', methods=['POST'])
@admin_required
def admin_reset_teacher_token(tid):
    token=secrets.token_urlsafe(16)
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE teachers SET teacher_token=%s WHERE id=%s",(token,tid))
    db.close(); return success({'token':token})

@app.route('/api/admin/teachers/<int:tid>/reset_password', methods=['POST'])
@admin_required
def admin_reset_teacher_password(tid):
    d=request.get_json() or {}
    new_p=d.get('new_password','123456')
    pw=bcrypt.hashpw(new_p.encode(),bcrypt.gensalt()).decode()
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE teachers SET password_hash=%s WHERE id=%s",(pw,tid))
    db.close(); return success({'message':f'密码已重置为: {new_p}'})

@app.route('/api/admin/classes', methods=['GET'])
@admin_required
def admin_get_classes():
    db=get_db(); cur=db.cursor()
    # 查询班级列表
    cur.execute("SELECT * FROM classes ORDER BY name")
    rows=cur.fetchall()
    
    # 为每个班级查询学生数量和列表
    classes_data = []
    for row in rows:
        cls = _row(row)
        cur.execute("SELECT COUNT(*) as cnt FROM students WHERE class_id=%s", (cls['id'],))
        cls['student_count'] = cur.fetchone()['cnt']
        cur.execute("""
            SELECT s.id, s.name, s.student_number, s.sort_order,
                   sa.id as account_id, sa.username as account_username
            FROM students s
            LEFT JOIN student_accounts sa ON sa.student_id=s.id
            WHERE s.class_id=%s
            ORDER BY s.sort_order, s.name
        """, (cls['id'],))
        students = cur.fetchall()
        cls['students'] = [_row(s) for s in students]
        classes_data.append(cls)
    
    db.close()
    return success(classes_data)

@app.route('/api/admin/classes', methods=['POST'])
@admin_required
def admin_create_class():
    d=request.get_json() or {}
    name=(d.get('name') or '').strip()
    desc=d.get('description','')
    if not name: return err('班级名称不能为空')
    cid=str(uuid.uuid4())[:8].upper()
    db=get_db(); cur=db.cursor()
    cur.execute("INSERT INTO classes (id,name,description) VALUES (%s,%s,%s)",(cid,name,desc))
    db.close(); return success({'id':cid})

@app.route('/api/admin/classes/<class_id>', methods=['PUT'])
@admin_required
def admin_update_class(class_id):
    d=request.get_json() or {}
    name=(d.get('name') or '').strip(); desc=d.get('description','')
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE classes SET name=%s,description=%s WHERE id=%s",(name,desc,class_id))
    db.close(); return success()

@app.route('/api/admin/classes/<class_id>', methods=['DELETE'])
@admin_required
def admin_delete_class(class_id):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM students WHERE class_id=%s",(class_id,))
    cur.execute("DELETE FROM course_classes WHERE class_id=%s",(class_id,))
    cur.execute("DELETE FROM classes WHERE id=%s",(class_id,))
    db.close(); return success()

@app.route('/api/admin/classes/<class_id>/students', methods=['GET'])
@admin_required
def admin_get_class_students(class_id):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT s.*,sa.username as account_username,sa.id as account_id FROM students s LEFT JOIN student_accounts sa ON sa.student_id=s.id WHERE s.class_id=%s ORDER BY s.sort_order,s.name",(class_id,))
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

@app.route('/api/admin/classes/<class_id>/students', methods=['POST'])
@admin_required
def admin_add_class_student(class_id):
    d = request.get_json() or {}
    students = d.get('students', [])
    # 兼容旧格式（单个学生）
    if not students:
        name = (d.get('name') or '').strip()
        student_number = d.get('student_number', '') or ''
        if not name:
            return err('姓名不能为空')
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT MAX(sort_order) as max_so FROM students WHERE class_id=%s", (class_id,))
        max_so = (cur.fetchone() or {}).get('max_so') or 0
        cur.execute(
            "INSERT INTO students (name,student_number,class_id,sort_order) VALUES (%s,%s,%s,%s)",
            (name, student_number, class_id, max_so + 1)
        )
        sid = cur.lastrowid
        db.close()
        return success({'id': sid, 'name': name, 'student_number': student_number})

    # 批量添加
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT MAX(sort_order) as max_so FROM students WHERE class_id=%s", (class_id,))
    max_so = (cur.fetchone() or {}).get('max_so') or 0

    added = []
    skipped = []
    for i, s in enumerate(students):
        name = (s.get('name') or s.get('姓名') or '').strip()
        student_number = s.get('student_number') or s.get('学号') or ''
        if not name:
            skipped.append({'index': i + 1, 'reason': '姓名为空'})
            continue
        # 检查学号是否重复（如果提供了学号）
        if student_number:
            cur.execute("SELECT id FROM students WHERE student_number=%s", (student_number,))
            if cur.fetchone():
                skipped.append({'index': i + 1, 'name': name, 'student_number': student_number, 'reason': '学号已存在'})
                continue
        cur.execute(
            "INSERT INTO students (name,student_number,class_id,sort_order) VALUES (%s,%s,%s,%s)",
            (name, student_number, class_id, max_so + 1 + len(added))
        )
        sid = cur.lastrowid
        added.append({'id': sid, 'name': name, 'student_number': student_number})

    db.close()
    return success({'added': len(added), 'skipped': len(skipped), 'students': added, 'skipped_details': skipped})

@app.route('/api/admin/students/<int:sid>', methods=['DELETE'])
@admin_required
def admin_delete_student(sid):
    db=get_db(); cur=db.cursor()
    cur.execute("DELETE FROM student_accounts WHERE student_id=%s",(sid,))
    cur.execute("DELETE FROM students WHERE id=%s",(sid,))
    db.close(); return success()

@app.route('/api/admin/students/create_accounts', methods=['POST'])
@admin_required
def admin_create_student_accounts():
    d=request.get_json() or {}; clid=str(d.get('class_id','')); def_pw=d.get('default_password','123456')
    if not clid: return err('class_id 不能为空')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT id,name,student_number FROM students WHERE class_id=%s AND id NOT IN (SELECT student_id FROM student_accounts)",(clid,))
    students=cur.fetchall()
    created=0; skipped=0
    for s in students:
        un=s.get('student_number') or f"stu_{s['id']}"
        pw_hash=bcrypt.hashpw(def_pw.encode(),bcrypt.gensalt()).decode()
        try:
            cur.execute("INSERT INTO student_accounts (student_id,username,password) VALUES (%s,%s,%s)",(s['id'],un,pw_hash))
            created+=1
        except:
            skipped+=1
    db.close(); return success({'created':created,'skipped':skipped})

@app.route('/api/admin/students/reset_password', methods=['POST'])
@admin_required
def admin_reset_student_password():
    d=request.get_json() or {}; aid=int(d.get('account_id',0)); new_p=d.get('new_password','123456')
    pw=bcrypt.hashpw(new_p.encode(),bcrypt.gensalt()).decode()
    db=get_db(); cur=db.cursor()
    cur.execute("UPDATE student_accounts SET password=%s WHERE id=%s",(pw,aid))
    db.close(); return success({'message':f'密码已重置为: {new_p}'})

@app.route('/api/admin/students/clear_accounts', methods=['POST'])
@admin_required
def admin_clear_student_accounts():
    """批量清除学生账号数据（账号变为未开通状态，学生端数据全部清除）"""
    d=request.get_json() or {}
    student_ids=d.get('student_ids',[])
    if not student_ids: return err('student_ids 不能为空')
    if not isinstance(student_ids,list): student_ids=[student_ids]
    db=get_db(); cur=db.cursor()
    cleared=0; errors=[]
    for sid in student_ids:
        try:
            # 1. 删除学生账号记录
            cur.execute("DELETE FROM student_accounts WHERE student_id=%s",(sid,))
            # 2. 删除作业提交记录
            cur.execute("DELETE FROM homework_submissions WHERE student_id=%s",(sid,))
            # 3. 删除考勤学生记录
            cur.execute("DELETE FROM attendance_student_records WHERE student_id=%s",(sid,))
            # 4. 删除学生通知
            cur.execute("DELETE FROM student_notifications WHERE student_id=%s",(sid,))
            cleared+=1
        except Exception as e:
            errors.append({'sid':sid,'error':str(e)})
    db.close()
    return success({'cleared':cleared,'errors':errors})

@app.route('/api/admin/attendance_logs', methods=['GET'])
@admin_required
def admin_attendance_logs():
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT ar.*,t.real_name as teacher_name FROM attendance_records ar JOIN teachers t ON t.id=ar.teacher_id ORDER BY ar.sign_time DESC LIMIT 200")
    rows=cur.fetchall(); db.close(); return success(_rows(rows))

@app.route('/api/admin/attendance_reports', methods=['GET'])
@admin_required
def admin_attendance_reports():
    cid=request.args.get('course_id',''); clid=request.args.get('class_id','')
    db=get_db(); cur=db.cursor()
    sql="SELECT ar.*,t.real_name as teacher_name FROM attendance_reports ar JOIN teachers t ON t.id=ar.teacher_id"; params=[]
    if cid: sql+=" WHERE ar.course_id=%s"; params.append(cid)
    if clid: sql+=" AND ar.class_id=%s" if cid else " WHERE ar.class_id=%s"; params.append(clid)
    sql+=" ORDER BY ar.created_at DESC LIMIT 100"
    cur.execute(sql,params); rows=cur.fetchall(); db.close(); return success(_rows(rows))

# ======= 时光墙（论坛） =======
@app.route('/api/forum/posts', methods=['GET'])
@forum_required
def forum_get_posts():
    cid=request.args.get('course_id',''); page=int(request.args.get('page',1)); ps=int(request.args.get('page_size',20))
    offset=(page-1)*ps
    db=get_db(); cur=db.cursor()
    sql="SELECT fp.*,t.real_name as author_real_name FROM forum_posts fp LEFT JOIN teachers t ON t.id=fp.author_id WHERE 1=1"; params=[]
    if cid: sql+=" AND fp.course_id=%s"; params.append(cid)
    sql+=" ORDER BY fp.created_at DESC LIMIT %s OFFSET %s"; params.extend([ps,offset])
    cur.execute(sql,params); posts=_rows(cur.fetchall())
    for p in posts:
        cur.execute("SELECT COUNT(*) as cnt FROM forum_comments WHERE post_id=%s",(p['id'],))
        p['comment_count']=cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as total FROM forum_posts" + (" WHERE course_id=%s" if cid else ""),([cid] if cid else []))
    total=cur.fetchone()['total']
    db.close(); return success({'posts':posts,'total':total,'page':page,'page_size':ps})

@app.route('/api/forum/posts', methods=['POST'])
@forum_required
def forum_create_post():
    ct = request.content_type or ''
    if 'multipart' in ct or 'form' in ct:
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()
        cid = str(request.form.get('course_id', ''))
        is_anonymous = request.form.get('is_anonymous', '0') in ('1', 'true', 'True')
        anon_nick = request.form.get('anonymous_nickname', '')
        images_raw = request.form.get('images', '[]')
        try: images = json.loads(images_raw)
        except: images = []
    else:
        d = request.get_json() or {}
        title = (d.get('title') or '').strip()
        content = (d.get('content') or '').strip()
        cid = str(d.get('course_id', ''))
        is_anonymous = bool(d.get('is_anonymous', False))
        anon_nick = d.get('anonymous_nickname', '')
        images = d.get('images', [])
    if not content or not cid: return err('内容和课程不能为空')
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT name as course_name FROM courses WHERE id=%s",(cid,))
    crs=cur.fetchone()
    if not crs: db.close(); return err('课程不存在',404)
    role=request.forum_role
    if role=='teacher':
        cur.execute("SELECT real_name FROM teachers WHERE id=%s",(request.forum_uid,))
        uname=(cur.fetchone() or {}).get('real_name','某老师')
    elif role=='student':
        cur.execute("SELECT name FROM students WHERE id=%s",(request.forum_uid,))
        nm=(cur.fetchone() or {}).get('name','某同学')
        uname=anon_nick if (is_anonymous and anon_nick) else nm
    else: uname='管理员'
    cur.execute("INSERT INTO forum_posts (title,content,course_id,course_name,author_id,author_name,author_type,is_anonymous,images,anonymous_nickname) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(title,content,cid,crs['course_name'],request.forum_uid,uname,role,1 if is_anonymous else 0,json.dumps(images),anon_nick))
    pid=cur.lastrowid; db.close()
    return success({'id':pid})

@app.route('/api/forum/posts/<int:pid>', methods=['GET'])
@forum_required
def forum_get_post(pid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT fp.*,t.real_name as author_real_name FROM forum_posts fp LEFT JOIN teachers t ON t.id=fp.author_id WHERE fp.id=%s",(pid,))
    post=cur.fetchone()
    if not post: db.close(); return err('帖子不存在',404)
    post=_row(post)
    cur.execute("SELECT fc.* FROM forum_comments fc WHERE fc.post_id=%s ORDER BY fc.created_at",(pid,))
    post['comments']=_rows(cur.fetchall())
    db.close(); return success(post)

@app.route('/api/forum/posts/<int:pid>', methods=['DELETE'])
@forum_required
def forum_delete_post(pid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM forum_posts WHERE id=%s",(pid,))
    post=cur.fetchone()
    if not post: db.close(); return err('帖子不存在',404)
    role=request.forum_role
    if role!='admin' and post['author_id']!=request.forum_uid: db.close(); return err('无权限删除',403)
    cur.execute("DELETE FROM forum_comments WHERE post_id=%s",(pid,))
    cur.execute("DELETE FROM forum_posts WHERE id=%s",(pid,))
    db.close(); return success()

@app.route('/api/forum/posts/<int:pid>/comments', methods=['POST'])
@forum_required
def forum_create_comment(pid):
    d=request.get_json() or {}; content=(d.get('content') or '').strip()
    is_anonymous=bool(d.get('is_anonymous',False)); anon_nick=d.get('anonymous_nickname','')
    if not content: return err('评论内容不能为空')
    db=get_db(); cur=db.cursor()
    role=request.forum_role
    if role=='teacher':
        cur.execute("SELECT real_name FROM teachers WHERE id=%s",(request.forum_uid,))
        uname=(cur.fetchone() or {}).get('real_name','某老师')
    elif role=='student':
        cur.execute("SELECT name FROM students WHERE id=%s",(request.forum_uid,))
        nm=(cur.fetchone() or {}).get('name','某同学')
        uname=anon_nick if (is_anonymous and anon_nick) else nm
    else: uname='管理员'
    cur.execute("INSERT INTO forum_comments (post_id,author_id,author_name,author_type,content,is_anonymous) VALUES (%s,%s,%s,%s,%s,%s)",(pid,request.forum_uid,uname,role,content,1 if is_anonymous else 0))
    cid=cur.lastrowid; db.close()
    return success({'id':cid})

@app.route('/api/forum/comments/<int:cid>', methods=['DELETE'])
@forum_required
def forum_delete_comment(cid):
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM forum_comments WHERE id=%s",(cid,))
    cmt=cur.fetchone()
    if not cmt: db.close(); return err('评论不存在',404)
    role=request.forum_role
    if role!='admin' and cmt['author_id']!=request.forum_uid: db.close(); return err('无权限删除',403)
    cur.execute("DELETE FROM forum_comments WHERE id=%s",(cid,))
    db.close(); return success()

@app.route('/api/forum/upload', methods=['POST'])
@forum_required
def forum_upload():
    if 'file' not in request.files: return err('请选择文件')
    f=request.files['file']
    if not f.filename: return err('文件名不能为空')
    fn=f.filename; ext=os.path.splitext(fn)[1].lower()
    if ext not in ('.jpg','.jpeg','.png','.gif','.webp'): return err('仅支持图片文件')
    sn=f"{uuid.uuid4().hex}{ext}"
    fp=os.path.join(UPLOAD_DIR,'forum',sn); f.save(fp)
    url=f"/api/forum/images/{sn}"
    return success({'url':url,'path':fp,'name':fn})

@app.route('/api/forum/images/<filename>', methods=['GET'])
def forum_image(filename):
    fp=os.path.join(UPLOAD_DIR,'forum',filename)
    if not os.path.exists(fp): return err('图片不存在',404)
    return send_file(fp)

# ======= 中药数据库API =======
@app.route('/api/herb/random', methods=['GET'])
def get_random_herb():
    """获取随机一味中药"""
    db=get_db(); cur=db.cursor()
    cur.execute("SELECT * FROM herbs ORDER BY RAND() LIMIT 1")
    herb=cur.fetchone()
    db.close()
    if not herb: return err('暂无中药数据')
    return success(_row(herb))

@app.route('/api/herbs', methods=['GET'])
def get_herbs():
    """获取中药列表"""
    db=get_db(); cur=db.cursor()
    page=int(request.args.get('page',1))
    page_size=int(request.args.get('page_size',50))
    offset=(page-1)*page_size
    cur.execute("SELECT * FROM herbs ORDER BY category,name LIMIT %s OFFSET %s",(page_size,offset))
    herbs=_rows(cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM herbs")
    total=cur.fetchone()['COUNT(*)']
    db.close()
    return success({'herbs':herbs,'total':total,'page':page,'page_size':page_size})

# ======= 扫码签到页面 =======
_SIGN_PAGE_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>智慧课堂签到</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#4f46e5;--primary-light:#818cf8;--bg:#eef2ff;
  --card-bg:#ffffff;--text:#1e1b4b;--text-sub:#6b7280;
  --success:#10b981;--warn:#f59e0b;--danger:#ef4444;
  --radius:20px;
}
body{
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue","Microsoft YaHei",sans-serif;
  background:var(--bg);
  background-image:radial-gradient(ellipse at 20% 10%, rgba(99,102,241,.12) 0%, transparent 50%),
                  radial-gradient(ellipse at 80% 90%, rgba(167,139,250,.10) 0%, transparent 50%);
  min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;
}
.card{
  background:var(--card-bg);border-radius:var(--radius);
  padding:36px 28px;width:100%;max-width:380px;
  box-shadow:0 8px 40px rgba(79,70,229,.12),0 2px 8px rgba(0,0,0,.06);
  text-align:center;position:relative;overflow:hidden;
}
.card::before{
  content:'';position:absolute;top:-60px;left:-60px;
  width:160px;height:160px;background:radial-gradient(circle,rgba(99,102,241,.08) 0%,transparent 70%);
  pointer-events:none;
}
.card::after{
  content:'';position:absolute;bottom:-40px;right:-40px;
  width:120px;height:120px;background:radial-gradient(circle,rgba(167,139,250,.08) 0%,transparent 70%);
  pointer-events:none;
}

/* header */
.logo{font-size:36px;margin-bottom:8px}
.hdr-title{font-size:22px;font-weight:800;color:var(--text);letter-spacing:.5px}
.hdr-sub{font-size:13px;color:var(--text-sub);margin-bottom:28px}

/* timer */
.timer-wrap{margin-bottom:24px}
.timer-label{font-size:12px;color:var(--text-sub);margin-bottom:8px;font-weight:500;letter-spacing:1px;text-transform:uppercase}
.timer-track{width:100%;height:6px;background:#e5e7eb;border-radius:99px;overflow:hidden;margin-bottom:8px}
.timer-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--primary),var(--primary-light));
  transition:width 1s linear;width:100%}
.timer-fill.warn{background:linear-gradient(90deg,var(--warn),var(--danger))}
.timer-num{font-size:14px;font-weight:700;color:var(--primary)}
.timer-num.warn{color:var(--danger)}

/* form */
.field{margin-bottom:18px;text-align:left}
.field label{display:block;font-size:13px;color:var(--text-sub);margin-bottom:8px;font-weight:600}
.field input{
  width:100%;padding:14px 18px;border:2px solid #e5e7eb;
  border-radius:14px;font-size:17px;color:var(--text);outline:none;
  transition:border-color .2s;background:#fafafa;font-weight:500;
}
.field input:focus{border-color:var(--primary);background:#fff}
.field input.warn{border-color:var(--danger);background:#fff5f5}

.btn-submit{
  width:100%;padding:16px;border:none;border-radius:14px;
  background:linear-gradient(135deg,var(--primary),#6366f1);
  color:#fff;font-size:18px;font-weight:700;cursor:pointer;
  letter-spacing:2px;transition:transform .15s,box-shadow .15s,opacity .15s;
  box-shadow:0 4px 16px rgba(79,70,229,.35);
}
.btn-submit:active{transform:scale(.97);box-shadow:0 2px 8px rgba(79,70,229,.25)}
.btn-submit:disabled{opacity:.45;cursor:not-allowed;transform:none}

/* msg */
.msg-box{
  margin-top:16px;padding:14px 18px;border-radius:14px;
  font-size:15px;font-weight:600;line-height:1.6;display:none;
}
.msg-box.ok{background:#d1fae5;color:#065f46;display:block;border:1.5px solid #a7f3d0}
.msg-box.err{background:#fee2e2;color:#991b1b;display:block;border:1.5px solid #fca5a5}

/* success panel */
#success-panel{display:none;text-align:center}
.succ-icon{font-size:60px;margin-bottom:12px;animation:popIn .5s cubic-bezier(.175,.885,.32,1.275)}
.succ-name{font-size:22px;font-weight:800;color:var(--text);margin-bottom:4px}
.succ-status{font-size:14px;color:var(--success);font-weight:600;margin-bottom:24px}
.succ-badge{
  display:inline-block;background:linear-gradient(135deg,#4f46e5,#818cf8);
  color:#fff;border-radius:50px;padding:14px 36px;font-size:18px;font-weight:800;
  box-shadow:0 4px 20px rgba(79,70,229,.3);margin-bottom:8px;letter-spacing:1px;
}
.succ-rank-sub{font-size:13px;color:var(--text-sub);margin-top:4px;margin-bottom:28px}
.succ-divider{width:60px;height:3px;background:linear-gradient(90deg,var(--primary),var(--primary-light));
  border-radius:99px;margin:0 auto 20px}
.succ-hint{font-size:12px;color:var(--text-sub);line-height:1.8}

/* init state */
.init-wrap{text-align:center;padding:40px 0}
.init-spinner{
  width:44px;height:44px;border:4px solid #e5e7eb;
  border-top-color:var(--primary);border-radius:50%;
  animation:spin .8s linear infinite;margin:0 auto 16px;
}
.init-text{font-size:14px;color:var(--text-sub);font-weight:500}

/* animations */
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes popIn{0%{transform:scale(0);opacity:0}60%{transform:scale(1.15)}100%{transform:scale(1);opacity:1}}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.succ-badge{animation:fadeUp .4s ease both}
</style>
</head>
<body>
<div class="card">
  <!-- Header -->
  <div class="logo">🎓</div>
  <div class="hdr-title">智慧课堂签到</div>
  <div class="hdr-sub" id="hdr-sub">正在连接签到系统...</div>

  <!-- Init loading -->
  <div class="init-wrap" id="init-area">
    <div class="init-spinner"></div>
    <div class="init-text">正在初始化，请稍候...</div>
  </div>

  <!-- Sign form -->
  <div id="form-area" style="display:none">
    <div class="timer-wrap">
      <div class="timer-label">签到剩余时间</div>
      <div class="timer-track"><div class="timer-fill" id="timer-fill"></div></div>
      <div class="timer-num" id="timer-num">15 秒</div>
    </div>
    <div class="field">
      <label>姓名</label>
      <input id="name-input" type="text" placeholder="请输入真实姓名" autocomplete="off" />
    </div>
    <button class="btn-submit" id="btn-submit" onclick="doSign()">确认签到</button>
    <div class="msg-box" id="msg-box"></div>
  </div>

  <!-- Success panel -->
  <div id="success-panel">
    <div class="succ-icon">🎉</div>
    <div class="succ-name" id="succ-name"></div>
    <div class="succ-status">✅ 签到成功</div>
    <div class="succ-badge" id="succ-badge"></div>
    <div class="succ-rank-sub" id="succ-rank-sub"></div>
    
  </div>
</div>

<script>
var params = new URLSearchParams(location.search);
var scanToken = params.get('token');
var cid = params.get('cid');
var clid = params.get('clid');

var signToken = null;
var timeLeft = 15;
var timerInterval = null;

// ── 设备指纹 ──
var deviceFp = '';
(function(){
  var ua = navigator.userAgent;
  var scr = window.screen.width+'x'+window.screen.height+'x'+window.screen.colorDepth;
  var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  deviceFp = btoa(unescape(encodeURIComponent(ua+'|'+scr+'|'+tz))).substring(0,64);
})();

// ── init_sign ──
async function initSign() {
  try {
    var r = await fetch('/api/attendance/init_sign', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({token:scanToken, cid:cid, clid:clid, device_fp:deviceFp})
    });
    var d = await r.json();
    if (d.success && d.data && d.data.sign_token) {
      signToken = d.data.sign_token;
      timeLeft = d.data.expires_in || 15;
      document.getElementById('hdr-sub').textContent = '请在规定时间内完成签到';
      document.getElementById('init-area').style.display = 'none';
      document.getElementById('form-area').style.display = 'block';
      startTimer();
      document.getElementById('name-input').focus();
    } else {
      showPageError('⚠️ ' + (d.message || '初始化失败，请重新扫码'));
    }
  } catch(e) {
    showPageError('网络异常，请检查网络后重试');
  }
}

// ── 15 秒倒计时 ──
function startTimer() {
  updateTimerUI();
  timerInterval = setInterval(function(){
    timeLeft--;
    updateTimerUI();
    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      expireSession();
    }
  }, 1000);
}

function updateTimerUI() {
  var fill = document.getElementById('timer-fill');
  var num  = document.getElementById('timer-num');
  var pct = Math.max(0, (timeLeft / 15) * 100);
  fill.style.width = pct + '%';
  num.textContent = timeLeft + ' 秒';
  if (timeLeft <= 5) {
    fill.classList.add('warn');
    num.classList.add('warn');
  } else {
    fill.classList.remove('warn');
    num.classList.remove('warn');
  }
}

function expireSession() {
  document.getElementById('form-area').style.display = 'none';
  showPageError('⏰ 签到已过期，请重新扫描新的二维码');
}

// ── 提交签到 ──
async function doSign() {
  if (!signToken) { showPageError('签到已过期，请重新扫码'); return; }
  var name = document.getElementById('name-input').value.trim();
  if (!name) { showMsg('请输入姓名', false); return; }
  var btn = document.getElementById('btn-submit');
  btn.disabled = true;
  btn.textContent = '提交中...';
  try {
    var r = await fetch('/api/attendance/submit', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name:name, sign_token:signToken, cid:cid, clid:clid})
    });
    var d = await r.json();
    if (d.success) {
      clearInterval(timerInterval);
      showSuccess(name, d.data);
    } else {
      showMsg('❌ ' + (d.message || '签到失败'), false);
      btn.disabled = false;
      btn.textContent = '确认签到';
    }
  } catch(e) {
    showMsg('提交失败，请检查网络后重试，或告知教师手动补签', false);
    btn.disabled = false;
    btn.textContent = '确认签到';
  }
}

// ── 显示签到成功（带名次） ──
function showSuccess(name, data) {
  var rank   = data && data.rank   ? data.rank   : '?';
  var total  = data && data.total  ? data.total  : '?';
  document.getElementById('succ-name').textContent = name;
  document.getElementById('succ-badge').textContent = '第 ' + rank + ' 名';
  document.getElementById('succ-rank-sub').textContent =
    '本轮次已有 ' + total + ' 人完成签到';
  document.getElementById('form-area').style.display = 'none';
  document.getElementById('success-panel').style.display = 'block';
}

// ── 消息提示 ──
function showMsg(text, ok) {
  var m = document.getElementById('msg-box');
  m.textContent = text;
  m.className = 'msg-box ' + (ok ? 'ok' : 'err');
  m.style.display = 'block';
}

function showPageError(text) {
  document.getElementById('init-area').style.display = 'none';
  document.getElementById('hdr-sub').textContent = text;
  var m = document.getElementById('msg-box');
  m.textContent = text;
  m.className = 'msg-box err';
  m.style.display = 'block';
}

// ── 启动 ──
if (!scanToken || !cid || !clid) {
  showPageError('二维码无效，请重新扫码');
} else {
  document.getElementById('hdr-sub').textContent = '正在连接签到系统...';
  initSign();
}

document.getElementById('name-input').addEventListener('keydown', function(e){
  if (e.key === 'Enter') doSign();
});
</script>
</body>
</html>'''

@app.route('/sign', methods=['GET'])
def sign_page():
    """扫码签到页面 - 手机端访问"""
    t_val = request.args.get('t', '0')
    # 旧二维码（t 参数超过 10 秒）直接返回过期提示
    try:
        qr_ts = int(t_val) / 1000.0
        if time.time() - qr_ts > 10:
            # 过期替换：显示错误，隐藏加载区
            expired_html = _SIGN_PAGE_HTML
            expired_html = expired_html.replace(
                "id='init-area'",
                "id='init-area' style='display:none'"
            )
            expired_html = expired_html.replace(
                "id='hdr-sub'>正在连接签到系统...",
                "id='hdr-sub'>⚠️ 二维码已失效"
            )
            expired_html = expired_html.replace(
                "id='msg-box'></div>",
                "id='msg-box' class='msg-box err' style='display:block'>请重新扫描新的二维码</div>"
            )
            from flask import make_response
            resp = make_response(expired_html)
            resp.content_type = 'text/html; charset=utf-8'
            return resp
    except Exception:
        pass
    from flask import make_response
    resp = make_response(_SIGN_PAGE_HTML)
    resp.content_type = 'text/html; charset=utf-8'
    return resp

@app.route('/api/attendance/init_sign', methods=['POST'])
def att_init_sign():
    """学生扫码进入页面 → 校验 scan_token → 分配 sign_token（15秒有效期）"""
    d = request.get_json() or {}
    token  = (d.get('token') or '').strip()
    cid    = str(d.get('cid') or '').strip()
    clid   = str(d.get('clid') or '').strip()
    device_fp = (d.get('device_fp') or '').strip()

    if not token: return fail('签到令牌缺失，请重新扫码')
    if not cid or not clid: return fail('参数不完整，请重新扫码')

    # ── 1. 校验 scan_token（扫码有效期 10 秒，从 DB 读取）──
    tk = _db_scan_token_get(token)
    if not tk:
        return fail('二维码已失效，请重新扫码')
    if tk['course_id'] != cid:
        return fail('二维码无效，请重新扫码')

    # ── 2. 找活跃会话（教师是否在签到）──
    active_session = None
    for sk, sv in _att_sessions.items():
        if sv['course_id'] == cid and sv['class_id'] == clid and sv.get('active'):
            active_session = (sk, sv)
            break

    if not active_session:
        return fail('签到已结束，请联系教师手动补签')

    # ── 3. 设备指纹防重：同一设备本轮次只能签到一次 ──
    sk = active_session[0]
    if device_fp:
        existing = _db_device_check(device_fp, sk)
        if existing:
            # 设备锁存在，且精确匹配当前 session_key → 重复扫码
            return fail('该设备已签到，请勿重复扫码')

    # ── 4. 保留 scan_token（不删除，多个学生可共用10秒有效期的二维码）
    #     生成 sign_token（15秒签到窗口）
    sign_token = secrets.token_hex(16)
    _db_sign_token_create(sign_token, cid, clid, sk, device_fp, int(time.time())+15)

    return success({'sign_token': sign_token, 'expires_in': 15})

@app.route('/api/attendance/submit', methods=['POST'])
def att_submit():
    """学生提交签到（凭 sign_token 校验，15秒有效期）"""
    d = request.get_json() or {}
    name       = (d.get('name') or '').strip()
    sign_token = (d.get('sign_token') or '').strip()
    cid        = str(d.get('cid') or '').strip()
    clid       = str(d.get('clid') or '').strip()

    if not name:  return fail('姓名不能为空')
    if not sign_token: return fail('签到令牌缺失，请重新扫码')
    if not cid or not clid: return fail('参数不完整，请重新扫码')

    # ── 1. 校验 sign_token（从 DB 读取）──
    tk = _db_sign_token_get(sign_token)
    if not tk:
        return fail('签到已过期，请重新扫码')
    if tk['course_id'] != cid or tk['class_id'] != clid:
        return fail('签到令牌无效')

    # ── 2. 查花名册 ──
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT name FROM students WHERE class_id=%s", (clid,))
    roster = [r['name'] for r in cur.fetchall()]
    if roster and name not in roster:
        db.close()
        return fail(f'"{name}" 不在该班级花名册中，请确认姓名或联系教师手动补签')

    # ── 3. 防重复签到（从 DB 查询已签到名单）──
    sk = tk['session_key']
    signed_names = _db_signed_names(sk)
    if name in signed_names:
        db.close()
        return fail(f'"{name}" 已签到，请勿重复提交')

    # ── 4. 消耗 sign_token，写入 DB，记录设备锁 ──
    _db_sign_token_del(sign_token)

    sign_key = f"{sk}:{name}"
    cur.execute(
        "INSERT INTO attendance_records (session_key,course_id,class_id,student_name,sign_time)"
        " VALUES (%s,%s,%s,%s,%s)"
        " ON DUPLICATE KEY UPDATE sign_time=VALUES(sign_time)",
        (sign_key, cid, clid, name, datetime.now())
    )
    db.close()

    # 记录设备指纹，防止该设备本轮次再次签到
    device_fp = tk.get('device_fp')
    if device_fp:
        _db_device_lock(device_fp, cid, clid, sk)

    # 计算签到名次（从 DB 重新查，保证准确性）
    updated_names = _db_signed_names(sk)
    rank = updated_names.index(name) + 1
    total = len(updated_names)
    return success({'message': f'{name} 签到成功', 'rank': rank, 'total': total})


if __name__ == '__main__':
    _init_token_tables()
    _ensure_indexes()
    logger.info("[启动] 考勤 token 表初始化完成，关键索引检查完成，开始监听...")
    print("Starting SmartClass Backend on http://0.0.0.0:5000")
    from waitress import serve
    logger.info("[启动] 使用 waitress 多线程模式（--threads=8）")
    print("Using waitress multi-threaded server (8 threads)")
    serve(app, host='0.0.0.0', port=5000, threads=8)

# gunicorn 启动时自动初始化（单 worker 模式推荐）
@app.before_request
def _startup_check():
    if not hasattr(app, '_indexes_ok'):
        _init_token_tables()
        _ensure_indexes()
        app._indexes_ok = True
        logger.info("[启动] 索引初始化完成")
