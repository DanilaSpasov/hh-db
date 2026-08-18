import psycopg2


def create_database(params: dict[str, str]) -> None:
    """Создаёт базу данных PostgreSQL."""
    database_name = params["dbname"]

    connection_params = params.copy()
    connection_params.pop("dbname")

    connection = psycopg2.connect(dbname="postgres", **connection_params)
    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
    cursor.execute(f'CREATE DATABASE "{database_name}"')

    cursor.close()
    connection.close()


def create_tables(params: dict[str, str]) -> None:
    """Создаёт таблицы работодателей и вакансий."""
    connection = psycopg2.connect(**params)

    with connection.cursor() as cur:
        cur.execute("""
        CREATE TABLE employers (
        employer_id BIGINT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url TEXT)
        """)
    with connection.cursor() as cur:
        cur.execute("""
        CREATE TABLE vacancies (
            vacancy_id BIGINT PRIMARY KEY,
            employer_id BIGINT REFERENCES employers(employer_id) NOT NULL,
            name VARCHAR(255) NOT NULL,
            salary INTEGER,
            url TEXT NOT NULL)
        """)

    connection.commit()
    connection.close()