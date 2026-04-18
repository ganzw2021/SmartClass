-- 智慧课堂系统数据库迁移脚本
-- 添加消息通知功能

USE smartclass;

-- 1. 给 homework 表添加 is_published 字段（如果不存在）
-- 先检查字段是否存在
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'smartclass' 
    AND TABLE_NAME = 'homework' 
    AND COLUMN_NAME = 'is_published'
);
SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE homework ADD COLUMN is_published TINYINT(1) DEFAULT 0 COMMENT "是否发布 0=草稿 1=已发布" AFTER total_score',
    'SELECT "is_published already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. 给 homework 表添加 auto_grade_enabled 字段（如果不存在）
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'smartclass' 
    AND TABLE_NAME = 'homework' 
    AND COLUMN_NAME = 'auto_grade_enabled'
);
SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE homework ADD COLUMN auto_grade_enabled TINYINT(1) DEFAULT 0 COMMENT "是否启用自动评分" AFTER is_published',
    'SELECT "auto_grade_enabled already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. 给 homework 表添加 has_grading_script 字段（如果不存在）
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'smartclass' 
    AND TABLE_NAME = 'homework' 
    AND COLUMN_NAME = 'has_grading_script'
);
SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE homework ADD COLUMN has_grading_script TINYINT(1) DEFAULT 0 COMMENT "是否有评分脚本" AFTER auto_grade_enabled',
    'SELECT "has_grading_script already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4. 创建学生通知表
CREATE TABLE IF NOT EXISTS student_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL COMMENT '学生ID',
    type VARCHAR(50) NOT NULL COMMENT '通知类型: homework_new(新作业), homework_reminder(作业提醒)',
    title VARCHAR(200) NOT NULL COMMENT '通知标题',
    content TEXT COMMENT '通知内容',
    related_id INT DEFAULT NULL COMMENT '关联ID(作业ID等)',
    related_type VARCHAR(50) DEFAULT NULL COMMENT '关联类型: homework',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读 0=未读 1=已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB COMMENT='学生通知表';

-- 5. 创建评分脚本表
CREATE TABLE IF NOT EXISTS homework_grading_scripts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    homework_id INT NOT NULL COMMENT '作业ID',
    script_name VARCHAR(255) NOT NULL COMMENT '脚本文件名',
    script_path VARCHAR(500) NOT NULL COMMENT '脚本存储路径',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_homework (homework_id),
    FOREIGN KEY (homework_id) REFERENCES homework(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业评分脚本表';

SELECT 'Migration completed successfully!' as status;
