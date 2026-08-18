import os

from dotenv import load_dotenv


def get_db_config() -> dict[str, str]:
    """Возвращает параметры подключения к PostgreSQL."""
    load_dotenv()
    dbhost = os.getenv("DB_HOST")
    dbport = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    dbuser = os.getenv("DB_USER")
    dbpassword = os.getenv("DB_PASSWORD")

    db_config = {"host": dbhost,
                 "port": dbport,
                 "dbname": dbname,
                 "user": dbuser,
                 "password": dbpassword,}
    return db_config