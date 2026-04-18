"""数据库迁移脚本 - 添加通知功能"""
import pymysql

conn = pymysql.connect(
    host='127.0.0.1', port=3306, user='root',
    password='Root@123456', database='smartclass', charset='utf8mb4'
)
cur = conn.cursor()

# 1. 添加 is_published 字段
try:
    cur.execute('''ALTER TABLE homework ADD COLUMN is_published TINYINT(1) DEFAULT 0 COMMENT '是否发布' AFTER total_score''')
    print('Added is_published column')
except Exception as e:
    if 'Duplicate' in str(e) or 'syntax' in str(e).lower():
        print('is_published column already exists or error')
    else:
        print(f'is_published: {e}')

# 2. 添加 auto_grade_enabled 字段
try:
    cur.execute('''ALTER TABLE homework ADD COLUMN auto_grade_enabled TINYINT(1) DEFAULT 0 COMMENT '是否启用自动评分' AFTER is_published''')
    print('Added auto_grade_enabled column')
except Exception as e:
    if 'Duplicate' in str(e) or 'syntax' in str(e).lower():
        print('auto_grade_enabled column already exists')
    else:
        print(f'auto_grade_enabled: {e}')

# 3. 添加 has_grading_script 字段
try:
    cur.execute('''ALTER TABLE homework ADD COLUMN has_grading_script TINYINT(1) DEFAULT 0 COMMENT '是否有评分脚本' AFTER auto_grade_enabled''')
    print('Added has_grading_script column')
except Exception as e:
    if 'Duplicate' in str(e) or 'syntax' in str(e).lower():
        print('has_grading_script column already exists')
    else:
        print(f'has_grading_script: {e}')

# 4. 创建通知表
try:
    cur.execute('''
    CREATE TABLE IF NOT EXISTS student_notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL COMMENT '学生ID',
        type VARCHAR(50) NOT NULL COMMENT '通知类型',
        title VARCHAR(200) NOT NULL COMMENT '通知标题',
        content TEXT COMMENT '通知内容',
        related_id INT DEFAULT NULL COMMENT '关联ID',
        related_type VARCHAR(50) DEFAULT NULL COMMENT '关联类型',
        is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_student_id (student_id),
        INDEX idx_type (type),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB
    ''')
    print('Created student_notifications table')
except Exception as e:
    print(f'notifications table: {e}')

# 5. 创建评分脚本表
try:
    cur.execute('''
    CREATE TABLE IF NOT EXISTS homework_grading_scripts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        homework_id INT NOT NULL COMMENT '作业ID',
        script_name VARCHAR(255) NOT NULL COMMENT '脚本文件名',
        script_path VARCHAR(500) NOT NULL COMMENT '脚本存储路径',
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_homework (homework_id),
        FOREIGN KEY (homework_id) REFERENCES homework(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    ''')
    print('Created homework_grading_scripts table')
except Exception as e:
    print(f'grading_scripts table: {e}')

conn.commit()
cur.close()
conn.close()
print('Migration completed!')
