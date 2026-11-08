
from datetime import date

from database import prepare_database
from models import Category, Expense
from user_service import UserService
from category_service import CategoryService
from expense_service import ExpenseService
from exceptions import ServiceError
from datetime import date, datetime

# Подготовка базы данных
prepare_database()

# Создание объектов сервисов
user_service = UserService()
category_service = CategoryService()
expense_service = ExpenseService()


# Ввод целого числа
def input_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Ошибка: необходимо ввести целое число.")


# Ввод положительного числа
def input_amount(message):
    while True:
        try:
            amount = float(input(message).replace(",", "."))

            if amount <= 0:
                print("Сумма должна быть больше нуля.")
                continue

            return amount

        except ValueError:
            print("Ошибка: необходимо ввести число.")

# Ввод и проверка даты
def input_date(message):
    while True:
        expense_date = input(message).strip()

        if not expense_date:
            return ""

        try:
            parsed_date = datetime.strptime(
                expense_date, "%Y-%m-%d"
            )

            if parsed_date.strftime("%Y-%m-%d") != expense_date:
                raise ValueError

            return expense_date

        except ValueError:
            print("Ошибка: неверная дата. Используйте формат ГГГГ-ММ-ДД.")



# Вывод списка пользователей
def show_users():
    users = user_service.get_all_users()

    if not users:
        print("\nПользователи отсутствуют.")
        return

    print("\n--- СПИСОК ПОЛЬЗОВАТЕЛЕЙ ---")

    for user in users:
        print(
            f"ID: {user.user_id} | "
            f"{user.last_name} {user.first_name} {user.middle_name} | "
            f"Семейная роль: {user.family_role} | "
            f"Логин: {user.username}"
        )


# Вывод списка категорий
def show_categories():
    categories = category_service.get_all_categories()

    if not categories:
        print("\nКатегории отсутствуют.")
        return

    print("\n--- СПИСОК КАТЕГОРИЙ ---")

    for category in categories:
        print(
            f"ID: {category.category_id} | "
            f"{category.category_name} | "
            f"{category.description or 'Описание отсутствует'}"
        )


# Вывод списка расходов
def show_expenses(expenses=None):
    if expenses is None:
        expenses = expense_service.get_all_expenses()

    if not expenses:
        print("\nРасходы отсутствуют.")
        return

    print("\n--- СПИСОК РАСХОДОВ ---")

    for expense in expenses:
        user = user_service.get_user(expense.user_id)
        category = category_service.get_category(expense.category_id)

        full_name = (
            f"{user.last_name} {user.first_name} {user.middle_name}"
        )

        print(
            f"\nID расхода: {expense.expense_id}\n"
            f"Пользователь: {full_name}\n"
            f"Семейная роль: {user.family_role}\n"
            f"Категория: {category.category_name}\n"
            f"Сумма: {expense.amount:.2f} руб.\n"
            f"Дата: {expense.expense_date}"
        )


# Добавление расхода
def add_expense():
    print("\n--- ДОБАВЛЕНИЕ РАСХОДА ---")

    show_users()
    user_id = input_int("\nВведите ID пользователя: ")

    show_categories()
    category_id = input_int("\nВведите ID категории: ")

    amount = input_amount("Введите сумму расхода: ")

    expense_date = input_date(
    "Введите дату (ГГГГ-ММ-ДД) или нажмите Enter для текущей даты: "
    )

    if not expense_date:
        expense_date = date.today().isoformat()

    expense = Expense(
        expense_id=None,
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        expense_date=expense_date
    )

    expense_service.add_expense(expense)

    print("\nРасход успешно добавлен.")


# Изменение расхода

# Изменение расхода
def edit_expense():
    print("\n--- ИЗМЕНЕНИЕ РАСХОДА ---")

    show_expenses()

    expense_id = input_int("\nВведите ID расхода: ")
    expense = expense_service.get_expense(expense_id)

    print("\nВведите новые данные.")
    print("Если хотите оставить прежнее значение, нажмите Enter.")

    # Изменение суммы
    amount_input = input(
        f"Новая сумма [{expense.amount}]: "
    ).strip()

    if amount_input:
        try:
            amount = float(amount_input.replace(",", "."))
        except ValueError:
            raise ServiceError("Сумма должна быть числом.")
    else:
        amount = expense.amount

    if amount <= 0:
        raise ServiceError("Сумма расхода должна быть положительной.")

    # Изменение пользователя
    user_input = input(
        f"Новый ID пользователя [{expense.user_id}]: "
    ).strip()

    user_id = int(user_input) if user_input else expense.user_id

    # Изменение категории
    category_input = input(
        f"Новый ID категории [{expense.category_id}]: "
    ).strip()

    category_id = (
        int(category_input) if category_input else expense.category_id
    )

    # Изменение даты
    expense_date = input_date(
        f"Новая дата [{expense.expense_date}] "
        "(ГГГГ-ММ-ДД, Enter — оставить прежнюю): "
    )

    if not expense_date:
        expense_date = expense.expense_date

    updated_expense = Expense(
        expense_id=expense.expense_id,
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        expense_date=expense_date
    )

    expense_service.update_expense(updated_expense)

    print("\nРасход успешно изменён.")



# Удаление расхода
def delete_expense():
    print("\n--- УДАЛЕНИЕ РАСХОДА ---")

    show_expenses()

    expense_id = input_int("\nВведите ID расхода: ")

    expense_service.get_expense(expense_id)

    confirmation = input(
        "Вы действительно хотите удалить расход? (да/нет): "
    ).strip().lower()

    if confirmation == "да":
        expense_service.delete_expense(expense_id)
        print("Расход успешно удалён.")
    else:
        print("Удаление отменено.")


# Меню расходов
def expense_menu():
    while True:
        print("""
========== РАСХОДЫ ==========
1. Просмотреть все расходы
2. Добавить расход
3. Изменить расход
4. Удалить расход
5. Показать расходы пользователя
6. Показать расходы по категории
0. Назад
=============================
""")

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                show_expenses()

            elif choice == "2":
                add_expense()

            elif choice == "3":
                edit_expense()

            elif choice == "4":
                delete_expense()

            elif choice == "5":
                show_users()
                user_id = input_int("\nВведите ID пользователя: ")
                expenses = expense_service.get_user_expenses(user_id)
                show_expenses(expenses)

            elif choice == "6":
                show_categories()
                category_id = input_int("\nВведите ID категории: ")
                expenses = expense_service.get_category_expenses(category_id)
                show_expenses(expenses)

            elif choice == "0":
                break

            else:
                print("Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}")


# Добавление категории
def add_category():
    print("\n--- ДОБАВЛЕНИЕ КАТЕГОРИИ ---")

    name = input("Введите название категории: ").strip()
    description = input("Введите описание категории: ").strip()

    category = Category(
        category_id=None,
        category_name=name,
        description=description or None
    )

    category_service.add_category(category)

    print("\nКатегория успешно добавлена.")


# Изменение категории
def edit_category():
    print("\n--- ИЗМЕНЕНИЕ КАТЕГОРИИ ---")

    show_categories()

    category_id = input_int("\nВведите ID категории: ")
    category = category_service.get_category(category_id)

    name = input(
        f"Новое название [{category.category_name}]: "
    ).strip()

    description = input(
        f"Новое описание [{category.description or ''}]: "
    ).strip()

    updated_category = Category(
        category_id=category.category_id,
        category_name=name if name else category.category_name,
        description=description if description else category.description
    )

    category_service.update_category(updated_category)

    print("\nКатегория успешно изменена.")


# Удаление категории
def delete_category():
    print("\n--- УДАЛЕНИЕ КАТЕГОРИИ ---")

    show_categories()

    category_id = input_int("\nВведите ID категории: ")

    category_service.get_category(category_id)

    confirmation = input(
        "Вы действительно хотите удалить категорию? (да/нет): "
    ).strip().lower()

    if confirmation == "да":
        category_service.delete_category(category_id)
        print("Категория успешно удалена.")
    else:
        print("Удаление отменено.")


# Меню категорий
def category_menu():
    while True:
        print("""
========== КАТЕГОРИИ ==========
1. Просмотреть категории
2. Добавить категорию
3. Изменить категорию
4. Удалить категорию
0. Назад
===============================
""")

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                show_categories()

            elif choice == "2":
                add_category()

            elif choice == "3":
                edit_category()

            elif choice == "4":
                delete_category()

            elif choice == "0":
                break

            else:
                print("Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}")


# Главное меню
def main_menu():
    while True:
        print("""
====================================
       УЧЁТ РАСХОДОВ СЕМЕЙНОГО БЮДЖЕТА
====================================
1. Управление расходами
2. Управление категориями
3. Просмотр пользователей
0. Выход
====================================
""")

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                expense_menu()

            elif choice == "2":
                category_menu()

            elif choice == "3":
                show_users()

            elif choice == "0":
                print("\nЗавершение работы программы.")
                break

            else:
                print("\nНеизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}")


# Запуск программы
if __name__ == "__main__":
    main_menu()
