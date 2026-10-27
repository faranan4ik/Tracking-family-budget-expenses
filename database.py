
import sqlite3
from pathlib import Path

DB_NAME = "family_budget.db"

# Создание базы данных
connection = sqlite3.connect(DB_NAME)
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Создание таблиц
cursor.executescript("""
DROP TABLE IF EXISTS Expenses;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    family_role TEXT NOT NULL
);

CREATE TABLE Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    family_role TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    expense_date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);
""")

# 28 категорий расходов
categories = [
    ("Продукты", "Продукты питания и напитки"),
    ("Кафе и рестораны", "Кафе, рестораны и готовая еда"),
    ("Жильё и аренда", "Аренда и расходы на жильё"),
    ("Коммунальные услуги", "Вода, электричество и отопление"),
    ("Телефон и интернет", "Мобильная связь и интернет"),
    ("Транспорт", "Общественный транспорт и такси"),
    ("Автомобиль", "Топливо, ремонт и обслуживание"),
    ("Здоровье", "Лекарства и медицинские услуги"),
    ("Одежда", "Одежда и обувь"),
    ("Бытовая химия", "Моющие и чистящие средства"),
    ("Товары для дома", "Посуда и другие товары для дома"),
    ("Техника и электроника", "Бытовая техника и электроника"),
    ("Образование", "Обучение и учебные материалы"),
    ("Дети", "Игрушки и товары для детей"),
    ("Развлечения", "Кино и другие развлечения"),
    ("Подписки", "Платные цифровые сервисы"),
    ("Спорт и фитнес", "Спортивные секции и тренажёрный зал"),
    ("Красота", "Косметика и услуги по уходу"),
    ("Путешествия", "Поездки и проживание"),
    ("Домашние животные", "Корм и ветеринарные услуги"),
    ("Подарки", "Подарки родственникам и друзьям"),
    ("Налоги и сборы", "Налоги и государственные пошлины"),
    ("Кредиты", "Платежи по кредитам и займам"),
    ("Страхование", "Страховые полисы"),
    ("Сбережения и инвестиции", "Накопления и инвестиции"),
    ("Благотворительность", "Пожертвования и помощь"),
    ("Непредвиденные расходы", "Незапланированные расходы"),
    ("Прочее", "Остальные расходы")
]

cursor.executemany("""
    INSERT INTO Categories (category_name, description)
    VALUES (?, ?)
""", categories)

# Три члена семьи
users = [
    ("father", "demo_hash_replace_me_1",
     "Иванов Иван Иванович", "Отец"),
    ("mother", "demo_hash_replace_me_2",
     "ЫВАыва аывавы аываыв", "Мать"),
    ("child", "demo_hash_replace_me_3",
     "Булаткин Егор Николаевич", "Ребёнок")
]

cursor.executemany("""
    INSERT INTO Users (
        username, password_hash, full_name, family_role
    )
    VALUES (?, ?, ?, ?)
""", users)

# Получение идентификаторов пользователей и категорий
user_ids = {
    username: (user_id, full_name, family_role)
    for user_id, username, full_name, family_role
    in cursor.execute("""
        SELECT user_id, username, full_name, family_role
        FROM Users
    """).fetchall()
}

category_ids = dict(cursor.execute("""
    SELECT category_name, category_id
    FROM Categories
""").fetchall())

# Примеры расходов.
# Суммы указаны в рублях, включая копейки.
expense_examples = [
    ("father", "Продукты", 2450.50,
     "2026-10-20", "Покупка продуктов на неделю"),

    ("mother", "Коммунальные услуги", 3850.00,
     "2026-10-20", "Оплата коммунальных услуг"),

    ("child", "Образование", 650.00,
     "2026-10-21", "Покупка учебных материалов"),
]

expenses = []

for username, category_name, amount, date, description in expense_examples:
    user_id, full_name, family_role = user_ids[username]
    category_id = category_ids[category_name]

    expenses.append((
        user_id,
        category_id,
        full_name,
        family_role,
        amount,
        date,
        description
    ))

cursor.executemany("""
    INSERT INTO Expenses (
        user_id,
        category_id,
        full_name,
        family_role,
        amount,
        expense_date,
        description
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", expenses)

connection.commit()

# Вывод результатов создания базы данных
print("База данных успешно создана!")
print("Файл:", Path(DB_NAME).resolve())

for table in ("Users", "Categories", "Expenses"):
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]
    print(f"Таблица {table}: {count} записей")

total = cursor.execute("""
    SELECT ROUND(SUM(amount), 2)
    FROM Expenses
""").fetchone()[0]

print(f"Общая сумма расходов: {total:.2f} руб.")
cursor.execute("SELECT * FROM Expenses")
print("Расходы:")
for row in cursor.fetchall():
    print(row)
connection.close()
