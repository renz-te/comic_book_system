"""
config.py

Central configuration for the Comic Book Management System.
Edit the settings below to match your environment.
This is the ONLY file you need to change when moving to another PC.
"""

# ── MySQL Database Settings ─────────────────────────────────
# Update these to match your XAMPP / MySQL setup.
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""              # Default XAMPP password is empty
DB_NAME = "comic_book_db"
DB_PORT = 3306

# ── Application Settings ────────────────────────────────────
APP_TITLE = "Comic Book Management System"
CURRENCY_SYMBOL = "₱"
LOW_STOCK_THRESHOLD = 5
DEFAULT_BORROW_LIMIT = 5
DEFAULT_BORROW_DAYS = 14
COVERS_DIR = "resources/covers"

SECURITY_QUESTIONS = [
    "What is your favorite color?",
    "What is your pet's name?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
]
