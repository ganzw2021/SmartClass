import requests
from io import BytesIO

r = requests.post('http://127.0.0.1:5000/api/auth/login',
    json={'type':'teacher','username':'18979576263','password':'081097'}, timeout=8)
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

py_code = b'import json\ndef grade(fp):\n    r={"score":10,"max_score":100,"passed":True,"message":"test","details":{}}\n    print(json.dumps(r))\nif __name__=="__main__": grade("x")'

files_data = [
    ('attachments', ('test1.txt', BytesIO(b'hello'), 'text/plain')),
    ('attachments', ('test2.txt', BytesIO(b'world'), 'text/plain')),
    ('script', ('grader_test.py', py_code, 'text/x-python')),
]

r2 = requests.post('http://127.0.0.1:5000/api/homework',
    headers=h, files=files_data,
    data={
        'course_id': '2', 'class_id': 'cls_1774589571125',
        'title': '自动化测试作业_edit_check',
        'content': 'test content',
        'deadline': '2026-04-30T23:59',
        'total_score': '100',
        'enable_auto': 'true'
    }, timeout=10)
print('Create status:', r2.status_code)
raw = r2.json()
print('Create code:', raw.get('code'), raw.get('message'))
hw_id = raw['data']['id']
print('New HW ID:', hw_id)

# 查作业列表，看新建的作业附件和脚本情况
r3 = requests.get('http://127.0.0.1:5000/api/homework', headers=h, timeout=8)
hws = r3.json()['data']
new_hw = next((hw for hw in hws if hw['id'] == hw_id), None)
if new_hw:
    print('\n=== Newly created HW in list ===')
    print('title:', new_hw['title'])
    print('attachments count:', len(new_hw.get('attachments', [])))
    for a in new_hw.get('attachments', []):
        print('  -', a.get('filename'), a.get('size'))
    print('has_grading_script:', new_hw.get('has_grading_script'))
    print('auto_grade_enabled:', new_hw.get('auto_grade_enabled'))
    print('grading_script:', new_hw.get('grading_script'))
else:
    print('HW not found in list!')
    # 列出所有作业的 id 和 title
    for hw in hws:
        print(' - id:', hw['id'], 'title:', hw['title'])
