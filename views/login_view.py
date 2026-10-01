"""
views/login_view.py
===============================================================
Login window with forgot password support.
===============================================================
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QSpacerItem, QSizePolicy, QDialog, QFormLayout, QHBoxLayout,
    QFrame, QBoxLayout, QGraphicsBlurEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent, QTimer
from PyQt6.QtGui import QFont, QPixmap, QColor, QIcon, QAction


class LoginView(QWidget):
    """Login screen with username, password, and forgot password."""

    login_successful = pyqtSignal(dict)
    _BASE_SIZE = QSize(860, 560)

    def __init__(self):
        super().__init__()
        self.setObjectName("LoginView")
        self.setWindowTitle("Comic Book Management — Login")
        self.setFixedSize(self._BASE_SIZE)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self._right_bg_source = QPixmap()
        self._eye_icon = self._icon_path("eye.svg")
        self._eye_off_icon = self._icon_path("eye_off.svg")
        self._login_in_progress = False
        self._login_anim_index = 0
        self._login_anim_timer = QTimer(self)
        self._login_anim_timer.setInterval(220)
        self._login_anim_timer.timeout.connect(self._animate_login_text)
        self.setupUi()
        self.retranslateUi()
        self._apply_styles()

    def setupUi(self):
        self.horizontalLayout_shell = QHBoxLayout(self)
        self.horizontalLayout_shell.setObjectName("horizontalLayout_shell")
        self.horizontalLayout_shell.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_shell.setSpacing(0)

        # Left branding panel
        self.frame_brand = QFrame(self)
        self.frame_brand.setObjectName("frame_brand")
        self.frame_brand.setFixedWidth(310)

        self.lbl_brand_bg = QLabel(self.frame_brand)
        self.lbl_brand_bg.setObjectName("lbl_brand_bg")
        self.lbl_brand_bg.setScaledContents(False)

        brand_bg_effect = QGraphicsBlurEffect(self.lbl_brand_bg)
        brand_bg_effect.setBlurRadius(5)
        self.lbl_brand_bg.setGraphicsEffect(brand_bg_effect)

        self.frame_brand_tint = QFrame(self.frame_brand)
        self.frame_brand_tint.setObjectName("frame_brand_tint")

        bg_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources",
            "login_background",
            "marvel-dc.jpg",
        )
        if os.path.exists(bg_path):
            self._right_bg_source = QPixmap(bg_path)

        self.brand_blob_top = QFrame(self.frame_brand)
        self.brand_blob_top.setObjectName("brand_blob_top")
        self.brand_blob_mid = QFrame(self.frame_brand)
        self.brand_blob_mid.setObjectName("brand_blob_mid")
        self.brand_blob_bottom = QFrame(self.frame_brand)
        self.brand_blob_bottom.setObjectName("brand_blob_bottom")

        self.layout_brand = QVBoxLayout(self.frame_brand)
        self.layout_brand.setContentsMargins(34, 36, 34, 36)
        self.layout_brand.setSpacing(8)

        self.layout_brand.addStretch()

        self.lbl_brand_title = QLabel(self.frame_brand)
        self.lbl_brand_title.setObjectName("lbl_brand_title")
        self.lbl_brand_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_brand.addWidget(self.lbl_brand_title)

        self.lbl_brand_subtitle = QLabel(self.frame_brand)
        self.lbl_brand_subtitle.setObjectName("lbl_brand_subtitle")
        self.lbl_brand_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_brand.addWidget(self.lbl_brand_subtitle)

        self.lbl_brand_divider = QLabel("────────────", self.frame_brand)
        self.lbl_brand_divider.setObjectName("lbl_brand_divider")
        self.lbl_brand_divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_brand.addWidget(self.lbl_brand_divider)

        self.lbl_brand_desc = QLabel(self.frame_brand)
        self.lbl_brand_desc.setObjectName("lbl_brand_desc")
        self.lbl_brand_desc.setWordWrap(True)
        self.lbl_brand_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_brand.addWidget(self.lbl_brand_desc)

        self.layout_brand.addStretch()
        self.lbl_brand_title.raise_()
        self.lbl_brand_subtitle.raise_()
        self.lbl_brand_divider.raise_()
        self.lbl_brand_desc.raise_()
        self._apply_brand_text_shadow(self.lbl_brand_title, blur=22, y=2, alpha=170)
        self._apply_brand_text_shadow(self.lbl_brand_subtitle, blur=16, y=1, alpha=130)
        self._apply_brand_text_shadow(self.lbl_brand_desc, blur=14, y=1, alpha=120)
        self.brand_blob_top.raise_()
        self.brand_blob_mid.raise_()
        self.brand_blob_bottom.raise_()
        self.horizontalLayout_shell.addWidget(self.frame_brand)

        # Right login panel
        self.frame_right = QFrame(self)
        self.frame_right.setObjectName("frame_right")

        self.layout_right_center = QHBoxLayout(self.frame_right)
        self.layout_right_center.setContentsMargins(12, 12, 12, 12)
        self.layout_right_center.setSpacing(0)

        self.layout_right_center.addStretch()

        self.frame_card = QFrame(self.frame_right)
        self.frame_card.setObjectName("frame_card")
        self.frame_card.setMaximumWidth(400)
        self.frame_card.setMinimumWidth(320)
        self.frame_card.setMaximumHeight(430)
        self.frame_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.verticalLayout_form = QVBoxLayout(self.frame_card)
        self.verticalLayout_form.setObjectName("verticalLayout_form")
        self.verticalLayout_form.setContentsMargins(24, 20, 24, 18)
        self.verticalLayout_form.setSpacing(6)
        self.verticalLayout_form.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_title = QLabel(self.frame_card)
        self.lbl_title.setObjectName("lbl_title")
        self.verticalLayout_form.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel(self.frame_card)
        self.lbl_subtitle.setObjectName("lbl_subtitle")
        self.verticalLayout_form.addWidget(self.lbl_subtitle)

        self.verticalLayout_form.addSpacing(5)

        self.lbl_username = QLabel(self.frame_card)
        self.lbl_username.setObjectName("lbl_username")
        self.verticalLayout_form.addWidget(self.lbl_username)

        self.txt_username = QLineEdit(self.frame_card)
        self.txt_username.setObjectName("txt_username")
        self.txt_username.setMinimumHeight(40)
        self.verticalLayout_form.addWidget(self.txt_username)

        self.verticalLayout_form.addSpacing(6)

        self.lbl_password = QLabel(self.frame_card)
        self.lbl_password.setObjectName("lbl_password")
        self.verticalLayout_form.addWidget(self.lbl_password)

        self.txt_password = QLineEdit(self.frame_card)
        self.txt_password.setObjectName("txt_password")
        self.txt_password.setMinimumHeight(40)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_password)
        self.verticalLayout_form.addWidget(self.txt_password)

        self.layout_forgot_row = QHBoxLayout()
        self.layout_forgot_row.setContentsMargins(0, 0, 0, 0)
        self.layout_forgot_row.setSpacing(0)
        self.layout_forgot_row.addStretch()

        self.btn_forgot = QPushButton(self.frame_card)
        self.btn_forgot.setObjectName("btn_forgot")
        self.btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout_forgot_row.addWidget(self.btn_forgot)
        self.verticalLayout_form.addLayout(self.layout_forgot_row)

        self.btn_login = QPushButton(self.frame_card)
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setMinimumHeight(42)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.verticalLayout_form.addWidget(self.btn_login)

        self.verticalLayout_form.addSpacing(8)

        self.lbl_footer = QLabel(self.frame_card)
        self.lbl_footer.setObjectName("lbl_footer")
        self.verticalLayout_form.addWidget(self.lbl_footer)

        self.layout_right_center.addWidget(self.frame_card)
        self.layout_right_center.setAlignment(self.frame_card, Qt.AlignmentFlag.AlignCenter)
        self.layout_right_center.addStretch()

        self.horizontalLayout_shell.addWidget(self.frame_right)
        self.horizontalLayout_shell.setStretch(0, 33)
        self.horizontalLayout_shell.setStretch(1, 67)

        self.lbl_brand_bg.lower()
        self.frame_brand_tint.lower()

        self.btn_login.clicked.connect(self._handle_login)
        self.txt_password.returnPressed.connect(self._handle_login)
        self.txt_username.returnPressed.connect(lambda: self.txt_password.setFocus())
        self.btn_forgot.clicked.connect(self._handle_forgot_password)

    def retranslateUi(self):
        self.lbl_brand_title.setText("Comic Book")
        self.lbl_brand_subtitle.setText("Management System")
        self.lbl_brand_desc.setText("Smart inventory, sales, and borrowing operations")

        self.lbl_title.setText("Welcome back")
        self.lbl_subtitle.setText("Login to your account")
        self.lbl_username.setText("Username")
        self.txt_username.setPlaceholderText("Enter your username")
        self.lbl_password.setText("Password")
        self.txt_password.setPlaceholderText("Enter your password")
        self.btn_login.setText("Login")
        self.btn_forgot.setText("Forgot Password?")
        self.lbl_footer.setText("© 2026 Comic Book Management")

    def _animate_login_text(self):
        states = ["Logging in", "Logging in.", "Logging in..", "Logging in..."]
        self.btn_login.setText(states[self._login_anim_index % len(states)])
        self._login_anim_index += 1

    def _set_login_loading(self, loading):
        self._login_in_progress = loading
        self.txt_username.setEnabled(not loading)
        self.txt_password.setEnabled(not loading)
        self.btn_forgot.setEnabled(not loading)
        self.btn_login.setEnabled(not loading)

        if loading:
            self._login_anim_index = 0
            self._animate_login_text()
            self._login_anim_timer.start()
        else:
            self._login_anim_timer.stop()
            self.btn_login.setText("Login")

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

    def _perform_login(self, username, password):
        from controllers.login_ctrl import attempt_login
        user = attempt_login(username, password)

        if user:
            self.login_successful.emit(user)
            return

        self._set_login_loading(False)
        QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
        self.txt_password.clear()
        self.txt_password.setFocus()

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget#LoginView {
                background-color: #eef1f5;
            }
            QFrame#frame_brand {
                background: qlineargradient(
                    x1:0, y1:0, x2:0.9, y2:1,
                    stop:0 #041632,
                    stop:0.55 #07204a,
                    stop:1 #041632
                );
            }
            QLabel#lbl_brand_bg {
                background-color: transparent;
            }
            QFrame#frame_brand_tint {
                background-color: rgba(4, 22, 50, 0.58);
            }
            QFrame#brand_blob_top {
                background-color: rgba(39, 123, 222, 0.18);
                border-radius: 120px;
            }
            QFrame#brand_blob_mid {
                background-color: rgba(77, 157, 255, 0.12);
                border-radius: 80px;
            }
            QFrame#brand_blob_bottom {
                background-color: rgba(30, 92, 173, 0.20);
                border-radius: 100px;
            }
            QLabel#lbl_brand_title {
                color: #f7fbff;
                font-size: 24px;
                font-weight: 800;
                letter-spacing: 0.4px;
            }
            QLabel#lbl_brand_subtitle {
                color: #c0d6f4;
                font-size: 14px;
                font-weight: 500;
            }
            QLabel#lbl_brand_divider {
                color: #78a8e8;
                font-size: 14px;
                padding-top: 6px;
                padding-bottom: 6px;
            }
            QLabel#lbl_brand_desc {
                color: #e7f0ff;
                font-size: 12px;
                line-height: 1.4;
                padding: 6px 18px;
            }
            QFrame#frame_right {
                background-color: #f4f6f9;
            }
            QFrame#frame_card {
                background-color: #ffffff;
                border: 1px solid #e5e8ee;
                border-radius: 12px;
            }
            QLabel#lbl_title {
                font-size: 22px;
                font-weight: 800;
                color: #1a2332;
                padding: 0;
                margin: 0;
            }
            QLabel#lbl_subtitle {
                font-size: 12px;
                color: #6f7f93;
                padding: 0 0 4px 0;
                margin: 0;
            }
            QLabel#lbl_username, QLabel#lbl_password {
                font-size: 12px;
                color: #324055;
                font-weight: bold;
                padding: 0;
                margin: 0;
            }
            QLineEdit {
                border: 1px solid #cfd7e3;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit#txt_password {
                lineedit-password-character: 8226;
            }
            QLineEdit:focus {
                border: 2px solid #2f7dd6;
            }
            QPushButton#btn_login {
                background-color: #1f8fe6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#btn_login:hover {
                background-color: #197fce;
            }
            QPushButton#btn_login:pressed {
                background-color: #156fb5;
            }
            QPushButton#btn_forgot {
                background-color: transparent;
                color: #2f8fdd;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                padding: 4px;
            }
            QPushButton#btn_forgot:hover {
                color: #1f6fb3;
            }
            QLabel#lbl_footer {
                color: #9aa5b5;
                font-size: 11px;
            }
        """)

    def _apply_brand_text_shadow(self, widget, blur=18, y=1, alpha=140):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y)
        shadow.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(shadow)

    def _handle_login(self):
        if self._login_in_progress:
            return

        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username:
            QMessageBox.warning(self, "Login Error", "Please enter your username.")
            self.txt_username.setFocus()
            return
        if not password:
            QMessageBox.warning(self, "Login Error", "Please enter your password.")
            self.txt_password.setFocus()
            return
        if len(username) < 3:
            QMessageBox.warning(self, "Login Error", "Username must be at least 3 characters.")
            self.txt_username.setFocus()
            return
        if len(password) < 4:
            QMessageBox.warning(self, "Login Error", "Password must be at least 4 characters.")
            self.txt_password.setFocus()
            return

        self._set_login_loading(True)
        QTimer.singleShot(120, lambda: self._perform_login(username, password))

    def _handle_forgot_password(self):
        dlg = ForgotPasswordDialog(self)
        dlg.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.horizontalLayout_shell.setDirection(QBoxLayout.Direction.LeftToRight)
        self.horizontalLayout_shell.setStretch(0, 33)
        self.horizontalLayout_shell.setStretch(1, 67)

        self.lbl_brand_bg.setGeometry(self.frame_brand.rect())
        self.frame_brand_tint.setGeometry(self.frame_brand.rect())
        if not self._right_bg_source.isNull():
            scaled = self._right_bg_source.scaled(
                self.frame_brand.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.lbl_brand_bg.setPixmap(scaled)

        w = self.frame_brand.width()
        h = self.frame_brand.height()
        self.brand_blob_top.setGeometry(-70, -50, 250, 250)
        self.brand_blob_mid.setGeometry(w - 110, int(h * 0.35), 170, 170)
        self.brand_blob_bottom.setGeometry(-50, h - 150, 220, 220)

        self.brand_blob_top.lower()
        self.brand_blob_mid.lower()
        self.brand_blob_bottom.lower()
        self.lbl_brand_bg.lower()
        self.frame_brand_tint.lower()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            blocked = (
                Qt.WindowState.WindowMaximized
                | Qt.WindowState.WindowFullScreen
            )
            if self.windowState() & blocked:
                self.showNormal()
                self.setFixedSize(self._BASE_SIZE)


class ForgotPasswordDialog(QDialog):
    """Multi-step forgot password dialog using security questions."""

    _BASE_WIDTH = 410
    _STEP_HEIGHTS = {
        "step1": 270,
        "step2": 390,
        "step3": 350,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setFixedSize(self._BASE_WIDTH, self._STEP_HEIGHTS["step1"])
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setSizeGripEnabled(False)
        self.setObjectName("ForgotPasswordDialog")
        self.user_id = None
        self.user_role = ""
        self._eye_icon = self._icon_path("eye.svg")
        self._eye_off_icon = self._icon_path("eye_off.svg")
        self._setup_step1()
        self._apply_styles()

    def _setup_step1(self):
        """Step 1: Enter username."""
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(18, 16, 18, 12)
        self.layout_main.setSpacing(8)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_step = QLabel("Step 1: Enter your username")
        self.lbl_step.setObjectName("lbl_step")
        self.layout_main.addWidget(self.lbl_step)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username")
        self.txt_username.setMinimumHeight(36)
        self.layout_main.addWidget(self.txt_username)

        # These are created but hidden until needed
        self.lbl_question_1 = QLabel()
        self.lbl_question_1.setObjectName("lbl_question")
        self.lbl_question_1.setWordWrap(True)
        self.lbl_question_1.hide()
        self.layout_main.addWidget(self.lbl_question_1)

        self.txt_answer_1 = QLineEdit()
        self.txt_answer_1.setPlaceholderText("Answer for question 1")
        self.txt_answer_1.setMinimumHeight(36)
        self.txt_answer_1.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_answer_1)
        self.txt_answer_1.hide()
        self.layout_main.addWidget(self.txt_answer_1)

        self.lbl_question_2 = QLabel()
        self.lbl_question_2.setObjectName("lbl_question")
        self.lbl_question_2.setWordWrap(True)
        self.lbl_question_2.hide()
        self.layout_main.addWidget(self.lbl_question_2)

        self.txt_answer_2 = QLineEdit()
        self.txt_answer_2.setPlaceholderText("Answer for question 2")
        self.txt_answer_2.setMinimumHeight(36)
        self.txt_answer_2.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_answer_2)
        self.txt_answer_2.hide()
        self.layout_main.addWidget(self.txt_answer_2)

        self.lbl_newpw = QLabel("Enter new password:")
        self.lbl_newpw.hide()
        self.layout_main.addWidget(self.lbl_newpw)

        self.txt_new_password = QLineEdit()
        self.txt_new_password.setPlaceholderText("New password (min 4 characters)")
        self.txt_new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_password.setMinimumHeight(36)
        self._attach_visibility_toggle(self.txt_new_password)
        self.txt_new_password.hide()
        self.layout_main.addWidget(self.txt_new_password)

        self.txt_confirm_password = QLineEdit()
        self.txt_confirm_password.setPlaceholderText("Confirm new password")
        self.txt_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirm_password.setMinimumHeight(36)
        self._attach_visibility_toggle(self.txt_confirm_password)
        self.txt_confirm_password.hide()
        self.layout_main.addWidget(self.txt_confirm_password)

        # Push actions to the bottom for cleaner dialog composition
        self.layout_main.addSpacing(4)
        self.layout_main.addStretch(1)

        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("btn_next")
        self.btn_next.setMinimumHeight(38)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self._step1_submit)
        self.layout_main.addWidget(self.btn_next)

        self.btn_verify = QPushButton("Verify")
        self.btn_verify.setObjectName("btn_verify")
        self.btn_verify.setMinimumHeight(38)
        self.btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verify.clicked.connect(self._step2_submit)
        self.btn_verify.hide()
        self.layout_main.addWidget(self.btn_verify)

        self.btn_reset = QPushButton("Reset Password")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setMinimumHeight(38)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self._step3_submit)
        self.btn_reset.hide()
        self.layout_main.addWidget(self.btn_reset)

        self._set_step_size("step1")

    def _set_step_size(self, step_name):
        h = self._STEP_HEIGHTS.get(step_name, self._STEP_HEIGHTS["step1"])
        self.setFixedSize(self._BASE_WIDTH, h)

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

    def _step1_submit(self):
        username = self.txt_username.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter your username.")
            return

        from controllers.login_ctrl import get_forgot_password_questions
        result = get_forgot_password_questions(username)

        if not result or not result.get("security_question_1") or not result.get("security_question_2"):
            QMessageBox.warning(self, "Not Found",
                                "Username not found or required security questions are not set.\n"
                                "Please contact an administrator.")
            return

        self.user_id = result["user_id"]
        self.user_role = result.get("role", "")

        self.lbl_step.setText("Step 2: Answer both security questions")
        self.txt_username.setEnabled(False)
        self.btn_next.hide()

        self.lbl_question_1.setText(f"Question 1: {result['security_question_1']}")
        self.lbl_question_1.show()
        self.txt_answer_1.show()
        self.lbl_question_2.setText(f"Question 2: {result['security_question_2']}")
        self.lbl_question_2.show()
        self.txt_answer_2.show()
        self.btn_verify.show()
        self._set_step_size("step2")
        self.txt_answer_1.setFocus()

    def _step2_submit(self):
        answer_1 = self.txt_answer_1.text().strip()
        answer_2 = self.txt_answer_2.text().strip()
        if not answer_1 or not answer_2:
            QMessageBox.warning(self, "Error", "Please answer both security questions.")
            return

        from controllers.login_ctrl import verify_forgot_password_answers
        if not verify_forgot_password_answers(self.user_id, answer_1, answer_2):
            if str(self.user_role).lower() == "admin":
                msg = (
                    "Security answers are incorrect.\n"
                    "For administrator accounts, please contact the system owner/database administrator."
                )
            else:
                msg = "Security answers are incorrect. Please contact an administrator."
            QMessageBox.critical(self, "Verification Failed", msg)
            return

        self.lbl_step.setText("Step 3: Set your new password")
        self.txt_answer_1.setEnabled(False)
        self.txt_answer_2.setEnabled(False)
        self.btn_verify.hide()

        self.lbl_newpw.show()
        self.txt_new_password.show()
        self.txt_confirm_password.show()
        self.btn_reset.show()
        self._set_step_size("step3")
        self.txt_new_password.setFocus()

    def _step3_submit(self):
        pw = self.txt_new_password.text().strip()
        confirm = self.txt_confirm_password.text().strip()

        if len(pw) < 4:
            QMessageBox.warning(self, "Error", "Password must be at least 4 characters.")
            return
        if pw != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        from controllers.login_ctrl import reset_user_password
        if reset_user_password(self.user_id, pw):
            QMessageBox.information(self, "Success",
                                    "Password has been reset successfully!\n"
                                    "You can now log in with your new password.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to reset password.")

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog#ForgotPasswordDialog {
                background-color: #f0f2f5;
            }
            QLabel#lbl_step {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                padding: 0;
                margin: 0;
            }
            QLabel#lbl_question {
                font-size: 12px;
                color: #555;
                padding: 2px 0;
                margin: 0;
            }
            QLineEdit {
                border: 1px solid #d0d4d8;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #3498db; }
            QPushButton#btn_next, QPushButton#btn_verify, QPushButton#btn_reset {
                background-color: #3498db; color: #ffffff; border: none;
                border-radius: 8px; font-size: 12px; font-weight: bold;
            }
            QPushButton#btn_next:hover, QPushButton#btn_verify:hover,
            QPushButton#btn_reset:hover { background-color: #2980b9; }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.layout_main.setContentsMargins(18, 14, 18, 14)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            blocked = (
                Qt.WindowState.WindowMaximized
                | Qt.WindowState.WindowFullScreen
            )
            if self.windowState() & blocked:
                self.showNormal()
                if self.btn_reset.isVisible():
                    self._set_step_size("step3")
                elif self.btn_verify.isVisible():
                    self._set_step_size("step2")
                else:
                    self._set_step_size("step1")
