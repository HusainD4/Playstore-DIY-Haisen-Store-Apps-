-- ============================================================
-- DATABASE SQL QUERY FOR HAISEN OFFICIAL APP STORE
-- Database: MySQL (XAMPP) - Port 3307
-- Database Name: haisen_db
-- ============================================================

-- ============================================================
-- TABLE: help_requests (Untuk menyimpan permohonan bantuan)
-- ============================================================
CREATE TABLE IF NOT EXISTS `help_requests` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(200) NOT NULL,
    `email` VARCHAR(200) NOT NULL,
    `issue_type` VARCHAR(100) NOT NULL,
    `issue_description` VARCHAR(200),
    `message` TEXT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'pending',
    `admin_response` TEXT,
    `response_at` DATETIME,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: users
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(100) NOT NULL,
    `email` VARCHAR(200) NOT NULL,
    `password` VARCHAR(200) NOT NULL,
    `role` VARCHAR(20) DEFAULT 'user',
    `is_active` BOOLEAN DEFAULT TRUE,
    `is_approved` BOOLEAN DEFAULT FALSE,
    `is_temp_password` BOOLEAN DEFAULT FALSE,
    `delete_requested` BOOLEAN DEFAULT FALSE,
    `delete_requested_at` DATETIME,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: categories
-- ============================================================
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `description` VARCHAR(500),
    `icon` VARCHAR(50) DEFAULT 'folder',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: apps
-- ============================================================
CREATE TABLE IF NOT EXISTS `apps` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `category_id` INTEGER,
    `developer` VARCHAR(200),
    `user_id` INTEGER,
    `version` VARCHAR(50),
    `size` VARCHAR(50),
    `price` VARCHAR(20) DEFAULT 'Gratis',
    `icon` VARCHAR(200),
    `screenshots` TEXT,
    `file_path` VARCHAR(500),
    `rating` FLOAT DEFAULT 0.0,
    `downloads` INTEGER DEFAULT 0,
    `is_featured` BOOLEAN DEFAULT FALSE,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: reviews
-- ============================================================
CREATE TABLE IF NOT EXISTS `reviews` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `app_id` INTEGER NOT NULL,
    `user_id` INTEGER NOT NULL,
    `rating` INTEGER NOT NULL,
    `comment` TEXT,
    `admin_reply` TEXT,
    `admin_reply_at` DATETIME,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`app_id`) REFERENCES `apps`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: app_uploads
-- ============================================================
CREATE TABLE IF NOT EXISTS `app_uploads` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `app_id` INTEGER NOT NULL,
    `developer_id` INTEGER NOT NULL,
    `version` VARCHAR(50) NOT NULL,
    `notes` TEXT,
    `uploaded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`app_id`) REFERENCES `apps`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`developer_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: app_downloads
-- ============================================================
CREATE TABLE IF NOT EXISTS `app_downloads` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `app_id` INTEGER NOT NULL,
    `user_id` INTEGER NOT NULL,
    `version` VARCHAR(50),
    `downloaded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`app_id`) REFERENCES `apps`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: user_follow_developer
-- ============================================================
CREATE TABLE IF NOT EXISTS `user_follow_developer` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `user_id` INTEGER NOT NULL,
    `developer_id` INTEGER NOT NULL,
    `followed_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_user_follow` (`user_id`, `developer_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`developer_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: notifications
-- ============================================================
CREATE TABLE IF NOT EXISTS `notifications` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `user_id` INTEGER NOT NULL,
    `app_id` INTEGER NOT NULL,
    `message` TEXT NOT NULL,
    `notification_type` VARCHAR(50),
    `is_read` BOOLEAN DEFAULT FALSE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`app_id`) REFERENCES `apps`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: maintenance_routes (Untuk manage maintenance halaman)
-- ============================================================
CREATE TABLE IF NOT EXISTS `maintenance_routes` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `route_name` VARCHAR(200) NOT NULL,
    `route_path` VARCHAR(200) NOT NULL,
    `is_maintenance` BOOLEAN DEFAULT FALSE,
    `maintenance_message` TEXT DEFAULT 'Platform sedang dalam pemeliharaan. Mohon menunggu.',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `route_name` (`route_name`),
    INDEX `idx_is_maintenance` (`is_maintenance`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- INSERT SAMPLE CATEGORIES (Optional)
-- ============================================================
INSERT INTO `categories` (`name`, `description`, `icon`) VALUES 
('Game', 'Aplikasi dan game entertainment', 'gamepad'),
('Produktivitas', 'Aplikasi untuk meningkatkan produktivitas', 'briefcase'),
('Sosial', 'Aplikasi media sosial dan komunikasi', 'users'),
('Edukasi', 'Aplikasi pembelajaran dan pendidikan', 'book'),
('Hiburan', 'Aplikasi hiburan dan multimedia', 'film'),
('Kesehatan', 'Aplikasi kesehatan dan kebugaran', 'heart'),
('Bisnis', 'Aplikasi untuk bisnis dan profesional', 'briefcase'),
('WIB', 'Aplikasi style dan gaya hidup', 'shirt'),
('Fotografi', 'Aplikasi kamera dan edit foto', 'camera'),
('Musik', 'Aplikasi musik dan audio', 'music');
