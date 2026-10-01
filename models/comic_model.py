"""
models/comic_model.py

Handles all database operations for the comics table.
Includes chapters, cover images, and synopsis support.
"""

from database.db_connection import get_connection


def get_all_comics():
    """Get all comics from the database."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comics ORDER BY title")
        return cursor.fetchall()
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return []
    finally:
        conn.close()


def search_comics(keyword):
    """Search comics by title, author, or category."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT * FROM comics
                   WHERE title LIKE %s OR author LIKE %s OR category LIKE %s
                   ORDER BY title"""
        search = f"%{keyword}%"
        cursor.execute(query, (search, search, search))
        return cursor.fetchall()
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return []
    finally:
        conn.close()


def get_comic_by_id(comic_id):
    """Get a single comic by its ID."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comics WHERE comic_id = %s", (comic_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return None
    finally:
        conn.close()


def add_comic(title, author, issue_number, publisher, category, price,
              stock_quantity, chapters=1, cover_image="", synopsis=""):
    """Add a new comic to the database."""
    conn = get_connection()
    if not conn:
        return False

    try:
        status = "Available" if stock_quantity > 0 else "Out of Stock"

        cursor = conn.cursor()
        query = """INSERT INTO comics (title, author, issue_number, publisher,
                   category, price, stock_quantity, chapters, cover_image,
                   synopsis, availability_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (title, author, issue_number, publisher,
                               category, price, stock_quantity, chapters,
                               cover_image, synopsis, status))
        conn.commit()
        return True
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return False
    finally:
        conn.close()


def update_comic(comic_id, title, author, issue_number, publisher, category,
                 price, stock_quantity, chapters=1, cover_image="", synopsis=""):
    """Update an existing comic."""
    conn = get_connection()
    if not conn:
        return False

    try:
        status = "Available" if stock_quantity > 0 else "Out of Stock"

        cursor = conn.cursor()
        query = """UPDATE comics SET title=%s, author=%s, issue_number=%s,
                   publisher=%s, category=%s, price=%s, stock_quantity=%s,
                   chapters=%s, cover_image=%s, synopsis=%s,
                   availability_status=%s WHERE comic_id=%s"""
        cursor.execute(query, (title, author, issue_number, publisher,
                               category, price, stock_quantity, chapters,
                               cover_image, synopsis, status, comic_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return False
    finally:
        conn.close()


def delete_comic(comic_id):
    """Delete a comic by ID."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comics WHERE comic_id = %s", (comic_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return False
    finally:
        conn.close()


def update_stock(comic_id, quantity_change):
    """
    Update stock quantity by a given amount.
    Positive = add stock, Negative = reduce stock.
    Also updates availability_status automatically.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """UPDATE comics SET stock_quantity = stock_quantity + %s
                   WHERE comic_id = %s"""
        cursor.execute(query, (quantity_change, comic_id))

        cursor.execute("SELECT stock_quantity FROM comics WHERE comic_id = %s", (comic_id,))
        result = cursor.fetchone()
        if result:
            new_stock = result[0]
            status = "Available" if new_stock > 0 else "Out of Stock"
            cursor.execute("UPDATE comics SET availability_status = %s WHERE comic_id = %s",
                           (status, comic_id))

        conn.commit()
        return True
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return False
    finally:
        conn.close()


def get_low_stock_comics(threshold=5):
    """Get comics with stock below the given threshold."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comics WHERE stock_quantity < %s ORDER BY stock_quantity",
                       (threshold,))
        return cursor.fetchall()
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return []
    finally:
        conn.close()


def get_available_comics():
    """Get only comics that are available (stock > 0)."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comics WHERE stock_quantity > 0 ORDER BY title")
        return cursor.fetchall()
    except Exception as e:
        print(f"[COMIC ERROR] {e}")
        return []
    finally:
        conn.close()
