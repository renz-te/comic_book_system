"""
controllers/users_ctrl.py

Business logic for the User Management module (Admin only).
Includes archive, restore, and login history.
"""

from models.user_model import (
    get_all_users, add_user, update_user, delete_user,
    archive_user, get_archived_users, restore_user,
    get_login_history, get_user_by_id
)


def load_all_users():
    """Get all active users from the database."""
    return get_all_users()


def add_user_ctrl(username, full_name, role, password=None,
                  security_question_1="", security_answer_1="",
                  security_question_2="", security_answer_2="",
                  security_question_3="", security_answer_3="",
                  borrow_limit=5):
    """Add a new user."""
    if not password:
        return False
    return add_user(
        username, password, full_name, role, "",
        security_question_1, security_answer_1,
        security_question_2, security_answer_2,
        security_question_3, security_answer_3,
        borrow_limit,
    )


def update_user_ctrl(user_id, username, full_name, role, password=None,
                     security_question_1="", security_answer_1="",
                     security_question_2="", security_answer_2="",
                     security_question_3="", security_answer_3="",
                     borrow_limit=5):
    """Update an existing user."""
    return update_user(
        user_id, username, full_name, role, password, "",
        security_question_1, security_answer_1,
        security_question_2, security_answer_2,
        security_question_3, security_answer_3,
        borrow_limit,
    )


def delete_user_ctrl(user_id, archived_by=None):
    """Archive a user (soft delete) instead of permanent deletion."""
    if archived_by:
        return archive_user(user_id, archived_by)
    return delete_user(user_id)


def get_archived_users_ctrl():
    """Get archived users."""
    return get_archived_users()


def restore_user_ctrl(archive_id):
    """Restore an archived user."""
    return restore_user(archive_id)


def get_login_history_ctrl(limit=50):
    """Get recent login history."""
    return get_login_history(limit)


def get_user_details(user_id):
    """Get a user by ID."""
    return get_user_by_id(user_id)
