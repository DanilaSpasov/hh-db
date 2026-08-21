import os
from unittest.mock import patch

from src.config import get_db_config


@patch("src.config.load_dotenv")
def test_get_db_config_reads_environment(mock_load_dotenv) -> None:
    """Проверяет получение параметров базы данных из окружения."""
    environment = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "hh_test",
        "DB_USER": "postgres",
        "DB_PASSWORD": "password",
    }
    with patch.dict(os.environ, environment, clear=True):
        result = get_db_config()

    assert result == {
        "host": "localhost",
        "port": "5432",
        "dbname": "hh_test",
        "user": "postgres",
        "password": "password",
    }
    mock_load_dotenv.assert_called_once()
