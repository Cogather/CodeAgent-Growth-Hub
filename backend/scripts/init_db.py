#!/usr/bin/env python3
"""手工初始化 MySQL 库与表：cd backend && .venv/bin/python scripts/init_db.py"""

from app.db_init import init_tables
from app.database import ensure_mysql_database


def main() -> None:
    ensure_mysql_database()
    init_tables()
    print("Database and tables are ready.")


if __name__ == "__main__":
    main()
