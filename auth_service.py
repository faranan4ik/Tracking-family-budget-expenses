
import hashlib
import hmac
import secrets

from models import User
from user_service import UserService
from exceptions import ServiceError


ITERATIONS = 600_000


class AuthService:

    def __init__(self):
        self.user_service = UserService()

    # Хеширование пароля
    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            ITERATIONS
        )

        return (
            f"pbkdf2_sha256${ITERATIONS}$"
            f"{salt.hex()}${password_hash.hex()}"
        )

    # Проверка пароля
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$")

            if algorithm != "pbkdf2_sha256":
                return False

            iterations = int(iterations)

            if not 100_000 <= iterations <= 2_000_000:
                return False

            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(hash_hex)

            actual_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations
            )

            return hmac.compare_digest(actual_hash, expected_hash)

        except (ValueError, TypeError, AttributeError):
            return False

    # Регистрация пользователя
    def register(
        self,
        username: str,
        password: str,
        last_name: str,
        first_name: str,
        middle_name: str,
        family_role: str
    ) -> User:

        if not password or len(password) < 8:
            raise ServiceError(
                "Пароль должен содержать не менее 8 символов."
            )

        password_hash = self.hash_password(password)

        user = User(
            user_id=None,
            username=username,
            password_hash=password_hash,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            family_role=family_role,
            role="user"
        )

        return self.user_service.add_user(user)

    # Авторизация пользователя
    def authenticate(self, username: str, password: str):

        if not username.strip() or not password:
            raise ServiceError("Введите логин и пароль.")

        user = self.user_service.get_user_by_username(username)

        if user is None:
            return None

        if not self.verify_password(password, user.password_hash):
            return None

        return user
