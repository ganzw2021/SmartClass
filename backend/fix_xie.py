import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='Root@123456', database='smartclass', charset='utf8mb4')
cur = conn.cursor()
# 查谢旭华
cur.execute("SELECT id, name, class_id FROM students WHERE id=6011")
r = cur.fetchone()
print('student:', r)
# 更新排名表
cur.execute("UPDATE homework_score_ranking SET total_score=60, homework_count=2 WHERE student_id=6011")
print('affected rows:', cur.rowcount)
conn.commit()
conn.close()
print('done')

