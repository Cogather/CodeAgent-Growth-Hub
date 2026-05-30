-- MySQL 8.x DDL（应用启动时也会通过 SQLAlchemy 自动建表，此文件供 DBA 参考或手工执行）

CREATE DATABASE IF NOT EXISTS codeagent_growth_hub
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE codeagent_growth_hub;

CREATE TABLE IF NOT EXISTS meta_department (
    dept_code         VARCHAR(64) NOT NULL PRIMARY KEY,
    parent_dept_code  VARCHAR(64) NULL,
    name              VARCHAR(128) NOT NULL,
    CONSTRAINT fk_dept_parent FOREIGN KEY (parent_dept_code) REFERENCES meta_department(dept_code) ON DELETE RESTRICT,
    CONSTRAINT uq_dept_parent_name UNIQUE (parent_dept_code, name),
    INDEX idx_dept_parent (parent_dept_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS meta_focus_pdu (
    dept_code     VARCHAR(64) NOT NULL PRIMARY KEY,
    alias         VARCHAR(128) NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_focus_pdu_dept FOREIGN KEY (dept_code) REFERENCES meta_department(dept_code) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS meta_personnel (
    emp_no          VARCHAR(64) PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    name_initial    VARCHAR(8) NOT NULL,
    dept_l1_name    VARCHAR(128) NULL,
    dept_l1_code    VARCHAR(64) NULL,
    dept_l2_name    VARCHAR(128) NULL,
    dept_l2_code    VARCHAR(64) NULL,
    dept_l3_name    VARCHAR(128) NULL,
    dept_l3_code    VARCHAR(64) NULL,
    dept_l4_name    VARCHAR(128) NULL,
    dept_l4_code    VARCHAR(64) NULL,
    dept_l5_name    VARCHAR(128) NULL,
    dept_l5_code    VARCHAR(64) NULL,
    dept_l6_name    VARCHAR(128) NULL,
    dept_l6_code    VARCHAR(64) NULL,
    dept_l7_name    VARCHAR(128) NULL,
    dept_l7_code    VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS perm_zone_yellow (
    emp_no      VARCHAR(64) PRIMARY KEY,
    models      VARCHAR(512) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS perm_zone_blue (
    emp_no      VARCHAR(64) PRIMARY KEY,
    models      VARCHAR(512) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS perm_zone_green (
    emp_no      VARCHAR(64) PRIMARY KEY,
    models      VARCHAR(512) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stat_usage (
    emp_no          VARCHAR(64) PRIMARY KEY,
    usage_count     INT NOT NULL DEFAULT 0,
    imported_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_user (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    username                VARCHAR(64) NOT NULL,
    name                    VARCHAR(128) NOT NULL,
    password_hash           VARCHAR(255) NOT NULL,
    role                    VARCHAR(16) NOT NULL DEFAULT 'viewer',
    is_active               TINYINT(1) NOT NULL DEFAULT 1,
    must_change_password    TINYINT(1) NOT NULL DEFAULT 1,
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_sys_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
