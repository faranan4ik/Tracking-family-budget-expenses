
import sqlite3

from models import Category
from repositories import CategoryRepository
from exceptions import ServiceError


class CategoryService:

    def __init__(self):
        self.repository = CategoryRepository()

    # Проверка данных категории
    def validate_category(self, category: Category):
        if not category.category_name.strip():
            raise ServiceError("Название категории не может быть пустым.")

        if category.description is not None:
            category.description = category.description.strip()

    # Добавление категории
    def add_category(self, category: Category) -> Category:
        self.validate_category(category)

        category.category_name = category.category_name.strip()

        if self.repository.get_by_name(category.category_name):
            raise ServiceError("Такая категория уже существует.")

        try:
            return self.repository.add(category)
        except sqlite3.IntegrityError as error:
            raise ServiceError("Категория с таким названием уже существует.") from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при добавлении категории.") from error

    # Получение категории по ID
    def get_category(self, category_id: int):
        if category_id <= 0:
            raise ServiceError("ID категории должен быть положительным.")

        category = self.repository.get_by_id(category_id)

        if category is None:
            raise ServiceError("Категория не найдена.")

        return category

    # Получение всех категорий
    def get_all_categories(self):
        return self.repository.get_all()

    # Изменение категории
    def update_category(self, category: Category):
        if category.category_id is None:
            raise ServiceError("Не указан ID категории.")

        self.get_category(category.category_id)
        self.validate_category(category)

        category.category_name = category.category_name.strip()

        existing_category = self.repository.get_by_name(category.category_name)

        if (
            existing_category
            and existing_category.category_id != category.category_id
        ):
            raise ServiceError("Категория с таким названием уже существует.")

        try:
            if not self.repository.update(category):
                raise ServiceError("Не удалось изменить категорию.")
        except sqlite3.IntegrityError as error:
            raise ServiceError("Нарушено ограничение базы данных.") from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при изменении категории.") from error

        return category

    # Удаление категории
    def delete_category(self, category_id: int):
        self.get_category(category_id)

        try:
            if not self.repository.delete(category_id):
                raise ServiceError("Не удалось удалить категорию.")
        except sqlite3.IntegrityError as error:
            raise ServiceError(
                "Нельзя удалить категорию, к которой относятся расходы."
            ) from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при удалении категории.") from error

        return True
