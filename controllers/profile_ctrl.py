"""
controllers/profile_ctrl.py

Business logic for the My Profile page.
"""

from models.user_model import get_user_by_id, update_profile_settings


def get_profile_details(user_id):
    """Get current profile details for the signed-in user."""
    return get_user_by_id(user_id)


def update_profile_details(user_id, username, current_password=None,
                           new_password=None,
                           security_question_1=None, security_answer_1=None,
                           security_question_2=None, security_answer_2=None,
                           security_question_3=None, security_answer_3=None,
                           profile_image=None,
                           remove_profile_image=False):
    """Update signed-in user's own profile settings."""
    return update_profile_settings(
        user_id=user_id,
        username=username,
        current_password=current_password,
        new_password=new_password,
        security_question=security_question_1,
        security_answer=security_answer_1,
        security_question_2=security_question_2,
        security_answer_2=security_answer_2,
        security_question_3=security_question_3,
        security_answer_3=security_answer_3,
        profile_image=profile_image,
        remove_profile_image=remove_profile_image,
    )
