# -*- coding: utf-8 -*-
"""
修复 homework_submissions 中 score=NULL 但 auto_score 有值的情况
"""
import pymysql
from pymysql.cursors import DictCursor

conn = pymysql.connect(host='localhost', user='root', password='Root@123456', database='smartclass', charset='utf8mb4', cursorclass=DictCursor)
cur = conn.cursor()

print('=== Step 1: 修复 score=NULL 的记录 ===')

# 找到所有 score=NULL 但 auto_score 有值的记录
cur.execute("""
    SELECT hs.id, hs.homework_id, hs.student_id, hs.student_name, hs.auto_score,
           h.total_score, h.title, sa.file_path
    FROM homework_submissions hs
    JOIN homework h ON h.id = hs.homework_id
    LEFT JOIN submission_attachments sa ON sa.submission_id = hs.id
    WHERE hs.score IS NULL AND hs.auto_score IS NOT NULL
    ORDER BY hs.homework_id, hs.id
""")
null_subs = cur.fetchall()
print(f'Found {len(null_subs)} submissions with NULL score but auto_score exists')

fixed = 0
errors = 0
for sub in null_subs:
    sid = sub['id']
    hid = sub['homework_id']
    auto_score = float(sub['auto_score'])
    total_score = float(sub['total_score'] or 100)
    norm = round(auto_score / 100 * total_score, 2)

    try:
        # 直接从 auto_score 计算 norm 并更新
        cur.execute("""
            UPDATE homework_submissions
            SET score=%s, grading_status='done'
            WHERE id=%s AND (score IS NULL OR score != %s)
        """, (norm, sid, norm))
        fixed += 1
        print(f'  FIXED ID={sid} | {sub["student_name"]} | HW{hid}({sub["title"]}) | auto_score={auto_score} -> score={norm}')
    except Exception as e:
        errors += 1
        print(f'  ERROR ID={sid}: {e}')

print(f'\nFixed: {fixed}, Errors: {errors}')

print('\n=== Step 2: 重建排行榜 ===')

# 获取所有有分数的班级
cur.execute("SELECT DISTINCT h.class_id FROM homework h JOIN homework_submissions hs ON hs.homework_id=h.id WHERE hs.score IS NOT NULL")
classes = cur.fetchall()

total_updated = 0
for cls in classes:
    class_id = cls['class_id']

    # 使用 ROW_NUMBER 重新统计每个学生每个作业的最新一次分数
    cur.execute("""
        SELECT hs.student_id, hs.student_name,
               SUM(score) as total, COUNT(DISTINCT hs.homework_id) as cnt
        FROM (
            SELECT hs.homework_id, hs.student_id, hs.student_name, hs.score,
                   ROW_NUMBER() OVER (PARTITION BY hs.homework_id ORDER BY hs.submitted_at DESC) as rn
            FROM homework_submissions hs
            JOIN homework h2 ON h2.id = hs.homework_id
            WHERE h2.class_id = %s AND hs.score IS NOT NULL
        ) hs2
        JOIN homework h3 ON h3.id = hs2.homework_id
        WHERE hs2.rn = 1 AND h3.class_id = %s
        GROUP BY hs2.student_id, hs2.student_name
    """, (class_id, class_id))
    stats = cur.fetchall()

    # 清空该班级的现有排行数据
    cur.execute("DELETE FROM homework_score_ranking WHERE class_id=%s", (class_id,))

    # 重新插入
    for s in stats:
        cur.execute("""
            INSERT INTO homework_score_ranking (class_id, student_id, student_name, total_score, homework_count, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (class_id, s['student_id'], s['student_name'], float(s['total'] or 0), int(s['cnt'] or 0)))
        total_updated += 1

print(f'Rebuilt rankings for {len(classes)} classes, {total_updated} students updated')

# 验证药管班
cur.execute("""
    SELECT sr.student_id, sr.student_name, sr.total_score, sr.homework_count
    FROM homework_score_ranking sr
    WHERE sr.class_id = 'cls_1774917553355'
    ORDER BY sr.total_score DESC, sr.homework_count DESC
""")
yaoguan = cur.fetchall()
print('\n=== 药管班排行榜验证 ===')
for r in yaoguan:
    print('  %s: %.2f (%d HWs)' % (r['student_name'], r['total_score'], r['homework_count']))

conn.close()
print('\nDone!')
