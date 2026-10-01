"""
controllers/sales_history_ctrl.py

Business logic for the Sales History module.
Includes weekly/monthly/yearly filtering.
"""

from models.sale_model import (
    get_sales_history, get_sale_items,
    get_weekly_sales, get_monthly_sales, get_yearly_sales,
    get_refundable_items_for_sale, process_sale_refund
)


def get_all_sales():
    """Get all sales (no date filter)."""
    return get_sales_history()


def get_filtered_sales(start_date, end_date):
    """Get sales filtered by date range."""
    return get_sales_history(start_date, end_date)


def get_sale_detail(sale_id):
    """Get the line items for a specific sale."""
    return get_sale_items(sale_id)


def get_weekly_sales_ctrl():
    """Get sales for the current week."""
    return get_weekly_sales()


def get_monthly_sales_ctrl():
    """Get sales for the current month."""
    return get_monthly_sales()


def get_yearly_sales_ctrl():
    """Get sales for the current year."""
    return get_yearly_sales()


def get_refundable_items_ctrl(sale_id):
    """Get refundable sale items for a selected sale."""
    return get_refundable_items_for_sale(sale_id)


def process_sale_refund_ctrl(sale_id, comic_id, quantity, refund_amount,
                             reason, condition_status, refunded_by):
    """Process refund linked to selected sale transaction."""
    return process_sale_refund(
        sale_id, comic_id, quantity, refund_amount,
        reason, condition_status, refunded_by
    )
