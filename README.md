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

## 13. Практическая работа № 9: Модели Django, связи и операции с базой данных через ORM
На этапе ПР9 слой доступа к данным проекта переведён с прямых SQL-запросов и низкоуровневых соединений на **Django ORM** с соблюдением принципов архитектуры MTV (Model-Template-View):

### 1. Модели данных и связи
- **`Group` (`contacts/models.py`)** — категории для группировки контактов:
  - `name` (CharField, max_length=100) — название группы;
  - `description` (TextField, blank=True) — описание группы;
  - `owner` (ForeignKey к `User`, `on_delete=CASCADE`, `related_name="contact_groups"`) — владелец группы.
- **`Contact` (`contacts/models.py`)** — запись в адресной книге:
  - `name` (CharField, max_length=100) — имя;
  - `firstname` (CharField, max_length=100, blank=True) — фамилия;
  - `number` (BigIntegerField) — номер телефона;
  - `birthday` (DateField) — дата рождения;
  - `is_favorite` (BooleanField, default=False) — признак избранного;
  - `tags` (CharField, max_length=200, blank=True) — строковые теги через запятую;
  - `owner` (ForeignKey к `User`, `on_delete=CASCADE`, `related_name="contacts"`) — владелец записи;
  - `group` (ForeignKey к `Group`, `on_delete=SET_NULL`, null=True, blank=True, `related_name="contacts"`) — привязанная группа;
  - Методы модели: `toggle_favorite()`, `matches(query)`, свойства `tag_list`, `initials`, `formatted_phone`, `days_until_birthday`, `age`, `next_age`.

### 2. Управление структурой БД и миграции
Структура базы данных управляется миграциями Django:
```bash
python manage.py makemigrations contacts
python manage.py showmigrations
python manage.py migrate
```

### 3. Инспекция и безопасный перенос данных
- **`db/inspect_source_db.py`**: скрипт инспекции пользовательских таблиц, типов колонок, первичных ключей и количества записей.
- **`db/import_to_orm.py`**: скрипт синхронизации данных через ORM-метод `update_or_create()` в рамках атомарной транзакции `with transaction.atomic():`.

### 4. Реализованные ORM-выражения (соответствие Таблице 1 ПР9)
В проекте реализовано 16 различных ORM-выражений:
1. `Contact.objects.all()` — базовое получение всего набора объектов;
2. `get_object_or_404(Contact, pk=pk)` — получение отдельного объекта с автоматической генерацией 404;
3. `Contact.objects.filter(is_favorite=True)` — одиночная фильтрация;
4. `Contact.objects.filter(group_id=..., is_favorite=True)` — множественная фильтрация («И»);
5. `Contact.objects.filter(group__name__icontains=...)` — фильтрация по полю связанной модели;
6. `Contact.objects.exclude(tags="")` — исключение записей через `exclude()`;
7. `Contact.objects.filter(name__icontains=query)` — поиск по строковому полю без учета регистра;
8. `Contact.objects.filter(Q(name__icontains=q) | Q(firstname__icontains=q) | Q(number__icontains=q))` — комплексный поиск через `Q`-объекты;
9. `Contact.objects.order_by("name", "firstname")` — статическая сортировка по нескольким полям;
10. `Contact.objects.order_by(sort_fields.get(sort, "name"), "id")` — безопасная динамическая сортировка по белому списку полей;
11. `Contact.objects.select_related("group", "owner")` — жадная загрузка связанных сущностей для предотвращения проблемы N+1;
12. `group.contacts.all()` / `user.contacts.all()` — обратная связь по внешнему ключу (`related_name`);
13. `Contact.objects.aggregate(total=Count("id"), fav=Count("id", filter=Q(is_favorite=True)), oldest=Min("birthday"), youngest=Max("birthday"))` — расчет сводных агрегатных показателей;
14. `Group.objects.annotate(contacts_count=Count("contacts"))` — группировка и аннотирование (аналог LEFT JOIN + COUNT);
15. `Group.objects.annotate(contacts_count=Count("contacts")).filter(contacts_count__gt=1)` — фильтрация по аннотированному полю (аналог SQL HAVING);
16. `Paginator(contacts, 6)` & `paginator.get_page(page)` — постраничный вывод с тегом `{% querystring %}`, сохраняющим фильтры и сортировку.

### 5. Адаптированные представления
- `/contacts/` (`contact_list`) — многопараметрический поиск (`Q`), фильтрация по группе, динамическая сортировка и пагинация (`Paginator`);
- `/contacts/<id>/` (`contact_detail`) — оптимизированная выборка через `get_object_or_404` и `select_related`;
- `/contacts/statistics/` (`contact_statistics`) — дашборд на `aggregate()`, `annotate()`, `Count`, `Min`, `Max`;
- `/contacts/by-date/` (`contact_search_date`) — параметризованный поиск по дате рождения с валидацией `datetime.strptime`;
- `/contacts/sql-list/` (`contact_sql_list`) — каталог с `select_related("group", "owner")`.

Исходные файлы ПР7 (`sql/schema.sql`, `sql/queries.sql`, `db/database.py`) сохранены в репозитории как предыдущая реализация предметной области, однако представления полностью переведены на Django ORM.

## 14. Текущее состояние проекта
На этапе Практической работы №9 проект содержит:
- полнофункциональный слой доступа к данным на базе Django ORM;
- модели `Group` и `Contact` с настроенными внешними ключами и каскадным поведением;
- миграции Django в системе контроля версий;
- 16 отлаженных типов ORM-выражений (агрегаты, аннотации, фильтры, сортировка, пагинация);
- скрипты инспекции `db/inspect_source_db.py` и переноса `db/import_to_orm.py`;
- 45 юнит-тестов (100% passing) в `pytest -v`;
- полное соответствие чек-листам и 30 показателям оценивания ПР9.

## 15. Дальнейшее развитие
Следующие этапы развития проекта предполагают внедрение Django Forms для создания и валидации записей в веб-интерфейсе (ПР10), разработку REST API на базе Django REST Framework, экспорт базы контактов (CSV/vCard) и систему напоминаний о днях рождения.
