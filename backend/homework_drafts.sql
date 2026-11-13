CREATE TABLE IF NOT EXISTS homework_drafts (
    homework_id INT NOT NULL,
    student_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_key CHAR(32) NOT NULL,
    file_size INT UNSIGNED NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (homework_id, student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
