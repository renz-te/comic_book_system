"""
setup.py

Optional helper script for first-time setup.
Run this if you want to set up the project manually instead
of relying on the automatic checks in main.py.

Usage:
    python setup.py
"""

import sys
import os
import subprocess

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 54)
    print("  Comic Book Management System — First-Time Setup")
    print("=" * 54)
    print()

    # ── Step 1: Install Python packages ─────────────────
    print("[1/3] Checking Python packages ...")

    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", req_file],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        print("      Packages OK.\n")
    except Exception as e:
        print(f"      [ERROR] {e}")
        print("      Please run:  pip install -r requirements.txt")
        print()

    # ── Step 2: Check MySQL connection ──────────────────
    print("[2/3] Testing MySQL connection ...")

    try:
        from database.db_connection import database_exists, create_database_from_sql, test_connection
        from config import DB_HOST, DB_PORT, DB_USER, DB_NAME
    except ImportError as e:
        print(f"      [ERROR] Cannot import modules: {e}")
        print("      Make sure packages installed correctly.")
        input("\nPress Enter to exit ...")
        sys.exit(1)

    # ── Step 3: Check / create database ─────────────────
    print(f"[3/3] Checking database '{DB_NAME}' ...")

    if test_connection():
        print(f"      Database '{DB_NAME}' already exists and is connected.\n")
    elif database_exists():
        print(f"      Database '{DB_NAME}' exists but connection fails.")
        print(f"      Check config.py (host={DB_HOST}, port={DB_PORT}, user={DB_USER})\n")
    else:
        print(f"      Database '{DB_NAME}' not found.")
        answer = input("      Create it now? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            if create_database_from_sql():
                print("      Database created successfully!\n")
            else:
                print("      [ERROR] Failed to create database.")
                print("      Please import database/comic_book_system.sql via phpMyAdmin.\n")
        else:
            print("      Skipped. You can import the SQL file manually.\n")

    # ── Done ────────────────────────────────────────────
    print("=" * 54)
    print("  Setup complete!  Run the app with:  python main.py")
    print("=" * 54)
    print()
    print("  Default login accounts:")
    print("    admin / admin123   (Administrator)")
    print("    staff / staff123   (Staff)")
    print()
    input("Press Enter to exit ...")


if __name__ == "__main__":
    main()
