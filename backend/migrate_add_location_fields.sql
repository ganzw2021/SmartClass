-- 为 attendance_sessions 表添加地理围栏字段
-- 执行此脚本以添加教室位置字段

ALTER TABLE attendance_sessions
ADD COLUMN IF NOT EXISTS classroom_lat DECIMAL(10, 8) DEFAULT NULL COMMENT '教室纬度',
ADD COLUMN IF NOT EXISTS classroom_lng DECIMAL(11, 8) DEFAULT NULL COMMENT '教室经度',
ADD COLUMN IF NOT EXISTS classroom_radius INT DEFAULT 10 COMMENT '允许签到半径（米）';
