import pymysql
from dbutils.pooled_db import PooledDB

DB_CONFIG = {'host':'127.0.0.1','port':3306,'user':'root','password':'Root@123456','database':'smartclass','charset':'utf8mb4'}
pool = PooledDB(creator=pymysql, maxconnections=8, mincached=2, **DB_CONFIG)
conn = pool.connection()
conn.autocommit(True)
print('Pool connection OK')
cur = conn.cursor()
cur.execute('SELECT 1')
print(cur.fetchone())
conn.close()
print('Closed')
