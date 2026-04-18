#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 homework 表添加 class_id 字段
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
            # 检查 class_id 字段是否已存在
            cur.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'homework' AND COLUMN_NAME = 'class_id'
            """)
            if cur.fetchone():
                print("[OK] class_id 字段已存在，无需迁移")
                return
            
            # 添加 class_id 字段
            cur.execute("""
                ALTER TABLE homework 
                ADD COLUMN class_id VARCHAR(50) NOT NULL DEFAULT '' COMMENT '班级ID' AFTER course_id,
                ADD INDEX idx_class (class_id)
            """)
            print("[OK] 已添加 class_id 字段")
            
            # 添加外键约束（可选，如果数据不干净可能会失败）
            try:
                cur.execute("""
                    ALTER TABLE homework 
                    ADD CONSTRAINT fk_homework_class 
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
                """)
                print("[OK] 已添加外键约束")
            except Exception as e:
                print(f"[WARN] 外键约束添加失败（可能已有脏数据）: {e}")
            
            conn.commit()
            print("[OK] 迁移完成")
            
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
