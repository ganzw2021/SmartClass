import pymysql, jwt
conn = pymysql.connect(host='localhost', port=3306, user='root', password='Root@123456', database='smartclass', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT id FROM students LIMIT 1")
sid = cur.fetchone()[0]
conn.close()
token = jwt.encode({'user_id': sid, 'role': 'student'}, 'smartclass_jwt_secret_2026', algorithm='HS256')
print('student_id:', sid)

import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:5000/api/student/courses',
    headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    print(json.loads(r.read()))
