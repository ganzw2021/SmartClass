# -*- coding: utf-8 -*-
"""测试考勤流程：session_key不刷新，scan_token不删除"""
import warnings, time, sys, os
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from backend.app import app, _db_scan_token_get

OK = "[OK]"
FAIL = "[FAIL]"

print("=" * 50)
print("Test: scan_token can be used by multiple students")
print("=" * 50)

with app.test_client() as client:
    # Login as admin
    resp = client.post('/api/auth/login', json={'type': 'admin', 'username': 'admin', 'password': 'Admin@123456'})
    teacher_token = resp.get_json()['data']['token']
    headers = {'Authorization': teacher_token}

    # Get course and class
    resp = client.get('/api/courses', headers=headers)
    courses = resp.get_json().get('data', {}).get('courses', [])
    if not courses:
        print(f"{FAIL} No courses found")
        sys.exit(1)
    
    cid = courses[0]['id']
    classes = courses[0].get('classes', [])
    if not classes:
        print(f"{FAIL} No classes found")
        sys.exit(1)
    clid = classes[0]['id']
    print(f"Using course {cid}, class {clid}")

    # Start attendance
    resp = client.post('/api/attendance/start', json={'course_id': cid, 'class_id': clid}, headers=headers)
    data = resp.get_json()
    if not data.get('success'):
        print(f"{FAIL} Start failed: {data}")
        sys.exit(1)
    sk = data['data']['session_key']
    print(f"1. Start attendance: session_key = {sk}")

    # Call qr multiple times, verify session_key stays the same
    sk_list = []
    token_list = []
    for i in range(3):
        resp = client.get(f'/api/attendance/qr?course_id={cid}&class_id={clid}', headers=headers)
        d = resp.get_json()['data']
        sk_list.append(d['session_key'])
        token_list.append(d['token'])
        print(f"2.{i+1} Refresh QR: token = {d['token'][:16]}..., session_key = {d['session_key']}")
        time.sleep(0.2)

    # Verify session_key is consistent
    if len(set(sk_list)) == 1:
        print(f"{OK} session_key is consistent: {sk_list[0]}")
    else:
        print(f"{FAIL} session_key changed: {sk_list}")

    # Verify scan_token exists
    token = token_list[-1]
    tk = _db_scan_token_get(token)
    if tk:
        print(f"{OK} scan_token exists: {token[:16]}...")
    else:
        print(f"{FAIL} scan_token not found")

    # Student A scans
    resp = client.post('/api/attendance/init_sign', json={
        'token': token,
        'cid': cid,
        'clid': clid,
        'device_fp': 'device_A'
    })
    result = resp.get_json()
    print(f"3. Student A scans: {'OK' if result.get('success') else 'FAIL'} - {result.get('message', '')}")

    # Verify token not deleted
    tk = _db_scan_token_get(token)
    if tk:
        print(f"4. {OK} scan_token still valid (not deleted): {token[:16]}...")
    else:
        print(f"4. {FAIL} scan_token was deleted")

    # Student B scans with same token
    resp = client.post('/api/attendance/init_sign', json={
        'token': token,
        'cid': cid,
        'clid': clid,
        'device_fp': 'device_B'
    })
    result = resp.get_json()
    print(f"5. Student B scans (same token): {'OK' if result.get('success') else 'FAIL'} - {result.get('message', '')}")

print("\n" + "=" * 50)
print("Test complete!")
print("=" * 50)