import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='Root@123456',
    database='smartclass',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # 检查排行榜表是否有数据
        cursor.execute('SELECT COUNT(*) as cnt FROM homework_score_ranking')
        result = cursor.fetchone()
        print(f'排行榜记录数: {result["cnt"]}')

        # 查看几条记录
        cursor.execute('SELECT * FROM homework_score_ranking LIMIT 5')
        rows = cursor.fetchall()
        print('\n前5条记录:')
        for row in rows:
            print(row)

        # 检查学生表
        cursor.execute('SELECT * FROM students LIMIT 5')
        rows = cursor.fetchall()
        print('\n学生表:')
        for row in rows:
            print(f"  ID: {row['id']}, 姓名: {row['name']}, 班级: {row['class_id']}")

        # 检查学生账号
        cursor.execute('SELECT * FROM student_accounts LIMIT 5')
        rows = cursor.fetchall()
        print('\n学生账号:')
        for row in rows:
            print(f"  ID: {row['id']}, 用户名: {row['username']}, 学生ID: {row.get('student_id')}")

        # 查找甘祖文的账号
        cursor.execute("SELECT * FROM student_accounts WHERE student_id = 5624")
        row = cursor.fetchone()
        print(f'\n甘祖文的账号: {row}')

finally:
    conn.close()
