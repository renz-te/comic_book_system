"""
views/comics_view.py
===============================================================
Comics management page — full CRUD with chapters, cover image,
synopsis, and stock level tracking.
===============================================================
"""

import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit,
    QFrame,
    QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPixmap

from controllers.comics_ctrl import (
    load_all_comics, search_comics_ctrl,
    add_comic_ctrl, update_comic_ctrl, delete_comic_ctrl
)


class ComicsView(QWidget):
    """Page for managing comic book inventory."""

    def __init__(self):
        super().__init__()
        self.setObjectName("comicsPage")
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

        self.horizontalLayout_toolbar = QHBoxLayout()
        self.horizontalLayout_toolbar.setObjectName("horizontalLayout_toolbar")
        self.horizontalLayout_toolbar.setSpacing(8)

        self.txt_search = QLineEdit(self)
        self.txt_search.setObjectName("txt_search")
        self.txt_search.setMinimumHeight(38)
        self.txt_search.textChanged.connect(self._on_search)
        self.horizontalLayout_toolbar.addWidget(self.txt_search)

        self.btn_add = QPushButton(self)
        self.btn_add.setObjectName("btn_add")
        self.btn_add.setMinimumHeight(38)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self._open_add_dialog)
        self.horizontalLayout_toolbar.addWidget(self.btn_add)

        self.btn_edit = QPushButton(self)
        self.btn_edit.setObjectName("btn_edit")
        self.btn_edit.setMinimumHeight(38)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.clicked.connect(self._open_edit_dialog)
        self.horizontalLayout_toolbar.addWidget(self.btn_edit)

        self.btn_delete = QPushButton(self)
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setMinimumHeight(38)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self._delete_comic)
        self.horizontalLayout_toolbar.addWidget(self.btn_delete)

        self.btn_view = QPushButton(self)
        self.btn_view.setObjectName("btn_view")
        self.btn_view.setMinimumHeight(38)
        self.btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view.clicked.connect(self._view_details)
        self.horizontalLayout_toolbar.addWidget(self.btn_view)

        self.verticalLayout_main.addLayout(self.horizontalLayout_toolbar)

        # Table with extra columns for chapters and hidden cover_image
        self.table = QTableWidget(self)
        self.table.setObjectName("table")
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Author", "Issue #", "Publisher",
            "Category", "Price", "Stock", "Chapters", "Status", "Cover"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)   # ID
        self.table.setColumnHidden(10, True)  # Cover path
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self._view_details)
        self.verticalLayout_main.addWidget(self.table)

    def retranslateUi(self):
        self.lbl_header.setText("Products Inventory")
        self.txt_search.setPlaceholderText("Search by title, author, or category...")
        self.btn_add.setText("Add Product")
        self.btn_edit.setText("Edit")
        self.btn_delete.setText("Delete")
        self.btn_view.setText("View Details")

    # ── Data ────────────────────────────────────────────────
    def refresh_data(self):
        comics = load_all_comics()
        self._fill_table(comics)

    def _fill_table(self, comics):
        self.table.setRowCount(len(comics))
        for r, comic in enumerate(comics):
            self.table.setItem(r, 0, QTableWidgetItem(str(comic["comic_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(comic["title"]))
            self.table.setItem(r, 2, QTableWidgetItem(comic["author"]))
            self.table.setItem(r, 3, QTableWidgetItem(comic.get("issue_number", "")))
            self.table.setItem(r, 4, QTableWidgetItem(comic.get("publisher", "")))
            self.table.setItem(r, 5, QTableWidgetItem(comic.get("category", "")))
            self.table.setItem(r, 6, QTableWidgetItem(f"₱{comic['price']:,.2f}"))
            self.table.setItem(r, 7, QTableWidgetItem(str(comic["stock_quantity"])))
            self.table.setItem(r, 8, QTableWidgetItem(str(comic.get("chapters", 1))))
            self.table.setItem(r, 9, QTableWidgetItem(comic["availability_status"]))
            self.table.setItem(r, 10, QTableWidgetItem(comic.get("cover_image", "") or ""))
            if comic["stock_quantity"] < 5:
                for c in range(11):
                    item = self.table.item(r, c)
                    if item:
                        item.setBackground(QColor("#ffeaa7"))

    def _on_search(self):
        keyword = self.txt_search.text().strip()
        comics = search_comics_ctrl(keyword) if keyword else load_all_comics()
        self._fill_table(comics)

    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def _get_selected_data(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return {
            "comic_id": int(self.table.item(row, 0).text()),
            "title": self.table.item(row, 1).text(),
            "author": self.table.item(row, 2).text(),
            "issue_number": self.table.item(row, 3).text(),
            "publisher": self.table.item(row, 4).text(),
            "category": self.table.item(row, 5).text(),
            "price": float(self.table.item(row, 6).text().replace("₱", "").replace(",", "")),
            "stock_quantity": int(self.table.item(row, 7).text()),
            "chapters": int(self.table.item(row, 8).text()),
            "cover_image": self.table.item(row, 10).text() if self.table.item(row, 10) else "",
        }

    # ── CRUD dialogs ────────────────────────────────────────
    def _open_add_dialog(self):
        dialog = ComicDialog(self, title="Add New Product")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if add_comic_ctrl(**data):
                QMessageBox.information(self, "Success", "Product added successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to add product.")

    def _open_edit_dialog(self):
        current = self._get_selected_data()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return

        comic_id = current.pop("comic_id")
        # Fetch synopsis from DB (not in table)
        from models.comic_model import get_comic_by_id
        full = get_comic_by_id(comic_id)
        if full:
            current["synopsis"] = full.get("synopsis", "") or ""

        dialog = ComicDialog(self, title="Edit Product", data=current)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if update_comic_ctrl(comic_id, **data):
                QMessageBox.information(self, "Success", "Product updated successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to update product.")

    def _delete_comic(self):
        comic_id = self._get_selected_id()
        if not comic_id:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if delete_comic_ctrl(comic_id):
                QMessageBox.information(self, "Deleted", "Product deleted successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error",
                                     "Failed to delete product.\n"
                                     "This product may have existing sales or borrow records.")

    def _view_details(self):
        data = self._get_selected_data()
        if not data:
            QMessageBox.warning(self, "No Selection", "Please select a product to view.")
            return
        from models.comic_model import get_comic_by_id
        full = get_comic_by_id(data["comic_id"])
        if full:
            dlg = ComicDetailDialog(self, full)
            dlg.exec()

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #comicsPage { background-color: #f0f2f5; }
            QLabel#lbl_header {
                font-size: 20px; font-weight: bold; color: #2c3e50; padding-bottom: 4px;
            }
            QLineEdit#txt_search {
                border: 1px solid #d0d4d8; border-radius: 8px; padding: 10px 14px;
                font-size: 13px; background-color: #ffffff; color: #333333;
            }
            QLineEdit#txt_search:focus { border: 2px solid #3498db; }
            QPushButton#btn_add {
                background-color: #3498db; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_add:hover { background-color: #2980b9; }
            QPushButton#btn_edit {
                background-color: #e67e22; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_edit:hover { background-color: #d35400; }
            QPushButton#btn_delete {
                background-color: #c0392b; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_delete:hover { background-color: #a93226; }
            QPushButton#btn_view {
                background-color: #8e44ad; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_view:hover { background-color: #7d3c98; }
            QTableWidget {
                background-color: #ffffff; color: #333333;
                alternate-background-color: #f8f9fa; border: none; border-radius: 10px;
                gridline-color: #f0f0f0; font-size: 13px; padding: 4px;
            }
            QTableWidget::item { padding: 6px 8px; }
            QTableWidget::item:hover { background-color: #eaf2fb; }
            QTableWidget::item:selected { background-color: #3498db; color: #ffffff; }
            QHeaderView::section {
                background-color: #2c3e50; color: #ffffff; padding: 10px 8px;
                border: none; font-weight: bold; font-size: 12px;
            }
        """)


# ═══════════════════════════════════════════════════════════
#  Comic Add / Edit Dialog — with chapters, synopsis, cover
# ═══════════════════════════════════════════════════════════
class ComicDialog(QDialog):
    """Reusable dialog for adding or editing a comic."""

    def __init__(self, parent=None, title="Product", data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(860, 620)
        parent_w = parent.width() if parent else 1200
        parent_h = parent.height() if parent else 800
        self.resize(max(900, int(parent_w * 0.72)), max(640, int(parent_h * 0.78)))
        self.data = data
        self.cover_path = ""
        self._setup()

    def _setup(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(24, 22, 24, 20)

        self.lbl_dialog_title = QLabel(self.windowTitle())
        self.lbl_dialog_title.setObjectName("lbl_dialog_title")
        main_layout.addWidget(self.lbl_dialog_title)

        self.lbl_dialog_subtitle = QLabel("Complete all required fields before saving.")
        self.lbl_dialog_subtitle.setObjectName("lbl_dialog_subtitle")
        main_layout.addWidget(self.lbl_dialog_subtitle)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        form_card = QFrame()
        form_card.setObjectName("comic_form_card")
        form_layout = QFormLayout(form_card)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Spider-Man")
        form_layout.addRow("Title:", self.title_input)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("e.g. Stan Lee")
        form_layout.addRow("Author:", self.author_input)

        self.issue_input = QLineEdit()
        self.issue_input.setPlaceholderText("e.g. #15")
        form_layout.addRow("Issue #:", self.issue_input)

        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText("e.g. Marvel")
        form_layout.addRow("Publisher:", self.publisher_input)

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "Superhero", "Manga", "Horror", "Sci-Fi",
            "Fantasy", "Filipino Hero", "Comedy", "Action"
        ])
        form_layout.addRow("Category:", self.category_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("₱ ")
        self.price_input.setMaximum(99999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSingleStep(10)
        form_layout.addRow("Price:", self.price_input)

        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(99999)
        form_layout.addRow("Stock Qty:", self.stock_input)

        self.chapters_input = QSpinBox()
        self.chapters_input.setMinimum(1)
        self.chapters_input.setMaximum(9999)
        self.chapters_input.setValue(1)
        form_layout.addRow("Chapters:", self.chapters_input)

        self.synopsis_input = QTextEdit()
        self.synopsis_input.setPlaceholderText("Enter book synopsis...")
        self.synopsis_input.setMinimumHeight(120)
        self.synopsis_input.setMaximumHeight(170)
        form_layout.addRow("Synopsis:", self.synopsis_input)

        body_layout.addWidget(form_card, 3)

        preview_card = QFrame()
        preview_card.setObjectName("cover_preview_card")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setSpacing(10)
        preview_layout.setContentsMargins(16, 16, 16, 16)

        self.lbl_preview_title = QLabel("Cover Preview")
        self.lbl_preview_title.setObjectName("lbl_preview_title")
        preview_layout.addWidget(self.lbl_preview_title)

        # Cover image preview
        self.lbl_cover_preview = QLabel()
        self.lbl_cover_preview.setMinimumSize(210, 290)
        self.lbl_cover_preview.setMaximumSize(260, 350)
        self.lbl_cover_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cover_preview.setStyleSheet(
            "background-color: #f3f6fb; border: 2px dashed #c0ccdc; border-radius: 12px;"
        )
        self.lbl_cover_preview.setText("No Image")
        preview_layout.addWidget(self.lbl_cover_preview, 1, Qt.AlignmentFlag.AlignHCenter)

        self.lbl_cover_tip = QLabel("Recommended: portrait image, clear title, good lighting")
        self.lbl_cover_tip.setObjectName("lbl_cover_tip")
        self.lbl_cover_tip.setWordWrap(True)
        preview_layout.addWidget(self.lbl_cover_tip)

        cover_layout = QHBoxLayout()
        self.lbl_cover_path = QLabel("No file selected")
        self.lbl_cover_path.setObjectName("lbl_cover_path")
        cover_layout.addWidget(self.lbl_cover_path)
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.clicked.connect(self._browse_cover)
        cover_layout.addWidget(self.btn_browse)
        self.btn_clear_cover = QPushButton("Clear")
        self.btn_clear_cover.setObjectName("btn_clear_cover")
        self.btn_clear_cover.clicked.connect(self._clear_cover)
        cover_layout.addWidget(self.btn_clear_cover)
        preview_layout.addLayout(cover_layout)
        preview_layout.addStretch(1)

        body_layout.addWidget(preview_card, 2)
        main_layout.addLayout(body_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("btn_save")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self._validate_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("btn_cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Pre-fill if editing
        if self.data:
            self.title_input.setText(self.data.get("title", ""))
            self.author_input.setText(self.data.get("author", ""))
            self.issue_input.setText(self.data.get("issue_number", ""))
            self.publisher_input.setText(self.data.get("publisher", ""))
            self.category_input.setCurrentText(self.data.get("category", ""))
            self.price_input.setValue(self.data.get("price", 0))
            self.stock_input.setValue(self.data.get("stock_quantity", 0))
            self.chapters_input.setValue(self.data.get("chapters", 1))
            self.synopsis_input.setPlainText(self.data.get("synopsis", ""))
            if self.data.get("cover_image"):
                self.cover_path = self.data["cover_image"]
                self.lbl_cover_path.setText(os.path.basename(self.cover_path))
                self._update_preview(self.cover_path)

        self.setStyleSheet("""
            QDialog { background-color: #edf1f7; color: #1f2937; }
            QLabel#lbl_dialog_title {
                font-size: 24px;
                font-weight: 800;
                color: #13253f;
                padding-bottom: 2px;
            }
            QLabel#lbl_dialog_subtitle {
                font-size: 12px;
                color: #5f7088;
                padding-bottom: 4px;
            }
            QFrame#comic_form_card, QFrame#cover_preview_card {
                background-color: #ffffff;
                border: 1px solid #d7deea;
                border-radius: 14px;
            }
            QLabel#lbl_preview_title {
                font-size: 13px;
                font-weight: 700;
                color: #1f2f45;
            }
            QLabel#lbl_cover_tip {
                color: #6b7280;
                font-size: 11px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                border: 1px solid #d0d4d8; border-radius: 6px; padding: 8px 12px;
                min-height: 30px; background-color: #ffffff; color: #333333; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton#btn_save {
                background-color: #1f7dd6; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_save:hover { background-color: #1a69b5; }
            QPushButton#btn_cancel {
                background-color: #6b7280; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_cancel:hover { background-color: #4b5563; }
            QPushButton#btn_browse {
                background-color: #374151; color: #ffffff; border: none; border-radius: 6px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton#btn_browse:hover { background-color: #1f2937; }
            QPushButton#btn_clear_cover {
                background-color: #b9382a; color: #ffffff; border: none; border-radius: 6px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton#btn_clear_cover:hover { background-color: #8f271d; }
            QLabel#lbl_cover_path { color: #6b7280; font-size: 11px; }
        """)

    def _browse_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            covers_dir = os.path.join(project_root, "resources", "covers")
            os.makedirs(covers_dir, exist_ok=True)
            filename = os.path.basename(file_path)
            dest = os.path.join(covers_dir, filename)
            if os.path.abspath(file_path) != os.path.abspath(dest):
                shutil.copy2(file_path, dest)
            self.cover_path = os.path.join("resources", "covers", filename)
            self.lbl_cover_path.setText(filename)
            self._update_preview(self.cover_path)

    def _clear_cover(self):
        self.cover_path = ""
        self.lbl_cover_path.setText("No file selected")
        self.lbl_cover_preview.setPixmap(QPixmap())
        self.lbl_cover_preview.setText("No Image")
        self.lbl_cover_preview.setStyleSheet(
            "background-color: #e8e8e8; border: 2px dashed #bbb; border-radius: 8px;"
        )

    def _update_preview(self, rel_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(project_root, rel_path)
        if os.path.exists(full_path):
            target = self.lbl_cover_preview.size()
            pixmap = QPixmap(full_path).scaled(
                max(40, target.width() - 4), max(40, target.height() - 4), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_cover_preview.setPixmap(pixmap)
            self.lbl_cover_preview.setStyleSheet(
                "background-color: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 2px;"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.cover_path:
            self._update_preview(self.cover_path)

    def _validate_and_accept(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        category = self.category_input.currentText().strip()
        price = self.price_input.value()

        if not title or len(title) < 2:
            QMessageBox.warning(self, "Validation Error", "Title is required (min 2 chars).")
            self.title_input.setFocus()
            return
        if not author or len(author) < 2:
            QMessageBox.warning(self, "Validation Error", "Author is required (min 2 chars).")
            self.author_input.setFocus()
            return
        if not category:
            QMessageBox.warning(self, "Validation Error", "Category is required.")
            self.category_input.setFocus()
            return
        if price <= 0:
            QMessageBox.warning(self, "Validation Error", "Price must be greater than 0.")
            self.price_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "title": self.title_input.text().strip(),
            "author": self.author_input.text().strip(),
            "issue_number": self.issue_input.text().strip(),
            "publisher": self.publisher_input.text().strip(),
            "category": self.category_input.currentText().strip(),
            "price": self.price_input.value(),
            "stock_quantity": self.stock_input.value(),
            "chapters": self.chapters_input.value(),
            "cover_image": self.cover_path,
            "synopsis": self.synopsis_input.toPlainText().strip(),
        }


# ═══════════════════════════════════════════════════════════
#  Comic Detail Dialog — shows cover, synopsis, all fields
# ═══════════════════════════════════════════════════════════
class ComicDetailDialog(QDialog):
    """Shows full comic details including cover image and synopsis."""

    def __init__(self, parent, comic):
        super().__init__(parent)
        self.setWindowTitle(f"Product Details — {comic['title']}")
        self.setMinimumSize(520, 480)
        parent_w = parent.width() if parent else 1200
        parent_h = parent.height() if parent else 800
        self.resize(max(540, int(parent_w * 0.5)), max(500, int(parent_h * 0.7)))
        self.setObjectName("ComicDetailDialog")
        self._setup(comic)

    def _setup(self, comic):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl_title = QLabel(comic["title"])
        lbl_title.setObjectName("lbl_detail_title")
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Product profile and inventory details")
        lbl_sub.setObjectName("lbl_detail_sub")
        layout.addWidget(lbl_sub)

        body = QHBoxLayout()
        body.setSpacing(14)

        left_card = QFrame()
        left_card.setObjectName("detail_left_card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(8)

        lbl_cover_title = QLabel("Cover")
        lbl_cover_title.setObjectName("lbl_cover_card_title")
        left_layout.addWidget(lbl_cover_title)

        lbl_cover = QLabel()
        lbl_cover.setObjectName("lbl_cover_preview")
        lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_cover.setMinimumSize(210, 300)

        # Cover image
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cover_path = comic.get("cover_image") or ""
        if cover_path:
            full_path = os.path.join(project_root, cover_path)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path).scaled(
                    220, 320, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lbl_cover.setPixmap(pixmap)
            else:
                lbl_cover.setText("No Image")
        else:
            lbl_cover.setText("No Image")

        left_layout.addWidget(lbl_cover, 1)
        body.addWidget(left_card, 2)

        right_card = QFrame()
        right_card.setObjectName("detail_right_card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(8)

        lbl_info = QLabel("Information")
        lbl_info.setObjectName("lbl_info_card_title")
        right_layout.addWidget(lbl_info)

        details = [
            ("Title", comic["title"]),
            ("Author", comic["author"]),
            ("Issue #", comic.get("issue_number", "N/A")),
            ("Publisher", comic.get("publisher", "N/A")),
            ("Category", comic.get("category", "N/A")),
            ("Price", f"₱{comic['price']:,.2f}"),
            ("Stock", str(comic["stock_quantity"])),
            ("Chapters", str(comic.get("chapters", 1))),
            ("Status", comic.get("availability_status", "N/A")),
        ]
        for label, value in details:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setObjectName("lbl_info_key")
            lbl.setMinimumWidth(96)
            val = QLabel(value)
            val.setObjectName("lbl_info_val")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            right_layout.addLayout(row)

        synopsis = comic.get("synopsis") or "No synopsis available."
        lbl_syn_title = QLabel("Synopsis")
        lbl_syn_title.setObjectName("lbl_synopsis_title")
        right_layout.addWidget(lbl_syn_title)
        lbl_syn = QLabel(synopsis)
        lbl_syn.setObjectName("lbl_synopsis")
        lbl_syn.setWordWrap(True)
        right_layout.addWidget(lbl_syn)

        right_layout.addStretch(1)
        body.addWidget(right_card, 3)
        layout.addLayout(body)

        btn_close = QPushButton("Close")
        btn_close.setObjectName("btn_close")
        btn_close.setMinimumHeight(40)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignRight)

        self.setStyleSheet("""
            QDialog#ComicDetailDialog { background-color: #edf1f7; color: #1f2937; }
            QLabel#lbl_detail_title {
                font-size: 24px;
                font-weight: 800;
                color: #13253f;
            }
            QLabel#lbl_detail_sub {
                font-size: 12px;
                color: #5f7088;
                padding-bottom: 2px;
            }
            QFrame#detail_left_card, QFrame#detail_right_card {
                background-color: #ffffff;
                border: 1px solid #d7deea;
                border-radius: 14px;
            }
            QLabel#lbl_cover_card_title, QLabel#lbl_info_card_title {
                font-size: 13px;
                font-weight: 700;
                color: #1f2f45;
            }
            QLabel#lbl_cover_preview {
                background-color: #f3f6fb;
                border: 1px dashed #c0ccdc;
                border-radius: 10px;
                color: #6b7280;
            }
            QLabel#lbl_info_key {
                color: #4b5563;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#lbl_info_val {
                color: #111827;
                font-size: 12px;
            }
            QLabel#lbl_synopsis_title {
                color: #1f2f45;
                font-size: 12px;
                font-weight: 700;
                padding-top: 6px;
            }
            QLabel#lbl_synopsis {
                color: #374151;
                font-size: 12px;
                background-color: #f8fafc;
                border: 1px solid #e5eaf2;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton#btn_close {
                background-color: #6b7280; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_close:hover { background-color: #4b5563; }
        """)
