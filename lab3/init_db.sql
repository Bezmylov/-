-- Создание базы данных
CREATE DATABASE archdb;

-- Подключение к базе данных
\c archdb;

-- Создание таблицы пользователей с полями для хранения хешированного пароля
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого поиска по имени пользователя
CREATE INDEX IF NOT EXISTS idx_username ON users(username);

-- Создание таблицы для групповых чатов
CREATE TABLE IF NOT EXISTS group_chats (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения членов группового чата
CREATE TABLE IF NOT EXISTS group_chat_members (
    group_chat_id INT REFERENCES group_chats(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (group_chat_id, user_id)
);

-- Создание таблицы для приватных чатов
CREATE TABLE IF NOT EXISTS private_chats (
    id SERIAL PRIMARY KEY,
    user1 INT REFERENCES users(id) ON DELETE CASCADE,
    user2 INT REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения сообщений (поддерживает как групповые, так и приватные чаты)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    chat_id INT NOT NULL,
    sender_id INT REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Индекс для ускорения поиска сообщений по ID чата
CREATE INDEX IF NOT EXISTS idx_chat_id ON messages(chat_id);

-- Тестовые данные
INSERT INTO users (username, email, hashed_password, age) VALUES 
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 30)
ON CONFLICT DO NOTHING;

INSERT INTO group_chats (name) VALUES ('Study Group') ON CONFLICT DO NOTHING;
