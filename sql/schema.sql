-- ========================================================
-- KeepInTouch: Схема базы данных (PostgreSQL)
-- Практическая работа № 7: Основы баз данных и SQL
-- ========================================================

-- 1. Таблица пользователей (User / auth_user)
CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    password VARCHAR(128) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблица групп контактов (Group / contacts_group)
CREATE TABLE IF NOT EXISTS contacts_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    owner_id INTEGER NOT NULL,
    CONSTRAINT fk_group_owner FOREIGN KEY (owner_id) 
        REFERENCES auth_user(id) ON DELETE CASCADE
);

-- 3. Таблица телефонных контактов (Contact / contacts_contact)
CREATE TABLE IF NOT EXISTS contacts_contact (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) DEFAULT '',
    number BIGINT NOT NULL,
    birthday DATE NOT NULL,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    tags VARCHAR(200) DEFAULT '',
    owner_id INTEGER NOT NULL,
    group_id INTEGER,
    CONSTRAINT fk_contact_owner FOREIGN KEY (owner_id) 
        REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_contact_group FOREIGN KEY (group_id) 
        REFERENCES contacts_group(id) ON DELETE SET NULL
);

-- Индексы для оптимизации выборок и внешних ключей
CREATE INDEX IF NOT EXISTS idx_contact_owner ON contacts_contact(owner_id);
CREATE INDEX IF NOT EXISTS idx_contact_group ON contacts_contact(group_id);
CREATE INDEX IF NOT EXISTS idx_contact_birthday ON contacts_contact(birthday);

-- Представления (VIEWS) для удобства выполнения учебных запросов:
CREATE OR REPLACE VIEW users AS 
SELECT 
    id, 
    COALESCE(NULLIF(TRIM(first_name || ' ' || last_name), ''), username) AS name, 
    email 
FROM auth_user;

CREATE OR REPLACE VIEW groups AS 
SELECT 
    id, 
    name, 
    description, 
    owner_id 
FROM contacts_group;

CREATE OR REPLACE VIEW contacts AS 
SELECT 
    id, 
    name, 
    firstname, 
    number, 
    birthday, 
    is_favorite, 
    tags, 
    owner_id AS user_id, 
    group_id 
FROM contacts_contact;
