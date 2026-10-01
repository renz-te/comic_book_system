"""
controllers/borrow_ctrl.py

Business logic for the Borrow / Return module.
Includes borrow limit checks, damage assessment, and archive.
"""

from models.borrow_model import (
    borrow_comic, return_comic,
    get_all_borrow_records, get_borrowed_records,
    get_active_borrow_count_for_borrower,
    archive_borrow_record, restore_borrow_record,
    get_archived_borrow_records, get_damaged_and_lost_records
)
from models.comic_model import get_available_comics
from models.user_model import get_user_borrow_limit


def get_available_comics_list():
    """Get comics that are available for borrowing."""
    return get_available_comics()


def get_borrowed_list():
    """Get list of currently borrowed records (for return dropdown)."""
    return get_borrowed_records()


def get_all_records():
    """Get all active borrow/return records."""
    return get_all_borrow_records(include_archived=False)


def borrow_comic_ctrl(comic_id, borrower_name, borrow_date, due_date, user_id):
    """Process a borrow transaction."""
    return borrow_comic(comic_id, borrower_name, borrow_date, due_date, user_id)


def return_comic_ctrl(borrow_id, return_date, condition="Good",
                      damage_notes="", damage_fee=0.0):
    """Process a return transaction with condition assessment."""
    return return_comic(borrow_id, return_date, condition, damage_notes, damage_fee)


def check_borrow_limit(borrower_name, user_id):
    """
    Check if borrower has reached their borrow limit.
    Returns (can_borrow, current_count, limit).
    """
    current = get_active_borrow_count_for_borrower(borrower_name)
    limit = get_user_borrow_limit(user_id)
    return current < limit, current, limit


def archive_record(borrow_id):
    """Archive a borrow record."""
    return archive_borrow_record(borrow_id)


def restore_record(borrow_id):
    """Restore an archived borrow record."""
    return restore_borrow_record(borrow_id)


def get_archived_records():
    """Get all archived borrow records."""
    return get_archived_borrow_records()


def get_damaged_lost_records():
    """Get records of damaged or lost books."""
    return get_damaged_and_lost_records()
