"""
views/profile_view.py

My Profile page for username/password/security Q&A updates.
"""

import os
import shutil
import uuid

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox,
    QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont, QAction, QIcon
from config import SECURITY_QUESTIONS


class ProfileView(QWidget):
    """Self-service profile settings page for signed-in user."""

    profile_updated = pyqtSignal(dict)

    def __init__(self, user):
        super().__init__()
        self.setObjectName("profilePage")
        self.user = user
        self._current_profile = None
        self._selected_profile_image = None
        self._remove_profile_image = False
        self._eye_icon = self._icon_path("eye.svg")
        self._eye_off_icon = self._icon_path("eye_off.svg")
        self.setupUi()
        self.retranslateUi()
        self._apply_styles()

    def setupUi(self):
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(28, 22, 28, 26)
        self.layout_main.setSpacing(8)

        self.lbl_header = QLabel(self)
        self.lbl_header.setObjectName("lbl_header")
        self.layout_main.addWidget(self.lbl_header)

        self.lbl_hint = QLabel(self)
        self.lbl_hint.setObjectName("lbl_hint")
        self.lbl_hint.setWordWrap(True)
        self.layout_main.addWidget(self.lbl_hint)

        self.layout_main.addSpacing(10)

        self.frame_card = QFrame(self)
        self.frame_card.setObjectName("frame_card")
        self.frame_card.setMaximumWidth(1020)
        self.frame_card.setMinimumWidth(700)
        self.form_layout = QVBoxLayout(self.frame_card)
        self.form_layout.setContentsMargins(28, 24, 28, 24)
        self.form_layout.setSpacing(8)

        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(16)

        self.lbl_avatar = QLabel()
        self.lbl_avatar.setObjectName("lbl_avatar")
        self.lbl_avatar.setMinimumSize(72, 72)
        self.lbl_avatar.setMaximumSize(128, 128)
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_row.addWidget(self.lbl_avatar)

        avatar_actions = QVBoxLayout()
        avatar_actions.setSpacing(10)
        avatar_actions.addStretch()

        self.btn_upload_avatar = QPushButton("Upload Photo")
        self.btn_upload_avatar.setObjectName("btn_avatar_action")
        self.btn_upload_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upload_avatar.clicked.connect(self._choose_profile_image)
        avatar_actions.addWidget(self.btn_upload_avatar)

        self.btn_remove_avatar = QPushButton("Remove Photo")
        self.btn_remove_avatar.setObjectName("btn_avatar_remove")
        self.btn_remove_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove_avatar.clicked.connect(self._remove_profile_image_action)
        avatar_actions.addWidget(self.btn_remove_avatar)
        avatar_actions.addStretch()

        avatar_row.addLayout(avatar_actions)
        avatar_row.addStretch()
        self.form_layout.addLayout(avatar_row)
        self.form_layout.addSpacing(12)

        self.lbl_account_section = QLabel("Account")
        self.lbl_account_section.setObjectName("lbl_section")
        self.form_layout.addWidget(self.lbl_account_section)

        self.lbl_username = QLabel("Username")
        self.form_layout.addWidget(self.lbl_username)
        self.txt_username = QLineEdit()
        self.txt_username.setMinimumHeight(40)
        self.form_layout.addWidget(self.txt_username)

        self.lbl_role = QLabel("Role")
        self.form_layout.addWidget(self.lbl_role)
        self.txt_role = QLineEdit()
        self.txt_role.setReadOnly(True)
        self.txt_role.setMinimumHeight(40)
        self.form_layout.addWidget(self.txt_role)

        self.line_pw = QFrame()
        self.line_pw.setFrameShape(QFrame.Shape.HLine)
        self.line_pw.setObjectName("section_divider")
        self.form_layout.addSpacing(10)
        self.form_layout.addWidget(self.line_pw)
        self.form_layout.addSpacing(6)

        self.lbl_password_section = QLabel("Password")
        self.lbl_password_section.setObjectName("lbl_section")
        self.form_layout.addWidget(self.lbl_password_section)

        self.lbl_current_password = QLabel("Current Password")
        self.form_layout.addWidget(self.lbl_current_password)
        self.txt_current_password = QLineEdit()
        self.txt_current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_current_password.setPlaceholderText("Enter current password")
        self.txt_current_password.setMinimumHeight(40)
        self._attach_visibility_toggle(self.txt_current_password)
        self.form_layout.addWidget(self.txt_current_password)

        self.lbl_password = QLabel("New Password")
        self.form_layout.addWidget(self.lbl_password)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Leave blank to keep current password")
        self.txt_password.setMinimumHeight(40)
        self._attach_visibility_toggle(self.txt_password)
        self.form_layout.addWidget(self.txt_password)

        self.lbl_confirm = QLabel("Confirm Password")
        self.form_layout.addWidget(self.lbl_confirm)
        self.txt_confirm = QLineEdit()
        self.txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirm.setPlaceholderText("Repeat new password")
        self.txt_confirm.setMinimumHeight(40)
        self._attach_visibility_toggle(self.txt_confirm)
        self.form_layout.addWidget(self.txt_confirm)

        self.line_security = QFrame()
        self.line_security.setFrameShape(QFrame.Shape.HLine)
        self.line_security.setObjectName("section_divider")
        self.form_layout.addSpacing(10)
        self.form_layout.addWidget(self.line_security)
        self.form_layout.addSpacing(6)

        self.lbl_security_section = QLabel("Security")
        self.lbl_security_section.setObjectName("lbl_section")
        self.form_layout.addWidget(self.lbl_security_section)

        self.lbl_question_1 = QLabel("Security Question 1*")
        self.form_layout.addWidget(self.lbl_question_1)
        self.cmb_question_1 = QComboBox()
        self.cmb_question_1.setMinimumHeight(40)
        self.cmb_question_1.addItem("-- Select --")
        self.cmb_question_1.addItems(SECURITY_QUESTIONS)
        self.form_layout.addWidget(self.cmb_question_1)

        self.lbl_answer_1 = QLabel("New Security Answer 1*")
        self.form_layout.addWidget(self.lbl_answer_1)
        self.txt_answer_1 = QLineEdit()
        self.txt_answer_1.setPlaceholderText("Leave blank to keep current answer #1")
        self.txt_answer_1.setMinimumHeight(40)
        self.txt_answer_1.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_answer_1)
        self.form_layout.addWidget(self.txt_answer_1)

        self.lbl_question_2 = QLabel("Security Question 2*")
        self.form_layout.addWidget(self.lbl_question_2)
        self.cmb_question_2 = QComboBox()
        self.cmb_question_2.setMinimumHeight(40)
        self.cmb_question_2.addItem("-- Select --")
        self.cmb_question_2.addItems(SECURITY_QUESTIONS)
        self.form_layout.addWidget(self.cmb_question_2)

        self.lbl_answer_2 = QLabel("New Security Answer 2*")
        self.form_layout.addWidget(self.lbl_answer_2)
        self.txt_answer_2 = QLineEdit()
        self.txt_answer_2.setPlaceholderText("Leave blank to keep current answer #2")
        self.txt_answer_2.setMinimumHeight(40)
        self.txt_answer_2.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_answer_2)
        self.form_layout.addWidget(self.txt_answer_2)

        self.lbl_question_3 = QLabel("Security Question 3 (Optional)")
        self.form_layout.addWidget(self.lbl_question_3)
        self.cmb_question_3 = QComboBox()
        self.cmb_question_3.setMinimumHeight(40)
        self.cmb_question_3.addItem("-- Optional --")
        self.cmb_question_3.addItems(SECURITY_QUESTIONS)
        self.form_layout.addWidget(self.cmb_question_3)

        self.lbl_answer_3 = QLabel("New Security Answer 3 (Optional)")
        self.form_layout.addWidget(self.lbl_answer_3)
        self.txt_answer_3 = QLineEdit()
        self.txt_answer_3.setPlaceholderText("Leave blank to keep current answer #3")
        self.txt_answer_3.setMinimumHeight(40)
        self.txt_answer_3.setEchoMode(QLineEdit.EchoMode.Password)
        self._attach_visibility_toggle(self.txt_answer_3)
        self.form_layout.addWidget(self.txt_answer_3)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 12, 0, 0)
        btn_row.addStretch()

        self.btn_save = QPushButton("Save Changes")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_changes)
        btn_row.addWidget(self.btn_save)

        self.form_layout.addLayout(btn_row)
        self.layout_card_wrap = QHBoxLayout()
        self.layout_card_wrap.setContentsMargins(0, 0, 0, 0)
        self.layout_card_wrap.addStretch()
        self.layout_card_wrap.addWidget(self.frame_card)
        self.layout_card_wrap.addStretch()
        self.layout_main.addLayout(self.layout_card_wrap)
        self.layout_main.addStretch()

    def retranslateUi(self):
        self.lbl_header.setText("My Profile")
        self.lbl_hint.setText("Update your username, password, and security questions.")

    def refresh_data(self):
        from controllers.profile_ctrl import get_profile_details

        profile = get_profile_details(self.user["user_id"])
        if not profile:
            return

        self._current_profile = profile
        self.txt_username.setText(profile.get("username", ""))
        self.txt_role.setText(profile.get("role", ""))

        self._selected_profile_image = None
        self._remove_profile_image = False
        self._set_avatar_preview(profile.get("profile_image", ""), profile.get("username", ""))

        q1 = profile.get("security_question_1", profile.get("security_question", "")) or ""
        q2 = profile.get("security_question_2", "") or ""
        q3 = profile.get("security_question_3", "") or ""

        idx1 = self.cmb_question_1.findText(q1)
        self.cmb_question_1.setCurrentIndex(idx1 if idx1 >= 0 else 0)

        idx2 = self.cmb_question_2.findText(q2)
        self.cmb_question_2.setCurrentIndex(idx2 if idx2 >= 0 else 0)

        idx3 = self.cmb_question_3.findText(q3)
        self.cmb_question_3.setCurrentIndex(idx3 if idx3 >= 0 else 0)

        self._original_q1 = q1
        self._original_q2 = q2
        self._original_q3 = q3

        self.txt_password.clear()
        self.txt_current_password.clear()
        self.txt_confirm.clear()
        self.txt_answer_1.clear()
        self.txt_answer_2.clear()
        self.txt_answer_3.clear()

    def _save_changes(self):
        username = self.txt_username.text().strip()
        current_password = self.txt_current_password.text().strip()
        new_password = self.txt_password.text().strip()
        confirm = self.txt_confirm.text().strip()
        q1 = self.cmb_question_1.currentText().strip()
        if q1 == "-- Select --":
            q1 = ""
        q2 = self.cmb_question_2.currentText().strip()
        if q2 == "-- Select --":
            q2 = ""
        q3 = self.cmb_question_3.currentText().strip()
        if q3 == "-- Optional --":
            q3 = ""

        a1 = self.txt_answer_1.text().strip()
        a2 = self.txt_answer_2.text().strip()
        a3 = self.txt_answer_3.text().strip()

        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            self.txt_username.setFocus()
            return
        if len(username) < 3:
            QMessageBox.warning(self, "Validation Error", "Username must be at least 3 characters.")
            self.txt_username.setFocus()
            return

        if new_password or confirm:
            if not current_password:
                QMessageBox.warning(self, "Validation Error", "Current password is required.")
                self.txt_current_password.setFocus()
                return
            if len(new_password) < 4:
                QMessageBox.warning(self, "Validation Error", "New password must be at least 4 characters.")
                self.txt_password.setFocus()
                return
            if new_password != confirm:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                self.txt_confirm.setFocus()
                return

        if not q1:
            QMessageBox.warning(self, "Validation Error", "Security Question 1 is required.")
            self.cmb_question_1.setFocus()
            return
        if not q2:
            QMessageBox.warning(self, "Validation Error", "Security Question 2 is required.")
            self.cmb_question_2.setFocus()
            return
        if q1 == q2:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Security Question 1 and Question 2 must be different.",
            )
            self.cmb_question_2.setFocus()
            return

        if (q3 and not a3) or (a3 and not q3):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Security Question 3 and Answer 3 must both be filled or both blank.",
            )
            self.cmb_question_3.setFocus()
            return

        current_profile = self._current_profile or {}
        current_a1 = (current_profile.get("security_answer_1") or current_profile.get("security_answer") or "")
        current_a2 = (current_profile.get("security_answer_2") or "")

        if q1 != getattr(self, "_original_q1", "") and not a1:
            QMessageBox.warning(self, "Validation Error", "Provide Answer 1 when changing Security Question 1.")
            self.txt_answer_1.setFocus()
            return
        if q2 != getattr(self, "_original_q2", "") and not a2:
            QMessageBox.warning(self, "Validation Error", "Provide Answer 2 when changing Security Question 2.")
            self.txt_answer_2.setFocus()
            return
        if q3 != getattr(self, "_original_q3", "") and not a3 and q3:
            QMessageBox.warning(self, "Validation Error", "Provide Answer 3 when changing Security Question 3.")
            self.txt_answer_3.setFocus()
            return

        if not a1 and not current_a1:
            QMessageBox.warning(self, "Validation Error", "Security Answer 1 is required.")
            self.txt_answer_1.setFocus()
            return
        if not a2 and not current_a2:
            QMessageBox.warning(self, "Validation Error", "Security Answer 2 is required.")
            self.txt_answer_2.setFocus()
            return

        password_payload = new_password if new_password else None

        from controllers.profile_ctrl import update_profile_details
        ok, msg = update_profile_details(
            user_id=self.user["user_id"],
            username=username,
            current_password=current_password if (new_password or confirm) else None,
            new_password=password_payload,
            security_question_1=q1,
            security_answer_1=(a1 if a1 else None),
            security_question_2=q2,
            security_answer_2=(a2 if a2 else None),
            security_question_3=(q3 if q3 else ""),
            security_answer_3=(a3 if a3 else None),
            profile_image=self._selected_profile_image,
            remove_profile_image=self._remove_profile_image,
        )
        if not ok:
            QMessageBox.critical(self, "Update Failed", msg)
            return

        from controllers.profile_ctrl import get_profile_details
        updated_profile = get_profile_details(self.user["user_id"])
        if updated_profile:
            self.user.update(updated_profile)
        QMessageBox.information(self, "Success", msg)
        self.profile_updated.emit(self.user)
        self.refresh_data()

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

    def _choose_profile_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not file_path:
            return

        profiles_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources",
            "profiles",
        )
        os.makedirs(profiles_dir, exist_ok=True)

        ext = os.path.splitext(file_path)[1].lower() or ".png"
        filename = f"u{self.user['user_id']}_{uuid.uuid4().hex[:10]}{ext}"
        dest = os.path.join(profiles_dir, filename)
        try:
            shutil.copyfile(file_path, dest)
        except Exception as exc:
            QMessageBox.critical(self, "Upload Failed", f"Could not save image.\n{exc}")
            return

        rel_path = f"resources/profiles/{filename}"
        self._selected_profile_image = rel_path
        self._remove_profile_image = False
        self._set_avatar_preview(rel_path, self.txt_username.text().strip())

    def _remove_profile_image_action(self):
        self._selected_profile_image = None
        self._remove_profile_image = True
        self._set_avatar_preview("", self.txt_username.text().strip())

    def _set_avatar_preview(self, image_path, name_text):
        size = self.lbl_avatar.width()
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addEllipse(0, 0, size, size)
        painter.setClipPath(clip)

        abs_path = ""
        if image_path:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            abs_path = os.path.join(root, image_path.replace("/", os.sep))

        if abs_path and os.path.exists(abs_path):
            img = QPixmap(abs_path)
            if not img.isNull():
                scaled = img.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                    Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(0, 0, scaled)
                painter.end()
                self.lbl_avatar.setPixmap(pix)
                return

        painter.fillPath(clip, QColor("#2f7dd6"))
        initial = (name_text[:1] or "U").upper()
        painter.setPen(Qt.GlobalColor.white)
        font = QFont("Inter", 30, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, initial)
        painter.end()
        self.lbl_avatar.setPixmap(pix)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        target = max(72, min(112, int(self.frame_card.width() * 0.14)))
        self.lbl_avatar.resize(target, target)
        profile = self._current_profile or {}
        image_path = self._selected_profile_image
        if image_path is None and not self._remove_profile_image:
            image_path = profile.get("profile_image", "")
        name_text = self.txt_username.text().strip() or profile.get("username", "")
        self._set_avatar_preview(image_path or "", name_text)

    def _apply_styles(self):
        self.setStyleSheet("""
            #profilePage { background-color: #f0f2f5; }
            QLabel#lbl_header {
                font-size: 22px; font-weight: bold; color: #2c3e50;
            }
            QLabel#lbl_hint {
                font-size: 13px; color: #6b7a8f;
            }
            QFrame#frame_card {
                background-color: #ffffff;
                border: 1px solid #e1e6ef;
                border-radius: 14px;
            }
            QLabel#lbl_section {
                font-size: 11px;
                color: #7a8ca3;
                font-weight: bold;
                letter-spacing: 0.8px;
                text-transform: uppercase;
                padding-top: 2px;
            }
            QFrame#section_divider {
                background-color: #e9edf3;
                max-height: 1px;
                border: none;
            }
            QLabel#lbl_avatar {
                border: 2px solid #d5dce6;
                border-radius: 44px;
                background-color: #eef2f7;
            }
            QLabel {
                font-size: 13px;
                color: #2f3f52;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #d0d4d8;
                border-radius: 8px;
                padding: 9px 12px;
                background-color: #ffffff;
                color: #333333;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QPushButton#btn_save {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 22px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#btn_save:hover { background-color: #2980b9; }
            QPushButton#btn_avatar_action {
                background-color: #1abc9c;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#btn_avatar_action:hover { background-color: #16a085; }
            QPushButton#btn_avatar_remove {
                background-color: #95a5a6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#btn_avatar_remove:hover { background-color: #7f8c8d; }
        """)
