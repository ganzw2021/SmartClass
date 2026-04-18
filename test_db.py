import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests, pymysql, bcrypt

BASE = 'http://127.0.0.1:5000'
r = requests.post(f'{BASE}/api/auth/login',
    json={'type': 'admin', 'username': 'admin', 'password': 'Admin@123456'}, timeout=8)
admin_h = {'Authorization': f"Bearer {r.json()['data']['token']}"}

# 找所有班级及学生
classes = requests.get(f'{BASE}/api/admin/classes', headers=admin_h, timeout=8).json()['data']
print(f"班级列表: {[(c['id'], c['name']) for c in classes]}")

# 给所有班级的学生创建账号（默认密码 123456）
for cls in classes:
    r2 = requests.post(f'{BASE}/api/admin/students/create_accounts',
        json={'class_id': cls['id'], 'default_password': '123456'},
        headers=admin_h, timeout=8)
    result = r2.json()['data']
    print(f"班级 {cls['id']} ({cls['name']}): created={result['created']} skipped={result['skipped']}")

# 再找 HW4 已评分的学生，用账号登录测试
r3 = requests.get(f'{BASE}/api/admin/classes/{classes[0]["id"]}/students', headers=admin_h, timeout=8)
students = r3.json()['data']
print(f"\n班级1学生数: {len(students)}, 有账号: {sum(1 for s in students if s.get('account_id'))}")

# 找 HW4 中 周佳 (id=5973) - 已知 score=80
r4 = requests.post(f'{BASE}/api/auth/login',
    json={'type': 'admin', 'username': 'admin', 'password': 'Admin@123456'}, timeout=8)
admin_h2 = {'Authorization': f"Bearer {r4.json()['data']['token']}"}

# 直接通过数据库查周佳的账号
conn = pymysql.connect(host='localhost', user='root', password='Root@123456',
    database='smartclass', charset='utf8mb4')
cur = conn.cursor()
cur.execute("""
    SELECT sa.username, sa.student_id, s.name, s.student_number
    FROM student_accounts sa
    JOIN students s ON sa.student_id = s.id
    WHERE s.id = 5973
""")
row = cur.fetchone()
print(f"\n周佳账号: {row}")
if row:
    username, student_id, name, sn = row
    r5 = requests.post(f'{BASE}/api/auth/login',
        json={'type': 'student', 'username': username, 'password': '123456'}, timeout=8)
    print(f"周佳登录 {username}/123456: {r5.status_code} {r5.text[:100]}")
    if r5.status_code == 200:
        stu_token = r5.json()['data']['token']
        stu_h = {'Authorization': f'Bearer {stu_token}'}
        r6 = requests.get(f'{BASE}/api/student/homework', headers=stu_h, timeout=8)
        hws = r6.json().get('data', [])
        print(f"\n周佳学生端作业 ({len(hws)} 个):")
        for hw in hws:
            sub = hw.get('submission') or {}
            gs_top = hw.get('grading_status')
            gs_sub = sub.get('grading_status')
            score_top = hw.get('score')
            score_sub = sub.get('score')
            msg_top = hw.get('auto_grade_message')
            print(f"  [{hw['id']}] {hw['title'][:20]}")
            print(f"    submitted={hw.get('submitted')} sub_id={sub.get('id')}")
            print(f"    top:  gs={gs_top!r} score={score_top}")
            print(f"    sub:  gs={gs_sub!r} score={score_sub}")
            print(f"    msg={str(msg_top)[:50]!r}")
conn.close()
