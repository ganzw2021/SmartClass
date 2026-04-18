#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试更新班级功能"""

import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'smartclass',
    'charset': 'utf8mb4'
}

def test_update():
    class_id = 'cls_1774406783623'
    students = [
        {'name': '张三', 'student_number': '2024001'},
        {'name': '李四', 'student_number': '2024002'}
    ]
    
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # 先删除该班级现有学生
            print("删除现有学生...")
            cur.execute("DELETE FROM students WHERE class_id=%s", (class_id,))
            print(f"  删除了 {cur.rowcount} 条记录")
            
            # 插入新学生
            for i, stu in enumerate(students):
                stu_name = stu.get('name', '').strip()
                stu_number = stu.get('student_number', '').strip() or None
                print(f"插入学生: name={stu_name}, number={stu_number}, class_id={class_id}, order={i}")
                try:
                    cur.execute(
                        "INSERT INTO students (name, student_number, class_id, sort_order) VALUES (%s, %s, %s, %s)",
                        (stu_name, stu_number, class_id, i)
                    )
                    print(f"  成功插入，ID: {cur.lastrowid}")
                except Exception as e:
                    print(f"  插入失败: {e}")
                    conn.rollback()
                    return
        
        conn.commit()
        print("测试成功！")
    except Exception as e:
        conn.rollback()
        print(f"测试失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    test_update()
