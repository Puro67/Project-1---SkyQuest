"""Database Configuration for SkyQuest.

Configure your SQL database connection settings here.
Supports MariaDB / MySQL (e.g., via HeidiSQL, XAMPP, or MySQL Workbench)
with an automatic local SQLite fallback if the server is offline.
"""

# Database engine selection: "mysql" (MariaDB / HeidiSQL) or "sqlite"
DB_ENGINE = "mysql"

# MySQL / MariaDB Connection Parameters
MYSQL_CONFIG = {
    "host": "127.0.0.1",           # Server hostname or IP (default: "127.0.0.1" or "localhost")
    "port": 3306,                  # MySQL port (default: 3306)
    "database": "db_flight_game",  # Target database name
    "user": "root",                # SQL username (e.g., "root")
    "password": "Hoang",           # SQL password (enter your password here)
    "autocommit": True,
    "connection_timeout": 3
}

# SQLite database filename (used automatically as fallback if MySQL is unreachable)
SQLITE_DB_NAME = "skyquest.db"
