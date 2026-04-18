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

# 1. 新建 grading_scripts 表
try:
    cur.execute("""
        CREATE TABLE homework_grading_scripts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            homework_id INT NOT NULL UNIQUE,
            script_path VARCHAR(512) NOT NULL,
            language VARCHAR(20) NOT NULL DEFAULT 'python',
            timeout_seconds INT NOT NULL DEFAULT 60,
            created_by INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (homework_id) REFERENCES homework(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES teachers(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print('✅ homework_grading_scripts 表创建成功')
except Exception as e:
    print(f'homework_grading_scripts: {e}')

# 2. homework 表加字段
for col_sql, name in [
    ("ALTER TABLE homework ADD COLUMN has_grading_script BOOLEAN DEFAULT FALSE AFTER total_score", 'has_grading_script'),
    ("ALTER TABLE homework ADD COLUMN auto_grade_enabled BOOLEAN DEFAULT FALSE AFTER has_grading_script", 'auto_grade_enabled'),
]:
    try:
        cur.execute(col_sql)
        conn.commit()
        print(f'✅ homework.{name} 添加成功')
    except Exception as e:
        print(f'homework.{name}: {e}')

# 3. homework_submissions 表加字段
for col_sql, name in [
    ("ALTER TABLE homework_submissions ADD COLUMN grading_status ENUM('none','pending','grading','done','failed') DEFAULT 'none' AFTER attachment_url", 'grading_status'),
    ("ALTER TABLE homework_submissions ADD COLUMN auto_score FLOAT DEFAULT NULL AFTER grading_status", 'auto_score'),
    ("ALTER TABLE homework_submissions ADD COLUMN auto_grade_message TEXT DEFAULT NULL AFTER auto_score", 'auto_grade_message'),
    ("ALTER TABLE homework_submissions ADD COLUMN auto_grade_details JSON DEFAULT NULL AFTER auto_grade_message", 'auto_grade_details'),
    ("ALTER TABLE homework_submissions ADD COLUMN graded_at DATETIME DEFAULT NULL AFTER auto_grade_details", 'graded_at'),
]:
    try:
        cur.execute(col_sql)
        conn.commit()
        print(f'✅ homework_submissions.{name} 添加成功')
    except Exception as e:
        print(f'homework_submissions.{name}: {e}')

# 验证
print('\n--- homework 表结构 ---')
cur.execute('DESCRIBE homework')
for r in cur.fetchall():
    print(r[0], r[1])

print('\n--- homework_submissions 表结构 ---')
cur.execute('DESCRIBE homework_submissions')
for r in cur.fetchall():
    print(r[0], r[1])

print('\n--- homework_grading_scripts 表 ---')
cur.execute('SHOW TABLES LIKE "homework_grading_scripts"')
print(cur.fetchall())

conn.close()
