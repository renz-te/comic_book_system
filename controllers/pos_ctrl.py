"""
controllers/pos_ctrl.py

Business logic for the POS module.
"""

from models.comic_model import get_available_comics
from models.sale_model import create_sale, get_refund_history


def get_available_comics_list():
    """Get list of comics that are in stock."""
    return get_available_comics()


def process_sale(user_id, cart_items):
    """Process a sale transaction. Returns sale_id or False."""
    return create_sale(user_id, cart_items)


def process_refund(sale_id, comic_id, quantity, refund_amount, reason,
                   condition_status, refunded_by):
    """Deprecated: refunds are now processed from Sales History only."""
    return False


def get_refunds():
    """Get refund history."""
    return get_refund_history()
