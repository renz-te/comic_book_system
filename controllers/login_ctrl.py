"""
controllers/login_ctrl.py

Handles the login logic and forgot password flow.
"""

from models.user_model import (
    authenticate_user, record_login,
    get_security_questions, verify_security_answers, reset_password
)


def attempt_login(username, password):
    """Try to log in. Returns user dict if successful."""
    user = authenticate_user(username, password)
    if user:
        record_login(user["user_id"])
    return user


def get_forgot_password_questions(username):
    """Get required security questions for a username."""
    return get_security_questions(username)


def verify_forgot_password_answers(user_id, answer_1, answer_2):
    """Verify two required security answers. Returns True/False."""
    return verify_security_answers(user_id, answer_1, answer_2)


def reset_user_password(user_id, new_password):
    """Reset user password. Returns True/False."""
    return reset_password(user_id, new_password)
