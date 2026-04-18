"""
数据迁移脚本：将 tcm_data.json 迁移到 MySQL 数据库
运行方式：python migrate_data.py
"""
import json
import sys
import os
import bcrypt
import pymysql

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'smartclass',
    'charset': 'utf8mb4',
    'autocommit': True
}

JSON_FILE = r"C:\Users\Administrator\Desktop\smartclassproject - 副本\智慧课堂教师端\tcm_data.json"

def get_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def migrate():
    print("=" * 50)
    print("智慧课堂数据迁移工具")
    print("=" * 50)

    # 读取 JSON 数据
    if not os.path.exists(JSON_FILE):
        print(f"❌ 找不到数据文件：{JSON_FILE}")
        sys.exit(1)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ 读取数据文件成功")
    print(f"   - 班级数量：{len(data.get('classes', []))}")
    print(f"   - 课程数量：{len(data.get('courses', []))}")
    print(f"   - 成绩记录：{len(data.get('scores', {}))}")

    conn = get_db()
    cur = conn.cursor()

    # 1. 获取或创建默认教师（使用 JSON 中的 teacherId）
    teacher_token = data.get('settings', {}).get('teacherId', 'teacher_default')
    teacher = cur.execute("SELECT id FROM teachers WHERE teacher_token=%s", (teacher_token,))
    teacher = cur.fetchone()

    if not teacher:
        # 检查是否有 admin 账号
        cur.execute("SELECT id FROM teachers WHERE username='admin'")
        teacher = cur.fetchone()

    if not teacher:
        # 创建默认管理员
        pwd_hash = bcrypt.hashpw('Admin@123456'.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO teachers (username, real_name, password_hash, teacher_token) VALUES (%s,%s,%s,%s)",
            ('admin', '管理员教师', pwd_hash, teacher_token)
        )
        teacher_id = cur.lastrowid
        print(f"✅ 已创建默认教师账号 (admin / Admin@123456)")
    else:
        teacher_id = teacher['id']
        # 更新 teacher_token
        cur.execute("UPDATE teachers SET teacher_token=%s WHERE id=%s", (teacher_token, teacher_id))
        print(f"✅ 使用已有教师账号 (id={teacher_id})")

    # 2. 迁移班级和学生
    print("\n📚 迁移班级数据...")
    classes_migrated = 0
    students_migrated = 0

    for cls in data.get('classes', []):
        cls_id = cls['id']
        cls_name = cls['name']
        students = cls.get('students', [])

        # 插入班级（若存在则跳过）
        cur.execute("SELECT id FROM classes WHERE id=%s", (cls_id,))
        existing = cur.fetchone()
        if not existing:
            cur.execute(
                "INSERT INTO classes (id, name, teacher_id) VALUES (%s, %s, %s)",
                (cls_id, cls_name, teacher_id)
            )
            classes_migrated += 1
        else:
            cur.execute("UPDATE classes SET name=%s, teacher_id=%s WHERE id=%s", (cls_name, teacher_id, cls_id))

        # 清空并重新插入学生
        cur.execute("DELETE FROM students WHERE class_id=%s", (cls_id,))
        for i, stu_name in enumerate(students):
            if stu_name.strip():
                cur.execute(
                    "INSERT IGNORE INTO students (name, class_id, sort_order) VALUES (%s, %s, %s)",
                    (stu_name.strip(), cls_id, i)
                )
                students_migrated += 1

        print(f"   ✓ {cls_name} ({len(students)} 名学生)")

    print(f"   → 迁移班级 {classes_migrated} 个，学生 {students_migrated} 名")

    # 3. 迁移课程
    print("\n📖 迁移课程数据...")
    courses_migrated = 0

    for course in data.get('courses', []):
        crs_id = course['id']
        crs_name = course['name']
        crs_term = course.get('term', '')

        cur.execute("SELECT id FROM courses WHERE id=%s", (crs_id,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO courses (id, name, term, teacher_id) VALUES (%s, %s, %s, %s)",
                (crs_id, crs_name, crs_term, teacher_id)
            )
            courses_migrated += 1
            print(f"   ✓ {crs_name} ({crs_term})")
        else:
            cur.execute("UPDATE courses SET name=%s, term=%s, teacher_id=%s WHERE id=%s",
                       (crs_name, crs_term, teacher_id, crs_id))

    print(f"   → 迁移课程 {courses_migrated} 门")

    # 4. 迁移成绩
    print("\n🏆 迁移成绩数据...")
    scores_migrated = 0
    scores_skipped = 0

    for key, score in data.get('scores', {}).items():
        # key 格式: crs_xxx_cls_xxx_姓名
        parts = key.split('_')
        # 解析：前两段是 course_id，中间两段是 class_id，剩余是姓名
        try:
            # 找到第二个 cls_ 的位置
            # key: crs_1767600319496_cls_1767599510284_李江平
            crs_prefix = 'crs_'
            cls_prefix = '_cls_'
            crs_end = key.index(cls_prefix)
            course_id = key[:crs_end]
            rest = key[crs_end + 5:]  # 去掉 _cls_
            # rest: 1767599510284_李江平
            underscore_pos = rest.index('_')
            class_id = 'cls_' + rest[:underscore_pos]
            student_name = rest[underscore_pos + 1:]

            att = score.get('att', 20)
            interact = score.get('interact', 0)
            hw = score.get('hw', 20)

            # 验证课程和班级存在
            cur.execute("SELECT id FROM courses WHERE id=%s", (course_id,))
            if not cur.fetchone():
                scores_skipped += 1
                continue
            cur.execute("SELECT id FROM classes WHERE id=%s", (class_id,))
            if not cur.fetchone():
                scores_skipped += 1
                continue

            cur.execute(
                """INSERT INTO scores (course_id, class_id, student_name, att_score, interact_score, hw_score)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE att_score=%s, interact_score=%s, hw_score=%s""",
                (course_id, class_id, student_name, att, interact, hw, att, interact, hw)
            )
            scores_migrated += 1

        except Exception as e:
            print(f"   ⚠️  跳过 {key}: {e}")
            scores_skipped += 1

    print(f"   → 迁移成绩 {scores_migrated} 条，跳过 {scores_skipped} 条")

    cur.close()
    conn.close()

    print("\n" + "=" * 50)
    print("✅ 数据迁移完成！")
    print("=" * 50)
    print(f"教师账号：admin")
    print(f"初始密码：Admin@123456")
    print(f"登录地址：http://localhost:3001")
    print("=" * 50)


if __name__ == '__main__':
    migrate()
