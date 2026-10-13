from django.test import TestCase
from django.urls import reverse
from pathlib import Path
import re
from db.database import get_connection, BASE_DIR


class SqlLayerTests(TestCase):
    """Тестирование прямого SQL-слоя (ПР7)."""

    def test_database_connection(self):
        """Проверка прямого подключения к базе данных через psycopg."""
        conn = get_connection()
        self.assertIsNotNone(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS num;")
            row = cur.fetchone()
            self.assertEqual(row["num"], 1)
        conn.close()

    def test_sql_queries_file(self):
        """Проверка наличия файла sql/queries.sql и выполнения всех запросов."""
        queries_path = BASE_DIR / "sql" / "queries.sql"
        self.assertTrue(queries_path.exists())
        with open(queries_path, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned_sql = re.sub(r"--.*", "", content)
        queries = [q.strip() for q in cleaned_sql.split(";") if q.strip()]
        self.assertGreaterEqual(len(queries), 10, "Должно быть разработано не менее 10 SQL-запросов")

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for q in queries:
                    cur.execute(q)
                    # Проверяем, что запрос выполняется без исключений
                    self.assertIsNotNone(cur.description)
        finally:
            conn.close()

    def test_statistics_view(self):
        """Проверка работы представления статистики на чистом SQL."""
        resp = self.client.get(reverse("contacts:statistics"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Статистика контактов и групп")
        self.assertIn("summary", resp.context)
        self.assertIn("group_stats", resp.context)
        self.assertIn("popular_groups", resp.context)

    def test_search_date_view(self):
        """Проверка параметризованного поиска контактов по дате рождения."""
        # 1. Запрос без параметров
        resp = self.client.get(reverse("contacts:search_date"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Поиск контактов по дате рождения")

        # 2. Параметризованный запрос
        resp_filtered = self.client.get(reverse("contacts:search_date"), {"date": "2006-12-31"})
        self.assertEqual(resp_filtered.status_code, 200)
        self.assertContains(resp_filtered, "Результаты выборки")

    def test_sql_list_view(self):
        """Проверка представления каталога с объединением таблиц (JOIN)."""
        resp = self.client.get(reverse("contacts:sql_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Каталог контактов (SQL JOIN)")
        self.assertIn("contacts", resp.context)
