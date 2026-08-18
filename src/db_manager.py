import psycopg2


class DBManager:
    """Предоставляет методы для получения данных из PostgreSQL."""

    def __init__(self, params: dict[str, str]) -> None:
        """Сохраняет параметры подключения к PostgreSQL."""
        self._params = params

    def _execute_query(
        self, query: str, query_params: tuple | None = None
    ) -> list[tuple]:
        """Выполняет SQL-запрос и возвращает полученные строки."""
        connection = psycopg2.connect(**self._params)

        try:
            with connection.cursor() as cur:
                cur.execute(query, query_params)
                result = cur.fetchall()
        finally:
            connection.close()

        return result

    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]]:
        """Возвращает компании и количество вакансий каждой компании."""
        query = """
            SELECT employers.name, COUNT(vacancies.vacancy_id)
            FROM employers
            LEFT JOIN vacancies
                ON employers.employer_id = vacancies.employer_id
            GROUP BY employers.employer_id, employers.name
            ORDER BY employers.name
        """
        return self._execute_query(query)

    def get_all_vacancies(
        self,
    ) -> list[tuple[str, str, int | None, str]]:
        """Возвращает компании, вакансии, зарплаты и ссылки."""
        query = """
            SELECT
                employers.name,
                vacancies.name,
                vacancies.salary,
                vacancies.url
            FROM vacancies
            JOIN employers
                ON vacancies.employer_id = employers.employer_id
            ORDER BY employers.name, vacancies.name
        """
        return self._execute_query(query)

    def get_avg_salary(self) -> float | None:
        """Возвращает среднюю зарплату по всем вакансиям."""
        query = """
            SELECT AVG(salary)
            FROM vacancies
        """
        result = self._execute_query(query)
        average_salary = result[0][0]

        if average_salary is None:
            return None

        return float(average_salary)

    def get_vacancies_with_higher_salary(
        self,
    ) -> list[tuple[str, str, int | None, str]]:
        """Возвращает вакансии с зарплатой выше средней."""
        query = """
            SELECT
                employers.name,
                vacancies.name,
                vacancies.salary,
                vacancies.url
            FROM vacancies
            JOIN employers
                ON vacancies.employer_id = employers.employer_id
            WHERE vacancies.salary > (
                SELECT AVG(salary)
                FROM vacancies
            )
            ORDER BY vacancies.salary DESC
        """
        return self._execute_query(query)

    def get_vacancies_with_keyword(
        self, keyword: str
    ) -> list[tuple[str, str, int | None, str]]:
        """Возвращает вакансии, содержащие ключевое слово в названии."""
        query = """
            SELECT
                employers.name,
                vacancies.name,
                vacancies.salary,
                vacancies.url
            FROM vacancies
            JOIN employers
                ON vacancies.employer_id = employers.employer_id
            WHERE LOWER(vacancies.name) LIKE LOWER(%s)
            ORDER BY employers.name, vacancies.name
        """
        return self._execute_query(query, (f"%{keyword}%",))
