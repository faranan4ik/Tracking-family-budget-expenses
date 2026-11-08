
from datetime import date, datetime

from database import prepare_database
from models import Category, Expense
from services.user_service import UserService
from services.category_service import CategoryService
from services.expense_service import ExpenseService
from services.auth_service import AuthService
from exceptions import ServiceError


# Подготовка базы данных
prepare_database()

# Создание объектов сервисов
user_service = UserService()
category_service = CategoryService()
expense_service = ExpenseService()
auth_service = AuthService()


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

# Ввод целого числа
def input_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("\nОшибка: необходимо ввести целое число.")


# Ввод положительной суммы
def input_amount(message):
    while True:
        try:
            amount = float(input(message).replace(",", "."))

            if amount <= 0:
                print("\nОшибка: сумма должна быть больше нуля.")
                continue

            return amount

        except ValueError:
            print("\nОшибка: необходимо ввести число.")


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
            print("\nОшибка: неверная дата. Используйте формат ГГГГ-ММ-ДД.")


# Проверка принадлежности расхода пользователю
def check_expense_owner(expense, current_user):
    if expense.user_id != current_user.user_id:
        raise ServiceError("\nОшибка: У вас нет доступа к этому расходу.")


# ==========================================
# РЕГИСТРАЦИЯ И АВТОРИЗАЦИЯ
# ==========================================

# Создание первого администратора
def create_initial_admin():
    print("\n=================================")
    print("Первоначальная настройка системы")
    print("=================================\n")
    print("Пользователи отсутствуют.")
    print("Необходимо создать администратора.\n")

    while True:
        try:
            username = input("Придумайте логин: ").strip()
            password = input("Придумайте пароль: ")
            password_repeat = input("Повторите пароль: ")

            if password != password_repeat:
                print("\nОшибка: пароли не совпадают.")
                continue

            last_name = input("Фамилия: ").strip()
            first_name = input("Имя: ").strip()
            middle_name = input("Отчество: ").strip()
            family_role = input("Роль в семье: ").strip()

            user = auth_service.create_initial_admin(
                username=username,
                password=password,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                family_role=family_role
            )

            print("\nАдминистратор успешно создан.")
            print(f"Логин: {user.username}")
            print("Теперь войдите в систему.")

            break

        except ServiceError as error:
            print(f"\nОшибка: {error}")


# Регистрация обычного пользователя
def register_user():
    print("\n===============================")
    print("Регистрация нового пользователя")
    print("===============================\n")

    username = input("Логин: ").strip()
    password = input("Пароль: ")
    password_repeat = input("Повторите пароль: ")

    if password != password_repeat:
        raise ServiceError("\nОшибка: пароли не совпадают.")

    last_name = input("Фамилия: ").strip()
    first_name = input("Имя: ").strip()
    middle_name = input("Отчество: ").strip()
    family_role = input("Роль в семье: ").strip()

    user = auth_service.register(
        username=username,
        password=password,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        family_role=family_role
    )

    print("\nПользователь успешно зарегистрирован.\n")
    print(f"ID: {user.user_id}")
    print(f"Логин: {user.username}")
    print(f"ФИО: {user.last_name} {user.first_name} {user.middle_name}")
    print("Системная роль: user")


# Авторизация
def login():
    print("\n===========")
    print("Авторизация")
    print("===========\n")

    username = input("Логин: ").strip()
    password = input("Пароль: ")

    user = auth_service.authenticate(username, password)

    if user is None:
        print("\nОшибка: неверный логин или пароль.")
        return None

    print(
        f"\nДобро пожаловать, "
        f"{user.first_name} {user.middle_name}!"
    )

    return user


# ==========================================
# ПОЛЬЗОВАТЕЛИ
# ==========================================

# Вывод списка пользователей
def show_users():
    users = user_service.get_all_users()

    if not users:
        print("\nОшибка: Пользователи отсутствуют.")
        return
    print("\n====================")
    print("Список пользователей")
    print("====================\n")

    for user in users:
        print(
            f"\nID: {user.user_id}\n"
            f"ФИО: {user.last_name} {user.first_name} {user.middle_name}\n"
            f"Семейная роль: {user.family_role}\n"
            f"Логин: {user.username}\n"
            f"Системная роль: {user.role}"
        )


# Меню пользователей
def user_menu():
    while True:
        print("""
=================================
          Пользователи
=================================
1. Просмотреть пользователей
2. Зарегистрировать пользователя

0. Назад
=================================
        """)

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                show_users()

            elif choice == "2":
                register_user()

            elif choice == "0":
                break

            else:
                print("\nОшибка: Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}")


# ==========================================
# РАСХОДЫ
# ==========================================

# Вывод списка расходов
def show_expenses(expenses=None):
    if expenses is None:
        expenses = expense_service.get_all_expenses()

    if not expenses:
        print("\nОшибка: Расходы отсутствуют.")
        return

    print("\n===============")
    print("Список расходов")
    print("===============\n")

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


# Получение доступных пользователю расходов
def get_accessible_expense(expense_id, current_user):
    expense = expense_service.get_expense(expense_id)

    if current_user.role != "admin":
        check_expense_owner(expense, current_user)

    return expense


# Добавление расхода
def add_expense(current_user):
    print("\n==================")
    print("Добавление расхода")
    print("==================\n")

    if current_user.role == "admin":
        show_users()
        user_id = input_int("\nВведите ID пользователя: ")
    else:
        user_id = current_user.user_id

    show_categories()
    category_id = input_int("\nВведите ID категории: ")

    amount = input_amount("Введите сумму расхода: ")

    expense_date = input_date(
        "Введите дату (ГГГГ-ММ-ДД) или Enter для текущей даты: "
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
def edit_expense(current_user):
    print("\n==================")
    print("Изменение расхода")
    print("==================\n")

    if current_user.role == "admin":
        show_expenses()
    else:
        show_expenses(
            expense_service.get_user_expenses(current_user.user_id)
        )

    expense_id = input_int("\nВведите ID расхода: ")
    expense = get_accessible_expense(expense_id, current_user)

    print("\nВведите новые данные.")
    print("Для сохранения прежнего значения нажмите Enter.")

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

    # Изменение пользователя доступно только администратору
    if current_user.role == "admin":
        user_input = input(
            f"Новый ID пользователя [{expense.user_id}]: "
        ).strip()

        user_id = int(user_input) if user_input else expense.user_id
    else:
        user_id = current_user.user_id

    # Изменение категории
    show_categories()

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
def delete_expense(current_user):
    print("\n=================")
    print("Удаление расхода")
    print("=================\n")

    if current_user.role == "admin":
        show_expenses()
    else:
        show_expenses(
            expense_service.get_user_expenses(current_user.user_id)
        )

    expense_id = input_int("\nВведите ID расхода: ")

    get_accessible_expense(expense_id, current_user)

    confirmation = input(
        "Вы действительно хотите удалить расход? (да/нет): "
    ).strip().lower()

    if confirmation == "да":
        expense_service.delete_expense(expense_id)
        print("Расход успешно удалён.")
    else:
        print("Удаление отменено.")


# Меню расходов
def expense_menu(current_user):
    while True:
        print("""
=======================
        Расходы
=======================
1. Просмотреть расходы
2. Добавить расход
3. Изменить расход
4. Удалить расход""")

        if current_user.role == "admin":
            print("""5. Показать расходы пользователя
6. Показать расходы по категории

0. Выход
=======================
""")


        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                if current_user.role == "admin":
                    show_expenses()
                else:
                    expenses = expense_service.get_user_expenses(
                        current_user.user_id
                    )
                    show_expenses(expenses)

            elif choice == "2":
                add_expense(current_user)

            elif choice == "3":
                edit_expense(current_user)

            elif choice == "4":
                delete_expense(current_user)

            elif choice == "5" and current_user.role == "admin":
                show_users()
                user_id = input_int("\nВведите ID пользователя: ")
                expenses = expense_service.get_user_expenses(user_id)
                show_expenses(expenses)

            elif choice == "6" and current_user.role == "admin":
                show_categories()
                category_id = input_int("\nВведите ID категории: ")
                expenses = expense_service.get_category_expenses(category_id)
                show_expenses(expenses)

            elif choice == "0":
                break

            else:
                print("\nОшибка: Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}\n")


# ==========================================
# КАТЕГОРИИ
# ==========================================

# Вывод списка категорий
def show_categories():
    categories = category_service.get_all_categories()

    if not categories:
        print("\nОшибка: Категории отсутствуют.")
        return
    print("\n================")
    print("Список категорий")
    print("================\n")


    for category in categories:
        print(
            f"ID: {category.category_id} | "
            f"{category.category_name} | "
            f"{category.description or 'Описание отсутствует'}"
        )


# Добавление категории
def add_category():
    print("\n====================")
    print("Добавление категории") 
    print("====================\n")

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
    print("\n===================")
    print("Изменение категории")
    print("===================\n")

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
    print("\n==================")
    print("Удаление категории")
    print("==================\n")

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
=========================
        Категории
=========================
1. Просмотреть категории
2. Добавить категорию
3. Изменить категорию
4. Удалить категорию

0. Назад
=========================
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
                print("\nОшибка: Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}")


# ==========================================
# МЕНЮ АДМИНИСТРАТОРА
# ==========================================

def admin_menu(current_user):
    while True:
        print(f"""
=============================
     Меню администратора
=============================
ID: {current_user.user_id}
Пользователь: {current_user.username}
ФИО: {current_user.last_name} {current_user.first_name} {current_user.middle_name}
-----------------------------
1. Управление расходами
2. Управление категориями
3. Управление пользователями

0. Выйти из аккаунта
=============================
            """)

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                expense_menu(current_user)

            elif choice == "2":
                category_menu()

            elif choice == "3":
                user_menu()

            elif choice == "0":
                print("\nВыход из аккаунта.")
                break

            else:
                print("\nОшибка: Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}\n")


# ==========================================
# МЕНЮ ОБЫЧНОГО ПОЛЬЗОВАТЕЛЯ
# ==========================================

def show_project_description():
    print("\n"+"="*56)
    print("          Учёт расходов семейного бюджета")
    print("="*56)

    print("""
Программа предназначена для ведения и анализа расходов семейного бюджета.

Основные возможности программы:

1. Регистрация новых пользователей.
2. Авторизация пользователей с проверкой логина и пароля.
3. Разграничение прав доступа администратора и обычного пользователя.
4. Добавление, просмотр, редактирование и удаление расходов.
5. Использование заранее подготовленных категорий расходов.
6. Управление категориями расходов.
7. Просмотр расходов по пользователям и категориям.

Для хранения информации используется база данных SQLite.

В системе предусмотрены две роли:
- Администратор — управление пользователями, категориями и расходами.
- Пользователь — управление собственными расходами.

Цель проекта — упростить учёт семейных расходов,
обеспечить хранение информации и помочь контролировать бюджет.
""")
    print("="*56)
  
    input("\nНажмите Enter, чтобы вернуться в главное меню")

def regular_user_menu(current_user):
    while True:
        print(f"""
===============================
       Меню пользователя
===============================
ID: {current_user.user_id}
Пользователь: {current_user.username}
ФИО: {current_user.last_name} {current_user.first_name} {current_user.middle_name}
--------------------------------
1. Управление своими расходами

0. Выйти из аккаунта
===============================
        """)

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                expense_menu(current_user)

            elif choice == "0":
                print("\nВыход из аккаунта.")
                break

            else:
                print("\nОшибка: Неизвестная команда.")

        except (ServiceError, ValueError) as error:
            print(f"\nОшибка: {error}")


# ==========================================
# ГЛАВНОЕ МЕНЮ
# ==========================================

def main_menu():

    # Если пользователей нет, создаём первого администратора
    if not user_service.get_all_users():
        create_initial_admin()

    while True:
        print("""
=======================================
    Учёт расходов семейного бюджета
=======================================
             Главное меню
---------------------------------------
1. Войти в систему
2. Описание проекта

0. Выход
=======================================
            """)

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            try:
                current_user = login()

                if current_user is None:
                    continue

                if current_user.role == "admin":
                    admin_menu(current_user)

                elif current_user.role == "user":
                    regular_user_menu(current_user)

                else:
                    print("\nОшибка: Неизвестная системная роль пользователя.")

            except (ServiceError, ValueError) as error:
                print(f"\nОшибка: {error}")

        elif choice == "2":
            show_project_description()

        elif choice == "0":
            print("\nЗавершение работы программы.")
            break

        else:
            print("\nОшибка: Неизвестная команда.")


# ==========================================
# ЗАПУСК ПРОГРАММЫ
# ==========================================

if __name__ == "__main__":
    main_menu()