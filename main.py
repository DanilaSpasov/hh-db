from src.config import get_db_config
from src.database import (
    create_database,
    create_tables,
    save_data_to_database,
)
from src.db_manager import DBManager
from src.file_manager import load_hh_data


def print_vacancies(vacancies: list[tuple]) -> None:
    """Печатает вакансии в человекочитаемом виде."""
    if not vacancies:
        print("Вакансии не найдены.")
        return

    for company_name, vacancy_name, salary, url in vacancies:
        salary_text = f"{salary} руб." if salary is not None else "не указана"
        print(
            f"Компания: {company_name} | "
            f"Вакансия: {vacancy_name} | "
            f"Зарплата: {salary_text} | "
            f"Ссылка: {url}"
        )


def user_interaction(db_manager: DBManager) -> None:
    """Показывает меню и выводит выбранные пользователем данные."""
    menu = """
1. Показать компании и количество вакансий
2. Показать все вакансии
3. Показать среднюю зарплату
4. Показать вакансии с зарплатой выше средней
5. Найти вакансии по ключевому слову
6. Выйти
"""

    while True:
        print(menu)
        choice = input("Выберите пункт меню: ")

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            for company_name, vacancies_count in companies:
                print(f"{company_name}: {vacancies_count} вакансий")

        elif choice == "2":
            print_vacancies(db_manager.get_all_vacancies())

        elif choice == "3":
            average_salary = db_manager.get_avg_salary()
            if average_salary is None:
                print("Нет данных о зарплатах.")
            else:
                print(f"Средняя зарплата: {average_salary:.2f} руб.")

        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            print_vacancies(vacancies)

        elif choice == "5":
            keyword = input("Введите ключевое слово: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            print_vacancies(vacancies)

        elif choice == "6":
            print("Работа программы завершена.")
            break

        else:
            print("Неизвестный пункт. Выберите число от 1 до 6.")


def main() -> None:
    """Запускает основную логику программы."""
    db_config = get_db_config()
    data = load_hh_data("data/hh_vacancies.json")

    create_database(db_config)
    create_tables(db_config)
    save_data_to_database(data, db_config)

    db_manager = DBManager(db_config)
    user_interaction(db_manager)


if __name__ == "__main__":
    main()
