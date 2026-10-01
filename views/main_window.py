"""
views/main_window.py
===============================================================
Main application window with sidebar navigation and stacked pages.
Follows setupUi / retranslateUi pattern (Qt Designer compatible).
All widgets have objectNames for easy conversion to a .ui file.

Widget hierarchy:
  QMainWindow (MainWindow)
    └─ centralWidget
        └─ horizontalLayout_main
            ├─ frame_sidebar  (fixed 230px)
            │   └─ verticalLayout_sidebar
            │       ├─ lbl_app_title
            │       ├─ line_separator
            │       ├─ lbl_nav_section
            │       ├─ btn_dashboard … btn_users  (nav buttons)
            │       ├─ spacer
                        │       ├─ btn_profile
            │       └─ btn_logout
            └─ stackedWidget  (content area)
===============================================================
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QMessageBox,
    QSpacerItem, QSizePolicy, QFrame, QTableWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QIcon
import os


class MainWindow(QMainWindow):
    """
    Main window with:
    - Left sidebar for navigation
    - Right content area using QStackedWidget
    """

    logout_signal = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self._base_min_size = QSize(1200, 750)
        self._windowed_locked_size = None
        self.setObjectName("MainWindow")
        self.setWindowTitle("Comic Book Management System")
        self.setMinimumSize(self._base_min_size)
        self.setupUi()
        self.retranslateUi()

    # =============================================================
    #  setupUi
    # =============================================================
    def setupUi(self):
        """Create sidebar and content area."""
        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.setCentralWidget(self.centralWidget)

        self.horizontalLayout_main = QHBoxLayout(self.centralWidget)
        self.horizontalLayout_main.setObjectName("horizontalLayout_main")
        self.horizontalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_main.setSpacing(0)

        # ── SIDEBAR ─────────────────────────────────────────
        self.frame_sidebar = QFrame(self.centralWidget)
        self.frame_sidebar.setObjectName("frame_sidebar")
        self.frame_sidebar.setMinimumWidth(210)
        self.frame_sidebar.setMaximumWidth(300)
        self.frame_sidebar.setFrameShape(QFrame.Shape.StyledPanel)

        self.verticalLayout_sidebar = QVBoxLayout(self.frame_sidebar)
        self.verticalLayout_sidebar.setObjectName("verticalLayout_sidebar")
        self.verticalLayout_sidebar.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_sidebar.setSpacing(4)

        # App title
        self.lbl_app_title = QLabel(self.frame_sidebar)
        self.lbl_app_title.setObjectName("lbl_app_title")
        self.lbl_app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_app_title.setMinimumHeight(76)
        self.verticalLayout_sidebar.addWidget(self.lbl_app_title)

        # Separator
        self.line_separator = QFrame(self.frame_sidebar)
        self.line_separator.setObjectName("line_separator")
        self.line_separator.setFrameShape(QFrame.Shape.HLine)
        self.line_separator.setStyleSheet("color: #3d5068;")
        self.verticalLayout_sidebar.addWidget(self.line_separator)

        # Navigation section label
        self.lbl_nav_section = QLabel(self.frame_sidebar)
        self.lbl_nav_section.setObjectName("lbl_nav_section")
        self.lbl_nav_section.setMinimumHeight(24)
        self.verticalLayout_sidebar.addWidget(self.lbl_nav_section)
        self.verticalLayout_sidebar.addSpacing(2)

        # ── Navigation buttons ──────────────────────────────
        is_admin = self.user["role"] == "Admin"

        icon_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources",
            "icons",
        )
        nav_icon_map = {
            "dashboard": os.path.join(icon_dir, "nav_dashboard.svg"),
            "comics": os.path.join(icon_dir, "nav_products.svg"),
            "pos": os.path.join(icon_dir, "nav_pos.svg"),
            "borrow": os.path.join(icon_dir, "nav_borrow.svg"),
            "sales_history": os.path.join(icon_dir, "nav_sales.svg"),
            "reports": os.path.join(icon_dir, "nav_reports.svg"),
            "users": os.path.join(icon_dir, "nav_users.svg"),
        }

        self.nav_buttons = []
        nav_items = [
            ("Dashboard",       "dashboard",      True),
            ("Products",        "comics",         True),
            ("Point of Sale",   "pos",            True),
            ("Borrow / Return", "borrow",         True),
            ("Sales History",   "sales_history",  True),
            ("Reports",         "reports",        is_admin),
            ("User Management", "users",          is_admin),
        ]

        for text, page_name, visible in nav_items:
            if not visible:
                continue
            btn = QPushButton(text, self.frame_sidebar)
            btn.setObjectName("navButton")
            btn.setMinimumHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("page", page_name)
            icon_path = nav_icon_map.get(page_name, "")
            if icon_path and os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(18, 18))
            btn.clicked.connect(self._on_nav_clicked)
            self.verticalLayout_sidebar.addWidget(btn)
            self.nav_buttons.append(btn)

        # Spacer
        self.verticalLayout_sidebar.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self.btn_profile = QPushButton(self.frame_sidebar)
        self.btn_profile.setObjectName("btn_profile")
        self.btn_profile.setMinimumHeight(60)
        self.btn_profile.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_profile.clicked.connect(self._open_profile)

        self.profile_layout = QHBoxLayout(self.btn_profile)
        self.profile_layout.setContentsMargins(12, 8, 12, 8)
        self.profile_layout.setSpacing(10)

        self.lbl_profile_avatar = QLabel(self.btn_profile)
        self.lbl_profile_avatar.setObjectName("lbl_profile_avatar")
        self.lbl_profile_avatar.setFixedSize(34, 34)
        self.lbl_profile_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_layout.addWidget(self.lbl_profile_avatar)

        self.profile_text_layout = QVBoxLayout()
        self.profile_text_layout.setContentsMargins(0, 0, 0, 0)
        self.profile_text_layout.setSpacing(2)

        self.lbl_profile_name = QLabel(self.btn_profile)
        self.lbl_profile_name.setObjectName("lbl_profile_name")
        self.profile_text_layout.addWidget(self.lbl_profile_name)

        self.lbl_profile_role = QLabel(self.btn_profile)
        self.lbl_profile_role.setObjectName("lbl_profile_role")
        self.profile_text_layout.addWidget(self.lbl_profile_role)

        self.profile_layout.addLayout(self.profile_text_layout)
        self.profile_layout.addStretch()

        self.lbl_profile_chevron = QLabel(self.btn_profile)
        self.lbl_profile_chevron.setObjectName("lbl_profile_chevron")
        self.lbl_profile_chevron.setText(">")
        self.lbl_profile_chevron.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.profile_layout.addWidget(self.lbl_profile_chevron)

        self.verticalLayout_sidebar.addWidget(self.btn_profile)

        # Logout
        self.btn_logout = QPushButton(self.frame_sidebar)
        self.btn_logout.setObjectName("btn_logout")
        self.btn_logout.setMinimumHeight(40)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_icon_path = os.path.join(icon_dir, "nav_logout.svg")
        if os.path.exists(logout_icon_path):
            self.btn_logout.setIcon(QIcon(logout_icon_path))
            self.btn_logout.setIconSize(QSize(18, 18))
        self.btn_logout.clicked.connect(self._handle_logout)
        self.verticalLayout_sidebar.addWidget(self.btn_logout)

        self.horizontalLayout_main.addWidget(self.frame_sidebar)

        # ── CONTENT AREA ────────────────────────────────────
        self.stacked_widget = QStackedWidget(self.centralWidget)
        self.stacked_widget.setObjectName("stackedWidget")
        self.horizontalLayout_main.addWidget(self.stacked_widget)

        # Page name -> index mapping
        self.page_map = {}

        # Stylesheet
        self._apply_styles()

    # =============================================================
    #  retranslateUi
    # =============================================================
    def retranslateUi(self):
        """Set translatable text for all widgets."""
        self.lbl_app_title.setText("COMIC BOOK\nMANAGEMENT")
        self.lbl_nav_section.setText("  NAVIGATION")
        self.refresh_profile_button()
        self.btn_logout.setText("Logout")

    def refresh_profile_button(self):
        username = self.user.get("username", "user")
        role = str(self.user.get("role", "")).upper()
        icon = self._build_profile_icon()
        self.lbl_profile_avatar.setPixmap(icon.pixmap(QSize(32, 32)))
        self.lbl_profile_name.setText(username)
        self.lbl_profile_role.setText(role)
        self.btn_profile.setText("")

    def _build_profile_icon(self):
        size = 32
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        img_path = self.user.get("profile_image", "") or ""
        abs_path = ""
        if img_path:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            abs_path = os.path.join(root, img_path.replace("/", os.sep))

        if abs_path and os.path.exists(abs_path):
            photo = QPixmap(abs_path)
            if not photo.isNull():
                scaled = photo.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                painter.drawPixmap(0, 0, scaled)
                painter.end()
                return QIcon(pix)

        painter.fillPath(path, QColor("#2f7dd6"))
        initial = (self.user.get("username") or "U").strip()[:1].upper()
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, initial)
        painter.end()
        return QIcon(pix)

    # ── Page management ─────────────────────────────────────
    def add_page(self, page_name, widget):
        """Register a page widget with a name."""
        index = self.stacked_widget.addWidget(widget)
        self.page_map[page_name] = index

    def switch_page(self, page_name):
        """Switch to a named page and highlight the active nav button."""
        if page_name in self.page_map:
            self.stacked_widget.setCurrentIndex(self.page_map[page_name])

            for btn in self.nav_buttons:
                is_active = btn.property("page") == page_name
                btn.setProperty("active", is_active)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

            profile_active = page_name == "profile"
            self.btn_profile.setProperty("active", profile_active)
            self.btn_profile.style().unpolish(self.btn_profile)
            self.btn_profile.style().polish(self.btn_profile)

    # ── Slots ───────────────────────────────────────────────
    def _on_nav_clicked(self):
        """Handle sidebar button click."""
        button = self.sender()
        page_name = button.property("page")
        self.switch_page(page_name)

    def _open_profile(self):
        self.switch_page("profile")

    def _handle_logout(self):
        """Confirm and log out."""
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        """Apply the sidebar and content area stylesheet."""
        self.setStyleSheet("""
            /* ── Sidebar ─────────────────────────────────── */
            QFrame#frame_sidebar {
                background-color: #1a2332;
                border: none;
            }
            QLabel#lbl_app_title {
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                padding: 14px 12px 8px 12px;
                letter-spacing: 0.8px;
            }
            QLabel#lbl_nav_section {
                color: #506a84;
                font-size: 10px;
                font-weight: bold;
                padding: 6px 0 2px 10px;
                letter-spacing: 1.5px;
            }

            /* ── Nav buttons ─────────────────────────────── */
            QPushButton#navButton {
                background-color: transparent;
                color: #b0bec5;
                border: none;
                text-align: left;
                padding: 0 0 0 14px;
                font-size: 14px;
                border-radius: 0;
                margin: 1px 0 1px 0;
            }
            QPushButton#navButton:hover {
                background-color: rgba(52, 152, 219, 0.12);
                color: #ffffff;
                border-radius: 10px;
            }
            QPushButton#navButton[active="true"] {
                background-color: rgba(52, 152, 219, 0.22);
                color: #ffffff;
                font-weight: bold;
                border-left: 3px solid #3498db;
                border-radius: 10px;
            }

            QPushButton#btn_profile {
                background-color: #13253f;
                color: #d7e6fb;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding: 0;
                margin: 8px 0 6px 0;
            }
            QPushButton#btn_profile:hover {
                background-color: #1b3251;
                color: #ffffff;
            }
            QPushButton#btn_profile[active="true"] {
                background-color: #214468;
                color: #ffffff;
            }
            QLabel#lbl_profile_name {
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#lbl_profile_role {
                color: #e3efff;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#lbl_profile_chevron {
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }

            /* ── Logout button ───────────────────────────── */
            QPushButton#btn_logout {
                background-color: transparent;
                color: #e57373;
                border: none;
                border-top: 1px solid rgba(255, 255, 255, 0.06);
                text-align: left;
                padding-left: 14px;
                font-size: 14px;
                font-weight: bold;
                margin: 2px 0 4px 0;
            }
            QPushButton#btn_logout:hover {
                background-color: rgba(229, 115, 115, 0.12);
                border-radius: 8px;
            }

            /* ── Content area ────────────────────────────── */
            QStackedWidget#stackedWidget {
                background-color: #f0f2f5;
            }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        w = self.width()
        if w >= 1900:
            sidebar_w = 285
            nav_h = 48
        elif w >= 1500:
            sidebar_w = 255
            nav_h = 46
        elif w >= 1200:
            sidebar_w = 235
            nav_h = 44
        else:
            sidebar_w = max(210, int(w * 0.2))
            nav_h = 40

        self.frame_sidebar.setMinimumWidth(sidebar_w)
        self.frame_sidebar.setMaximumWidth(sidebar_w)
        for btn in self.nav_buttons:
            btn.setMinimumHeight(nav_h)
        self.btn_profile.setMinimumHeight(max(54, nav_h + 8))
        self._apply_dynamic_scaling(w)

    def _apply_dynamic_scaling(self, window_width):
        """Adjust table density and shell icon sizing based on current window width."""
        if window_width >= 1800:
            icon_size = 36
            row_h = 36
            header_h = 42
        elif window_width >= 1400:
            icon_size = 34
            row_h = 32
            header_h = 38
        elif window_width >= 1100:
            icon_size = 32
            row_h = 30
            header_h = 36
        else:
            icon_size = 30
            row_h = 27
            header_h = 33

        self.lbl_profile_avatar.setFixedSize(icon_size + 2, icon_size + 2)
        self.lbl_profile_avatar.setPixmap(self._build_profile_icon().pixmap(QSize(icon_size, icon_size)))

        for table in self.stacked_widget.findChildren(QTableWidget):
            table.verticalHeader().setDefaultSectionSize(row_h)
            table.horizontalHeader().setMinimumHeight(header_h)

    def set_windowed_locked_size(self, size: QSize):
        """Remember preferred normal size without enforcing hard lock constraints."""
        self._windowed_locked_size = QSize(size.width(), size.height())

    def _apply_windowed_size_lock(self):
        if not self._windowed_locked_size:
            return
        self._release_windowed_size_lock()
        if self.windowState() == Qt.WindowState.WindowNoState:
            self.resize(self._windowed_locked_size)

    def _release_windowed_size_lock(self):
        self.setMinimumSize(self._base_min_size)
        self.setMaximumSize(QSize(16777215, 16777215))

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() != QEvent.Type.WindowStateChange:
            return

        state = self.windowState()
        if state & (Qt.WindowState.WindowMaximized | Qt.WindowState.WindowFullScreen):
            self._release_windowed_size_lock()
            return

        if state == Qt.WindowState.WindowNoState and self._windowed_locked_size:
            self._apply_windowed_size_lock()
