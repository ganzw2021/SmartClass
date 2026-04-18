#!/usr/bin/env python3
"""测试API返回的数据"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# 先登录获取token
def login():
    # 教师登录
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "teacher1",
        "password": "123456"
    })
    data = res.json()
    if data.get("success"):
        return data["data"]["token"]
    return None

def test_get_students(token, class_id):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/api/classes/{class_id}/students", headers=headers)
    data = res.json()
    
    print("=" * 60)
    print(f"班级ID: {class_id}")
    print(f"请求状态: {res.status_code}")
    print(f"返回数据条数: {len(data.get('data', []))}")
    
    if data.get("data") and len(data["data"]) > 0:
        student = data["data"][0]
        print(f"\n第一个学生数据:")
        print(f"  ID: {student.get('id')}")
        print(f"  姓名: {student.get('name')}")
        print(f"  学号: {student.get('student_number')}")
        print(f"  是否有avatar字段: {'avatar' in student}")
        print(f"  avatar类型: {type(student.get('avatar'))}")
        print(f"  avatar长度: {len(str(student.get('avatar', '')))}")
        print(f"  avatar前100字符: {str(student.get('avatar', ''))[:100]}")
        print(f"  是否有bio字段: {'bio' in student}")
        print(f"  bio值: {student.get('bio')}")
        
        # 检查所有学生的avatar情况
        print(f"\n所有学生avatar统计:")
        for s in data["data"]:
            has_avatar = s.get('avatar') and len(str(s.get('avatar', ''))) > 100
            print(f"  {s.get('name')} (学号:{s.get('student_number')}): avatar={'有' if has_avatar else '无'}")
    
    return data

if __name__ == "__main__":
    token = login()
    if token:
        print(f"登录成功，token: {token[:30]}...")
        # 测试班级ID，你需要根据实际班级ID修改
        test_get_students(token, "cls_20250325104053")
    else:
        print("登录失败")
