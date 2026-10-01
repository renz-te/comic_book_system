"""
models/borrow_model.py

Handles all database operations for the borrow_records table.
Includes due dates, damage/lost assessment, and archive functionality.
"""

from database.db_connection import get_connection
from models.comic_model import update_stock


def borrow_comic(comic_id, borrower_name, borrow_date, due_date, user_id):
    """Create a borrow record and decrease stock by 1."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Safety check at DB level to prevent borrowing out-of-stock items.
        cursor.execute("SELECT stock_quantity FROM comics WHERE comic_id = %s", (comic_id,))
        stock_row = cursor.fetchone()
        if not stock_row:
            return False
        if int(stock_row[0] or 0) <= 0:
            return False

        query = """INSERT INTO borrow_records
                   (comic_id, borrower_name, borrow_date, due_date, status, user_id)
                   VALUES (%s, %s, %s, %s, 'Borrowed', %s)"""
        cursor.execute(query, (comic_id, borrower_name, borrow_date, due_date, user_id))
        conn.commit()

        update_stock(comic_id, -1)
        return True
    except Exception as e:
        conn.rollback()
        print(f"[BORROW ERROR] {e}")
        return False
    finally:
        conn.close()


def return_comic(borrow_id, return_date, condition="Good", damage_notes="", damage_fee=0.0):
    """
    Mark a borrow record as returned with condition assessment.
    If condition is 'Lost', stock is NOT restored.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Only active borrowed records are allowed to be returned.
        cursor.execute(
            """SELECT comic_id, status, archive_status
               FROM borrow_records
               WHERE borrow_id = %s""",
            (borrow_id,)
        )
        result = cursor.fetchone()
        if not result:
            return False

        comic_id, status, archive_status = result
        if status != "Borrowed" or archive_status != "Active":
            return False

        query = """UPDATE borrow_records SET return_date = %s, status = 'Returned',
                   condition_on_return = %s, damage_notes = %s, damage_fee = %s
                   WHERE borrow_id = %s AND status = 'Borrowed' AND archive_status = 'Active'"""
        cursor.execute(query, (return_date, condition, damage_notes, damage_fee, borrow_id))
        if cursor.rowcount != 1:
            conn.rollback()
            return False
        conn.commit()

        # Only restore stock if not lost
        if condition != "Lost":
            update_stock(comic_id, 1)

        return True
    except Exception as e:
        conn.rollback()
        print(f"[RETURN ERROR] {e}")
        return False
    finally:
        conn.close()


def get_all_borrow_records(include_archived=False):
    """Get all borrow records with comic title."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        where = "" if include_archived else "WHERE br.archive_status = 'Active'"
        query = f"""SELECT br.borrow_id, c.title AS comic_title, br.borrower_name,
                          br.borrow_date, br.due_date, br.return_date, br.status,
                          br.condition_on_return, br.damage_notes, br.damage_fee,
                          br.archive_status, br.created_at
                   FROM borrow_records br
                   JOIN comics c ON br.comic_id = c.comic_id
                   {where}
                   ORDER BY br.created_at DESC"""
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return []
    finally:
        conn.close()


def get_borrowed_records():
    """Get only currently borrowed (not yet returned) records."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT br.borrow_id, c.title AS comic_title, br.borrower_name,
                          br.borrow_date, br.due_date, br.status, c.price
                   FROM borrow_records br
                   JOIN comics c ON br.comic_id = c.comic_id
                   WHERE br.status = 'Borrowed' AND br.archive_status = 'Active'
                   ORDER BY br.borrow_date DESC"""
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return []
    finally:
        conn.close()


def get_borrow_count():
    """Get the count of currently borrowed comics."""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE status = 'Borrowed'")
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return 0
    finally:
        conn.close()


def get_most_borrowed_comic():
    """Get the most borrowed comic/product with borrow count."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT c.title, COUNT(*) AS borrow_count
               FROM borrow_records br
               JOIN comics c ON br.comic_id = c.comic_id
               GROUP BY br.comic_id, c.title
               ORDER BY borrow_count DESC, c.title ASC
               LIMIT 1"""
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return None
    finally:
        conn.close()


def get_borrow_vs_returned():
    """Get counts of borrowed vs returned comics for charts."""
    conn = get_connection()
    if not conn:
        return {"borrowed": 0, "returned": 0}

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""SELECT status, COUNT(*) AS count
                          FROM borrow_records GROUP BY status""")
        results = cursor.fetchall()

        data = {"borrowed": 0, "returned": 0}
        for row in results:
            if row["status"] == "Borrowed":
                data["borrowed"] = row["count"]
            elif row["status"] == "Returned":
                data["returned"] = row["count"]
        return data
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return {"borrowed": 0, "returned": 0}
    finally:
        conn.close()


def get_active_borrow_count_for_borrower(borrower_name):
    """Get the number of active borrows for a specific borrower."""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM borrow_records "
            "WHERE borrower_name = %s AND status = 'Borrowed' AND archive_status = 'Active'",
            (borrower_name,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return 0
    finally:
        conn.close()


# ── Archive Functions ───────────────────────────────────────

def archive_borrow_record(borrow_id):
    """Archive a borrow record."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE borrow_records SET archive_status = 'Archived' WHERE borrow_id = %s",
            (borrow_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ARCHIVE ERROR] {e}")
        return False
    finally:
        conn.close()


def restore_borrow_record(borrow_id):
    """Restore an archived borrow record."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE borrow_records SET archive_status = 'Active' WHERE borrow_id = %s",
            (borrow_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[RESTORE ERROR] {e}")
        return False
    finally:
        conn.close()


def get_archived_borrow_records():
    """Get archived borrow records."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT br.borrow_id, c.title AS comic_title, br.borrower_name,
                          br.borrow_date, br.due_date, br.return_date, br.status,
                          br.condition_on_return, br.damage_notes, br.damage_fee,
                          br.archive_status, br.created_at
                   FROM borrow_records br
                   JOIN comics c ON br.comic_id = c.comic_id
                   WHERE br.archive_status = 'Archived'
                   ORDER BY br.created_at DESC"""
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ARCHIVE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_damaged_and_lost_records():
    """Get records of damaged or lost books."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT br.borrow_id, c.title AS comic_title, br.borrower_name,
                          br.borrow_date, br.return_date, br.condition_on_return,
                          br.damage_notes, br.damage_fee
                   FROM borrow_records br
                   JOIN comics c ON br.comic_id = c.comic_id
                   WHERE br.condition_on_return IN ('Damaged', 'Lost')
                   ORDER BY br.return_date DESC"""
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[BORROW ERROR] {e}")
        return []
    finally:
        conn.close()
