CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'customer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT NULL,
    image_original_path VARCHAR(255) NULL,
    image_processed_path VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS category_image_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    celery_task_id VARCHAR(120) NULL,
    status VARCHAR(30) NOT NULL,
    original_image_path VARCHAR(255) NOT NULL,
    processed_image_path VARCHAR(255) NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_category_image_jobs_category_id (category_id),
    INDEX ix_category_image_jobs_celery_task_id (celery_task_id),
    INDEX ix_category_image_jobs_status (status),
    CONSTRAINT fk_category_image_jobs_category FOREIGN KEY (category_id)
        REFERENCES categories(id) ON DELETE CASCADE
);
