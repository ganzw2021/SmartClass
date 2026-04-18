import pymysql
import pymysql.cursors

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='Root@123456',
    database='smartclass',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        # 查询所有学生账号的头像和签名
        cur.execute('SELECT id, student_id, username, LENGTH(avatar) as avatar_len, LEFT(avatar, 50) as avatar_preview, bio FROM student_accounts')
        rows = cur.fetchall()
        print('=== student_accounts 表数据 ===')
        for r in rows:
            print(f"ID={r['id']}, student_id={r['student_id']}, username={r['username']}, avatar_len={r['avatar_len']}, bio={r['bio']}")
            if r['avatar_preview']:
                print(f"  avatar_preview={r['avatar_preview']}...")
        
        # 查询学生表关联
        cur.execute('SELECT s.id, s.name, s.student_number, s.class_id, c.name as class_name FROM students s LEFT JOIN classes c ON s.class_id = c.id')
        students = cur.fetchall()
        print('\n=== students 表数据 ===')
        for s in students:
            print(f"ID={s['id']}, name={s['name']}, student_number={s['student_number']}, class_id={s['class_id']}, class_name={s['class_name']}")
finally:
    conn.close()
