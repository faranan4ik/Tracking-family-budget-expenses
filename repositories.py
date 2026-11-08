
from database import get_connection
from models import User, Category, Expense


class UserRepository:

    # Добавление пользователя
    def add(self, user: User) -> User:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO Users (
                    username, password_hash, last_name,
                    first_name, middle_name, family_role, role
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.username,
                    user.password_hash,
                    user.last_name,
                    user.first_name,
                    user.middle_name,
                    user.family_role,
                    user.role
                )
            )
            user.user_id = cursor.lastrowid
        return user

    # Получение пользователя по ID
    def get_by_id(self, user_id: int):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM Users WHERE user_id = ?",
                (user_id,)
            ).fetchone()

        if row is None:
            return None

        return User(**dict(row))

    # Получение пользователя по логину
    def get_by_username(self, username: str):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM Users WHERE username = ?",
                (username,)
            ).fetchone()

        if row is None:
            return None

        return User(**dict(row))

    # Получение всех пользователей
    def get_all(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM Users ORDER BY user_id"
            ).fetchall()

        return [User(**dict(row)) for row in rows]

    # Изменение данных пользователя
    def update(self, user: User) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE Users
                SET username = ?,
                    password_hash = ?,
                    last_name = ?,
                    first_name = ?,
                    middle_name = ?,
                    family_role = ?,
                    role = ?
                WHERE user_id = ?
                """,
                (
                    user.username,
                    user.password_hash,
                    user.last_name,
                    user.first_name,
                    user.middle_name,
                    user.family_role,
                    user.role,
                    user.user_id
                )
            )

        return cursor.rowcount > 0

    # Удаление пользователя
    def delete(self, user_id: int) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM Users WHERE user_id = ?",
                (user_id,)
            )

        return cursor.rowcount > 0

class CategoryRepository:

    # Добавление категории
    def add(self, category: Category) -> Category:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO Categories (category_name, description)
                VALUES (?, ?)
                """,
                (category.category_name, category.description)
            )
            category.category_id = cursor.lastrowid

        return category

    # Получение категории по ID
    def get_by_id(self, category_id: int):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM Categories WHERE category_id = ?",
                (category_id,)
            ).fetchone()

        if row is None:
            return None

        return Category(**dict(row))

    # Получение категории по названию
    def get_by_name(self, category_name: str):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM Categories WHERE category_name = ?",
                (category_name,)
            ).fetchone()

        if row is None:
            return None

        return Category(**dict(row))

    # Получение всех категорий
    def get_all(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM Categories ORDER BY category_name"
            ).fetchall()

        return [Category(**dict(row)) for row in rows]

    # Изменение категории
    def update(self, category: Category) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE Categories
                SET category_name = ?,
                    description = ?
                WHERE category_id = ?
                """,
                (
                    category.category_name,
                    category.description,
                    category.category_id
                )
            )

        return cursor.rowcount > 0

    # Удаление категории
    def delete(self, category_id: int) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM Categories WHERE category_id = ?",
                (category_id,)
            )

        return cursor.rowcount > 0

class ExpenseRepository:

    # Добавление расхода
    def add(self, expense: Expense) -> Expense:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO Expenses (
                    user_id, category_id, amount, expense_date
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    expense.user_id,
                    expense.category_id,
                    expense.amount,
                    expense.expense_date
                )
            )
            expense.expense_id = cursor.lastrowid

        return expense

    # Получение расхода по ID
    def get_by_id(self, expense_id: int):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM Expenses WHERE expense_id = ?",
                (expense_id,)
            ).fetchone()

        if row is None:
            return None

        return Expense(**dict(row))

    # Получение всех расходов
    def get_all(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM Expenses ORDER BY expense_date DESC"
            ).fetchall()

        return [Expense(**dict(row)) for row in rows]

    # Получение расходов конкретного пользователя
    def get_by_user(self, user_id: int):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM Expenses
                WHERE user_id = ?
                ORDER BY expense_date DESC
                """,
                (user_id,)
            ).fetchall()

        return [Expense(**dict(row)) for row in rows]

    # Получение расходов определённой категории
    def get_by_category(self, category_id: int):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM Expenses
                WHERE category_id = ?
                ORDER BY expense_date DESC
                """,
                (category_id,)
            ).fetchall()

        return [Expense(**dict(row)) for row in rows]

    # Изменение расхода
    def update(self, expense: Expense) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE Expenses
                SET user_id = ?,
                    category_id = ?,
                    amount = ?,
                    expense_date = ?
                WHERE expense_id = ?
                """,
                (
                    expense.user_id,
                    expense.category_id,
                    expense.amount,
                    expense.expense_date,
                    expense.expense_id
                )
            )

        return cursor.rowcount > 0

    # Удаление расхода
    def delete(self, expense_id: int) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM Expenses WHERE expense_id = ?",
                (expense_id,)
            )

        return cursor.rowcount > 0
