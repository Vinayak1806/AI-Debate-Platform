-- Database setup script for Debate Platform
-- Run this script in your MySQL Workbench

CREATE DATABASE IF NOT EXISTS debate_platform;
USE debate_platform;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    joined_date VARCHAR(50) NOT NULL,
    debates INT DEFAULT 0,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    win_rate VARCHAR(10) DEFAULT '0%',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_label VARCHAR(100) NOT NULL,
    skill_value INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill (user_id, skill_label)
);

-- Create achievements table
CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50) DEFAULT '⭐',
    unlocked BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_achievement (user_id, title)
);

-- Create debate_sessions table (tracks every debate the user participates in)
CREATE TABLE IF NOT EXISTS debate_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    position VARCHAR(10) NOT NULL,       -- 'for' or 'against'
    result VARCHAR(10) DEFAULT NULL,     -- 'win', 'lose', 'draw', NULL means in progress
    messages_count INT DEFAULT 0,
    ai_judgment TEXT DEFAULT NULL,       -- The Gemini evaluation summary
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

