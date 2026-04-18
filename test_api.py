import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# 1. 学生登录
login_data = {
    'username': '202401',
    'password': '123456',
    'type': 'student'
}
resp = requests.post(f'{BASE_URL}/auth/login', json=login_data)
print('登录响应:', resp.status_code)
print(resp.text)

if resp.status_code == 200:
    data = resp.json()
    if data.get('success'):
        token = data['data']['token']
        print(f'\n获取到 token: {token[:20]}...')

        # 2. 获取排行榜
        headers = {'Authorization': f'Bearer {token}'}
        resp2 = requests.get(f'{BASE_URL}/student/homework/ranking', headers=headers)
        print('\n排行榜响应:', resp2.status_code)
        print(resp2.text)
