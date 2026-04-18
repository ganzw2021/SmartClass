import requests, time

BASE = 'http://127.0.0.1:5000'

# 登录获取 token
r = requests.post(f'{BASE}/api/auth/login', json={'type':'admin','username':'admin','password':'Admin@123456'}, timeout=15)
admin_token = r.json()['data']['token']
admin_hdr = {'Authorization': f'Bearer {admin_token}'}

r2 = requests.post(f'{BASE}/api/auth/login', json={'type':'teacher','username':'18979576263','password':'081097'}, timeout=15)
teacher_token = r2.json()['data']['token']
teacher_hdr = {'Authorization': f'Bearer {teacher_token}'}

r3 = requests.post(f'{BASE}/api/auth/login', json={'type':'student','username':'2515030301','password':'25150303'}, timeout=15)
student_token = r3.json()['data']['token']
student_hdr = {'Authorization': f'Bearer {student_token}'}

endpoints = [
    # 管理端
    ('GET', '/api/admin/stats', admin_hdr, 'admin: 统计概览'),
    ('GET', '/api/admin/classes', admin_hdr, 'admin: 班级列表'),
    ('GET', '/api/admin/teachers', admin_hdr, 'admin: 教师列表'),
    ('GET', '/api/admin/courses', admin_hdr, 'admin: 课程列表'),
    ('GET', '/api/admin/homework', admin_hdr, 'admin: 作业列表'),
    # 教师端
    ('GET', '/api/teacher/homework', teacher_hdr, 'teacher: 作业列表'),
    ('GET', '/api/teacher/scores/list?page=1&pageSize=20', teacher_hdr, 'teacher: 平时分列表'),
    ('GET', '/api/homework/ranking/cls_1774597906326', teacher_hdr, 'teacher: 作业排行榜'),
    # 学生端
    ('GET', '/api/student/profile', student_hdr, 'student: 个人信息'),
    ('GET', '/api/student/homework', student_hdr, 'student: 作业列表'),
]

print(f"{'端点':<50} {'耗时':>8}")
print("-" * 60)
for method, path, hdr, label in endpoints:
    url = f'{BASE}{path}'
    for _ in range(3):
        t0 = time.time()
        if method == 'GET':
            r = requests.get(url, headers=hdr, timeout=30)
        ms = (time.time() - t0) * 1000
    print(f"{label:<50} {ms:>7.0f}ms  code={r.status_code}")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:200]}")
