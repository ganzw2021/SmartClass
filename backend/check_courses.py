import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Root@123456', database='smartclass')
cur = conn.cursor()

# 查看所有课程
cur.execute('SELECT id, name, teacher_id FROM courses')
print('=== 所有课程 ===')
for row in cur.fetchall():
    print(f'ID:{row[0]}, 名称:{row[1]}, 教师ID:{row[2]}')

# 查看课程关联的班级和学生
cur.execute('''
SELECT c.id, c.name, COUNT(s.id) as student_count
FROM courses co
JOIN course_classes cc ON cc.course_id = co.id
JOIN classes c ON c.id = cc.class_id
LEFT JOIN students s ON s.class_id = c.id
GROUP BY c.id, c.name
''')
print('\n=== 课程关联班级及学生数 ===')
for row in cur.fetchall():
    print(f'班级ID:{row[0]}, 名称:{row[1]}, 学生数:{row[2]}')

conn.close()
