import requests

r = requests.post('http://127.0.0.1:5000/api/auth/login',
    json={'type':'teacher','username':'18979576263','password':'081097'}, timeout=8)
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 查看所有作业，找最新的那个
r2 = requests.get('http://127.0.0.1:5000/api/homework', headers=h, timeout=8)
hws = r2.json()['data']
print('=== 所有作业 ===')
for hw in hws:
    print(f"ID={hw['id']} title={hw['title']} auto={hw.get('auto_grade_enabled')} script={hw.get('has_grading_script')} attachments={len(hw.get('attachments',[]))}")

# 取最新的一个有脚本的作业
hw_with_script = [hw for hw in hws if hw.get('has_grading_script')]
if hw_with_script:
    hid = hw_with_script[0]['id']
    print(f'\n=== 详情: ID={hid} ===')
    r3 = requests.get(f'http://127.0.0.1:5000/api/homework/{hid}', headers=h, timeout=8)
    d = r3.json()
    if d.get('success'):
        hw = d['data']
        print('title:', hw.get('title'))
        print('auto_grade_enabled:', hw.get('auto_grade_enabled'))
        print('has_grading_script:', hw.get('has_grading_script'))
        print('script_info:', hw.get('grading_script_info'))
        print('attachments count:', len(hw.get('attachments', [])))
        for att in hw.get('attachments', []):
            print(f'  - {att.get("original_name")} ({att.get("file_size")} bytes)')
