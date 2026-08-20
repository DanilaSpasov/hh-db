import psycopg2


def calculate_salary(
    salary_data: dict[str, int | None] | None,
) -> int | None:
    """Рассчитывает зарплату с учётом отсутствующих границ."""
    if salary_data is None:
        return None

    salary_from = salary_data.get("from")
    salary_to = salary_data.get("to")

    if salary_from is not None and salary_to is not None:
        return (salary_from + salary_to) // 2

    if salary_from is not None:
        return salary_from

    return salary_to


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


def save_data_to_database(data: list[dict], params: dict[str, str]) -> None:
    """Сохраняет работодателей и вакансии в базу данных."""
    connection = psycopg2.connect(**params)

    with connection.cursor() as cur:
        for company in data:
            employer = company["employer"]
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, url)
                VALUES (%s, %s, %s)
                """,
                (
                    int(employer["id"]),
                    employer["name"],
                    employer["alternate_url"],
                ),
            )

            for vacancy in company["vacancies"]:
                salary = calculate_salary(vacancy["salary"])

                cur.execute(
                    """
                    INSERT INTO vacancies (
                        vacancy_id,
                        employer_id,
                        name,
                        salary,
                        url
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        int(vacancy["id"]),
                        int(employer["id"]),
                        vacancy["name"],
                        salary,
                        vacancy["alternate_url"],
                    ),
                )

    connection.commit()
    connection.close()
