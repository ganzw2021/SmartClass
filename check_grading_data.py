import requests, sys

BASE = 'http://127.0.0.1:5000'
r = requests.post(f'{BASE}/api/auth/login', json={'type':'admin','username':'admin','password':'Admin@123456'}, timeout=8)
admin_h = {'Authorization': f"Bearer {r.json()['data']['token']}"}

r2 = requests.get(f'{BASE}/api/admin/classes', headers=admin_h, timeout=8)
classes = r2.json()['data']
print(f"Classes: {len(classes)}")

all_students = []
for c in classes:
    r3 = requests.get(f'{BASE}/api/admin/classes/{c["id"]}/students', headers=admin_h, timeout=8)
    students = r3.json()['data']
    all_students.extend(students)

with_acc = [s for s in all_students if s.get('account_id')]
print(f"Students with accounts: {len(with_acc)}")
if with_acc:
    stu = with_acc[0]
    print(f"Using: {stu['name']} / {stu.get('account_username')} / acc_id={stu['account_id']}")
else:
    print("No students with accounts found")
    sys.exit(0)

import bcrypt
pw = bcrypt.hashpw('123456'.encode(), bcrypt.gensalt()).decode()
r4 = requests.post(f'{BASE}/api/admin/students/reset_password',
    json={'account_id': stu['account_id'], 'new_password': '123456'},
    headers=admin_h, timeout=8)
print(f"Reset: {r4.json()}")

r5 = requests.post(f'{BASE}/api/auth/login',
    json={'type':'student','username':stu.get('account_username'),'password':'123456'}, timeout=8)
print(f"Login: {r5.status_code} {r5.text[:200]}")
if r5.status_code != 200:
    sys.exit(0)

stu_token = r5.json()['data']['token']
stu_h = {'Authorization': f"Bearer {stu_token}"}

r6 = requests.get(f'{BASE}/api/student/homework', headers=stu_h, timeout=8)
print(f"Homework API: {r6.status_code}")
hws = r6.json()['data']
print(f"Homework count: {len(hws)}")
for hw in hws:
    sub = hw.get('submission')
    print(f"  HW{hw['id']} [{hw['title'][:20]}] submitted={hw.get('submitted')} sub={type(sub)} score={hw.get('score')} status={hw.get('grading_status')} msg={str(hw.get('auto_grade_message',''))[:40]}")
    if sub:
        print(f"    sub keys: {list(sub.keys()) if isinstance(sub, dict) else 'N/A'}")
