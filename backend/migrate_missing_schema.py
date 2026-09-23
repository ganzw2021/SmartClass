#!/usr/bin/env python3
"""Idempotent schema repair for the current SmartClass backend."""
import os
import pymysql
from seed_lucky_herbs import HERBS

# Keep the migration runnable from a clean virtualenv; the backend's .env is
# intentionally not required as an installed Python dependency.
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

DB = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'user': os.environ.get('DB_USER', 'smartclass'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'smartclass'),
    'charset': 'utf8mb4',
    'autocommit': True,
}


def columns(cur, table):
    cur.execute("""SELECT COLUMN_NAME FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s""", (table,))
    return {row[0] for row in cur.fetchall()}


def add_columns(cur, table, definitions):
    existing = columns(cur, table)
    for name, definition in definitions:
        if name not in existing:
            cur.execute(f"ALTER TABLE `{table}` ADD COLUMN `{name}` {definition}")
            print(f"added {table}.{name}")


conn = pymysql.connect(**DB)
try:
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS course_resources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_id VARCHAR(50) NOT NULL,
        course_name VARCHAR(100) NOT NULL DEFAULT '',
        term VARCHAR(50) NOT NULL DEFAULT '',
        teacher_id INT NOT NULL,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size INT NOT NULL DEFAULT 0,
        file_type VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_resource_course (course_id),
        INDEX idx_resource_teacher (teacher_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

    cur.execute("""CREATE TABLE IF NOT EXISTS student_notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        type VARCHAR(50) NOT NULL,
        title VARCHAR(200) NOT NULL,
        content TEXT,
        related_id INT DEFAULT NULL,
        related_type VARCHAR(50) DEFAULT NULL,
        is_read TINYINT(1) NOT NULL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_notification_student (student_id),
        INDEX idx_notification_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

    cur.execute("""CREATE TABLE IF NOT EXISTS student_login_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        login_date DATE NOT NULL,
        UNIQUE KEY uk_student_login_date (student_id, login_date),
        INDEX idx_login_date (login_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

    cur.execute("""CREATE TABLE IF NOT EXISTS herbs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        category VARCHAR(50) NOT NULL,
        efficacy TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_herb_name (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    # 新环境和旧环境均可重复执行；已有药材资料保持原样。
    herb_rows = [(name, category, efficacy)
                 for category, herbs in HERBS.items() for name, efficacy in herbs]
    cur.executemany("INSERT IGNORE INTO herbs (name,category,efficacy) VALUES (%s,%s,%s)", herb_rows)

    cur.execute("""CREATE TABLE IF NOT EXISTS homework_grading_scripts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        homework_id INT NOT NULL UNIQUE,
        script_path VARCHAR(512) NOT NULL,
        language VARCHAR(20) NOT NULL DEFAULT 'python',
        timeout_seconds INT NOT NULL DEFAULT 60,
        created_by INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_grading_homework (homework_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

    add_columns(cur, 'homework', [
        ('is_published', "TINYINT(1) NOT NULL DEFAULT 0"),
        ('auto_grade_enabled', "TINYINT(1) NOT NULL DEFAULT 0"),
        ('has_grading_script', "TINYINT(1) NOT NULL DEFAULT 0"),
    ])
    add_columns(cur, 'homework_submissions', [
        ('grading_status', "ENUM('none','pending','grading','done','failed') NOT NULL DEFAULT 'none'"),
        ('auto_score', 'FLOAT DEFAULT NULL'),
        ('auto_grade_message', 'TEXT DEFAULT NULL'),
        ('auto_grade_details', 'JSON DEFAULT NULL'),
    ])
    add_columns(cur, 'classes', [
        ('class_type', "VARCHAR(20) NOT NULL DEFAULT 'administrative'"),
    ])
    cur.execute("""CREATE TABLE IF NOT EXISTS class_students (
        class_id VARCHAR(50) NOT NULL,
        student_id INT NOT NULL,
        sort_order INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (class_id, student_id),
        INDEX idx_class_students_student (student_id),
        CONSTRAINT fk_class_students_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
        CONSTRAINT fk_class_students_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    # 将历史行政班归属补为成员关系；重复执行安全。
    cur.execute("""INSERT IGNORE INTO class_students (class_id, student_id, sort_order)
                   SELECT class_id, id, sort_order FROM students""")
    print('schema migration complete')
finally:
    conn.close()
