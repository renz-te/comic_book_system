"""
views/users_view.py
===============================================================
User Management page — CRUD with archive, restore, and login history.
===============================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QSizePolicy, QSpacerItem,
    QTabWidget, QSpinBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction, QIcon
import os
from config import SECURITY_QUESTIONS, DEFAULT_BORROW_LIMIT


# =================================================================
#  UserDialog
# =================================================================
class UserDialog(QDialog):
    """Add / Edit user dialog with extended fields."""

    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setObjectName("UserDialog")
        self.user_data = user_data
        self.setMinimumWidth(420)
        self._eye_icon = self._icon_path("eye.svg")
        self._eye_off_icon = self._icon_path("eye_off.svg")
        parent_w = parent.width() if parent else 1200
        parent_h = parent.height() if parent else 800
        dialog_w = max(440, int(parent_w * 0.42))
        dialog_h = max(430, int(parent_h * 0.56))
        self.setFixedSize(dialog_w, dialog_h)
        self.setupUi()
        self.retranslateUi()
        self._apply_styles()

        if user_data:
            self.txt_username.setText(user_data.get("username", ""))
            self.txt_full_name.setText(user_data.get("full_name", ""))
            idx = self.cmb_role.findText(user_data.get("role", "Staff"))
            if idx >= 0:
                self.cmb_role.setCurrentIndex(idx)

            sq1 = user_data.get("security_question_1", user_data.get("security_question", ""))
            sq2 = user_data.get("security_question_2", "")
            sq3 = user_data.get("security_question_3", "")

            sq1_idx = self.cmb_security_question_1.findText(sq1)
            if sq1_idx >= 0:
                self.cmb_security_question_1.setCurrentIndex(sq1_idx)
            sq2_idx = self.cmb_security_question_2.findText(sq2)
            if sq2_idx >= 0:
                self.cmb_security_question_2.setCurrentIndex(sq2_idx)
            sq3_idx = self.cmb_security_question_3.findText(sq3)
            if sq3_idx >= 0:
                self.cmb_security_question_3.setCurrentIndex(sq3_idx)

            self._original_q1 = sq1
            self._original_q2 = sq2
            self._original_q3 = sq3

            self.spn_borrow_limit.setValue(int(user_data.get("borrow_limit", DEFAULT_BORROW_LIMIT)))

    def setupUi(self):
        shell = QVBoxLayout(self)
        shell.setContentsMargins(20, 18, 20, 18)
        shell.setSpacing(10)

        self.lbl_title = QLabel("User Profile")
        self.lbl_title.setObjectName("lbl_dialog_title")
        shell.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Enter account details and access settings.")
        self.lbl_subtitle.setObjectName("lbl_dialog_subtitle")
        shell.addWidget(self.lbl_subtitle)

        form_card = QFrame()
        form_card.setObjectName("user_form_card")
        self.formLayout = QFormLayout(form_card)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setSpacing(12)
        self.formLayout.setContentsMargins(16, 16, 16, 16)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.txt_username = QLineEdit()
        self.txt_username.setObjectName("txt_username")
        self.txt_username.setMinimumHeight(35)
        self.formLayout.addRow("Username:", self.txt_username)

        self.txt_password = QLineEdit()
        self.txt_password.setObjectName("txt_password")
        self.txt_password.setMinimumHeight(35)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_password)
        self.formLayout.addRow("Password:", self.txt_password)

        self.txt_full_name = QLineEdit()
        self.txt_full_name.setObjectName("txt_full_name")
        self.txt_full_name.setMinimumHeight(35)
        self.formLayout.addRow("Full Name:", self.txt_full_name)

        self.cmb_role = QComboBox()
        self.cmb_role.setObjectName("cmb_role")
        self.cmb_role.setMinimumHeight(35)
        self.cmb_role.addItems(["Staff", "Admin"])
        self.formLayout.addRow("Role:", self.cmb_role)

        self.cmb_security_question_1 = QComboBox()
        self.cmb_security_question_1.setObjectName("cmb_security_question_1")
        self.cmb_security_question_1.setMinimumHeight(35)
        self.cmb_security_question_1.addItem("-- Select --")
        self.cmb_security_question_1.addItems(SECURITY_QUESTIONS)
        self.formLayout.addRow("Security Q1*:", self.cmb_security_question_1)

        self.txt_security_answer_1 = QLineEdit()
        self.txt_security_answer_1.setObjectName("txt_security_answer_1")
        self.txt_security_answer_1.setMinimumHeight(35)
        self.txt_security_answer_1.setPlaceholderText("Required answer #1")
        self.txt_security_answer_1.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_security_answer_1)
        self.formLayout.addRow("Security A1*:", self.txt_security_answer_1)

        self.cmb_security_question_2 = QComboBox()
        self.cmb_security_question_2.setObjectName("cmb_security_question_2")
        self.cmb_security_question_2.setMinimumHeight(35)
        self.cmb_security_question_2.addItem("-- Select --")
        self.cmb_security_question_2.addItems(SECURITY_QUESTIONS)
        self.formLayout.addRow("Security Q2*:", self.cmb_security_question_2)

        self.txt_security_answer_2 = QLineEdit()
        self.txt_security_answer_2.setObjectName("txt_security_answer_2")
        self.txt_security_answer_2.setMinimumHeight(35)
        self.txt_security_answer_2.setPlaceholderText("Required answer #2")
        self.txt_security_answer_2.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_security_answer_2)
        self.formLayout.addRow("Security A2*:", self.txt_security_answer_2)

        self.cmb_security_question_3 = QComboBox()
        self.cmb_security_question_3.setObjectName("cmb_security_question_3")
        self.cmb_security_question_3.setMinimumHeight(35)
        self.cmb_security_question_3.addItem("-- Optional --")
        self.cmb_security_question_3.addItems(SECURITY_QUESTIONS)
        self.formLayout.addRow("Security Q3:", self.cmb_security_question_3)

        self.txt_security_answer_3 = QLineEdit()
        self.txt_security_answer_3.setObjectName("txt_security_answer_3")
        self.txt_security_answer_3.setMinimumHeight(35)
        self.txt_security_answer_3.setPlaceholderText("Optional answer #3")
        self.txt_security_answer_3.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_security_answer_3)
        self.formLayout.addRow("Security A3:", self.txt_security_answer_3)

        self.spn_borrow_limit = QSpinBox()
        self.spn_borrow_limit.setObjectName("spn_borrow_limit")
        self.spn_borrow_limit.setMinimumHeight(35)
        self.spn_borrow_limit.setMinimum(1)
        self.spn_borrow_limit.setMaximum(50)
        self.spn_borrow_limit.setValue(DEFAULT_BORROW_LIMIT)
        self.formLayout.addRow("Borrow Limit:", self.spn_borrow_limit)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_save = QPushButton()
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setMinimumHeight(38)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton()
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setMinimumHeight(38)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.formLayout.addRow(btn_layout)
        shell.addWidget(form_card)

    def retranslateUi(self):
        self.setWindowTitle("Edit User" if self.user_data else "Add User")
        self.txt_username.setPlaceholderText("Enter username")
        self.txt_password.setPlaceholderText(
            "Enter password" if not self.user_data else "Leave blank to keep current")
        self.txt_full_name.setPlaceholderText("Enter full name")
        self.btn_save.setText("Save")
        self.btn_cancel.setText("Cancel")

    def _icon_path(self, filename):
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources",
            "icons",
            filename,
        )

    def _attach_visibility_toggle(self, line_edit):
        action = QAction(QIcon(self._eye_off_icon), "Show/Hide", line_edit)
        action.setCheckable(True)

        def on_toggle(checked):
            line_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
            action.setIcon(QIcon(self._eye_icon if checked else self._eye_off_icon))

        action.toggled.connect(on_toggle)
        line_edit.addAction(action, QLineEdit.ActionPosition.TrailingPosition)

    def get_data(self):
        sq1 = self.cmb_security_question_1.currentText()
        sq2 = self.cmb_security_question_2.currentText()
        sq3 = self.cmb_security_question_3.currentText()
        if sq1 == "-- Select --":
            sq1 = ""
        if sq2 == "-- Select --":
            sq2 = ""
        if sq3 == "-- Optional --":
            sq3 = ""
        return {
            "username": self.txt_username.text().strip(),
            "password": self.txt_password.text().strip(),
            "full_name": self.txt_full_name.text().strip(),
            "role": self.cmb_role.currentText(),
            "security_question_1": sq1,
            "security_answer_1": self.txt_security_answer_1.text().strip(),
            "security_question_2": sq2,
            "security_answer_2": self.txt_security_answer_2.text().strip(),
            "security_question_3": sq3,
            "security_answer_3": self.txt_security_answer_3.text().strip(),
            "borrow_limit": self.spn_borrow_limit.value(),
        }

    def _validate_and_accept(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        full_name = self.txt_full_name.text().strip()

        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            self.txt_username.setFocus()
            return
        if len(username) < 3:
            QMessageBox.warning(self, "Validation Error",
                                "Username must be at least 3 characters.")
            self.txt_username.setFocus()
            return
        if not self.user_data and not password:
            QMessageBox.warning(self, "Validation Error",
                                "Password is required for new users.")
            self.txt_password.setFocus()
            return
        if password and len(password) < 4:
            QMessageBox.warning(self, "Validation Error",
                                "Password must be at least 4 characters.")
            self.txt_password.setFocus()
            return
        if not full_name:
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            self.txt_full_name.setFocus()
            return

        data = self.get_data()
        if not data["security_question_1"] or not data["security_answer_1"]:
            if not self.user_data:
                QMessageBox.warning(self, "Validation Error",
                                    "Security Question 1 and Answer 1 are required.")
                self.cmb_security_question_1.setFocus()
                return
        if not data["security_question_2"] or not data["security_answer_2"]:
            if not self.user_data:
                QMessageBox.warning(self, "Validation Error",
                                    "Security Question 2 and Answer 2 are required.")
                self.cmb_security_question_2.setFocus()
                return
        if data["security_question_1"] == data["security_question_2"]:
            QMessageBox.warning(self, "Validation Error",
                                "Security Question 1 and Question 2 must be different.")
            self.cmb_security_question_2.setFocus()
            return

        if self.user_data:
            if data["security_question_1"] != getattr(self, "_original_q1", "") and not data["security_answer_1"]:
                QMessageBox.warning(self, "Validation Error",
                                    "Provide Answer 1 when changing Security Question 1.")
                self.txt_security_answer_1.setFocus()
                return
            if data["security_question_2"] != getattr(self, "_original_q2", "") and not data["security_answer_2"]:
                QMessageBox.warning(self, "Validation Error",
                                    "Provide Answer 2 when changing Security Question 2.")
                self.txt_security_answer_2.setFocus()
                return
            if data["security_question_3"] != getattr(self, "_original_q3", "") and not data["security_answer_3"]:
                QMessageBox.warning(self, "Validation Error",
                                    "Provide Answer 3 when changing Security Question 3.")
                self.txt_security_answer_3.setFocus()
                return
        if (data["security_question_3"] and not data["security_answer_3"]) or \
           (data["security_answer_3"] and not data["security_question_3"]):
            QMessageBox.warning(self, "Validation Error",
                                "Security Question 3 and Answer 3 must both be filled or both blank.")
            self.cmb_security_question_3.setFocus()
            return

        self.accept()

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog#UserDialog { background-color: #edf1f7; color: #1f2937; }
            QLabel#lbl_dialog_title {
                font-size: 22px;
                font-weight: 800;
                color: #13253f;
            }
            QLabel#lbl_dialog_subtitle {
                font-size: 12px;
                color: #5f7088;
                padding-bottom: 2px;
            }
            QFrame#user_form_card {
                background-color: #ffffff;
                border: 1px solid #d7deea;
                border-radius: 12px;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #ccd6e3; border-radius: 8px; padding: 8px 12px;
                background-color: #ffffff; color: #111827; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #1f7dd6; }
            QPushButton#btn_save {
                background-color: #1f7dd6; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 26px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_save:hover { background-color: #1a69b5; }
            QPushButton#btn_cancel {
                background-color: #6b7280; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 26px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_cancel:hover { background-color: #4b5563; }
        """)


# =================================================================
#  UsersView
# =================================================================
class UsersView(QWidget):
    """Page for managing system users with archive and login history."""

    def __init__(self, user):
        super().__init__()
        self.setObjectName("usersPage")
        self.user = user
        self.users_list = []
        self.archived_list = []
        self.setupUi()
        self.retranslateUi()
        self._apply_styles()

    def setupUi(self):
        self.verticalLayout_main = QVBoxLayout(self)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.verticalLayout_main.setSpacing(20)
        self.verticalLayout_main.setContentsMargins(32, 32, 32, 32)

        self.lbl_header = QLabel(self)
        self.lbl_header.setObjectName("lbl_header")
        self.verticalLayout_main.addWidget(self.lbl_header)

        # Action buttons
        self.horizontalLayout_actions = QHBoxLayout()
        self.horizontalLayout_actions.setObjectName("horizontalLayout_actions")
        self.horizontalLayout_actions.setSpacing(10)

        self.btn_add = QPushButton()
        self.btn_add.setObjectName("btn_add")
        self.btn_add.setMinimumHeight(36)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self._open_add_dialog)
        self.horizontalLayout_actions.addWidget(self.btn_add)

        self.btn_edit = QPushButton()
        self.btn_edit.setObjectName("btn_edit")
        self.btn_edit.setMinimumHeight(36)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.clicked.connect(self._open_edit_dialog)
        self.horizontalLayout_actions.addWidget(self.btn_edit)

        self.btn_delete = QPushButton()
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self._archive_user)
        self.horizontalLayout_actions.addWidget(self.btn_delete)

        self.horizontalLayout_actions.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.verticalLayout_main.addLayout(self.horizontalLayout_actions)

        # Tabs
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName("tab_widget")

        # ── Tab 1: Active Users ──
        self.tab_active = QWidget()
        tab_active_layout = QVBoxLayout(self.tab_active)
        self.table = QTableWidget()
        self.table.setObjectName("table")
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Full Name", "Role",
            "Borrow Limit", "Created"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        tab_active_layout.addWidget(self.table)
        self.tab_widget.addTab(self.tab_active, "Active Users")

        # ── Tab 2: Archived Users ──
        self.tab_archived = QWidget()
        tab_archived_layout = QVBoxLayout(self.tab_archived)

        btn_restore_row = QHBoxLayout()
        self.btn_restore = QPushButton("Restore User")
        self.btn_restore.setObjectName("btn_restore")
        self.btn_restore.setMinimumHeight(36)
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.clicked.connect(self._restore_user)
        btn_restore_row.addWidget(self.btn_restore)
        btn_restore_row.addStretch()
        tab_archived_layout.addLayout(btn_restore_row)

        self.table_archived = QTableWidget()
        self.table_archived.setObjectName("table_archived")
        self.table_archived.setColumnCount(5)
        self.table_archived.setHorizontalHeaderLabels([
            "Archive ID", "Username", "Full Name", "Role", "Archived At"
        ])
        self.table_archived.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_archived.setColumnHidden(0, True)
        self.table_archived.verticalHeader().setVisible(False)
        self.table_archived.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_archived.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_archived.setAlternatingRowColors(True)
        tab_archived_layout.addWidget(self.table_archived)
        self.tab_widget.addTab(self.tab_archived, "Archived Users")

        # ── Tab 3: Login History ──
        self.tab_login = QWidget()
        tab_login_layout = QVBoxLayout(self.tab_login)
        self.table_login = QTableWidget()
        self.table_login.setObjectName("table_login")
        self.table_login.setColumnCount(3)
        self.table_login.setHorizontalHeaderLabels([
            "Username", "Full Name", "Login Time"
        ])
        self.table_login.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_login.verticalHeader().setVisible(False)
        self.table_login.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_login.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_login.setAlternatingRowColors(True)
        tab_login_layout.addWidget(self.table_login)
        self.tab_widget.addTab(self.tab_login, "Login History")

        self.verticalLayout_main.addWidget(self.tab_widget)

    def retranslateUi(self):
        self.lbl_header.setText("User Management")
        self.btn_add.setText("Add User")
        self.btn_edit.setText("Edit User")
        self.btn_delete.setText("Archive User")

    # ── Data ────────────────────────────────────────────────
    def refresh_data(self):
        from controllers.users_ctrl import (
            load_all_users, get_archived_users_ctrl, get_login_history_ctrl
        )
        self.users_list = load_all_users()
        self._fill_active_table(self.users_list)

        self.archived_list = get_archived_users_ctrl()
        self._fill_archived_table(self.archived_list)

        login_history = get_login_history_ctrl(100)
        self._fill_login_table(login_history)

    def _fill_active_table(self, users):
        self.table.setRowCount(len(users))
        for r, u in enumerate(users):
            self.table.setItem(r, 0, QTableWidgetItem(str(u["user_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(u["username"]))
            self.table.setItem(r, 2, QTableWidgetItem(u.get("full_name", "")))
            self.table.setItem(r, 3, QTableWidgetItem(u.get("role", "staff")))
            self.table.setItem(r, 4, QTableWidgetItem(
                str(u.get("borrow_limit", DEFAULT_BORROW_LIMIT))))
            cd = u.get("created_at", "")
            if hasattr(cd, "strftime"):
                cd = cd.strftime("%d/%m/%Y %I:%M %p")
            self.table.setItem(r, 5, QTableWidgetItem(str(cd)))

    def _fill_archived_table(self, archived):
        self.table_archived.setRowCount(len(archived))
        for r, a in enumerate(archived):
            self.table_archived.setItem(r, 0, QTableWidgetItem(str(a.get("archive_id", ""))))
            self.table_archived.setItem(r, 1, QTableWidgetItem(a.get("username", "")))
            self.table_archived.setItem(r, 2, QTableWidgetItem(a.get("full_name", "")))
            self.table_archived.setItem(r, 3, QTableWidgetItem(a.get("role", "")))
            ad = a.get("archived_at", "")
            if hasattr(ad, "strftime"):
                ad = ad.strftime("%d/%m/%Y %I:%M %p")
            self.table_archived.setItem(r, 4, QTableWidgetItem(str(ad)))

    def _fill_login_table(self, history):
        self.table_login.setRowCount(len(history))
        for r, h in enumerate(history):
            self.table_login.setItem(r, 0, QTableWidgetItem(h.get("username", "")))
            self.table_login.setItem(r, 1, QTableWidgetItem(h.get("full_name", "")))
            lt = h.get("login_time", "")
            if hasattr(lt, "strftime"):
                lt = lt.strftime("%d/%m/%Y %I:%M %p")
            self.table_login.setItem(r, 2, QTableWidgetItem(str(lt)))

    # ── Handlers ────────────────────────────────────────────
    def _open_add_dialog(self):
        dlg = UserDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            from controllers.users_ctrl import add_user_ctrl
            if add_user_ctrl(data["username"], data["full_name"],
                             data["role"], data["password"],
                             data["security_question_1"], data["security_answer_1"],
                             data["security_question_2"], data["security_answer_2"],
                             data["security_question_3"], data["security_answer_3"],
                             data["borrow_limit"]):
                QMessageBox.information(self, "Success", "User added successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error",
                                     "Failed to add user. Username may already exist.")

    def _open_edit_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
            return

        user_row = self.users_list[row]
        from controllers.users_ctrl import get_user_details
        user_data = get_user_details(user_row["user_id"])
        if not user_data:
            QMessageBox.critical(self, "Error", "Failed to load user details.")
            return

        dlg = UserDialog(self, user_data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            from controllers.users_ctrl import update_user_ctrl
            password = data["password"] if data["password"] else None
            if update_user_ctrl(user_data["user_id"], data["username"],
                                data["full_name"], data["role"], password,
                                data["security_question_1"], data["security_answer_1"],
                                data["security_question_2"], data["security_answer_2"],
                                data["security_question_3"], data["security_answer_3"],
                                data["borrow_limit"]):
                QMessageBox.information(self, "Success", "User updated successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to update user.")

    def _archive_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a user to archive.")
            return

        user_data = self.users_list[row]
        if user_data["user_id"] == self.user["user_id"]:
            QMessageBox.warning(self, "Not Allowed", "You cannot archive your own account.")
            return

        reply = QMessageBox.question(
            self, "Confirm Archive",
            f"Archive user '{user_data['username']}'?\nThey will not be able to log in.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from controllers.users_ctrl import delete_user_ctrl
            if delete_user_ctrl(user_data["user_id"],
                                archived_by=self.user["user_id"]):
                QMessageBox.information(self, "Success", "User archived successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to archive user.")

    def _restore_user(self):
        row = self.table_archived.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection",
                                "Please select an archived user to restore.")
            return

        archive_data = self.archived_list[row]
        reply = QMessageBox.question(
            self, "Confirm Restore",
            f"Restore user '{archive_data.get('username', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from controllers.users_ctrl import restore_user_ctrl
            if restore_user_ctrl(archive_data["archive_id"]):
                QMessageBox.information(self, "Success", "User restored successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to restore user.")

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #usersPage { background-color: #f0f2f5; }
            QLabel#lbl_header {
                font-size: 20px; font-weight: bold; color: #2c3e50; padding-bottom: 4px;
            }
            QPushButton#btn_add {
                background-color: #3498db; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_add:hover { background-color: #2980b9; }
            QPushButton#btn_edit {
                background-color: #e67e22; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_edit:hover { background-color: #cf6d17; }
            QPushButton#btn_delete {
                background-color: #c0392b; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_delete:hover { background-color: #a93226; }
            QPushButton#btn_restore {
                background-color: #27ae60; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_restore:hover { background-color: #229954; }
            QTabWidget::pane { border: none; background: #f0f2f5; }
            QTabBar::tab {
                background: #dfe6e9; color: #555; padding: 10px 22px;
                border: none; border-top-left-radius: 8px; border-top-right-radius: 8px;
                margin-right: 3px; font-weight: bold; font-size: 12px;
            }
            QTabBar::tab:selected { background: #3498db; color: #fff; }
            QTableWidget {
                background-color: #ffffff; color: #333333; alternate-background-color: #f8f9fa;
                border: none; border-radius: 10px; gridline-color: #f0f0f0;
                font-size: 13px; padding: 4px;
            }
            QTableWidget::item { padding: 6px 8px; }
            QTableWidget::item:hover { background-color: #eaf2fb; }
            QTableWidget::item:selected { background-color: #3498db; color: #ffffff; }
            QHeaderView::section {
                background-color: #2c3e50; color: #ffffff; padding: 10px 8px;
                border: none; font-weight: bold; font-size: 12px;
            }
        """)
