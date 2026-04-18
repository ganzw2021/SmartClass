import requests

# 登录
r = requests.post('http://localhost:5000/api/auth/login', json={'type':'teacher','username':'18979576263','password':'081097'})
print('login:', r.status_code)
data = r.json()
token = data['data']['token']

# 获取课程
r = requests.get('http://localhost:5000/api/courses', headers={'Authorization': 'Bearer ' + token})
print('\n=== 课程 ===')
courses = r.json()
print('count:', len(courses.get('data', [])))
for c in courses.get('data', []):
    print(f"  id: {c['id']}, name: {c['name']}, term: {c.get('term')}")
    print(f"  classes: {c.get('classes', [])}")

# 获取第一个班级学生
if courses.get('data'):
    first_course = courses['data'][0]
    if first_course.get('classes'):
        class_id = first_course['classes'][0]['id']
        print(f'\n=== 班级 {class_id} 学生 ===')
        r = requests.get(f'http://localhost:5000/api/classes/{class_id}/students', 
                        headers={'Authorization': 'Bearer ' + token})
        print('status:', r.status_code)
        print('data:', r.text[:200] if r.text else 'empty')
