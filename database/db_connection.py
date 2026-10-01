"""
database/db_connection.py

Handles the MySQL database connection using mysql-connector-python.
All models use this module to get a connection to the database.

Reads settings from config.py so only ONE file needs editing
when transferring the project to another PC.
"""

import os
import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT


# ── Database configuration (built from config.py) ──────────
DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "port": DB_PORT,
    "use_pure": True,         # Required: C extension crashes with PyQt6
}


def get_connection():
    """
    Create and return a new MySQL connection.
    Returns None if the connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        return None


def test_connection():
    """
    Quick test to see if the database is reachable.
    Returns True if successful, False otherwise.
    """
    conn = get_connection()
    if conn and conn.is_connected():
        conn.close()
        return True
    return False


def _server_connection():
    """Connect to MySQL *without* selecting a database."""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            use_pure=True,
        )
    except Error:
        return None


def database_exists():
    """Return True if the configured database already exists on the server."""
    conn = _server_connection()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
        found = cur.fetchone() is not None
        cur.close()
        return found
    except Error:
        return False
    finally:
        conn.close()


def create_database_from_sql():
    """
    Import the .sql schema file that ships with the project.
    Returns True on success, False on failure.
    """
    sql_path = os.path.join(os.path.dirname(__file__), "comic_book_system.sql")
    if not os.path.isfile(sql_path):
        print(f"[DB ERROR] SQL file not found: {sql_path}")
        return False

    conn = _server_connection()
    if conn is None:
        return False

    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # DELIMITER directives are mysql-client commands, not SQL statements.
        cleaned_script = "\n".join(
            line for line in sql_script.splitlines()
            if not line.strip().upper().startswith("DELIMITER ")
        )

        cursor = conn.cursor()
        for _ in cursor.execute(cleaned_script, multi=True):
            pass
        conn.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"[DB ERROR] Failed to import SQL: {e}")
        return False
    finally:
        conn.close()


def run_migrations():
    """
    Apply schema migrations for new columns and tables.
    Safe to run multiple times — uses IF NOT EXISTS and column checks.
    """
    conn = get_connection()
    if not conn:
        return

    migrations = [
        # Users table new columns
        ("users", "email", "ALTER TABLE users ADD COLUMN email VARCHAR(100) DEFAULT '' AFTER role"),
        ("users", "security_question", "ALTER TABLE users ADD COLUMN security_question VARCHAR(200) DEFAULT '' AFTER email"),
        ("users", "security_answer", "ALTER TABLE users ADD COLUMN security_answer VARCHAR(200) DEFAULT '' AFTER security_question"),
        ("users", "security_question_1", "ALTER TABLE users ADD COLUMN security_question_1 VARCHAR(200) DEFAULT '' AFTER security_answer"),
        ("users", "security_answer_1", "ALTER TABLE users ADD COLUMN security_answer_1 VARCHAR(255) DEFAULT '' AFTER security_question_1"),
        ("users", "security_question_2", "ALTER TABLE users ADD COLUMN security_question_2 VARCHAR(200) DEFAULT '' AFTER security_answer_1"),
        ("users", "security_answer_2", "ALTER TABLE users ADD COLUMN security_answer_2 VARCHAR(255) DEFAULT '' AFTER security_question_2"),
        ("users", "security_question_3", "ALTER TABLE users ADD COLUMN security_question_3 VARCHAR(200) DEFAULT '' AFTER security_answer_2"),
        ("users", "security_answer_3", "ALTER TABLE users ADD COLUMN security_answer_3 VARCHAR(255) DEFAULT '' AFTER security_question_3"),
        ("users", "borrow_limit", "ALTER TABLE users ADD COLUMN borrow_limit INT NOT NULL DEFAULT 5 AFTER security_answer"),
        ("users", "profile_image", "ALTER TABLE users ADD COLUMN profile_image VARCHAR(255) DEFAULT '' AFTER borrow_limit"),
        ("users", "is_archived", "ALTER TABLE users ADD COLUMN is_archived TINYINT NOT NULL DEFAULT 0 AFTER borrow_limit"),
        # Comics table new columns
        ("comics", "chapters", "ALTER TABLE comics ADD COLUMN chapters INT NOT NULL DEFAULT 1 AFTER stock_quantity"),
        ("comics", "cover_image", "ALTER TABLE comics ADD COLUMN cover_image VARCHAR(255) DEFAULT '' AFTER chapters"),
        ("comics", "synopsis", "ALTER TABLE comics ADD COLUMN synopsis TEXT AFTER cover_image"),
        # Borrow records new columns
        ("borrow_records", "due_date", "ALTER TABLE borrow_records ADD COLUMN due_date DATE DEFAULT NULL AFTER borrow_date"),
        ("borrow_records", "condition_on_return", "ALTER TABLE borrow_records ADD COLUMN condition_on_return ENUM('Good','Damaged','Lost') DEFAULT NULL AFTER status"),
        ("borrow_records", "damage_notes", "ALTER TABLE borrow_records ADD COLUMN damage_notes TEXT AFTER condition_on_return"),
        ("borrow_records", "damage_fee", "ALTER TABLE borrow_records ADD COLUMN damage_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER damage_notes"),
        ("borrow_records", "archive_status", "ALTER TABLE borrow_records ADD COLUMN archive_status ENUM('Active','Archived') NOT NULL DEFAULT 'Active' AFTER damage_fee"),
    ]

    new_tables = [
        """CREATE TABLE IF NOT EXISTS login_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        ) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS archived_users (
            archive_id INT AUTO_INCREMENT PRIMARY KEY,
            original_user_id INT,
            username VARCHAR(50),
            password VARCHAR(255),
            full_name VARCHAR(100),
            email VARCHAR(100) DEFAULT '',
            role ENUM('Admin', 'Staff'),
            archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            archived_by INT,
            FOREIGN KEY (archived_by) REFERENCES users(user_id)
        ) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS refunds (
            refund_id INT AUTO_INCREMENT PRIMARY KEY,
            sale_id INT DEFAULT NULL,
            comic_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            refund_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            reason TEXT,
            condition_status ENUM('Good','Damaged','Lost') DEFAULT 'Good',
            refunded_by INT NOT NULL,
            refund_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
            FOREIGN KEY (comic_id) REFERENCES comics(comic_id),
            FOREIGN KEY (refunded_by) REFERENCES users(user_id)
        ) ENGINE=InnoDB""",
    ]

    try:
        cursor = conn.cursor()

        # Add new columns if they don't exist
        for table, column, sql in migrations:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
                    (DB_NAME, table, column)
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(sql)
                    print(f"[MIGRATION] Added {table}.{column}")
            except Error as e:
                print(f"[MIGRATION WARN] {table}.{column}: {e}")

        # Create new tables
        for sql in new_tables:
            try:
                cursor.execute(sql)
            except Error as e:
                print(f"[MIGRATION WARN] Table creation: {e}")

        # Backfill new multi-question fields from legacy single-question fields.
        try:
            cursor.execute(
                "UPDATE users SET security_question_1 = security_question "
                "WHERE COALESCE(security_question_1, '') = '' AND COALESCE(security_question, '') <> ''"
            )
            cursor.execute(
                "UPDATE users SET security_answer_1 = security_answer "
                "WHERE COALESCE(security_answer_1, '') = '' AND COALESCE(security_answer, '') <> ''"
            )
            cursor.execute(
                "UPDATE users SET security_question_2 = security_question_1 "
                "WHERE COALESCE(security_question_2, '') = '' AND COALESCE(security_question_1, '') <> ''"
            )
            cursor.execute(
                "UPDATE users SET security_answer_2 = security_answer_1 "
                "WHERE COALESCE(security_answer_2, '') = '' AND COALESCE(security_answer_1, '') <> ''"
            )
        except Error as e:
            print(f"[MIGRATION WARN] Security question backfill: {e}")

        conn.commit()
        cursor.close()
        print("[MIGRATION] Schema migrations completed.")
    except Error as e:
        print(f"[MIGRATION ERROR] {e}")
    finally:
        conn.close()
