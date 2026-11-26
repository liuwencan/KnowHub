-- KnowHub organization and authorization schema.
CREATE DATABASE IF NOT EXISTS `knowhub` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `knowhub`;

CREATE TABLE IF NOT EXISTS `departments` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `parent_id` BIGINT UNSIGNED NULL,
  `name` VARCHAR(128) NOT NULL,
  `path` VARCHAR(512) NOT NULL,
  `sort_order` INT NOT NULL DEFAULT 0,
  `status` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `deleted_at` DATETIME(3) NULL,
  PRIMARY KEY (`id`), KEY `idx_departments_parent` (`parent_id`), KEY `idx_departments_path` (`path`), KEY `idx_departments_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `roles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(64) NOT NULL, `name` VARCHAR(64) NOT NULL, `description` VARCHAR(255) NULL,
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`), UNIQUE KEY `uk_roles_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `employee_no` VARCHAR(64) NOT NULL, `username` VARCHAR(64) NOT NULL, `real_name` VARCHAR(128) NOT NULL,
  `password` VARCHAR(255) NOT NULL, `department_id` BIGINT UNSIGNED NULL, `avatar_url` VARCHAR(512) NULL,
  `status` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `deleted_at` DATETIME(3) NULL,
  PRIMARY KEY (`id`), UNIQUE KEY `uk_users_employee_no` (`employee_no`), UNIQUE KEY `uk_users_username` (`username`),
  KEY `idx_users_department_status` (`department_id`, `status`), KEY `idx_users_status` (`status`), KEY `idx_users_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `user_roles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, `user_id` BIGINT UNSIGNED NOT NULL, `role_id` BIGINT UNSIGNED NOT NULL,
  `department_id` BIGINT UNSIGNED NULL, `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`), UNIQUE KEY `uk_user_roles_scope` (`user_id`, `role_id`, `department_id`), KEY `idx_user_roles_role` (`role_id`), KEY `idx_user_roles_dept` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `role_departments` (
  `role_id` BIGINT UNSIGNED NOT NULL, `department_id` BIGINT UNSIGNED NOT NULL,
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`role_id`, `department_id`), KEY `idx_role_departments_dept` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
