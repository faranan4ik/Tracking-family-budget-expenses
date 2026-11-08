
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: Optional[int]
    username: str
    password_hash: str
    last_name: str
    first_name: str
    middle_name: str
    family_role: str
    role: str = "user"


@dataclass
class Category:
    category_id: Optional[int]
    category_name: str
    description: Optional[str] = None


@dataclass
class Expense:
    expense_id: Optional[int]
    user_id: int
    category_id: int
    amount: float
    expense_date: str

if __name__ == "__main__":
    user = User(
        user_id=1,
        username="ivan",
        password_hash="example_hash",
        last_name="Иванов",
        first_name="Иван",
        middle_name="Иванович",
        family_role="Отец",
        role="admin"
    )

    category = Category(
        category_id=1,
        category_name="Продукты",
        description="Покупка продуктов питания"
    )

    expense = Expense(
        expense_id=1,
        user_id=1,
        category_id=1,
        amount=1500.0,
        expense_date="2026-11-08"
    )

    print(user)
    print(category)
    print(expense)
