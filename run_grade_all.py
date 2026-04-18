import pymysql, os, threading, sys, time
from dotenv import load_dotenv
load_dotenv('backend/.env')

conn = pymysql.connect(
    host=os.getenv('DB_HOST','localhost'),
    port=int(os.getenv('DB_PORT',3306)),
    user=os.getenv('DB_USER','root'),
    password=os.getenv('DB_PASSWORD',''),
    database=os.getenv('DB_NAME','smartclass'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()
sql = "SELECT hs.id FROM homework_submissions hs JOIN submission_attachments sa ON sa.submission_id=hs.id WHERE hs.homework_id=6 AND hs.grading_status IN ('none','pending','failed')"
cur.execute(sql)
rows = cur.fetchall()
sub_ids = [r['id'] for r in rows]
cur.close()
conn.close()
print('待评分总数:', len(sub_ids))

sys.path.insert(0, r'C:\smartclass\backend')
import app as flask_app
time.sleep(2)

for sid in sub_ids:
    t = threading.Thread(target=flask_app._trigger_auto_grading, args=(sid,), daemon=True)
    t.start()

print('已全部触发，等待评分完成...')
time.sleep(30)

conn2 = pymysql.connect(
    host=os.getenv('DB_HOST','localhost'),
    port=int(os.getenv('DB_PORT',3306)),
    user=os.getenv('DB_USER','root'),
    password=os.getenv('DB_PASSWORD',''),
    database=os.getenv('DB_NAME','smartclass'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cur2 = conn2.cursor()
cur2.execute("SELECT id, student_name, grading_status, auto_score, LEFT(auto_grade_message,80) as msg FROM homework_submissions WHERE homework_id=6 ORDER BY id")
all_rows = cur2.fetchall()
done = [r for r in all_rows if r['grading_status']=='done']
failed = [r for r in all_rows if r['grading_status']=='failed']
pending = [r for r in all_rows if r['grading_status'] in ('grading','pending','none')]
print()
print('=== 统计 ===')
print('总提交:', len(all_rows), '  已评分:', len(done), '  失败:', len(failed), '  待处理:', len(pending))
print()
print('=== 已评分结果 ===')
for r in done:
    print(r['student_name'], r['auto_score'], '分  |', r['msg'])
if failed:
    print()
    print('=== 失败 ===')
    for r in failed:
        print(r['student_name'], '|', r['grading_status'], '|', r['msg'])
cur2.close()
conn2.close()
