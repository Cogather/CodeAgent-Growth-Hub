-- MySQL 8.x DDL（应用启动时也会通过 SQLAlchemy 自动建表，此文件供 DBA 参考或手工执行）

CREATE DATABASE IF NOT EXISTS codeagent_growth_hub
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE codeagent_growth_hub;

CREATE TABLE IF NOT EXISTS meta_department (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    parent_id   INT NULL,
    name        VARCHAR(128) NOT NULL,
    CONSTRAINT fk_dept_parent FOREIGN KEY (parent_id) REFERENCES meta_department(id) ON DELETE RESTRICT,
    CONSTRAINT uq_dept_parent_name UNIQUE (parent_id, name),
    INDEX idx_dept_parent (parent_id)
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
