import pymysql, os
from dotenv import load_dotenv
load_dotenv('C:/smartclass/backend/.env')
conn = pymysql.connect(
    host=os.environ.get('DB_HOST', 'localhost'),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', ''),
    db=os.environ.get('DB_NAME', 'smartclass'),
    charset='utf8mb4'
)
cur = conn.cursor()

# 添加 canvas_fp 字段
try:
    cur.execute("""
        ALTER TABLE attendance_records
        ADD COLUMN canvas_fp VARCHAR(128) DEFAULT NULL AFTER device_fingerprint
    """)
    conn.commit()
    print('canvas_fp column added successfully')
except Exception as e:
    print(f'Add column result: {e}')

# 验证字段
cur.execute("SHOW COLUMNS FROM attendance_records")
cols = {r[0]: r for r in cur.fetchall()}
for col in ['device_fingerprint', 'canvas_fp']:
    if col in cols:
        print(f'{col}: {cols[col]}')
    else:
        print(f'{col}: NOT FOUND')

conn.close()
