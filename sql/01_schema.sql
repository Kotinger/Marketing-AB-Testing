-- Active: 1788868810471@@127.0.0.1@3306@marketing_ab
-- схема. одна строка = один user_id после pipeline
CREATE DATABASE IF NOT EXISTS marketing_ab
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE marketing_ab;

DROP TABLE IF EXISTS clean_users;

CREATE TABLE clean_users (
  user_id VARCHAR(32) NOT NULL,
  test_group VARCHAR(16) NOT NULL,
  converted TINYINT NOT NULL,
  total_ads INT NOT NULL,
  most_ads_day VARCHAR(16) NULL,
  most_ads_hour TINYINT NULL,
  PRIMARY KEY (user_id),
  INDEX idx_test_group (test_group)
) ENGINE=InnoDB;
