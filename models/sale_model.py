"""
models/sale_model.py

Handles all database operations for the sales, sale_items, and refunds tables.
"""

from database.db_connection import get_connection
from models.comic_model import update_stock


def create_sale(user_id, cart_items):
    """
    Create a new sale transaction.

    cart_items is a list of dicts:
        [{"comic_id": 1, "quantity": 2, "unit_price": 150.00}, ...]
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        total_amount = sum(item["unit_price"] * item["quantity"] for item in cart_items)

        cursor.execute(
            "INSERT INTO sales (user_id, total_amount) VALUES (%s, %s)",
            (user_id, total_amount)
        )
        sale_id = cursor.lastrowid

        for item in cart_items:
            subtotal = item["unit_price"] * item["quantity"]
            cursor.execute(
                """INSERT INTO sale_items (sale_id, comic_id, quantity, unit_price, subtotal)
                   VALUES (%s, %s, %s, %s, %s)""",
                (sale_id, item["comic_id"], item["quantity"], item["unit_price"], subtotal)
            )

        conn.commit()

        for item in cart_items:
            update_stock(item["comic_id"], -item["quantity"])

        return sale_id
    except Exception as e:
        conn.rollback()
        print(f"[SALE ERROR] {e}")
        return False
    finally:
        conn.close()


def get_sales_history(start_date=None, end_date=None):
    """Get all sales, optionally filtered by date range."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)

        if start_date and end_date:
            query = """SELECT s.sale_id, s.total_amount, s.sale_date,
                              u.full_name AS cashier
                       FROM sales s
                       JOIN users u ON s.user_id = u.user_id
                       WHERE DATE(s.sale_date) BETWEEN %s AND %s
                       ORDER BY s.sale_date DESC"""
            cursor.execute(query, (start_date, end_date))
        else:
            query = """SELECT s.sale_id, s.total_amount, s.sale_date,
                              u.full_name AS cashier
                       FROM sales s
                       JOIN users u ON s.user_id = u.user_id
                       ORDER BY s.sale_date DESC"""
            cursor.execute(query)

        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_sale_items(sale_id):
    """Get all items for a specific sale."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT si.*, c.title AS comic_title
                   FROM sale_items si
                   JOIN comics c ON si.comic_id = c.comic_id
                   WHERE si.sale_id = %s"""
        cursor.execute(query, (sale_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_today_sales_total():
    """Get the total sales amount for today."""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(sale_date) = CURDATE()"
        )
        result = cursor.fetchone()
        return float(result[0]) if result else 0
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return 0
    finally:
        conn.close()


def get_daily_sales_for_chart(days=7):
    """Get daily sales totals for the last N days."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT DATE(sale_date) AS sale_day,
                          COALESCE(SUM(total_amount), 0) AS total
                   FROM sales
                   WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                   GROUP BY DATE(sale_date)
                   ORDER BY sale_day"""
        cursor.execute(query, (days,))
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_top_selling_comics(limit=5):
    """Get the top selling comics by total quantity sold."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT c.title, SUM(si.quantity) AS total_sold
                   FROM sale_items si
                   JOIN comics c ON si.comic_id = c.comic_id
                   GROUP BY c.comic_id, c.title
                   ORDER BY total_sold DESC
                   LIMIT %s"""
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_most_sold_comic():
    """Get the most sold comic/product with sold quantity."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT c.title, SUM(si.quantity) AS total_sold
               FROM sale_items si
               JOIN comics c ON si.comic_id = c.comic_id
               GROUP BY c.comic_id, c.title
               ORDER BY total_sold DESC, c.title ASC
               LIMIT 1"""
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return None
    finally:
        conn.close()


def get_recent_transactions(limit=5):
    """Get the most recent sales transactions."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT s.sale_id, s.total_amount, s.sale_date,
                          u.full_name AS cashier
                   FROM sales s
                   JOIN users u ON s.user_id = u.user_id
                   ORDER BY s.sale_date DESC
                   LIMIT %s"""
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


# ── Refund Functions ────────────────────────────────────────

def create_refund(sale_id, comic_id, quantity, refund_amount, reason,
                  condition_status, refunded_by):
    """Create a refund record and restore stock if condition is not Lost."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO refunds (sale_id, comic_id, quantity, refund_amount,
               reason, condition_status, refunded_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (sale_id, comic_id, quantity, refund_amount, reason,
             condition_status, refunded_by)
        )
        conn.commit()

        if condition_status != "Lost":
            update_stock(comic_id, quantity)

        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"[REFUND ERROR] {e}")
        return False
    finally:
        conn.close()


def get_refundable_items_for_sale(sale_id):
    """Return sale items with remaining refundable quantity for one sale."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT sold.comic_id,
                   c.title AS comic_title,
                   sold.sold_qty,
                   sold.unit_price,
                   COALESCE(ref.refunded_qty, 0) AS refunded_qty,
                   (sold.sold_qty - COALESCE(ref.refunded_qty, 0)) AS refundable_qty
            FROM (
                SELECT sale_id, comic_id, SUM(quantity) AS sold_qty,
                       MAX(unit_price) AS unit_price
                FROM sale_items
                WHERE sale_id = %s
                GROUP BY sale_id, comic_id
            ) AS sold
            JOIN comics c ON c.comic_id = sold.comic_id
            LEFT JOIN (
                SELECT sale_id, comic_id, SUM(quantity) AS refunded_qty
                FROM refunds
                WHERE sale_id = %s
                GROUP BY sale_id, comic_id
            ) AS ref ON ref.sale_id = sold.sale_id AND ref.comic_id = sold.comic_id
            WHERE (sold.sold_qty - COALESCE(ref.refunded_qty, 0)) > 0
            ORDER BY c.title
        """
        cursor.execute(query, (sale_id, sale_id))
        return cursor.fetchall()
    except Exception as e:
        print(f"[REFUND ERROR] {e}")
        return []
    finally:
        conn.close()


def process_sale_refund(sale_id, comic_id, quantity, refund_amount, reason,
                        condition_status, refunded_by):
    """Process refund strictly tied to a sale and remaining refundable quantity."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)

        items = get_refundable_items_for_sale(sale_id)
        target = next((i for i in items if int(i["comic_id"]) == int(comic_id)), None)
        if not target:
            return False

        qty = int(quantity)
        if qty <= 0 or qty > int(target["refundable_qty"]):
            return False

        max_allowed = float(target["unit_price"]) * qty
        amount = float(refund_amount)
        if amount <= 0 or amount > max_allowed:
            return False

        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO refunds (sale_id, comic_id, quantity, refund_amount,
               reason, condition_status, refunded_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (sale_id, comic_id, qty, amount, reason, condition_status, refunded_by)
        )

        if condition_status != "Lost":
            cursor.execute(
                "UPDATE comics SET stock_quantity = stock_quantity + %s WHERE comic_id = %s",
                (qty, comic_id)
            )
            cursor.execute("SELECT stock_quantity FROM comics WHERE comic_id = %s", (comic_id,))
            row = cursor.fetchone()
            if row:
                new_stock = int(row[0])
                new_status = "Available" if new_stock > 0 else "Out of Stock"
                cursor.execute(
                    "UPDATE comics SET availability_status = %s WHERE comic_id = %s",
                    (new_status, comic_id)
                )

        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"[REFUND ERROR] {e}")
        return False
    finally:
        conn.close()


def get_refund_history(limit=100):
    """Get refund history."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT r.*, c.title AS comic_title, u.full_name AS refunded_by_name
               FROM refunds r
               JOIN comics c ON r.comic_id = c.comic_id
               JOIN users u ON r.refunded_by = u.user_id
               ORDER BY r.refund_date DESC
               LIMIT %s""", (limit,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[REFUND ERROR] {e}")
        return []
    finally:
        conn.close()


def get_weekly_sales():
    """Get sales for the current week."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT s.sale_id, s.total_amount, s.sale_date, u.full_name AS cashier
               FROM sales s JOIN users u ON s.user_id = u.user_id
               WHERE YEARWEEK(s.sale_date, 1) = YEARWEEK(CURDATE(), 1)
               ORDER BY s.sale_date DESC"""
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_monthly_sales():
    """Get sales for the current month."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT s.sale_id, s.total_amount, s.sale_date, u.full_name AS cashier
               FROM sales s JOIN users u ON s.user_id = u.user_id
               WHERE YEAR(s.sale_date) = YEAR(CURDATE())
                 AND MONTH(s.sale_date) = MONTH(CURDATE())
               ORDER BY s.sale_date DESC"""
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()


def get_yearly_sales():
    """Get sales for the current year."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT s.sale_id, s.total_amount, s.sale_date, u.full_name AS cashier
               FROM sales s JOIN users u ON s.user_id = u.user_id
               WHERE YEAR(s.sale_date) = YEAR(CURDATE())
               ORDER BY s.sale_date DESC"""
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[SALE ERROR] {e}")
        return []
    finally:
        conn.close()
