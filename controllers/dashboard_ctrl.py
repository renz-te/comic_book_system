"""
controllers/dashboard_ctrl.py

Gathers all the data needed for the dashboard page.
"""

from models.sale_model import (
    get_today_sales_total,
    get_daily_sales_for_chart,
    get_top_selling_comics,
    get_most_sold_comic,
    get_recent_transactions,
)
from models.comic_model import get_all_comics, get_low_stock_comics
from models.borrow_model import get_borrow_count, get_borrow_vs_returned, get_most_borrowed_comic
from database.db_connection import get_connection


def get_dashboard_data():
    """
    Collect all data needed for the dashboard.
    Returns a dictionary with all stats and chart data.
    """
    data = {
        "today_sales": get_today_sales_total(),
        "total_comics": get_total_comics_count(),
        "borrowed_count": get_borrow_count(),
        "low_stock_count": len(get_low_stock_comics(5)),
        "most_borrowed": get_most_borrowed_comic(),
        "most_sold": get_most_sold_comic(),
        "daily_sales": get_daily_sales_for_chart(7),
        "top_selling": get_top_selling_comics(5),
        "stock_distribution": get_stock_by_category(),
        "borrow_vs_returned": get_borrow_vs_returned(),
        "recent_transactions": get_recent_transactions(5),
    }
    return data


def get_total_comics_count():
    """Get the total number of comics in inventory."""
    conn = get_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(stock_quantity), 0) FROM comics")
        result = cursor.fetchone()
        return int(result[0]) if result else 0
    except Exception as e:
        print(f"[DASHBOARD ERROR] {e}")
        return 0
    finally:
        conn.close()


def get_stock_by_category():
    """
    Get stock totals grouped by category (for pie chart).
    Returns: [{"category": "Manga", "total_stock": 55}, ...]
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT category, SUM(stock_quantity) AS total_stock
            FROM comics
            WHERE category != ''
            GROUP BY category
            ORDER BY total_stock DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"[DASHBOARD ERROR] {e}")
        return []
    finally:
        conn.close()
