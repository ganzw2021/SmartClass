import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='Root@123456', database='smartclass', charset='utf8mb4', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 检查有没有 pending 状态的提交（还未触发自动评分）
cur.execute("SELECT COUNT(*) as cnt FROM homework_submissions WHERE grading_status='pending'")
r = cur.fetchone()
print('pending状态的提交:', r['cnt'])

# 检查 teacher_grade_enabled 和 grading_status='done' 的提交中，排行榜是否有对应记录
cur.execute('''
    SELECT COUNT(DISTINCT hs.student_id) as graded_students
    FROM homework_submissions hs
    JOIN homework h ON hs.homework_id = h.id
    WHERE (hs.score IS NOT NULL OR hs.auto_score IS NOT NULL)
''')
r2 = cur.fetchone()
print('有评分的提交学生数:', r2['graded_students'])

cur.execute('SELECT COUNT(*) as ranked_students FROM homework_score_ranking')
r3 = cur.fetchone()
print('排行榜学生数:', r3['ranked_students'])

cur.close()
conn.close()
