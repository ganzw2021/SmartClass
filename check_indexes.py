import pymysql, time

conn = pymysql.connect(host='localhost', port=3306, user='root', password='Root@123456', database='smartclass', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

tables = ['homework', 'homework_submissions', 'scores', 'students',
          'student_accounts', 'course_classes', 'courses', 'classes', 'teachers']
for t in tables:
    cur.execute(f"SHOW INDEX FROM {t}")
    indexes = cur.fetchall()
    if indexes:
        print(f"\n=== {t} ===")
        for idx in indexes:
            print(f"  {idx['Key_name']}: {idx['Column_name']} ({idx['Index_type']}) unique={idx['Non_unique']==0}")

conn.close()
