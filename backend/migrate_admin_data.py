"""
将admin账号下的数据迁移到新的教师账号
用法: python migrate_admin_data.py <新教师用户名>
"""
import sys
import pymysql

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'smartclass',
    'charset': 'utf8mb4',
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def migrate_data(new_teacher_username):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # 1. 查找admin账号
            cur.execute("SELECT id, username FROM teachers WHERE username='admin'")
            admin = cur.fetchone()
            if not admin:
                print("[ERR] admin账号不存在")
                return False
            admin_id = admin['id']
            print(f"[OK] 找到admin账号 (ID: {admin_id})")

            # 2. 查找新教师账号
            cur.execute("SELECT id, username FROM teachers WHERE username=%s", (new_teacher_username,))
            new_teacher = cur.fetchone()
            if not new_teacher:
                print(f"[ERR] 教师账号 '{new_teacher_username}' 不存在")
                print("[INFO] 请先创建该教师账号")
                return False
            new_teacher_id = new_teacher['id']
            print(f"[OK] 找到目标教师账号 '{new_teacher_username}' (ID: {new_teacher_id})")

            # 3. 统计要迁移的数据
            cur.execute("SELECT COUNT(*) as cnt FROM classes WHERE teacher_id=%s", (admin_id,))
            class_count = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) as cnt FROM courses WHERE teacher_id=%s", (admin_id,))
            course_count = cur.fetchone()['cnt']
            print(f"[INFO] 准备迁移: {class_count}个班级, {course_count}门课程")

            # 自动确认（可通过命令行参数控制）
            auto_confirm = len(sys.argv) > 2 and sys.argv[2] == '--yes'
            if not auto_confirm:
                confirm = input(f"\n确认将admin的数据迁移到 '{new_teacher_username}'? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("[INFO] 操作已取消")
                    return False

            # 4. 迁移班级
            cur.execute("UPDATE classes SET teacher_id=%s WHERE teacher_id=%s", (new_teacher_id, admin_id))
            migrated_classes = cur.rowcount
            print(f"[OK] 迁移了 {migrated_classes} 个班级")

            # 5. 迁移课程
            cur.execute("UPDATE courses SET teacher_id=%s WHERE teacher_id=%s", (new_teacher_id, admin_id))
            migrated_courses = cur.rowcount
            print(f"[OK] 迁移了 {migrated_courses} 门课程")

            # 6. 迁移考勤会话记录
            cur.execute("UPDATE attendance_sessions SET teacher_id=%s WHERE teacher_id=%s", (new_teacher_id, admin_id))
            migrated_sessions = cur.rowcount
            print(f"[OK] 迁移了 {migrated_sessions} 条考勤会话记录")

            conn.commit()
            print("\n[OK] 数据迁移完成!")
            print(f"[INFO] admin账号现在没有关联的班级和课程了")
            return True

    except Exception as e:
        print(f"[ERR] 迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python migrate_admin_data.py <新教师用户名>")
        print("示例: python migrate_admin_data.py teacher1")
        sys.exit(1)
    
    new_username = sys.argv[1]
    success = migrate_data(new_username)
    sys.exit(0 if success else 1)
