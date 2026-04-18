#!/usr/bin/env python3
"""测试API返回的数据 - 先获取班级列表"""
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

def get_courses(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/api/courses", headers=headers)
    return res.json()

def test_get_students(token, class_id):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/api/classes/{class_id}/students", headers=headers)
    data = res.json()
    
    print("=" * 60)
    print(f"班级ID: {class_id}")
    print(f"请求状态: {res.status_code}")
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
    
    return data

if __name__ == "__main__":
    token = login()
    if token:
        print(f"登录成功")
        # 先获取课程列表
        courses = get_courses(token)
        print(f"\n课程列表:")
        print(json.dumps(courses, ensure_ascii=False, indent=2)[:1500])
        
        # 如果有课程，获取第一个课程的班级
        if courses.get("data") and len(courses["data"]) > 0:
            course = courses["data"][0]
            print(f"\n课程: {course.get('name')}")
            if course.get("classes"):
                for cls in course["classes"]:
                    class_id = cls.get("id")
                    print(f"\n测试班级: {cls.get('name')} (ID: {class_id})")
                    test_get_students(token, class_id)
    else:
        print("登录失败")
