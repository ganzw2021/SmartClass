from seed_lucky_herbs import database_config
import pymysql


def ensure_publish_group(cur):
    cur.execute("SHOW COLUMNS FROM homework LIKE 'publish_group'")
    if not cur.fetchone():
        cur.execute("""ALTER TABLE homework ADD COLUMN publish_group CHAR(32) NULL,
                       ADD UNIQUE KEY uk_homework_publish_class (publish_group,class_id)""")


if __name__=='__main__':
    db=pymysql.connect(**database_config())
    try:
        with db.cursor() as cur:
            ensure_publish_group(cur)
        db.commit()
        print('HOMEWORK_PUBLISH_GROUP_READY')
    finally:
        db.close()
