from unittest.mock import Mock
from unittest.mock import patch

import main as app


def test_print_vacancies_formats_salary_and_missing_salary(capsys) -> None:
    """Проверяет вывод указанной и отсутствующей зарплаты вакансий."""
    app.print_vacancies(
        [
            ("First", "Developer", 100, "https://hh.ru/1"),
            ("Second", "Tester", None, "https://hh.ru/2"),
        ]
    )

    output = capsys.readouterr().out
    assert "Зарплата: 100 руб." in output
    assert "Зарплата: не указана" in output


def test_print_vacancies_reports_empty_result(capsys) -> None:
    """Проверяет сообщение при отсутствии найденных вакансий."""
    app.print_vacancies([])

    assert capsys.readouterr().out == "Вакансии не найдены.\n"


@patch(
    "builtins.input",
    side_effect=["1", "2", "3", "4", "5", "Python", "wrong", "6"],
)
def test_user_interaction_handles_all_menu_options(
    mock_input,
    capsys,
) -> None:
    """Проверяет обработку всех пунктов и ошибочного выбора меню."""
    manager = Mock()
    manager.get_companies_and_vacancies_count.return_value = [("Company", 2)]
    manager.get_all_vacancies.return_value = [
        ("Company", "Developer", 100, "https://hh.ru/1")
    ]
    manager.get_avg_salary.return_value = 125.5
    manager.get_vacancies_with_higher_salary.return_value = [
        ("Company", "Senior developer", 200, "https://hh.ru/2")
    ]
    manager.get_vacancies_with_keyword.return_value = [
        ("Company", "Python developer", None, "https://hh.ru/3")
    ]

    app.user_interaction(manager)

    output = capsys.readouterr().out
    assert "Company: 2 вакансий" in output
    assert "Средняя зарплата: 125.50 руб." in output
    assert "Senior developer" in output
    assert "Python developer" in output
    assert "Неизвестный пункт" in output
    assert "Работа программы завершена." in output
    manager.get_vacancies_with_keyword.assert_called_once_with("Python")


@patch("builtins.input", side_effect=["3", "6"])
def test_user_interaction_handles_missing_average(mock_input, capsys) -> None:
    """Проверяет сообщение при отсутствии данных о средней зарплате."""
    manager = Mock()
    manager.get_avg_salary.return_value = None

    app.user_interaction(manager)

    assert "Нет данных о зарплатах." in capsys.readouterr().out


@patch("main.user_interaction")
@patch("main.DBManager")
@patch("main.save_data_to_database")
@patch("main.create_tables")
@patch("main.create_database")
@patch("main.load_hh_data")
@patch("main.get_db_config")
def test_main_coordinates_application_startup(
    mock_get_db_config,
    mock_load_hh_data,
    mock_create_database,
    mock_create_tables,
    mock_save_data,
    mock_manager_class,
    mock_user_interaction,
) -> None:
    """Проверяет последовательность запуска основных компонентов."""
    config = {"dbname": "test_db"}
    data = [{"employer": {"id": "10"}, "vacancies": []}]
    manager = Mock()
    mock_get_db_config.return_value = config
    mock_load_hh_data.return_value = data
    mock_manager_class.return_value = manager

    app.main()

    mock_get_db_config.assert_called_once_with()
    mock_load_hh_data.assert_called_once_with("data/hh_vacancies.json")
    mock_create_database.assert_called_once_with(config)
    mock_create_tables.assert_called_once_with(config)
    mock_save_data.assert_called_once_with(data, config)
    mock_manager_class.assert_called_once_with(config)
    mock_user_interaction.assert_called_once_with(manager)
