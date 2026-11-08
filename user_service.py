
import sqlite3

from models import User
from repositories import UserRepository
from exceptions import ServiceError


class UserService:

    def __init__(self):
        self.repository = UserRepository()

    # Проверка данных пользователя
    def validate_user(self, user: User):
        if not user.username.strip():
            raise ServiceError("Логин не может быть пустым.")

        if not user.password_hash:
            raise ServiceError("Не указан хеш пароля.")

        if not user.last_name.strip():
            raise ServiceError("Не указана фамилия.")

        if not user.first_name.strip():
            raise ServiceError("Не указано имя.")

        if not user.middle_name.strip():
            raise ServiceError("Не указано отчество.")

        if not user.family_role.strip():
            raise ServiceError("Не указана роль в семье.")

        if user.role not in ("admin", "user"):
            raise ServiceError("Недопустимая системная роль.")

    # Добавление пользователя
    def add_user(self, user: User) -> User:
        self.validate_user(user)

        if self.repository.get_by_username(user.username.strip()):
            raise ServiceError("Пользователь с таким логином уже существует.")

        user.username = user.username.strip()

        try:
            return self.repository.add(user)
        except sqlite3.IntegrityError as error:
            raise ServiceError(
                "Не удалось добавить пользователя: нарушено ограничение базы данных."
            ) from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при добавлении пользователя.") from error

    # Получение пользователя по ID
    def get_user(self, user_id: int):
        if user_id <= 0:
            raise ServiceError("ID пользователя должен быть положительным.")

        user = self.repository.get_by_id(user_id)

        if user is None:
            raise ServiceError("Пользователь не найден.")

        return user

    # Получение пользователя по логину
    def get_user_by_username(self, username: str):
        if not username.strip():
            raise ServiceError("Необходимо указать логин.")

        return self.repository.get_by_username(username.strip())

    # Получение всех пользователей
    def get_all_users(self):
        return self.repository.get_all()

    # Изменение пользователя
    def update_user(self, user: User):
        if user.user_id is None:
            raise ServiceError("Не указан ID пользователя.")

        self.get_user(user.user_id)
        self.validate_user(user)

        existing_user = self.repository.get_by_username(user.username.strip())

        if existing_user and existing_user.user_id != user.user_id:
            raise ServiceError("Этот логин уже занят.")

        user.username = user.username.strip()

        try:
            if not self.repository.update(user):
                raise ServiceError("Не удалось изменить пользователя.")
        except sqlite3.IntegrityError as error:
            raise ServiceError("Нарушено ограничение базы данных.") from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при изменении пользователя.") from error

        return user

    # Удаление пользователя
    def delete_user(self, user_id: int):
        self.get_user(user_id)

        try:
            if not self.repository.delete(user_id):
                raise ServiceError("Не удалось удалить пользователя.")
        except sqlite3.IntegrityError as error:
            raise ServiceError(
                "Нельзя удалить пользователя, у которого есть расходы."
            ) from error
        except sqlite3.Error as error:
            raise ServiceError("Ошибка базы данных при удалении пользователя.") from error

        return True
