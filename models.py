
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
