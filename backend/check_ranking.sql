import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='Root@123456', database='smartclass', charset='utf8mb4', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 模拟 _trigger_auto_grading 中的查询（取 submission_id=47）
submission_id = 47
cur.execute('''
    SELECT hs.*, h.has_grading_script, h.auto_grade_enabled, h.total_score, h.class_id
    FROM homework_submissions hs
    JOIN homework h ON hs.homework_id = h.id
    WHERE hs.id = %s
''', (submission_id,))
sub = cur.fetchone()
print('sub student_id:', sub['student_id'], type(sub['student_id']))
print('sub class_id:', sub['class_id'], type(sub['class_id']))
print('sub student_id type check:', type(sub['student_id']) == int)

# 模拟 _do_update_ranking 的查询
student_id = sub['student_id']
cur.execute('''
    SELECT COUNT(*) as hw_count,
           COALESCE(SUM(COALESCE(score, auto_score)), 0) as total_score
    FROM homework_submissions
    WHERE student_id=%s
      AND (score IS NOT NULL OR auto_score IS NOT NULL)
''', (student_id,))
r = cur.fetchone()
print()
print('hw_count:', r['hw_count'], 'total_score:', r['total_score'])

# 测试 INSERT（用 id=47 的数据）
# 先删掉刚才测试插入的
cur.execute('DELETE FROM homework_score_ranking WHERE student_id = %s', (student_id,))
conn.commit()

# 模拟 _do_update_ranking 的 INSERT
class_id = sub['class_id']
cur.execute('SELECT name FROM students WHERE id=%s', (student_id,))
student_name_row = cur.fetchone()
student_name = student_name_row['name'] if student_name_row else ''

print()
print('准备插入: class_id=', class_id, 'student_id=', student_id, 'name=', student_name, 'total=', r['total_score'])
result = cur.execute(
    'INSERT INTO homework_score_ranking (class_id, student_id, student_name, total_score, homework_count) VALUES (%s, %s, %s, %s, %s)',
    (class_id, student_id, student_name, r['total_score'], r['hw_count'])
)
conn.commit()
print('INSERT result:', result)

# 验证
cur.execute('SELECT * FROM homework_score_ranking WHERE student_id=%s', (student_id,))
verify = cur.fetchone()
print('验证插入:', verify)

cur.close()
conn.close()
