import pymysql, time

# 测试不同连接方式耗时
configs = [
    ('localhost (socket)', {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'Root@123456', 'database': 'smartclass', 'charset': 'utf8mb4'}),
    ('127.0.0.1 (TCP)',    {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'Root@123456', 'database': 'smartclass', 'charset': 'utf8mb4'}),
]

for label, cfg in configs:
    cfg['cursorclass'] = pymysql.cursors.DictCursor
    t0 = time.time()
    conn = pymysql.connect(**cfg)
    cur = conn.cursor()
    cur.execute("SELECT 1")
    cur.fetchone()
    conn.close()
    t = (time.time() - t0) * 1000
    print(f"{label}: {t:.0f}ms")
