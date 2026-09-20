from datetime import date, datetime


def input_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите корректное число.")


def input_date(prompt: str) -> date:
    while True:
        raw = input(prompt).strip()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Ошибка: используйте формат даты ГГГГ-ММ-ДД.")


def input_bool(prompt: str) -> bool:
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("да", "yes", "y", "1"):
            return True
        if raw in ("нет", "no", "n", "0"):
            return False
        print("Ошибка: введите 'да' или 'нет'.")