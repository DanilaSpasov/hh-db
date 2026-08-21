from unittest.mock import patch

import pytest

from src import database


@pytest.mark.parametrize(
    ("salary_data", "expected_salary"),
    [
        ({"from": 100, "to": 200}, 150),
        ({"from": 100, "to": None}, 100),
        ({"from": None, "to": 200}, 200),
        ({"from": None, "to": None}, None),
        (None, None),
    ],
)
def test_calculate_salary_handles_missing_bounds(
    salary_data: dict[str, int | None] | None,
    expected_salary: int | None,
) -> None:
    """Проверяет расчёт зарплаты при отсутствующих границах."""
    assert database.calculate_salary(salary_data) == expected_salary


@patch("src.database.psycopg2.connect")
def test_save_data_to_database_uses_calculated_salary(mock_connect) -> None:
    """Проверяет сохранение рассчитанной зарплаты в параметры запроса."""
    salaries = [
        {"from": 100, "to": 200},
        {"from": 100, "to": None},
        {"from": None, "to": 200},
        {"from": None, "to": None},
        None,
    ]
    vacancies = [
        {
            "id": str(index),
            "name": f"Vacancy {index}",
            "alternate_url": f"https://hh.ru/vacancy/{index}",
            "salary": salary,
        }
        for index, salary in enumerate(salaries, start=1)
    ]
    data = [
        {
            "employer": {
                "id": "10",
                "name": "Test company",
                "alternate_url": "https://hh.ru/employer/10",
            },
            "vacancies": vacancies,
        }
    ]

    database.save_data_to_database(data, {"dbname": "test_db"})

    connection = mock_connect.return_value
    cursor = connection.cursor.return_value.__enter__.return_value
    vacancy_params = [
        call.args[1]
        for call in cursor.execute.call_args_list
        if "INSERT INTO vacancies" in call.args[0]
    ]
    assert [params[3] for params in vacancy_params] == [
        150,
        100,
        200,
        None,
        None,
    ]
    connection.commit.assert_called_once_with()
    connection.close.assert_called_once_with()


@patch("src.database.psycopg2.connect")
def test_create_database_recreates_requested_database(mock_connect) -> None:
    """Проверяет пересоздание базы данных с указанным именем."""
    params = {
        "host": "localhost",
        "port": "5432",
        "dbname": "test_db",
        "user": "postgres",
        "password": "password",
    }

    database.create_database(params)

    connection = mock_connect.return_value
    cursor = connection.cursor.return_value
    mock_connect.assert_called_once_with(
        dbname="postgres",
        host="localhost",
        port="5432",
        user="postgres",
        password="password",
    )
    assert connection.autocommit is True
    assert cursor.execute.call_args_list[0].args[0] == (
        'DROP DATABASE IF EXISTS "test_db"'
    )
    assert cursor.execute.call_args_list[1].args[0] == (
        'CREATE DATABASE "test_db"'
    )
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@patch("src.database.psycopg2.connect")
def test_create_tables_commits_schema_changes(mock_connect) -> None:
    """Проверяет создание таблиц и подтверждение изменений."""
    database.create_tables({"dbname": "test_db"})

    connection = mock_connect.return_value
    cursor = connection.cursor.return_value.__enter__.return_value
    queries = [call.args[0] for call in cursor.execute.call_args_list]
    assert any("CREATE TABLE employers" in query for query in queries)
    assert any("CREATE TABLE vacancies" in query for query in queries)
    connection.commit.assert_called_once_with()
    connection.close.assert_called_once_with()
