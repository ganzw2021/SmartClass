-- 智慧课堂系统数据库初始化脚本
-- 江西樟树中医药职业学院
-- 架构V2: 管理端统一管理班级和学生，教师端关联班级进行教学

CREATE DATABASE IF NOT EXISTS smartclass DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smartclass;

-- 教师表
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    teacher_token VARCHAR(100) UNIQUE COMMENT '教师唯一token（兼容旧系统）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='教师表';

-- 班级表（V2: 移除teacher_id外键，由管理端统一管理）
CREATE TABLE IF NOT EXISTS classes (
    id VARCHAR(50) PRIMARY KEY COMMENT '班级ID',
    name VARCHAR(100) NOT NULL COMMENT '班级名称',
    description VARCHAR(255) DEFAULT '' COMMENT '班级描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='班级表';

-- 学生表
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    student_number VARCHAR(50) DEFAULT NULL COMMENT '学号',
    class_id VARCHAR(50) NOT NULL COMMENT '班级ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    UNIQUE KEY uk_class_name (class_id, name),
    INDEX idx_student_number (student_number)
) ENGINE=InnoDB COMMENT='学生表';

-- 课程表（V2: 教师创建课程，通过course_classes关联班级）
CREATE TABLE IF NOT EXISTS courses (
    id VARCHAR(50) PRIMARY KEY COMMENT '课程ID',
    name VARCHAR(100) NOT NULL COMMENT '课程名称',
    term VARCHAR(50) NOT NULL COMMENT '学期',
    teacher_id INT NOT NULL COMMENT '创建教师ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='课程表';

-- 课程-班级关联表（V2新增: 一个课程可关联多个班级）
CREATE TABLE IF NOT EXISTS course_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL COMMENT '课程ID',
    class_id VARCHAR(50) NOT NULL COMMENT '班级ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    UNIQUE KEY uk_course_class (course_id, class_id)
) ENGINE=InnoDB COMMENT='课程班级关联表';

-- 平时成绩表
CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL COMMENT '课程ID',
    class_id VARCHAR(50) NOT NULL COMMENT '班级ID',
    student_id INT NOT NULL COMMENT '学生ID',
    student_name VARCHAR(50) NOT NULL COMMENT '学生姓名（冗余，方便显示）',
    att_score INT DEFAULT 20 COMMENT '考勤分(0-20)',
    interact_score INT DEFAULT 0 COMMENT '互动分(0-10)',
    hw_score INT DEFAULT 20 COMMENT '作业分(0-20)',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_score (course_id, class_id, student_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='平时成绩表';

-- ===================== 时光墙（论坛模块） =====================
-- 帖子表
CREATE TABLE IF NOT EXISTS forum_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL DEFAULT '' COMMENT '标题，空则为纯图文',
    content TEXT NOT NULL COMMENT '正文',
    course_id VARCHAR(50) NOT NULL COMMENT '关联课程ID',
    course_name VARCHAR(100) NOT NULL COMMENT '课程名称（冗余）',
    author_id INT NOT NULL COMMENT '作者用户ID（学生或教师）',
    author_name VARCHAR(50) NOT NULL COMMENT '作者姓名（匿名时保留）',
    author_type ENUM('student','teacher') NOT NULL COMMENT '作者身份',
    is_anonymous TINYINT(1) DEFAULT 0 COMMENT '是否匿名 0=实名 1=匿名',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course_id (course_id),
    INDEX idx_author_id (author_id),
    INDEX idx_author_type (author_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='时光墙帖子表';

-- 评论表
CREATE TABLE IF NOT EXISTS forum_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL COMMENT '所属帖子ID',
    author_id INT NOT NULL COMMENT '评论者用户ID',
    author_name VARCHAR(50) NOT NULL COMMENT '评论者姓名',
    author_type ENUM('student','teacher') NOT NULL COMMENT '评论者身份',
    content TEXT NOT NULL COMMENT '评论内容',
    is_anonymous TINYINT(1) DEFAULT 0 COMMENT '是否匿名',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_post_id (post_id),
    INDEX idx_author_id (author_id),
    FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='时光墙评论表';

-- 分数配置表
CREATE TABLE IF NOT EXISTS score_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL COMMENT '课程ID',
    att_max INT DEFAULT 20 COMMENT '考勤满分',
    interact_max INT DEFAULT 10 COMMENT '互动满分',
    hw_max INT DEFAULT 20 COMMENT '作业满分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY uk_course_config (course_id)
) ENGINE=InnoDB COMMENT='分数配置表';

-- 签到会话表
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_key VARCHAR(150) NOT NULL UNIQUE COMMENT 'teacherToken__courseId',
    course_id VARCHAR(50) NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    teacher_id INT NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    -- 教室位置（地理围栏）
    classroom_lat DECIMAL(10, 8) DEFAULT NULL COMMENT '教室纬度',
    classroom_lng DECIMAL(11, 8) DEFAULT NULL COMMENT '教室经度',
    classroom_radius INT DEFAULT 10 COMMENT '允许签到半径(米)',
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='签到会话表';

-- 签到记录表
CREATE TABLE IF NOT EXISTS attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_key VARCHAR(150) NOT NULL COMMENT '对应会话key',
    course_id VARCHAR(50) NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    student_name VARCHAR(50) NOT NULL,
    sign_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(50),
    device_info TEXT,
    device_fingerprint VARCHAR(255) COMMENT '设备指纹防重复',
    INDEX idx_session (session_key),
    INDEX idx_course_class (course_id, class_id)
) ENGINE=InnoDB COMMENT='签到记录表';

-- 学生账号表
CREATE TABLE IF NOT EXISTS student_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL COMMENT '关联students表ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    avatar TEXT DEFAULT '' COMMENT '头像Base64数据',
    bio VARCHAR(200) DEFAULT '' COMMENT '个性签名',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_student_id (student_id)
) ENGINE=InnoDB COMMENT='学生账号表';

-- 作业表
CREATE TABLE IF NOT EXISTS homework (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL COMMENT '课程ID',
    class_id VARCHAR(50) NOT NULL COMMENT '班级ID',
    teacher_id INT NOT NULL COMMENT '教师ID',
    title VARCHAR(200) NOT NULL COMMENT '作业标题',
    content TEXT COMMENT '作业内容',
    deadline DATETIME COMMENT '截止时间',
    total_score INT DEFAULT 100 COMMENT '满分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course (course_id),
    INDEX idx_class (class_id),
    INDEX idx_teacher (teacher_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业表';

-- 作业附件表（教师布置作业时上传的文件）
CREATE TABLE IF NOT EXISTS homework_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    homework_id INT NOT NULL COMMENT '作业ID',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size INT NOT NULL COMMENT '文件大小(字节)',
    file_type VARCHAR(100) COMMENT '文件MIME类型',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_homework (homework_id),
    FOREIGN KEY (homework_id) REFERENCES homework(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业附件表';

-- 作业提交表
CREATE TABLE IF NOT EXISTS homework_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    homework_id INT NOT NULL COMMENT '作业ID',
    student_id INT NOT NULL COMMENT '学生ID',
    student_name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    content TEXT COMMENT '提交内容',
    score INT DEFAULT NULL COMMENT '得分',
    feedback TEXT COMMENT '教师反馈',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    graded_at DATETIME DEFAULT NULL,
    INDEX idx_homework (homework_id),
    INDEX idx_student (student_id),
    UNIQUE KEY uk_homework_student (homework_id, student_id)
) ENGINE=InnoDB COMMENT='作业提交表';

-- 作业提交附件表（学生提交作业时上传的文件）
CREATE TABLE IF NOT EXISTS submission_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL COMMENT '提交记录ID',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size INT NOT NULL COMMENT '文件大小(字节)',
    file_type VARCHAR(100) COMMENT '文件MIME类型',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_submission (submission_id),
    FOREIGN KEY (submission_id) REFERENCES homework_submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业提交附件表';

-- 评分附件表（教师评分时上传的评分细节文件）
CREATE TABLE IF NOT EXISTS grade_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL COMMENT '提交记录ID',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size INT NOT NULL COMMENT '文件大小(字节)',
    file_type VARCHAR(100) COMMENT '文件MIME类型',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_submission (submission_id),
    FOREIGN KEY (submission_id) REFERENCES homework_submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='评分附件表';

-- 考勤报表表（每次考勤会话结束后生成一条记录）
CREATE TABLE IF NOT EXISTS attendance_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL COMMENT '教师ID',
    course_id VARCHAR(50) NOT NULL COMMENT '课程ID',
    class_id VARCHAR(50) NOT NULL COMMENT '班级ID',
    course_name VARCHAR(100) NOT NULL COMMENT '课程名称（冗余）',
    class_name VARCHAR(100) NOT NULL COMMENT '班级名称（冗余）',
    started_at DATETIME DEFAULT NULL COMMENT '签到开始时间',
    ended_at DATETIME DEFAULT NULL COMMENT '签到结束时间',
    total_students INT DEFAULT 0 COMMENT '班级总人数',
    signed_count INT DEFAULT 0 COMMENT '实到人数',
    absent_count INT DEFAULT 0 COMMENT '缺勤人数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    INDEX idx_teacher (teacher_id),
    INDEX idx_course_class (course_id, class_id),
    INDEX idx_ended_at (ended_at)
) ENGINE=InnoDB COMMENT='考勤报表表';

-- 考勤学生明细表（每个学生的考勤状态）
CREATE TABLE IF NOT EXISTS attendance_student_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT NOT NULL COMMENT '报表ID',
    student_id INT DEFAULT NULL COMMENT '学生ID（可能为NULL手动添加）',
    student_name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    student_number VARCHAR(50) DEFAULT NULL COMMENT '学号',
    status ENUM('signed','absent','leave_sick','leave_personal','late','early_leave') NOT NULL DEFAULT 'absent' COMMENT '考勤状态',
    sign_time DATETIME DEFAULT NULL COMMENT '签到时间',
    note VARCHAR(200) DEFAULT NULL COMMENT '备注',
    updated_by INT DEFAULT NULL COMMENT '操作教师ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES attendance_reports(id) ON DELETE CASCADE,
    INDEX idx_report (report_id),
    INDEX idx_student (student_id)
) ENGINE=InnoDB COMMENT='考勤学生明细表';

-- 作业分排行榜表（记录每个班级学生的作业分累计）
CREATE TABLE IF NOT EXISTS homework_score_ranking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id VARCHAR(50) NOT NULL COMMENT '班级ID',
    student_id INT NOT NULL COMMENT '学生ID',
    student_name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    total_score INT DEFAULT 0 COMMENT '作业分累计',
    homework_count INT DEFAULT 0 COMMENT '已评分作业数量',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_class (class_id),
    INDEX idx_student (student_id),
    UNIQUE KEY uk_class_student (class_id, student_id),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业分排行榜表';

-- 插入默认管理员账号（用户名: admin，密码: Admin@123456）
INSERT IGNORE INTO teachers (username, real_name, password_hash, teacher_token) VALUES 
('admin', '管理员教师', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMaEzGvSGd5VqBKdBZHIL9YWFS', 'teacher_1773622062292_xqjaap');
