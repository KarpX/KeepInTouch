# KeepInTouch – система управления телефонными контактами
Персональный органайзер контактов и связей на Python с веб-интерфейсом на Django.

## 1. Назначение проекта
KeepInTouch – учебное веб-приложение для управления контактами, персонализации связей и структурирования по группам.
Проект позволяет хранить сведения о контактах, пользователях и группах, выполнять основные операции с этими объектами (CRUD) и предоставлять доступ к информации через удобный веб-интерфейс Django.
Проект развивается поэтапно: консольная версия приложения (ПР1–ПР3) дополняется веб-интерфейсом и последовательно переводится на возможности экосистемы Django.

## 2. Используемые технологии
- Python 3;
- Django 5;
- Django Template Language (DTL);
- HTML5;
- CSS3;
- JavaScript;
- Tailwind CSS / Serene Pastel Minimal UI;
- PostgreSQL / JSON для хранения данных;
- Git;
- pytest;
- pytest-django.

## 3. Предметная область
В системе используются три основные сущности:
- **Пользователь (User)** – аутентификация, профиль и изоляция персональной записной книжки;
- **Контакт (Contact)** – имя, фамилия, номер телефона, дата рождения, заметки, признак «избранное», теги;
- **Группа (Group)** – категория для структурирования и быстрого поиска контактов (например: Семья, Работа, Друзья).

Для предметной области реализованы модели данных, формы валидации и представления Django.

## 4. Структура проекта
```text
KeepInTouch/
├── accounts/
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── contacts/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
│       ├── test_forms.py
│       ├── test_models.py
│       └── test_views.py
├── keep_in_touch/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── includes/
│   │   └── navigation.html
│   ├── contacts/
│   │   ├── includes/
│   │   │   ├── contact_card.html
│   │   │   └── contact_badge.html
│   │   ├── contact_list.html
│   │   ├── contact_detail.html
│   │   ├── contact_form.html
│   │   ├── contact_confirm_delete.html
│   │   ├── group_list.html
│   │   ├── group_form.html
│   │   ├── group_confirm_delete.html
│   │   ├── statistics.html
│   │   ├── sql_search_date.html
│   │   └── sql_contact_list.html
│   └── accounts/
│       ├── login.html
│       └── register.html
├── static/
│   └── keep_in_touch/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── img/
│           └── logo.png
├── db/
│   ├── __init__.py
│   ├── database.py
│   └── import_json.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── data/
│   ├── contacts.json
│   ├── groups.json
│   └── users.json
├── models/
│   ├── contacts.py
│   ├── groups.py
│   └── users.py
├── main.py
├── storage.py
├── utils.py
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## 5. Веб-интерфейс
Веб-часть приложения реализована на Django.
Основные страницы:
- **Главная страница (`/`)** – персональный дашборд со сводной статистикой, карточками быстрых действий и списком ближайших дней рождения;
- **Список контактов (`/contacts/`)** – каталог контактов с табличным и сеточным режимами просмотра, поиском и фильтрацией;
- **Избранное (`/contacts/favorites/`)** – быстрый доступ к важным контактам;
- **Информация о контакте (`/contacts/<id>/`)** – подробная карточка контакта с кнопками звонка, копирования и историей данных;
- **Формы добавления и редактирования контакта (`/contacts/add/`, `/contacts/<id>/edit/`)**;
- **Список групп (`/contacts/groups/`)** и облако тегов;
- **Страницы авторизации и регистрации (`/accounts/login/`, `/accounts/register/`)**.

Для формирования страниц используются Django-шаблоны. Генерация HTML непосредственно в Python-коде веб-представлений не используется. Представления подготавливают данные и передают их в шаблоны через контекст функции `render()`.

## 6. Django Template Language (DTL)
Шаблоны используют возможности Django Template Language.

### Базовый шаблон
Общий шаблон страниц: `templates/base.html`.
Он содержит общую HTML-структуру страницы, подключение собственных стилей и JavaScript, навигацию и блоки для содержимого отдельных страниц.
Дочерние шаблоны используют наследование:
```django
{% extends "base.html" %}
```
Содержимое страниц размещается в переопределяемых блоках:
```django
{% block title %}Заголовок страницы{% endblock %}
{% block content %}...{% endblock %}
```

### Включаемые шаблоны (include)
Повторяющиеся и составные части интерфейса вынесены в отдельные подключаемые шаблоны:
- `templates/includes/navigation.html` – адаптивная навигация (боковое меню для авторизованных пользователей, мобильный хедер и публичная шапка);
- `templates/contacts/includes/contact_card.html` – карточка контакта в сеточном представлении каталога;
- `templates/contacts/includes/contact_badge.html` – статусная плашка контакта (признак избранного, принадлежность к группе).

Подключение выполняется тегом `{% include %}`:
```django
{% include "includes/navigation.html" %}
{% include "contacts/includes/contact_card.html" %}
{% include "contacts/includes/contact_badge.html" %}
```

### Контекст
Представления передают данные в шаблоны через словарь контекста.
Например, для списка контактов:
```python
context = {
    "contacts": contacts,
    "query": query,
    "groups": groups,
    "total_contacts_count": total_contacts_count,
    "favorites_count": favorites_count,
}
return render(request, "contacts/contact_list.html", context)
```
В шаблоне данные доступны по именам ключей контекста: `{{ contacts }}`, `{{ total_contacts_count }}`.

### Циклы и условия
Для формирования списков используются циклы с обработкой отсутствия элементов:
```django
{% for contact in contacts %}
  {% include "contacts/includes/contact_card.html" %}
{% empty %}
  <p>Контакты не найдены.</p>
{% endfor %}
```

Условия используются для отображения альтернативных состояний интерфейса:
```django
{% if contact.is_favorite %}
  <span class="material-symbols-fill text-tertiary">star</span>
{% endif %}
```

## 7. Фильтры шаблонов
В шаблонах используются стандартные фильтры Django Template Language:
- `length` – подсчет количества элементов списка (например, `{{ contacts|length }}`, `{{ groups|length }}`);
- `default` – отображение значения по умолчанию (например, `{{ user.first_name|default:user.username }}`, `{{ contact.initials|default:"К" }}`);
- `date` – форматирование дат (например, `{{ contact.birthday|date:"d E Y" }}`);
- `slice` и `upper` – выделение первой буквы имени для монограммы аватара (`{{ user.username|slice:":1"|upper }}`).

Фильтры служат исключительно для форматирования представления данных и не переносят бизнес-логику в шаблоны.

## 8. URL-маршрутизация
Для страниц используются именованные маршруты Django с пространствами имён (namespaces):
- `app_name = "contacts"`
- `app_name = "accounts"`

Примеры формирования ссылок:
```django
{% url 'home' %}
{% url 'contacts:contact_list' %}
{% url 'contacts:contact_detail' contact.pk %}
{% url 'contacts:contact_create' %}
{% url 'contacts:group_list' %}
{% url 'accounts:login' %}
{% url 'accounts:logout' %}
```
Ссылки в шаблонах формируются через тег `{% url %}`, исключая зависимость HTML от жёстко заданных путей.

## 9. Статические файлы
Статические файлы проекта расположены в каталоге:
`static/keep_in_touch/`
Используются:
- `css/style.css` – собственные стили проекта (карточки контактов, анимации hover, оформление бейджей, логотип и футер);
- `js/main.js` – скрипты интерфейса (динамическое определение и вывод текущего года в элементе `#current-year`, автоматическое скрытие всплывающих сообщений);
- `img/logo.png` – графический логотип проекта.

Подключение статических ресурсов в базовом шаблоне:
```django
{% load static %}
<link rel="stylesheet" href="{% static 'keep_in_touch/css/style.css' %}">
<script src="{% static 'keep_in_touch/js/main.js' %}"></script>
<img src="{% static 'keep_in_touch/img/logo.png' %}" alt="KeepInTouch">
```

## 10. Запуск проекта

### 1. Запуск базы данных PostgreSQL (Docker)
```bash
docker compose up -d
```

### 2. Установка зависимостей и миграции
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 3. Проверка проекта и статических файлов
```bash
python manage.py check
python manage.py findstatic keep_in_touch/img/logo.png
```

### 4. Запуск сервера разработки
```bash
python manage.py runserver
```
Веб-интерфейс доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 11. Тестирование
Запуск полного набора юнит-тестов:
```bash
pytest -v
```

## 12. Практическая работа № 7: Реляционная база данных и язык SQL
На этапе ПР7 в проект внедрён самостоятельный слой реляционного хранения данных и прямого выполнения SQL-запросов (без Django ORM):
- **Схема базы данных (`sql/schema.sql`)**: DDL-описание таблиц `auth_user`, `contacts_group`, `contacts_contact` с первичными ключами (`PRIMARY KEY`), внешними ключами (`FOREIGN KEY` с правилами `ON DELETE CASCADE` и `SET NULL`), ограничениями `NOT NULL` и `DEFAULT`, а также представлениями (`VIEW`).
- **Модуль прямого подключения (`db/database.py`)**: функция `get_connection()` для создания низкоуровневого соединения через драйвер `psycopg` с фабрикой строк `row_factory=dict_row`, что обеспечивает доступ к столбцам по именам (`contact['name']` в Python и `{{ contact.name }}` в шаблонах).
- **Скрипт импорта данных (`db/import_json.py`)**: перенос данных из `data/users.json`, `data/groups.json` и `data/contacts.json` в реляционную базу с помощью метода `executemany()`, параметров `%s` и управления транзакциями (`commit()`, `rollback()`).
- **Файл SQL-запросов (`sql/queries.sql`)**: 13 документированных запросов предметной области, охватывающих:
  - выборку списков с сортировкой (`SELECT ... ORDER BY`);
  - пагинацию (`LIMIT`, `OFFSET`);
  - фильтрацию (`WHERE` с `ILIKE`, `BETWEEN`, `IS NULL`, `AND`, `OR`);
  - объединения таблиц (`INNER JOIN` и `LEFT JOIN`);
  - агрегатные функции (`COUNT`, `SUM`, `MIN`, `MAX`);
  - группировку (`GROUP BY`) и фильтрацию сформированных групп (`HAVING COUNT > 1`);
  - вложенные подзапросы (`NOT IN` для поиска пустых групп).
- **Django-представления на чистом SQL**:
  - `/contacts/statistics/` (`contact_statistics_sql`) — дашборд аналитики и группировок (`LEFT JOIN`, `GROUP BY`, `COUNT`, `HAVING`);
  - `/contacts/by-date/` (`contact_search_date_sql`) — форма параметризованного поиска контактов по дате рождения через `%s` без конкатенации строк;
  - `/contacts/sql-list/` (`contact_sql_list`) — каталог контактов с объединением данных из трёх таблиц через `JOIN`.
- **Навигация**: пункты «Статистика» и «SQL-Каталог» интегрированы в общую навигацию проекта (`templates/includes/navigation.html`).

## 13. Текущее состояние проекта
На этапе Практической работы №7 проект содержит:
- функционирующую реляционную базу данных PostgreSQL 16 в Docker;
- чистый SQL-слой в каталогах `db/` и `sql/`;
- скрипт миграции из JSON в БД (`python -m db.import_json`);
- 13 отлаженных SQL-запросов в `sql/queries.sql`;
- веб-страницы на чистом SQL с защитой от SQL-инъекций и фабрикой строк `dict_row`;
- полную обратную совместимость с функционалом ПР1–ПР6;
- успешное прохождение всех 32 тестов (`pytest -v`).

## 14. Дальнейшее развитие
Следующие этапы развития проекта предполагают углубление взаимодействия с Django ORM (ПР8–ПР10), разработку REST API (Django REST Framework), экспорт базы контактов (CSV/vCard) и систему напоминаний о днях рождения.
