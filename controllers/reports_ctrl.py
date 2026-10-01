"""
controllers/reports_ctrl.py

Business logic for the Reports module (Admin only).
"""

from models.sale_model import get_sales_history, get_daily_sales_for_chart
from database.db_connection import get_connection


def get_report_data(start_date, end_date):
    """
    Generate a sales report for the given date range.
    Returns a dict with sales list, totals, and daily breakdown.
    """
    sales = get_sales_history(start_date, end_date)
    daily = get_daily_sales_in_range(start_date, end_date)

    # Calculate summary
    total = sum(float(s["total_amount"]) for s in sales)
    count = len(sales)
    average = total / count if count > 0 else 0

    return {
        "sales": sales,
        "total": total,
        "count": count,
        "average": average,
        "daily": daily,
    }


def get_daily_sales_in_range(start_date, end_date):
    """Get daily sales totals within a specific date range."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """SELECT DATE(sale_date) AS sale_day,
                          COALESCE(SUM(total_amount), 0) AS total,
                          COUNT(*) AS txn_count
                   FROM sales
                   WHERE DATE(sale_date) BETWEEN %s AND %s
                   GROUP BY DATE(sale_date)
                   ORDER BY sale_day"""
        cursor.execute(query, (start_date, end_date))
        return cursor.fetchall()
    except Exception as e:
        print(f"[REPORT ERROR] {e}")
        return []
    finally:
        conn.close()
