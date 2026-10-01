"""
models/user_model.py

Handles all database operations for the users table,
including forgot password, login tracking, and archive functionality.
"""

import hashlib
import hmac
import os

from database.db_connection import get_connection


_PASSWORD_SCHEME = "pbkdf2_sha256"
_PASSWORD_ITERATIONS = 260000


def _hash_password(password):
    """Hash a plain-text password using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        _PASSWORD_ITERATIONS,
    ).hex()
    return f"{_PASSWORD_SCHEME}${_PASSWORD_ITERATIONS}${salt}${dk}"


def _normalize_security_answer(answer):
    return (answer or "").strip().lower()


def _is_hashed_password(value):
    return isinstance(value, str) and value.startswith(f"{_PASSWORD_SCHEME}$")


def _verify_password(plain_password, stored_password):
    """
    Verify password against hashed format.
    Falls back to plain-text comparison for legacy accounts.
    """
    if not stored_password:
        return False

    if _is_hashed_password(stored_password):
        try:
            _, iter_str, salt_hex, saved_hex = stored_password.split("$", 3)
            iterations = int(iter_str)
            computed_hex = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                iterations,
            ).hex()
            return hmac.compare_digest(computed_hex, saved_hex)
        except Exception:
            return False

    # Legacy plain-text support (for migration)
    return hmac.compare_digest(plain_password, stored_password)


def _hash_security_answer(answer):
    """Hash a normalized security answer using the same password scheme."""
    return _hash_password(_normalize_security_answer(answer))


def _verify_security_answer_value(input_answer, stored_answer):
    """Verify normalized security answer against hashed/plain stored value."""
    normalized = _normalize_security_answer(input_answer)

    if not stored_answer:
        return False

    if _is_hashed_password(stored_answer):
        return _verify_password(normalized, stored_answer)

    # Legacy plain-text support (case-insensitive, as before)
    return hmac.compare_digest(normalized, _normalize_security_answer(stored_answer))


def authenticate_user(username, password):
    """
    Check if the username and password are correct.
    Returns the user dict if valid, None otherwise.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND is_archived = 0"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if not user:
            return None

        if not _verify_password(password, user.get("password", "")):
            return None

        # Auto-upgrade legacy plain-text passwords after successful login.
        if not _is_hashed_password(user.get("password", "")):
            new_hash = _hash_password(password)
            cursor.execute(
                "UPDATE users SET password = %s WHERE user_id = %s",
                (new_hash, user["user_id"]),
            )
            conn.commit()
            user["password"] = new_hash

        return user
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return None
    finally:
        conn.close()


def get_all_users():
    """Get a list of all active users."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, full_name, role, email, borrow_limit, created_at "
            "FROM users WHERE is_archived = 0 ORDER BY user_id"
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return []
    finally:
        conn.close()


def add_user(username, password, full_name, role, email="",
             security_question_1="", security_answer_1="",
             security_question_2="", security_answer_2="",
             security_question_3="", security_answer_3="",
             borrow_limit=5):
    """Add a new user to the database."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        hashed_password = _hash_password(password)
        hashed_security_answer_1 = (
            _hash_security_answer(security_answer_1) if security_answer_1 else ""
        )
        hashed_security_answer_2 = (
            _hash_security_answer(security_answer_2) if security_answer_2 else ""
        )
        hashed_security_answer_3 = (
            _hash_security_answer(security_answer_3) if security_answer_3 else ""
        )
        query = """INSERT INTO users (username, password, full_name, role, email,
                   security_question, security_answer,
                   security_question_1, security_answer_1,
                   security_question_2, security_answer_2,
                   security_question_3, security_answer_3,
                   borrow_limit)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (username, hashed_password, full_name, role, email,
                               security_question_1, hashed_security_answer_1,
                               security_question_1, hashed_security_answer_1,
                               security_question_2, hashed_security_answer_2,
                               security_question_3, hashed_security_answer_3,
                               borrow_limit))
        conn.commit()
        return True
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return False
    finally:
        conn.close()


def update_user(user_id, username, full_name, role, password=None, email="",
                security_question_1="", security_answer_1="",
                security_question_2="", security_answer_2="",
                security_question_3="", security_answer_3="",
                borrow_limit=5):
    """Update an existing user."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT security_question, security_answer, "
            "security_question_1, security_answer_1, "
            "security_question_2, security_answer_2, "
            "security_question_3, security_answer_3 "
            "FROM users WHERE user_id = %s",
            (user_id,)
        )
        current = cursor.fetchone()
        if not current:
            return False

        final_q1 = security_question_1 if security_question_1 else (
            current.get("security_question_1") or current.get("security_question") or ""
        )
        final_a1 = _hash_security_answer(security_answer_1) if security_answer_1 else (
            current.get("security_answer_1") or current.get("security_answer") or ""
        )
        final_q2 = security_question_2 if security_question_2 else (
            current.get("security_question_2") or final_q1
        )
        final_a2 = _hash_security_answer(security_answer_2) if security_answer_2 else (
            current.get("security_answer_2") or final_a1
        )
        final_q3 = security_question_3 if security_question_3 else (
            current.get("security_question_3") or ""
        )
        final_a3 = _hash_security_answer(security_answer_3) if security_answer_3 else (
            current.get("security_answer_3") or ""
        )

        cursor = conn.cursor()
        if password:
            hashed_password = _hash_password(password)
            query = """UPDATE users SET username=%s, full_name=%s, role=%s, password=%s,
                       email=%s,
                       security_question=%s, security_answer=%s,
                       security_question_1=%s, security_answer_1=%s,
                       security_question_2=%s, security_answer_2=%s,
                       security_question_3=%s, security_answer_3=%s,
                       borrow_limit=%s
                       WHERE user_id=%s"""
            cursor.execute(
                query,
                (
                    username, full_name, role, hashed_password, email,
                    final_q1, final_a1,
                    final_q1, final_a1,
                    final_q2, final_a2,
                    final_q3, final_a3,
                    borrow_limit, user_id,
                ),
            )
        else:
            query = """UPDATE users SET username=%s, full_name=%s, role=%s,
                       email=%s,
                       security_question=%s, security_answer=%s,
                       security_question_1=%s, security_answer_1=%s,
                       security_question_2=%s, security_answer_2=%s,
                       security_question_3=%s, security_answer_3=%s,
                       borrow_limit=%s
                       WHERE user_id=%s"""
            cursor.execute(
                query,
                (
                    username, full_name, role, email,
                    final_q1, final_a1,
                    final_q1, final_a1,
                    final_q2, final_a2,
                    final_q3, final_a3,
                    borrow_limit, user_id,
                ),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return False
    finally:
        conn.close()


def delete_user(user_id):
    """Delete a user by ID."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return False
    finally:
        conn.close()


def get_security_questions(username):
    """Get two required security questions for forgot-password flow."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, role, "
            "COALESCE(NULLIF(security_question_1, ''), security_question) AS security_question_1, "
            "COALESCE(NULLIF(security_question_2, ''), "
            "COALESCE(NULLIF(security_question_1, ''), security_question)) AS security_question_2 "
            "FROM users "
            "WHERE username = %s AND is_archived = 0",
            (username,),
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return None
    finally:
        conn.close()


def verify_security_answers(user_id, answer_1, answer_2):
    """Verify two required security answers for forgot-password flow."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT "
            "COALESCE(NULLIF(security_answer_1, ''), security_answer) AS security_answer_1, "
            "COALESCE(NULLIF(security_answer_2, ''), "
            "COALESCE(NULLIF(security_answer_1, ''), security_answer)) AS security_answer_2 "
            "FROM users WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        if not result:
            return False

        stored_answer_1 = (result[0] or "").strip()
        stored_answer_2 = (result[1] or "").strip()

        valid_1 = _verify_security_answer_value(answer_1, stored_answer_1)
        valid_2 = _verify_security_answer_value(answer_2, stored_answer_2)
        if not (valid_1 and valid_2):
            return False

        # Auto-upgrade legacy plain-text security answers.
        if stored_answer_1 and not _is_hashed_password(stored_answer_1):
            cursor.execute(
                "UPDATE users SET security_answer = %s, security_answer_1 = %s WHERE user_id = %s",
                (_hash_security_answer(answer_1), _hash_security_answer(answer_1), user_id),
            )
        if stored_answer_2 and not _is_hashed_password(stored_answer_2):
            cursor.execute(
                "UPDATE users SET security_answer_2 = %s WHERE user_id = %s",
                (_hash_security_answer(answer_2), user_id),
            )

        conn.commit()

        return True
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return False
    finally:
        conn.close()


def reset_password(user_id, new_password):
    """Reset a user's password."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        hashed_password = _hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s",
                       (hashed_password, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return False
    finally:
        conn.close()


# ── Login Tracking ──────────────────────────────────────────

def record_login(user_id):
    """Record a login event."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO login_logs (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[LOGIN LOG ERROR] {e}")
        return False
    finally:
        conn.close()


def get_login_history(limit=50):
    """Get recent login history for all users."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT ll.log_id, u.username, u.full_name, u.role, ll.login_time "
            "FROM login_logs ll JOIN users u ON ll.user_id = u.user_id "
            "ORDER BY ll.login_time DESC LIMIT %s", (limit,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[LOGIN LOG ERROR] {e}")
        return []
    finally:
        conn.close()


# ── Archive / Soft Delete ───────────────────────────────────

def archive_user(user_id, archived_by):
    """Move a user to the archived_users table and soft-delete."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False

        cursor.execute(
            "INSERT INTO archived_users (original_user_id, username, password, full_name, email, role, archived_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user["user_id"], user["username"], user["password"],
             user["full_name"], user.get("email", ""), user["role"], archived_by)
        )
        cursor.execute("UPDATE users SET is_archived = 1 WHERE user_id = %s", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ARCHIVE ERROR] {e}")
        return False
    finally:
        conn.close()


def get_archived_users():
    """Get all archived user records."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT au.*, u.full_name AS archived_by_name "
            "FROM archived_users au "
            "LEFT JOIN users u ON au.archived_by = u.user_id "
            "ORDER BY au.archived_at DESC"
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[ARCHIVE ERROR] {e}")
        return []
    finally:
        conn.close()


def restore_user(archive_id):
    """Restore an archived user back to active status."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM archived_users WHERE archive_id = %s", (archive_id,))
        archived = cursor.fetchone()
        if not archived:
            return False

        original_id = archived["original_user_id"]
        cursor.execute("UPDATE users SET is_archived = 0 WHERE user_id = %s", (original_id,))
        cursor.execute("DELETE FROM archived_users WHERE archive_id = %s", (archive_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[RESTORE ERROR] {e}")
        return False
    finally:
        conn.close()


def get_user_borrow_limit(user_id):
    """Get the borrow limit for a user."""
    conn = get_connection()
    if not conn:
        return 5

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT borrow_limit FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 5
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return 5
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Get a single user by ID."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"[USER ERROR] {e}")
        return None
    finally:
        conn.close()


def migrate_plaintext_credentials():
    """
    One-time migration for legacy records:
    - Hash plain-text passwords
    - Hash plain-text security answers

    Returns a dict with update counts.
    """
    conn = get_connection()
    if not conn:
        return {"passwords": 0, "security_answers": 0}

    updates = {"passwords": 0, "security_answers": 0}

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, password, security_answer, security_answer_1, security_answer_2, security_answer_3 "
            "FROM users"
        )
        users = cursor.fetchall() or []

        for user in users:
            user_id = user["user_id"]
            pw = user.get("password") or ""
            sa = user.get("security_answer") or ""
            sa1 = user.get("security_answer_1") or ""
            sa2 = user.get("security_answer_2") or ""
            sa3 = user.get("security_answer_3") or ""

            if pw and not _is_hashed_password(pw):
                cursor.execute(
                    "UPDATE users SET password = %s WHERE user_id = %s",
                    (_hash_password(pw), user_id),
                )
                updates["passwords"] += 1

            if sa and not _is_hashed_password(sa):
                cursor.execute(
                    "UPDATE users SET security_answer = %s WHERE user_id = %s",
                    (_hash_security_answer(sa), user_id),
                )
                updates["security_answers"] += 1

            if sa1 and not _is_hashed_password(sa1):
                cursor.execute(
                    "UPDATE users SET security_answer_1 = %s WHERE user_id = %s",
                    (_hash_security_answer(sa1), user_id),
                )
                updates["security_answers"] += 1

            if sa2 and not _is_hashed_password(sa2):
                cursor.execute(
                    "UPDATE users SET security_answer_2 = %s WHERE user_id = %s",
                    (_hash_security_answer(sa2), user_id),
                )
                updates["security_answers"] += 1

            if sa3 and not _is_hashed_password(sa3):
                cursor.execute(
                    "UPDATE users SET security_answer_3 = %s WHERE user_id = %s",
                    (_hash_security_answer(sa3), user_id),
                )
                updates["security_answers"] += 1

        conn.commit()
        return updates
    except Exception as e:
        conn.rollback()
        print(f"[MIGRATION ERROR] {e}")
        return updates
    finally:
        conn.close()


def update_profile_settings(user_id, username=None, current_password=None,
                            new_password=None,
                            security_question=None, security_answer=None,
                            security_question_2=None, security_answer_2=None,
                            security_question_3=None, security_answer_3=None,
                            profile_image=None, remove_profile_image=False):
    """
    Update profile credentials/settings for the signed-in user.
    Fields not provided keep their current value.

    Returns (success, message).
    """
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, password, "
            "security_question, security_answer, "
            "security_question_1, security_answer_1, "
            "security_question_2, security_answer_2, "
            "security_question_3, security_answer_3, "
            "profile_image "
            "FROM users WHERE user_id = %s",
            (user_id,)
        )
        current = cursor.fetchone()
        if not current:
            return False, "User account not found."

        final_username = (username or current["username"]).strip()
        if not final_username:
            return False, "Username cannot be empty."

        if final_username != current["username"]:
            cursor.execute(
                "SELECT 1 FROM users WHERE username = %s AND user_id <> %s",
                (final_username, user_id)
            )
            if cursor.fetchone():
                return False, "Username is already taken."

        final_password = current["password"]
        if new_password:
            if not current_password:
                return False, "Current password is required to set a new password."
            if not _verify_password(current_password, current.get("password", "")):
                return False, "Current password is incorrect."
            final_password = _hash_password(new_password)

        final_question_1 = (
            current.get("security_question_1", "")
            or current.get("security_question", "")
        )
        if security_question is not None:
            final_question_1 = security_question

        final_answer_1 = (
            current.get("security_answer_1", "")
            or current.get("security_answer", "")
        )
        if security_answer is not None:
            final_answer_1 = _hash_security_answer(security_answer) if security_answer else ""

        final_question_2 = current.get("security_question_2", "")
        final_answer_2 = current.get("security_answer_2", "")
        if security_question_2 is not None:
            final_question_2 = security_question_2
        if security_answer_2 is not None:
            final_answer_2 = _hash_security_answer(security_answer_2) if security_answer_2 else ""

        final_question_3 = current.get("security_question_3", "")
        final_answer_3 = current.get("security_answer_3", "")
        if security_question_3 is not None:
            final_question_3 = security_question_3
        if security_answer_3 is not None:
            final_answer_3 = _hash_security_answer(security_answer_3) if security_answer_3 else ""

        final_profile_image = current.get("profile_image", "") or ""
        if remove_profile_image:
            final_profile_image = ""
        elif profile_image is not None:
            final_profile_image = profile_image

        cursor.execute(
            "UPDATE users SET username = %s, password = %s, "
            "security_question = %s, security_answer = %s, "
            "security_question_1 = %s, security_answer_1 = %s, "
            "security_question_2 = %s, security_answer_2 = %s, "
            "security_question_3 = %s, security_answer_3 = %s, "
            "profile_image = %s WHERE user_id = %s",
            (
                final_username, final_password,
                final_question_1, final_answer_1,
                final_question_1, final_answer_1,
                final_question_2, final_answer_2,
                final_question_3, final_answer_3,
                final_profile_image, user_id,
            )
        )
        conn.commit()
        return True, "Profile updated successfully."
    except Exception as e:
        conn.rollback()
        print(f"[PROFILE ERROR] {e}")
        return False, "Failed to update profile."
    finally:
        conn.close()
