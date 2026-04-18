#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为学生表添加学号字段
"""

import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'smartclass',
    'charset': 'utf8mb4'
}

def migrate():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # 检查 student_number 字段是否已存在
            cur.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'students' AND COLUMN_NAME = 'student_number'
            """)
            if cur.fetchone():
                print("[OK] student_number 字段已存在，无需迁移")
                return
            
            # 添加 student_number 字段
            cur.execute("""
                ALTER TABLE students 
                ADD COLUMN student_number VARCHAR(50) DEFAULT NULL COMMENT '学号' AFTER name,
                ADD INDEX idx_student_number (student_number)
            """)
            print("[OK] 已添加 student_number 字段")
            
            conn.commit()
            print("[OK] 迁移完成")
            
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
