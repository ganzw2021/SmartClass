#!/usr/bin/env python3
"""Idempotently add a curated classroom herb collection without changing existing entries."""
import os
from pathlib import Path

import pymysql


# Short textbook-style descriptions for classroom learning. No dosage or treatment advice.
HERBS = {
    '补气药': [
        ('人参', '大补元气，补脾益肺，生津养血，安神益智'),
        ('党参', '健脾益肺，养血生津'),
        ('太子参', '益气健脾，生津润肺'),
        ('黄芪', '补气升阳，固表止汗，利水消肿'),
        ('白术', '健脾益气，燥湿利水，止汗'),
        ('山药', '补脾养胃，生津益肺，补肾涩精'),
        ('甘草', '补脾益气，清热解毒，缓急止痛，调和诸药'),
        ('大枣', '补中益气，养血安神'),
        ('西洋参', '补气养阴，清热生津'),
        ('黄精', '补气养阴，健脾润肺，益肾'),
    ],
    '补血药': [
        ('当归', '补血活血，调经止痛，润肠通便'),
        ('熟地黄', '补血滋阴，益精填髓'),
        ('白芍', '养血调经，柔肝止痛，敛阴止汗'),
        ('阿胶', '补血止血，滋阴润燥'),
        ('龙眼肉', '补益心脾，养血安神'),
        ('鸡血藤', '活血补血，调经止痛，舒筋活络'),
    ],
    '补阴药': [
        ('枸杞子', '滋补肝肾，益精明目'),
        ('麦冬', '养阴润肺，益胃生津，清心除烦'),
        ('玉竹', '养阴润燥，生津止渴'),
        ('石斛', '益胃生津，滋阴清热'),
        ('百合', '养阴润肺，清心安神'),
        ('女贞子', '滋补肝肾，乌须明目'),
        ('桑椹', '滋阴补血，生津润燥'),
    ],
    '清热药': [
        ('金银花', '清热解毒，疏散风热'),
        ('连翘', '清热解毒，消肿散结，疏散风热'),
        ('蒲公英', '清热解毒，消肿散结，利尿通淋'),
        ('板蓝根', '清热解毒，凉血利咽'),
        ('鱼腥草', '清热解毒，消痈排脓，利尿通淋'),
        ('知母', '清热泻火，滋阴润燥'),
        ('栀子', '泻火除烦，清热利湿，凉血解毒'),
        ('决明子', '清热明目，润肠通便'),
        ('黄芩', '清热燥湿，泻火解毒，止血，安胎'),
        ('黄连', '清热燥湿，泻火解毒'),
        ('菊花', '散风清热，平肝明目，清热解毒'),
    ],
    '解表药': [
        ('薄荷', '疏散风热，清利头目，利咽，透疹'),
        ('桑叶', '疏散风热，清肺润燥，清肝明目'),
        ('葛根', '解肌退热，生津止渴，升阳止泻'),
        ('防风', '祛风解表，胜湿止痛，止痉'),
        ('荆芥', '解表散风，透疹，消疮'),
        ('紫苏叶', '解表散寒，行气和胃'),
        ('桂枝', '发汗解肌，温通经脉，助阳化气'),
        ('生姜', '解表散寒，温中止呕，温肺止咳'),
    ],
    '化痰止咳平喘药': [
        ('桔梗', '宣肺，利咽，祛痰，排脓'),
        ('川贝母', '清热润肺，化痰止咳，散结消痈'),
        ('浙贝母', '清热化痰止咳，解毒散结消痈'),
        ('苦杏仁', '降气止咳平喘，润肠通便'),
        ('紫菀', '润肺下气，消痰止咳'),
        ('款冬花', '润肺下气，止咳化痰'),
    ],
    '理气药': [
        ('陈皮', '理气健脾，燥湿化痰'),
        ('枳实', '破气消积，化痰散痞'),
        ('香附', '疏肝解郁，理气宽中，调经止痛'),
        ('木香', '行气止痛，健脾消食'),
        ('佛手', '疏肝理气，和胃止痛，燥湿化痰'),
        ('玫瑰花', '行气解郁，和血，止痛'),
    ],
    '活血化瘀药': [
        ('丹参', '活血祛瘀，通经止痛，清心除烦'),
        ('川芎', '活血行气，祛风止痛'),
        ('红花', '活血通经，散瘀止痛'),
        ('桃仁', '活血祛瘀，润肠通便，止咳平喘'),
        ('益母草', '活血调经，利尿消肿，清热解毒'),
        ('牛膝', '逐瘀通经，补肝肾，强筋骨，利尿通淋'),
    ],
    '利水渗湿药': [
        ('茯苓', '利水渗湿，健脾宁心'),
        ('薏苡仁', '利水渗湿，健脾止泻，除痹，排脓'),
        ('泽泻', '利水渗湿，泄热'),
        ('车前子', '清热利尿通淋，渗湿止泻，明目，祛痰'),
        ('玉米须', '利水消肿，利湿退黄'),
        ('金钱草', '利湿退黄，利尿通淋，解毒消肿'),
    ],
    '消食药': [
        ('山楂', '消食健胃，行气散瘀，化浊降脂'),
        ('麦芽', '行气消食，健脾开胃，回乳消胀'),
        ('谷芽', '消食和中，健脾开胃'),
        ('鸡内金', '健胃消食，涩精止遗，通淋化石'),
        ('莱菔子', '消食除胀，降气化痰'),
    ],
    '安神药': [
        ('酸枣仁', '养心补肝，宁心安神，敛汗，生津'),
        ('柏子仁', '养心安神，润肠通便，止汗'),
        ('合欢皮', '解郁安神，活血消肿'),
        ('远志', '安神益智，交通心肾，祛痰，消肿'),
        ('灵芝', '补气安神，止咳平喘'),
    ],
    '芳香化湿药': [
        ('广藿香', '芳香化浊，和中止呕，发表解暑'),
        ('佩兰', '芳香化湿，醒脾开胃，发表解暑'),
        ('砂仁', '化湿开胃，温脾止泻，理气安胎'),
        ('苍术', '燥湿健脾，祛风散寒，明目'),
        ('厚朴', '燥湿消痰，下气除满'),
    ],
}


def main():
    env_file = Path(__file__).with_name('.env')
    if env_file.exists():
        for raw in env_file.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    rows = [(name, category, efficacy) for category, herbs in HERBS.items() for name, efficacy in herbs]
    if len({name for name, _, _ in rows}) != len(rows):
        raise ValueError('药材名称存在重复')

    db = pymysql.connect(
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        port=int(os.environ.get('DB_PORT', '3306')),
        user=os.environ.get('DB_USER', 'smartclass'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'smartclass'),
        charset='utf8mb4',
        autocommit=False,
    )
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
