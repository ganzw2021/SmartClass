#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试更新班级API"""

import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'smartclass',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': False  # 禁用自动提交
}

def test_update():
    class_id = 'cls_1774406783623'
    name = '2025级中药材生产与加工2班'
    description = ''
    students = [
        {'name': '张三', 'student_number': '202401'},
        {'name': '李四', 'student_number': '202402'}
    ]
    
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            print("1. 更新班级信息...")
            cur.execute("UPDATE classes SET name=%s, description=%s WHERE id=%s", (name, description, class_id))
            print(f"   影响行数: {cur.rowcount}")
            
            print("2. 删除现有学生...")
            cur.execute("DELETE FROM students WHERE class_id=%s", (class_id,))
            print(f"   删除行数: {cur.rowcount}")
            
            print("3. 插入新学生...")
            for i, stu in enumerate(students):
                stu_name = stu.get('name', '').strip()
                stu_number = stu.get('student_number', '').strip() or None
                print(f"   插入: name={stu_name}, number={stu_number}")
                cur.execute(
                    "INSERT INTO students (name, student_number, class_id, sort_order) VALUES (%s, %s, %s, %s)",
                    (stu_name, stu_number, class_id, i)
                )
                print(f"   插入成功, ID: {cur.lastrowid}")
        
        print("4. 提交事务...")
        conn.commit()
        print("测试成功！")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print("已回滚")
    finally:
        conn.close()

if __name__ == '__main__':
    test_update()
