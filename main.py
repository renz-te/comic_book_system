"""
main.py

Entry point for the Comic Book Management System with POS.
Starts the login window and transitions to the main window on success.

Includes automatic checks for:
  1. Required Python packages (PyQt6, mysql-connector-python)
  2. MySQL server availability
  3. Database existence (auto-creates from .sql if missing)
"""

import sys
import os
import subprocess

# Add project root to sys.path so all imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ── Step 1: Check required packages before any imports ──────
def _check_dependencies():
    """
    Verify that all required packages are installed.
    Offers to install them automatically if missing.
    """
    required = {
        "PyQt6":                   "PyQt6",
        "PyQt6.QtCharts":          "PyQt6-Charts",
        "mysql.connector":         "mysql-connector-python",
    }
    missing = []
    for module, pip_name in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        return True  # All good

    # Try to install automatically
    print("=" * 50)
    print("  MISSING PACKAGES DETECTED")
    print("=" * 50)
    for pkg in missing:
        print(f"  - {pkg}")
    print()
    print("Installing missing packages now ...")
    print()

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        print()
        print("Packages installed successfully!")
        print("Please restart the application.")
        input("Press Enter to exit ...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Could not install packages: {e}")
        print("Please install them manually:")
        print(f"  pip install {' '.join(missing)}")
        input("Press Enter to exit ...")
        sys.exit(1)


_check_dependencies()

# ── Now safe to import project modules ──────────────────────
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase
from PyQt6.QtCore import QSize, QTimer
from config import APP_TITLE
from views.login_view import LoginView
from views.main_window import MainWindow
from views.dashboard_view import DashboardView
from views.comics_view import ComicsView
from views.pos_view import POSView
from views.borrow_view import BorrowView
from views.sales_history_view import SalesHistoryView
from views.reports_view import ReportsView
from views.users_view import UsersView
from views.profile_view import ProfileView
from database.db_connection import (
    test_connection, database_exists, create_database_from_sql,
    run_migrations
)
from models.user_model import migrate_plaintext_credentials


class App:
    """
    Main application controller.
    Manages the login flow and the main window with all pages.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")  # Clean cross-platform style
        self._pending_logout_notice = False

        # ── Load bundled Inter font for modern sans-serif look ───
        font_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resources", "fonts"
        )
        for ttf in ("Inter-Regular.ttf", "Inter-Medium.ttf",
                    "Inter-SemiBold.ttf", "Inter-Bold.ttf"):
            path = os.path.join(font_dir, ttf)
            if os.path.exists(path):
                QFontDatabase.addApplicationFont(path)

        # Set an adaptive application font size based on screen width.
        screen = self.app.primaryScreen()
        screen_w = screen.availableGeometry().width() if screen else 1366
        if screen_w >= 1900:
            base_font_size = 11
        elif screen_w >= 1360:
            base_font_size = 10
        else:
            base_font_size = 9
        self.app.setFont(QFont("Inter", base_font_size))

        # Force a light-mode palette so the UI is consistent
        # regardless of the OS dark / light mode setting.
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window,          QColor("#f0f2f5"))
        p.setColor(QPalette.ColorRole.WindowText,      QColor("#333333"))
        p.setColor(QPalette.ColorRole.Base,             QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.AlternateBase,    QColor("#f8f9fa"))
        p.setColor(QPalette.ColorRole.Text,             QColor("#333333"))
        p.setColor(QPalette.ColorRole.Button,           QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.ButtonText,       QColor("#333333"))
        p.setColor(QPalette.ColorRole.BrightText,       QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.Highlight,        QColor("#3498db"))
        p.setColor(QPalette.ColorRole.HighlightedText,  QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.ToolTipBase,      QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.ToolTipText,      QColor("#333333"))
        p.setColor(QPalette.ColorRole.PlaceholderText,  QColor("#999999"))
        p.setColor(QPalette.ColorRole.Link,             QColor("#3498db"))
        p.setColor(QPalette.ColorRole.Light,            QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.Midlight,         QColor("#e8e8e8"))
        p.setColor(QPalette.ColorRole.Mid,              QColor("#c0c0c0"))
        p.setColor(QPalette.ColorRole.Dark,             QColor("#a0a0a0"))
        p.setColor(QPalette.ColorRole.Shadow,           QColor("#707070"))
        for role in (QPalette.ColorRole.WindowText,
                     QPalette.ColorRole.Text,
                     QPalette.ColorRole.ButtonText):
            p.setColor(QPalette.ColorGroup.Disabled, role, QColor("#aaaaaa"))
        self.app.setPalette(p)

        # Prevent app from quitting when login window closes
        # before the main window opens
        self.app.setQuitOnLastWindowClosed(False)

        # ── Step 2: Database check ──────────────────────────
        # Try connecting. If the database doesn't exist yet,
        # offer to create it automatically from the .sql file.
        if not test_connection():
            # MySQL server might be up but the database missing
            if database_exists():
                # Database exists but connection still fails — real error
                QMessageBox.critical(
                    None, "Database Error",
                    "Could not connect to the MySQL database.\n\n"
                    "Please make sure:\n"
                    "1. XAMPP is running\n"
                    "2. MySQL service is started\n"
                    "3. Check config.py for correct settings\n\n"
                    "The application will now exit."
                )
                sys.exit(1)

            # Database does not exist — offer to create it
            reply = QMessageBox.question(
                None, "Database Not Found",
                "The database does not exist yet.\n\n"
                "Would you like to create it automatically?\n"
                "(This will import database/comic_book_system.sql)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                if create_database_from_sql():
                    QMessageBox.information(
                        None, "Success",
                        "Database created successfully!\n"
                        "Default accounts:\n"
                        "  admin / admin123\n"
                        "  staff / staff123"
                    )
                else:
                    QMessageBox.critical(
                        None, "Error",
                        "Failed to create the database.\n\n"
                        "Please import the SQL file manually\n"
                        "via phpMyAdmin."
                    )
                    sys.exit(1)
            else:
                QMessageBox.information(
                    None, "Setup Required",
                    "Please import database/comic_book_system.sql\n"
                    "into phpMyAdmin, then restart the application."
                )
                sys.exit(0)

            # Verify the connection works now
            if not test_connection():
                QMessageBox.critical(
                    None, "Database Error",
                    "Database was created but the connection\n"
                    "still fails. Please check config.py."
                )
                sys.exit(1)

        # Run database migrations (add new columns/tables safely)
        run_migrations()

        # One-time security upgrade for legacy plain-text credentials.
        migrated = migrate_plaintext_credentials()
        if migrated["passwords"] or migrated["security_answers"]:
            print(
                f"[SECURITY] Upgraded credentials: "
                f"{migrated['passwords']} password(s), "
                f"{migrated['security_answers']} security answer(s)."
            )

        # Ensure the covers directory exists
        os.makedirs(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "resources", "covers"),
            exist_ok=True
        )
        os.makedirs(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "resources", "profiles"),
            exist_ok=True
        )

        # Start with the login window
        self.login_window = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        """Show the login window."""
        # Close main window if it exists
        if self.main_window:
            self.main_window.close()
            self.main_window = None
            self._pending_logout_notice = True

        self.login_window = LoginView()
        self._fit_window_to_screen(self.login_window, max_width_ratio=0.68, max_height_ratio=0.76)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

        if self._pending_logout_notice:
            QTimer.singleShot(
                0,
                lambda: QMessageBox.information(
                    self.login_window,
                    "Logout",
                    "Logout successful.",
                ),
            )
            self._pending_logout_notice = False

    def on_login_success(self, user):
        """
        Called when the user logs in successfully.
        Sets up the main window with all pages based on user role.
        """
        QMessageBox.information(self.login_window, "Login", "Login successful.")

        # Close login window
        self.login_window.close()

        # Create main window
        self.main_window = MainWindow(user)
        self.main_window.logout_signal.connect(self.show_login)

        # ── Create all page views ───────────────────────────
        is_admin = user["role"] == "Admin"

        # Dashboard — available to all
        self.dashboard_view = DashboardView()
        self.main_window.add_page("dashboard", self.dashboard_view)

        # Comics — available to all
        self.comics_view = ComicsView()
        self.main_window.add_page("comics", self.comics_view)

        # POS — available to all
        self.pos_view = POSView(user)
        self.main_window.add_page("pos", self.pos_view)

        # Borrow / Return — available to all
        self.borrow_view = BorrowView(user)
        self.main_window.add_page("borrow", self.borrow_view)

        # Sales History — available to all
        self.sales_history_view = SalesHistoryView(user)
        self.main_window.add_page("sales_history", self.sales_history_view)

        # My Profile — available to all
        self.profile_view = ProfileView(user)
        self.profile_view.profile_updated.connect(self._on_profile_updated)
        self.main_window.add_page("profile", self.profile_view)

        # Reports — admin only
        if is_admin:
            self.reports_view = ReportsView(user)
            self.main_window.add_page("reports", self.reports_view)

        # Users — admin only
        if is_admin:
            self.users_view = UsersView(user)
            self.main_window.add_page("users", self.users_view)

        # ── Connect page switching to data refresh ──────────
        self.main_window.stacked_widget.currentChanged.connect(self.on_page_changed)

        # Show main window and start on dashboard
        self._fit_window_to_screen(self.main_window, max_width_ratio=0.94, max_height_ratio=0.92)
        self.main_window.showMaximized()
        self.main_window.switch_page("dashboard")
        self.dashboard_view.refresh_data()

    def _fit_window_to_screen(self, window, max_width_ratio=0.9, max_height_ratio=0.9):
        """Set an adaptive startup size based on current screen geometry."""
        screen = self.app.primaryScreen()
        if not screen:
            return

        geo = screen.availableGeometry()
        target_w = int(geo.width() * max_width_ratio)
        target_h = int(geo.height() * max_height_ratio)

        min_size = window.minimumSize()
        final_w = max(min_size.width(), target_w) if min_size.width() > 0 else target_w
        final_h = max(min_size.height(), target_h) if min_size.height() > 0 else target_h

        window.resize(QSize(final_w, final_h))

    def on_page_changed(self, index):
        """
        Refresh data when the user switches to a page.
        This keeps all data up-to-date.
        """
        # Get the current widget
        current_widget = self.main_window.stacked_widget.currentWidget()

        # Call refresh_data if the page has it
        if hasattr(current_widget, "refresh_data"):
            try:
                current_widget.refresh_data()
            except Exception as e:
                print(f"[REFRESH ERROR] {e}")

    def _on_profile_updated(self, updated_user):
        """Refresh shell profile info after My Profile changes."""
        self.main_window.user = updated_user
        self.main_window.refresh_profile_button()

    def run(self):
        """Start the application event loop."""
        sys.exit(self.app.exec())


# ── Run the application ─────────────────────────────────────
if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
