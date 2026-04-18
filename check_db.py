import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Root@123456', database='smartclass', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
cur.execute('SHOW TABLES')
tables = [t['Tables_in_smartclass'] for t in cur.fetchall()]
print('Tables:', tables)

# Check students table
cur.execute('DESC students')
print('\nstudents table:')
for col in cur.fetchall():
    print(f"  {col['Field']}: {col['Type']}")

conn.close()
