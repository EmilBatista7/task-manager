import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST") or os.getenv("MYSQLHOST", "localhost"),
        port=int(os.getenv("DB_PORT") or os.getenv("MYSQLPORT", "3306")),
        user=os.getenv("DB_USER") or os.getenv("MYSQLUSER", "root"),
        password=os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE", "task_manager"),
    )
