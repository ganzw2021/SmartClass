import requests

r = requests.post('http://127.0.0.1:5000/api/auth/login',
    json={'type':'teacher','username':'18979576263','password':'081097'}, timeout=8)
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}
r2 = requests.get('http://127.0.0.1:5000/api/homework', headers=h, timeout=8)
hws = r2.json()['data']
print('=== API list 作业字段 ===')
hw = hws[0]
for k, v in sorted(hw.items()):
    print(f'  {k}: {repr(v)[:80]}')
