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
        # 查询有头像的学生的完整信息
        cur.execute('''
            SELECT sa.id as account_id, sa.student_id, sa.username as account_username, 
                   sa.bio, LENGTH(sa.avatar) as avatar_len,
                   s.name as student_name, s.student_number, s.class_id,
                   c.name as class_name
            FROM student_accounts sa
            JOIN students s ON sa.student_id = s.id
            LEFT JOIN classes c ON s.class_id = c.id
            WHERE LENGTH(sa.avatar) > 0
        ''')
        rows = cur.fetchall()
        print('=== 有头像的学生 ===')
        for r in rows:
            print(f"account_id={r['account_id']}, student_id={r['student_id']}, name={r['student_name']}, number={r['student_number']}, class={r['class_name']}, bio={r['bio']}")
        
        # 查询所有班级
        cur.execute('SELECT * FROM classes')
        classes = cur.fetchall()
        print('\n=== 所有班级 ===')
        for c in classes:
            print(f"id={c['id']}, name={c['name']}")
            
        # 查询课程班级关联
        cur.execute('''
            SELECT cc.*, c.name as course_name, c.teacher_id, t.real_name as teacher_name
            FROM course_classes cc
            JOIN courses c ON cc.course_id = c.id
            JOIN teachers t ON c.teacher_id = t.id
        ''')
        cc = cur.fetchall()
        print('\n=== 课程班级关联 ===')
        for x in cc:
            print(f"course={x['course_name']}, class_id={x['class_id']}, teacher={x['teacher_name']}")
finally:
    conn.close()
