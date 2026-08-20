from decimal import Decimal
from unittest.mock import patch

from src import db_manager


@patch("src.db_manager.psycopg2.connect")
def test_execute_query_returns_rows_and_closes_connection(mock_connect) -> None:
    """Проверяет выполнение запроса, возврат строк и закрытие соединения."""
    connection = mock_connect.return_value
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [("Company", 2)]
    manager = db_manager.DBManager({"dbname": "test_db"})

    result = manager._execute_query("SELECT value FROM table", ("Python",))

    assert result == [("Company", 2)]
    mock_connect.assert_called_once_with(dbname="test_db")
    cursor.execute.assert_called_once_with(
        "SELECT value FROM table",
        ("Python",),
    )
    connection.close.assert_called_once_with()


@patch.object(db_manager.DBManager, "_execute_query")
def test_get_companies_and_vacancies_count_builds_count_query(
    mock_execute_query,
) -> None:
    """Проверяет запрос количества вакансий для каждой компании."""
    manager = db_manager.DBManager({})
    mock_execute_query.return_value = [("Company", 2)]

    result = manager.get_companies_and_vacancies_count()

    assert result == [("Company", 2)]
    query = mock_execute_query.call_args.args[0]
    assert "COUNT(vacancies.vacancy_id)" in query
    assert "LEFT JOIN vacancies" in query


@patch.object(db_manager.DBManager, "_execute_query")
def test_get_all_vacancies_builds_join_query(mock_execute_query) -> None:
    """Проверяет запрос всех вакансий вместе с работодателями."""
    manager = db_manager.DBManager({})
    rows = [("Company", "Python developer", 100, "https://hh.ru/1")]
    mock_execute_query.return_value = rows

    assert manager.get_all_vacancies() == rows
    query = mock_execute_query.call_args.args[0]
    assert "FROM vacancies" in query
    assert "JOIN employers" in query


@patch.object(db_manager.DBManager, "_execute_query")
def test_get_avg_salary_converts_database_value_to_float(
    mock_execute_query,
) -> None:
    """Проверяет преобразование средней зарплаты в число с точкой."""
    manager = db_manager.DBManager({})
    mock_execute_query.return_value = [(Decimal("125.50"),)]

    assert manager.get_avg_salary() == 125.5


@patch.object(db_manager.DBManager, "_execute_query")
def test_get_avg_salary_returns_none_without_salary_data(
    mock_execute_query,
) -> None:
    """Проверяет отсутствие средней зарплаты при пустых данных."""
    manager = db_manager.DBManager({})
    mock_execute_query.return_value = [(None,)]

    assert manager.get_avg_salary() is None


@patch.object(db_manager.DBManager, "_execute_query")
def test_get_vacancies_with_higher_salary_uses_average_subquery(
    mock_execute_query,
) -> None:
    """Проверяет запрос вакансий с зарплатой выше средней."""
    manager = db_manager.DBManager({})
    rows = [("Company", "Developer", 200, "https://hh.ru/1")]
    mock_execute_query.return_value = rows

    assert manager.get_vacancies_with_higher_salary() == rows
    query = mock_execute_query.call_args.args[0]
    assert "vacancies.salary >" in query
    assert "SELECT AVG(salary)" in query


@patch.object(db_manager.DBManager, "_execute_query")
def test_get_vacancies_with_keyword_passes_search_pattern(
    mock_execute_query,
) -> None:
    """Проверяет передачу шаблона поиска вакансий по ключевому слову."""
    manager = db_manager.DBManager({})
    rows = [("Company", "Python developer", 100, "https://hh.ru/1")]
    mock_execute_query.return_value = rows

    assert manager.get_vacancies_with_keyword("Python") == rows
    query, query_params = mock_execute_query.call_args.args
    assert "LOWER(vacancies.name) LIKE LOWER(%s)" in query
    assert query_params == ("%Python%",)
