from src.config import get_db_config
from src.database import create_database, create_tables


def main() -> None:
    db_config = get_db_config()
    create_database(db_config)
    create_tables(db_config)


if __name__ == "__main__":
    main()