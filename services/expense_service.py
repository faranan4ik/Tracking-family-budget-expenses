
import sqlite3
from datetime import date
from math import isfinite

from models import Expense
from repositories import ExpenseRepository
from services.user_service import UserService
from services.category_service import CategoryService
from exceptions import ServiceError


class ExpenseService:

    def __init__(self):
        self.repository = ExpenseRepository()
        self.user_service = UserService()
        self.category_service = CategoryService()

    # Проверка данных расхода
    def validate_expense(self, expense: Expense):
        if not isinstance(expense.amount, (int, float)):
            raise ServiceError("Сумма должна быть числом.")

        if not isfinite(expense.amount) or expense.amount <= 0:
            raise ServiceError("Сумма расхода должна быть положительной.")

        if expense.user_id <= 0:
            raise ServiceError("Некорректный ID пользователя.")

        if expense.category_id <= 0:
            raise ServiceError("Некорректный ID категории.")

        try:
            date.fromisoformat(expense.expense_date)
        except (ValueError, TypeError):
            raise ServiceError(
                "Неверная дата. Используйте формат ГГГГ-ММ-ДД."
            )

    # Добавление расхода
    def add_expense(self, expense: Expense) -> Expense:
        self.validate_expense(expense)

        # Проверка существования пользователя
        self.user_service.get_user(expense.user_id)

        # Проверка существования категории
        self.category_service.get_category(expense.category_id)

        try:
            return self.repository.add(expense)
        except sqlite3.IntegrityError as error:
            raise ServiceError(
                "Не удалось добавить расход: нарушена связь с пользователем или категорией."
            ) from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при добавлении расхода.") from error

    # Получение расхода по ID
    def get_expense(self, expense_id: int):
        if expense_id <= 0:
            raise ServiceError("ID расхода должен быть положительным.")

        expense = self.repository.get_by_id(expense_id)

        if expense is None:
            raise ServiceError("Расход не найден.")

        return expense

    # Получение всех расходов
    def get_all_expenses(self):
        return self.repository.get_all()

    # Получение расходов пользователя
    def get_user_expenses(self, user_id: int):
        self.user_service.get_user(user_id)
        return self.repository.get_by_user(user_id)

    # Получение расходов по категории
    def get_category_expenses(self, category_id: int):
        self.category_service.get_category(category_id)
        return self.repository.get_by_category(category_id)

    # Изменение расхода
    def update_expense(self, expense: Expense):
        if expense.expense_id is None:
            raise ServiceError("Не указан ID расхода.")

        self.get_expense(expense.expense_id)
        self.validate_expense(expense)

        self.user_service.get_user(expense.user_id)
        self.category_service.get_category(expense.category_id)

        try:
            if not self.repository.update(expense):
                raise ServiceError("Не удалось изменить расход.")
        except sqlite3.IntegrityError as error:
            raise ServiceError("Нарушена связь с пользователем или категорией.") from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при изменении расхода.") from error

        return expense

    # Удаление расхода
    def delete_expense(self, expense_id: int):
        self.get_expense(expense_id)

        try:
            if not self.repository.delete(expense_id):
                raise ServiceError("Не удалось удалить расход.")
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при удалении расхода.") from error

        return True
