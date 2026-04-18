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
        class_id = 'cls_1774406783623'
        
        # 模拟教师获取班级学生列表接口的SQL
        cur.execute("""
            SELECT s.id, s.name, s.student_number, s.sort_order, s.created_at,
                   sa.avatar, sa.bio
            FROM students s
            LEFT JOIN student_accounts sa ON s.id = sa.student_id
            WHERE s.class_id = %s
            ORDER BY s.sort_order, s.id
        """, (class_id,))
        
        students = cur.fetchall()
        print('=== 教师接口返回的学生数据 ===')
        for s in students:
            avatar_len = len(s['avatar']) if s['avatar'] else 0
            print(f"id={s['id']}, name={s['name']}, student_number={s['student_number']}, avatar_len={avatar_len}, bio={s['bio']}")
finally:
    conn.close()
