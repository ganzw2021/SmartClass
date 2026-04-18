-- ============================================================
-- scores 表迁移脚本：将 student_name 改为 student_id
-- 运行前请备份数据库！
-- ============================================================

-- 1. 添加新列（如果不存在）
ALTER TABLE scores 
ADD COLUMN IF NOT EXISTS student_id INT AFTER class_id,
ADD FOREIGN KEY IF NOT EXISTS (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- 2. 根据 student_name 和 class_id 匹配 students 表，更新 student_id
-- 注意：如果班级内有重名学生，此更新可能不准确，需要人工核对
UPDATE scores s
JOIN students st ON s.student_name = st.name AND s.class_id = st.class_id
SET s.student_id = st.id
WHERE s.student_id IS NULL;

-- 3. 检查是否有未匹配的记录（student_id 仍为 NULL）
SELECT * FROM scores WHERE student_id IS NULL;

-- 4. 删除未匹配的记录（或保留人工处理）
-- DELETE FROM scores WHERE student_id IS NULL;

-- 5. 修改唯一键（需要先删除旧唯一键）
-- 注意：如果旧表已有 uk_score，需要先删除
ALTER TABLE scores 
DROP INDEX IF EXISTS uk_score,
ADD UNIQUE KEY uk_score (course_id, class_id, student_id);

-- 6. 将 student_id 设为 NOT NULL（确认数据无误后执行）
-- ALTER TABLE scores MODIFY student_id INT NOT NULL;
