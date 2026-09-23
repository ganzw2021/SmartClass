#!/usr/bin/env python3
"""Idempotently seed the classroom herb catalog without changing existing entries."""
import json
import os
from pathlib import Path

CATALOG_PATH = Path(__file__).with_name('lucky_herbs_catalog.json')


def catalog_rows():
    catalog = json.loads(CATALOG_PATH.read_text(encoding='utf-8'))
    rows = [(item['name'], item['category'], item['efficacy']) for item in catalog]
    names = [name for name, _, _ in rows]
    if len(rows) != 500 or len(set(names)) != 500 or any(not all(row) for row in rows):
        raise ValueError('幸运签药材目录必须包含 500 味完整且不重复的药材')
    return rows


def database_config():
    env_file = Path(__file__).with_name('.env')
    if env_file.exists():
        for raw in env_file.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return {
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': int(os.environ.get('DB_PORT', '3306')),
        'user': os.environ.get('DB_USER', 'smartclass'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'smartclass'),
        'charset': 'utf8mb4',
        'autocommit': False,
    }


def main():
    import pymysql

    rows = catalog_rows()
    db = pymysql.connect(**database_config())
    try:
        with db.cursor() as cur:
            cur.executemany('INSERT IGNORE INTO herbs (name,category,efficacy) VALUES (%s,%s,%s)', rows)
            inserted = cur.rowcount
            cur.execute('SELECT COUNT(*) FROM herbs')
            total = cur.fetchone()[0]
        db.commit()
        print(f'Lucky herbs ready: {total} total, {inserted} new')
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
