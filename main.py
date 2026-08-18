from src.config import get_db_config
from src.database import (
    create_database,
    create_tables,
    save_data_to_database,
)
from src.file_manager import load_hh_data


def main() -> None:
    db_config = get_db_config()
    data = load_hh_data("data/hh_vacancies.json")

    create_database(db_config)
    create_tables(db_config)
    save_data_to_database(data, db_config)


if __name__ == "__main__":
    main()
