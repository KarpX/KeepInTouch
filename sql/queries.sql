-- ========================================================
-- KeepInTouch: SQL-запросы предметной области (ПР7)
-- Практическая работа № 7: Основы баз данных и SQL
-- Включает выборки (SELECT), фильтрацию (WHERE), объединения (JOIN),
-- агрегатные функции, группировку (GROUP BY), HAVING и подзапросы.
-- ========================================================


-- --------------------------------------------------------
-- 1. Выборка списка всех контактов с сортировкой по алфавиту
-- Назначение: базовый список контактов для телефонной книги
-- Используемые конструкции: SELECT, FROM, ORDER BY
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.number,
    c.birthday
FROM contacts_contact AS c
ORDER BY c.name ASC, c.firstname ASC;


-- --------------------------------------------------------
-- 2. Постраничная выборка контактов (пагинация)
-- Назначение: ограничение объема данных для вывода порциями
-- Используемые конструкции: ORDER BY, LIMIT, OFFSET
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.number
FROM contacts_contact AS c
ORDER BY c.id ASC
LIMIT 3 OFFSET 0;


-- --------------------------------------------------------
-- 3. Поиск контактов по подстроке имени или фамилии
-- Назначение: глобальный поиск в записной книжке по части слова
-- Используемые конструкции: WHERE, ILIKE, OR
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.number
FROM contacts_contact AS c
WHERE c.name ILIKE '%Никита%' OR c.firstname ILIKE '%Малютин%'
ORDER BY c.name;


-- --------------------------------------------------------
-- 4. Поиск контактов с датой рождения в заданном диапазоне
-- Назначение: выборка людей, родившихся в указанный период лет
-- Используемые конструкции: WHERE, BETWEEN, ORDER BY
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.birthday
FROM contacts_contact AS c
WHERE c.birthday BETWEEN '1995-01-01' AND '2005-12-31'
ORDER BY c.birthday ASC;


-- --------------------------------------------------------
-- 5. Поиск контактов без привязанной группы (NULL-значения)
-- Назначение: поиск записей, требующих категоризации
-- Используемые конструкции: WHERE, IS NULL
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.number
FROM contacts_contact AS c
WHERE c.group_id IS NULL;


-- --------------------------------------------------------
-- 6. Выборка избранных контактов конкретного пользователя
-- Назначение: быстрый доступ к избранным контактам владельца
-- Используемые конструкции: WHERE, AND, IN
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.number,
    c.is_favorite
FROM contacts_contact AS c
WHERE c.owner_id = 1 
  AND c.is_favorite = TRUE;


-- --------------------------------------------------------
-- 7. Полная информация о контакте со сведениями о группе и владельце
-- Назначение: отображение карточки контакта со связанными сущностями
-- Используемые конструкции: INNER JOIN (две связанные таблицы)
-- --------------------------------------------------------
SELECT 
    c.id AS contact_id,
    c.name AS contact_name,
    c.firstname AS contact_firstname,
    c.number AS phone_number,
    c.birthday,
    g.name AS group_name,
    u.username AS owner_username,
    u.email AS owner_email
FROM contacts_contact AS c
JOIN contacts_group AS g ON c.group_id = g.id
JOIN auth_user AS u ON c.owner_id = u.id
ORDER BY c.name;


-- --------------------------------------------------------
-- 8. Список всех контактов с левым соединением групп (LEFT JOIN)
-- Назначение: показ контактов даже в случае, если группа не назначена (NULL)
-- Используемые конструкции: LEFT JOIN, COALESCE
-- --------------------------------------------------------
SELECT 
    c.id,
    c.name,
    c.firstname,
    c.number,
    COALESCE(g.name, 'Без группы') AS group_name
FROM contacts_contact AS c
LEFT JOIN contacts_group AS g ON c.group_id = g.id
ORDER BY c.id;


-- --------------------------------------------------------
-- 9. Общее количество контактов и количество избранных (Агрегаты)
-- Назначение: сводная статистика на дашборде
-- Используемые конструкции: COUNT(*), SUM / FILTER (агрегатные функции)
-- --------------------------------------------------------
SELECT 
    COUNT(*) AS total_contacts,
    COUNT(CASE WHEN is_favorite THEN 1 END) AS favorite_contacts
FROM contacts_contact;


-- --------------------------------------------------------
-- 10. Определение экстремальных значений (MIN, MAX) дат рождения
-- Назначение: поиск самого старшего и самого младшего контакта
-- Используемые конструкции: MIN(), MAX()
-- --------------------------------------------------------
SELECT 
    MIN(birthday) AS oldest_birthday,
    MAX(birthday) AS youngest_birthday
FROM contacts_contact;


-- --------------------------------------------------------
-- 11. Статистика распределения контактов по группам
-- Назначение: группировка и подсчет контактов для каждой группы (включая пустые)
-- Используемые конструкции: LEFT JOIN, GROUP BY, COUNT()
-- --------------------------------------------------------
SELECT 
    g.id AS group_id,
    g.name AS group_name,
    COUNT(c.id) AS contacts_count
FROM contacts_group AS g
LEFT JOIN contacts_contact AS c ON g.id = c.group_id
GROUP BY g.id, g.name
ORDER BY contacts_count DESC, g.name ASC;


-- --------------------------------------------------------
-- 12. Поиск групп с количеством контактов больше одного (HAVING)
-- Назначение: фильтрация сформированных групп по агрегированному признаку
-- Используемые конструкции: GROUP BY, HAVING, COUNT()
-- --------------------------------------------------------
SELECT 
    g.id AS group_id,
    g.name AS group_name,
    COUNT(c.id) AS contacts_count
FROM contacts_group AS g
JOIN contacts_contact AS c ON g.id = c.group_id
GROUP BY g.id, g.name
HAVING COUNT(c.id) > 1
ORDER BY contacts_count DESC;


-- --------------------------------------------------------
-- 13. Поиск пустых групп без контактов (Подзапрос NOT IN)
-- Назначение: поиск неиспользуемых категорий (аналог свободных аудиторий)
-- Используемые конструкции: WHERE ... NOT IN (SELECT ...)
-- --------------------------------------------------------
SELECT 
    g.id,
    g.name,
    g.description
FROM contacts_group AS g
WHERE g.id NOT IN (
    SELECT DISTINCT c.group_id 
    FROM contacts_contact AS c 
    WHERE c.group_id IS NOT NULL
)
ORDER BY g.name;
