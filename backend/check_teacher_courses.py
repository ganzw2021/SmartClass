import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Root@123456', database='smartclass')
cur = conn.cursor()

# 甘祖文的课程
cur.execute("SELECT id, name, term FROM courses WHERE teacher_id=4")
print('=== 甘祖文(teacher_id=4)的课程 ===')
for row in cur.fetchall():
    print(f'课程ID:{row[0]}, 名称:{row[1]}, 学期:{row[2]}')

# 课程关联的班级
cur.execute('''
SELECT co.id, co.name, c.id as class_id, c.name as class_name, COUNT(s.id) as student_count
FROM courses co
JOIN course_classes cc ON cc.course_id = co.id
JOIN classes c ON c.id = cc.class_id
LEFT JOIN students s ON s.class_id = c.id
WHERE co.teacher_id = 4
GROUP BY co.id, co.name, c.id, c.name
''')
print('\n=== 课程关联的班级及学生 ===')
for row in cur.fetchall():
    print(f'课程:{row[1]}, 班级:{row[3]}, 学生数:{row[4]}')

conn.close()
