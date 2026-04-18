# 数据库迁移脚本：为 attendance_sessions 表添加地理围栏字段
import pymysql
import os

# 数据库配置（与 app.py 保持一致）
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Root@123456'),
    'database': os.environ.get('DB_NAME', 'smartclass'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def migrate():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cur.execute("SHOW COLUMNS FROM attendance_sessions LIKE 'classroom_lat'")
        result = cur.fetchone()
        
        if not result:
            print('字段不存在，正在添加...')
            cur.execute('ALTER TABLE attendance_sessions ADD COLUMN classroom_lat DECIMAL(10, 8) DEFAULT NULL')
            cur.execute('ALTER TABLE attendance_sessions ADD COLUMN classroom_lng DECIMAL(11, 8) DEFAULT NULL')
            cur.execute('ALTER TABLE attendance_sessions ADD COLUMN classroom_radius INT DEFAULT 10')
            conn.commit()
            print('字段添加成功！')
        else:
            print('字段已存在，无需添加')
    except Exception as e:
        print(f'错误: {e}')
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
