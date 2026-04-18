# E2E: 学生提交作业 → 自动评分触发 → 分数入库
import requests, time, json

BASE = "http://127.0.0.1:5000"

# 1. 教师登录，找到一个有脚本的作业
r = requests.post(f"{BASE}/api/auth/login", json={"type":"teacher","username":"18979576263","password":"081097"})
token = r.json()["data"]["token"]
h = {"Authorization": f"Bearer {token}"}

r2 = requests.get(f"{BASE}/api/homework?course_id=", headers=h)
hws = r2.json()["data"]
print("=== 作业列表 ===")
for hw in hws:
    print(f"  [{hw['id']}] {hw['title']} | has_script={hw.get('has_grading_script')} auto={hw.get('auto_grade_enabled')} att={len(hw.get('attachments',[]))}")

# 找有脚本+开启自动评分+有附件的作业
target = next((hw for hw in hws if hw.get('has_grading_script') and hw.get('auto_grade_enabled') and hw.get('attachments')), None)
if not target:
    print("❌ 没有找到有脚本+开启自动评分+有附件的作业")
    exit(1)
print(f"\n✅ 选用作业 [{target['id']}] {target['title']}")

# 2. 学生登录（选一个该作业班级内的学生）
r3 = requests.post(f"{BASE}/api/auth/login", json={"type":"student","username":"2023001","password":"123456"})
stu_token = r3.json()["data"]["token"]
stu_h = {"Authorization": f"Bearer {stu_token}"}
print(f"✅ 学生登录: {r3.json()['data'].get('name')}")

# 3. 提交一个测试文件
test_content = "test submission content"
files = {"files": ("test_submission.xlsx", b"fake xlsx content", "application/octet-stream")}
r4 = requests.post(f"{BASE}/api/student/homework/{target['id']}/submit", headers=stu_h, files=files, data={"content": test_content})
print(f"\n提交接口: {r4.status_code} {r4.json()}")

# 4. 立即轮询评分状态
sub_id = None
for i in range(15):
    time.sleep(2)
    r5 = requests.get(f"{BASE}/api/student/homework?course_id=", headers=stu_h)
    for hw in r5.json()["data"]:
        if hw["id"] == target["id"]:
            sub = hw.get("submission", {})
            print(f"  [{i*2}s] grading_status={sub.get('grading_status')} score={sub.get('score')} auto_score={sub.get('auto_score')}")
            if sub.get("grading_status") == "done":
                sub_id = sub.get("id")
                print(f"\n✅ 自动评分完成！score={sub.get('score')} auto_score={sub.get('auto_score')}")
                print(f"   auto_grade_message: {sub.get('auto_grade_message')}")
                details = sub.get("auto_grade_details")
                if details:
                    print(f"   auto_grade_details: {json.dumps(details, ensure_ascii=False)[:200]}")
                break
    if sub_id:
        break
else:
    print("\n⚠️ 轮询超时，评分未在30s内完成")
