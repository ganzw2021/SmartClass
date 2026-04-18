import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='Root@123456', database='smartclass', charset='utf8mb4', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 回填所有已有分数的学生到排行榜
backfill = '''
INSERT INTO homework_score_ranking (class_id, student_id, student_name, total_score, homework_count)
SELECT
    h.class_id,
    hs.student_id,
    MAX(hs.student_name) as student_name,
    COALESCE(SUM(COALESCE(hs.score, hs.auto_score)), 0) as total_score,
    COUNT(*) as homework_count
FROM homework_submissions hs
JOIN homework h ON hs.homework_id = h.id
WHERE hs.score IS NOT NULL OR hs.auto_score IS NOT NULL
GROUP BY h.class_id, hs.student_id
ON DUPLICATE KEY UPDATE
    total_score = VALUES(total_score),
    homework_count = VALUES(homework_count),
    student_name = VALUES(student_name),
    updated_at = CURRENT_TIMESTAMP
'''

result = cur.execute(backfill)
print(f'回填完成，影响行数: {result}')
conn.commit()

# 验证结果
cur.execute('SELECT class_id, student_id, student_name, total_score, homework_count FROM homework_score_ranking ORDER BY total_score DESC')
rows = cur.fetchall()
print()
print('=== homework_score_ranking 回填后数据 ===')
for r in rows:
    print(f"  班级={r['class_id']} 学生={r['student_name']} 总分={r['total_score']} 作业数={r['homework_count']}")

cur.close()
conn.close()
