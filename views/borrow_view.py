"""
views/borrow_view.py
===============================================================
Borrow / Return page — manage comic borrowing and returns.
Features: due date (no past dates), borrow limit confirmation,
damage/lost assessment on return, archive, printable receipts.
===============================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QComboBox, QDateEdit,
    QGroupBox, QFormLayout, QDialog, QTextEdit,
    QDoubleSpinBox, QTabWidget, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PyQt6.QtGui import QFont, QColor, QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter, QPrinterInfo
from datetime import datetime
from html import escape
import re

from config import DEFAULT_BORROW_DAYS


class BorrowView(QWidget):
    """Page for borrowing and returning comics."""

    def __init__(self, user):
        super().__init__()
        self.setObjectName("borrowPage")
        self.user = user
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

        # Forms row
        self.horizontalLayout_forms = QHBoxLayout()
        self.horizontalLayout_forms.setObjectName("horizontalLayout_forms")
        self.horizontalLayout_forms.setSpacing(14)

        # ── Borrow form ────────────────────────────────────
        self.groupBox_borrow = QGroupBox(self)
        self.groupBox_borrow.setObjectName("groupBox_borrow")
        borrow_form = QFormLayout()
        borrow_form.setSpacing(10)
        borrow_form.setContentsMargins(16, 20, 16, 16)

        self.cmb_comic = QComboBox()
        self.cmb_comic.setObjectName("cmb_comic")
        self.cmb_comic.setMinimumHeight(35)
        borrow_form.addRow("Product:", self.cmb_comic)

        self.txt_borrower = QLineEdit()
        self.txt_borrower.setObjectName("txt_borrower")
        self.txt_borrower.setMinimumHeight(35)
        borrow_form.addRow("Borrower:", self.txt_borrower)

        self.lbl_borrow_auto = QLabel("Auto: Today")
        self.lbl_borrow_auto.setObjectName("lbl_borrow_auto")
        borrow_form.addRow("Borrow Date:", self.lbl_borrow_auto)

        # Due date is auto-computed from current day + policy days.
        self.date_due = QDateEdit()
        self.date_due.setObjectName("date_due")
        self.date_due.setCalendarPopup(True)
        self.date_due.setDate(QDate.currentDate().addDays(DEFAULT_BORROW_DAYS))
        self.date_due.setMinimumDate(QDate.currentDate())
        self.date_due.setDisplayFormat("dd/MM/yyyy")
        self.date_due.setMinimumHeight(35)
        self.date_due.hide()

        self.lbl_due_auto = QLabel("Auto: --")
        self.lbl_due_auto.setObjectName("lbl_due_auto")
        borrow_form.addRow("Due Date:", self.lbl_due_auto)

        self.btn_borrow = QPushButton()
        self.btn_borrow.setObjectName("btn_borrow")
        self.btn_borrow.setMinimumHeight(40)
        self.btn_borrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_borrow.clicked.connect(self._handle_borrow)
        borrow_form.addRow(self.btn_borrow)

        self.groupBox_borrow.setLayout(borrow_form)
        self.horizontalLayout_forms.addWidget(self.groupBox_borrow)

        # ── Return form ────────────────────────────────────
        self.groupBox_return = QGroupBox(self)
        self.groupBox_return.setObjectName("groupBox_return")
        return_form = QFormLayout()
        return_form.setSpacing(10)
        return_form.setContentsMargins(16, 20, 16, 16)

        self.cmb_return = QComboBox()
        self.cmb_return.setObjectName("cmb_return")
        self.cmb_return.setMinimumHeight(35)
        return_form.addRow("Record:", self.cmb_return)

        self.date_return = QDateEdit()
        self.date_return.setObjectName("date_return")
        self.date_return.setCalendarPopup(True)
        self.date_return.setDate(QDate.currentDate())
        self.date_return.setDisplayFormat("dd/MM/yyyy")
        self.date_return.setMinimumHeight(35)
        self.date_return.hide()

        self.lbl_return_auto = QLabel("Auto: Today")
        self.lbl_return_auto.setObjectName("lbl_return_auto")
        return_form.addRow("Return Date:", self.lbl_return_auto)

        self.btn_return = QPushButton()
        self.btn_return.setObjectName("btn_return")
        self.btn_return.setMinimumHeight(40)
        self.btn_return.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_return.clicked.connect(self._handle_return)
        return_form.addRow(self.btn_return)

        self.groupBox_return.setLayout(return_form)
        self.horizontalLayout_forms.addWidget(self.groupBox_return)

        self.verticalLayout_main.addLayout(self.horizontalLayout_forms)

        # ── Tab widget for Active / Archived / Damaged ─────
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName("tab_widget")

        # Active records tab
        self.tab_active = QWidget()
        tab_active_layout = QVBoxLayout(self.tab_active)
        tab_active_layout.setContentsMargins(0, 8, 0, 0)

        self.table = QTableWidget()
        self.table.setObjectName("table")
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Borrower", "Borrow Date", "Due Date",
            "Return Date", "Condition", "Status", "Date/Time"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        tab_active_layout.addWidget(self.table)

        # Archive button row
        archive_btn_layout = QHBoxLayout()
        self.btn_archive = QPushButton("Archive Selected")
        self.btn_archive.setObjectName("btn_archive")
        self.btn_archive.setMinimumHeight(34)
        self.btn_archive.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_archive.clicked.connect(self._archive_record)
        archive_btn_layout.addWidget(self.btn_archive)

        self.btn_print_receipt = QPushButton("View Receipt")
        self.btn_print_receipt.setObjectName("btn_print_receipt")
        self.btn_print_receipt.setMinimumHeight(34)
        self.btn_print_receipt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print_receipt.clicked.connect(self._print_borrow_receipt)
        archive_btn_layout.addWidget(self.btn_print_receipt)

        archive_btn_layout.addStretch()
        tab_active_layout.addLayout(archive_btn_layout)
        self.tab_widget.addTab(self.tab_active, "Active Records")

        # Archived records tab
        self.tab_archived = QWidget()
        tab_archived_layout = QVBoxLayout(self.tab_archived)
        tab_archived_layout.setContentsMargins(0, 8, 0, 0)

        self.table_archived = QTableWidget()
        self.table_archived.setObjectName("table_archived")
        self.table_archived.setColumnCount(9)
        self.table_archived.setHorizontalHeaderLabels([
            "ID", "Product", "Borrower", "Borrow Date", "Due Date",
            "Return Date", "Condition", "Status", "Date/Time"
        ])
        self.table_archived.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_archived.setColumnHidden(0, True)
        self.table_archived.verticalHeader().setVisible(False)
        self.table_archived.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_archived.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_archived.setAlternatingRowColors(True)
        self.table_archived.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        tab_archived_layout.addWidget(self.table_archived)

        restore_btn_layout = QHBoxLayout()
        self.btn_restore = QPushButton("Restore Selected")
        self.btn_restore.setObjectName("btn_restore")
        self.btn_restore.setMinimumHeight(34)
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.clicked.connect(self._restore_record)
        restore_btn_layout.addWidget(self.btn_restore)
        restore_btn_layout.addStretch()
        tab_archived_layout.addLayout(restore_btn_layout)
        self.tab_widget.addTab(self.tab_archived, "Archived Records")

        # Damaged / Lost tab
        self.tab_damaged = QWidget()
        tab_damaged_layout = QVBoxLayout(self.tab_damaged)
        tab_damaged_layout.setContentsMargins(0, 8, 0, 0)

        self.table_damaged = QTableWidget()
        self.table_damaged.setObjectName("table_damaged")
        self.table_damaged.setColumnCount(7)
        self.table_damaged.setHorizontalHeaderLabels([
            "ID", "Product", "Borrower", "Condition", "Notes", "Fee", "Date"
        ])
        self.table_damaged.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_damaged.setColumnHidden(0, True)
        self.table_damaged.verticalHeader().setVisible(False)
        self.table_damaged.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_damaged.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_damaged.setAlternatingRowColors(True)
        self.table_damaged.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        tab_damaged_layout.addWidget(self.table_damaged)
        self.tab_widget.addTab(self.tab_damaged, "Damaged / Lost")

        self.verticalLayout_main.addWidget(self.tab_widget)

    def retranslateUi(self):
        self.lbl_header.setText("Borrow / Return Products")
        self.groupBox_borrow.setTitle("Borrow a Product")
        self.txt_borrower.setPlaceholderText("Borrower's full name")
        self.btn_borrow.setText("Borrow Product")
        self.groupBox_return.setTitle("Return a Product")
        self.btn_return.setText("Return Product")

    def _normalize_title(self, title):
        """Insert missing spaces in CamelCase-like titles for cleaner display."""
        text = str(title or "").strip()
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ── Data ────────────────────────────────────────────────
    def refresh_data(self):
        from controllers.borrow_ctrl import (
            get_available_comics_list, get_borrowed_list, get_all_records,
            get_archived_records, get_damaged_lost_records
        )

        comics = get_available_comics_list()
        self.cmb_comic.clear()
        self.cmb_comic.addItem("-- Select a product --", None)
        for comic in comics:
            clean_title = self._normalize_title(comic.get("title", "Product"))
            self.cmb_comic.addItem(
                f"{clean_title} (Stock: {comic['stock_quantity']})", comic
            )

        borrowed = get_borrowed_list()
        self.cmb_return.clear()
        self.cmb_return.addItem("-- Select a record --", None)
        for record in borrowed:
            bd = record["borrow_date"]
            if hasattr(bd, "strftime"):
                bd = bd.strftime("%d/%m/%Y")
            clean_title = self._normalize_title(record.get("comic_title", "Product"))
            self.cmb_return.addItem(
                f"#{record['borrow_id']} — {clean_title} / {record['borrower_name']} ({bd})",
                record
            )

        # Borrow/return/due dates are auto-set from current day.
        today = QDate.currentDate()
        due = today.addDays(DEFAULT_BORROW_DAYS)
        self.lbl_borrow_auto.setText(f"Auto: {today.toString('dd/MM/yyyy')}")
        self.lbl_return_auto.setText(f"Auto: {today.toString('dd/MM/yyyy')}")
        self.lbl_due_auto.setText(
            f"Auto: {due.toString('dd/MM/yyyy')} (+{DEFAULT_BORROW_DAYS} day(s))"
        )

        self.date_due.setDate(due)
        self.date_due.setMinimumDate(today)

        records = get_all_records()
        self._fill_table(self.table, records)

        archived = get_archived_records()
        self._fill_table(self.table_archived, archived)

        damaged = get_damaged_lost_records()
        self._fill_damaged_table(damaged)

    def _fill_table(self, table_widget, records):
        table_widget.setRowCount(len(records))
        for r, rec in enumerate(records):
            table_widget.setItem(r, 0, QTableWidgetItem(str(rec["borrow_id"])))
            table_widget.setItem(r, 1, QTableWidgetItem(self._normalize_title(rec["comic_title"])))
            table_widget.setItem(r, 2, QTableWidgetItem(rec["borrower_name"]))

            bd = rec["borrow_date"]
            if hasattr(bd, "strftime"):
                bd = bd.strftime("%d/%m/%Y")
            table_widget.setItem(r, 3, QTableWidgetItem(str(bd)))

            dd = rec.get("due_date")
            if dd and hasattr(dd, "strftime"):
                dd = dd.strftime("%d/%m/%Y")
            table_widget.setItem(r, 4, QTableWidgetItem(str(dd or "—")))

            rd = rec.get("return_date")
            if rd and hasattr(rd, "strftime"):
                rd = rd.strftime("%d/%m/%Y")
            table_widget.setItem(r, 5, QTableWidgetItem(str(rd or "—")))

            cond = rec.get("condition_on_return") or "—"
            table_widget.setItem(r, 6, QTableWidgetItem(cond))

            status_item = QTableWidgetItem(rec["status"])
            if rec["status"] == "Borrowed":
                status_item.setForeground(QColor("#c0392b"))
            else:
                status_item.setForeground(QColor("#27ae60"))
            table_widget.setItem(r, 7, status_item)

            ca = rec.get("created_at", "")
            if hasattr(ca, "strftime"):
                ca = ca.strftime("%d/%m/%Y %I:%M %p")
            table_widget.setItem(r, 8, QTableWidgetItem(str(ca or "")))

    def _fill_damaged_table(self, records):
        self.table_damaged.setRowCount(len(records))
        for r, rec in enumerate(records):
            self.table_damaged.setItem(r, 0, QTableWidgetItem(str(rec["borrow_id"])))
            self.table_damaged.setItem(r, 1, QTableWidgetItem(self._normalize_title(rec["comic_title"])))
            self.table_damaged.setItem(r, 2, QTableWidgetItem(rec["borrower_name"]))
            self.table_damaged.setItem(r, 3, QTableWidgetItem(rec.get("condition_on_return", "")))
            self.table_damaged.setItem(r, 4, QTableWidgetItem(rec.get("damage_notes", "") or ""))
            fee = float(rec.get("damage_fee", 0) or 0)
            self.table_damaged.setItem(r, 5, QTableWidgetItem(f"₱{fee:,.2f}"))
            ca = rec.get("created_at", "")
            if hasattr(ca, "strftime"):
                ca = ca.strftime("%d/%m/%Y")
            self.table_damaged.setItem(r, 6, QTableWidgetItem(str(ca or "")))

    # ── Handlers ────────────────────────────────────────────
    def _handle_borrow(self):
        comic = self.cmb_comic.currentData()
        if not comic:
            QMessageBox.warning(self, "No Product", "Please select a product to borrow.")
            return

        borrower = self.txt_borrower.text().strip()
        if not borrower:
            QMessageBox.warning(self, "No Borrower", "Please enter the borrower's name.")
            self.txt_borrower.setFocus()
            return
        if len(borrower) < 2:
            QMessageBox.warning(self, "Invalid Name",
                                "Borrower name must be at least 2 characters.")
            self.txt_borrower.setFocus()
            return

        # Check borrow limit
        from controllers.borrow_ctrl import check_borrow_limit
        can_borrow, current, limit = check_borrow_limit(borrower, self.user["user_id"])
        if not can_borrow:
            QMessageBox.warning(
                self, "Borrow Limit Reached",
                f"{borrower} has already borrowed {current} product(s).\n"
                f"The borrow limit is {limit}.\n\n"
                "Please return a product before borrowing another."
            )
            return

        # Confirm if nearing limit
        if current >= limit - 1:
            reply = QMessageBox.question(
                self, "Borrow Limit Warning",
                f"{borrower} currently has {current} of {limit} allowed borrows.\n\n"
                "Proceed with this borrow?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        today = QDate.currentDate()
        borrow_date = today.toString("yyyy-MM-dd")
        due_date = today.addDays(DEFAULT_BORROW_DAYS).toString("yyyy-MM-dd")

        from controllers.borrow_ctrl import borrow_comic_ctrl
        if borrow_comic_ctrl(comic["comic_id"], borrower, borrow_date, due_date,
                             self.user["user_id"]):
            self._show_borrow_receipt(comic, borrower, borrow_date, due_date)
            self.txt_borrower.clear()
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to borrow product.")

    def _handle_return(self):
        record = self.cmb_return.currentData()
        if not record:
            QMessageBox.warning(self, "No Record", "Please select a borrow record to return.")
            return

        return_qdate = QDate.currentDate()
        return_date = return_qdate.toString("yyyy-MM-dd")
        borrow_date = record.get("borrow_date")

        if borrow_date:
            bd_str = str(borrow_date)[:10]
            bd_qdate = QDate.fromString(bd_str, "yyyy-MM-dd")
            if bd_qdate.isValid() and return_qdate < bd_qdate:
                QMessageBox.warning(self, "Invalid Date",
                                    "Return date cannot be before the borrow date.\n"
                                    "Please check your system date/time.")
                return

        # Show condition assessment dialog
        dlg = ReturnConditionDialog(self, record)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        condition, notes, fee = dlg.get_data()

        from controllers.borrow_ctrl import return_comic_ctrl
        if return_comic_ctrl(record["borrow_id"], return_date, condition, notes, fee):
            self._show_return_receipt(record, return_date, condition, notes, fee)
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to return product.")

    def _archive_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a record to archive.")
            return

        borrow_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "Confirm Archive", "Archive this borrow record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from controllers.borrow_ctrl import archive_record
            if archive_record(borrow_id):
                QMessageBox.information(self, "Archived", "Record archived successfully.")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to archive record.")

    def _restore_record(self):
        row = self.table_archived.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a record to restore.")
            return

        borrow_id = int(self.table_archived.item(row, 0).text())
        from controllers.borrow_ctrl import restore_record
        if restore_record(borrow_id):
            QMessageBox.information(self, "Restored", "Record restored successfully.")
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to restore record.")

    def _print_borrow_receipt(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "No Records", "There are no borrow records to view.")
            return

        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "No Selection", "Please click a borrow record first.")
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please click a borrow record first.")
            return

        comic = self._normalize_title(self.table.item(row, 1).text())
        borrower = self.table.item(row, 2).text()
        borrow_date = self.table.item(row, 3).text()
        due_date = self.table.item(row, 4).text()
        status = self.table.item(row, 7).text()
        return_date = self.table.item(row, 5).text()

        lines = [
            "=" * 40,
            "       PRODUCT — BORROW RECEIPT",
            "=" * 40,
            f"  Product:     {comic}",
            f"  Borrower:    {borrower}",
            f"  Borrow Date: {borrow_date}",
            f"  Due Date:    {due_date}",
            f"  Status:      {status}",
        ]
        if status == "Returned":
            lines.append(f"  Return Date: {return_date}")
        lines += [
            "=" * 40,
            f"  Printed:     {datetime.now().strftime('%d/%m/%Y %I:%M %p')}",
            "=" * 40,
        ]
        self._show_printable_receipt("Borrow Receipt", lines)


    def _show_borrow_receipt(self, comic, borrower, borrow_date, due_date):
        lines = [
            "=" * 40,
            "       PRODUCT — BORROW RECEIPT",
            "=" * 40,
            f"  Product:     {self._normalize_title(comic['title'])}",
            f"  Borrower:    {borrower}",
            f"  Borrow Date: {borrow_date}",
            f"  Due Date:    {due_date}",
            f"  Status:      Borrowed",
            "-" * 40,
            f"  Issued by:   {self.user['full_name']}",
            f"  Time:        {datetime.now().strftime('%I:%M %p')}",
            "=" * 40,
        ]
        QMessageBox.information(self, "Success", f"Product borrowed by {borrower}!")
        self._show_printable_receipt("Borrow Receipt", lines)

    def _show_return_receipt(self, record, return_date, condition, notes, fee):
        lines = [
            "=" * 40,
            "       PRODUCT — RETURN RECEIPT",
            "=" * 40,
            f"  Product:     {self._normalize_title(record['comic_title'])}",
            f"  Borrower:    {record['borrower_name']}",
            f"  Return Date: {return_date}",
            f"  Condition:   {condition}",
        ]
        if notes:
            lines.append(f"  Notes:       {notes}")
        if fee > 0:
            lines.append(f"  Damage Fee:  ₱{fee:,.2f}")
        lines += [
            "-" * 40,
            f"  Processed by: {self.user['full_name']}",
            f"  Time:         {datetime.now().strftime('%I:%M %p')}",
            "=" * 40,
        ]
        QMessageBox.information(self, "Success", "Product returned successfully!")
        self._show_printable_receipt("Return Receipt", lines)

    def _build_receipt_html(self, title, lines):
        rows = []
        notes = []
        for line in lines:
            clean = line.strip()
            if not clean:
                continue
            if set(clean) == {"="} or set(clean) == {"-"}:
                continue
            if "RECEIPT" in clean.upper():
                continue
            if ":" in clean:
                key, value = clean.split(":", 1)
                rows.append((key.strip(), value.strip()))
            else:
                notes.append(clean)

        table_rows = "".join(
            f"<tr><td class='label'>{escape(k)}</td><td class='value'>{escape(v)}</td></tr>"
            for k, v in rows
        )
        notes_html = "".join(f"<div class='note'>{escape(n)}</div>" for n in notes)

        return f"""
        <html>
          <head>
            <style>
                              @page {{ size: A4; margin: 12mm; }}
              body {{ font-family: 'Segoe UI', sans-serif; color: #1f2937; margin: 0; }}
              .receipt {{
                border: 1px solid #dbe1ea;
                border-radius: 12px;
                padding: 18px;
                background: #ffffff;
                                max-width: 740px;
                                margin: 0 auto;
              }}
              .brand {{
                font-size: 11px;
                color: #6b7280;
                letter-spacing: 1px;
                text-transform: uppercase;
              }}
              .title {{
                font-size: 22px;
                font-weight: 700;
                color: #111827;
                margin-top: 4px;
                margin-bottom: 2px;
              }}
              .subtitle {{ font-size: 12px; color: #6b7280; margin-bottom: 14px; }}
              table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
              tr {{ border-bottom: 1px solid #eef2f7; }}
              td {{ padding: 9px 0; font-size: 13px; vertical-align: top; }}
              td.label {{ width: 34%; color: #4b5563; font-weight: 600; }}
              td.value {{ color: #111827; font-weight: 500; }}
              .note {{
                margin-top: 8px;
                padding: 10px 12px;
                background: #f8fafc;
                border: 1px solid #e5eaf2;
                border-radius: 8px;
                font-size: 12px;
                color: #374151;
              }}
            </style>
          </head>
          <body>
            <div class='receipt'>
              <div class='brand'>Comic Book System</div>
              <div class='title'>{escape(title)}</div>
              <div class='subtitle'>Official transaction receipt</div>
              <table>{table_rows}</table>
              {notes_html}
            </div>
          </body>
        </html>
        """

    def _show_printable_receipt(self, title, lines):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog_w = max(420, int(self.width() * 0.5))
        dialog_h = max(380, int(self.height() * 0.62))
        dialog.setFixedSize(dialog_w, dialog_h)
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        caption = QLabel("Preview before printing")
        caption.setObjectName("receipt_preview_caption")
        layout.addWidget(caption)

        receipt_html = self._build_receipt_html(title, lines)

        receipt = QTextEdit()
        receipt.setHtml(receipt_html)
        receipt.setReadOnly(True)
        receipt.setFont(QFont("Segoe UI", 10))
        layout.addWidget(receipt)

        btn_row = QHBoxLayout()
        btn_print = QPushButton("Print on Windows")
        btn_print.setObjectName("btn_print_action")
        btn_row.addWidget(btn_print)

        btn_close = QPushButton("Close")
        btn_close.setObjectName("btn_close_receipt")
        btn_close.clicked.connect(dialog.close)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #eef2f7;
                color: #1f2937;
            }
            QLabel#receipt_preview_caption {
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
                color: #4b5563;
                padding-left: 4px;
            }
            QTextEdit {
                background-color: #f7f9fc;
                color: #1f2937;
                border: 1px solid #d4dbe5;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton#btn_print_action {
                background-color: #1f7a45; color: #fff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_print_action:hover { background-color: #18663a; }
            QPushButton#btn_close_receipt {
                background-color: #6b7280; color: #fff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_close_receipt:hover { background-color: #4b5563; }
        """)

        btn_print.clicked.connect(
            lambda: self._simulate_print(dialog, receipt, btn_print, btn_close, title, receipt_html)
        )
        dialog.exec()

    def _simulate_print(self, dialog, text_edit, print_btn, close_btn, receipt_title, receipt_html):
        """Show a bottom printer mockup that ejects the receipt upward."""
        print_btn.setEnabled(False)
        close_btn.setEnabled(False)
        print_btn.setText("Printing...")

        preview = "\n".join(text_edit.toPlainText().splitlines()[:12])

        stage_w = min(max(320, text_edit.width() - 60), 430)
        stage_h = 230
        stage_x = (dialog.width() - stage_w) // 2
        stage_y = dialog.height() - stage_h - 46

        stage = QFrame(dialog)
        stage.setGeometry(stage_x, stage_y, stage_w, stage_h)
        stage.setStyleSheet("QFrame { background: transparent; border: none; }")

        printer_top = QFrame(stage)
        printer_top.setGeometry(28, 92, stage_w - 56, 24)
        printer_top.setStyleSheet(
            "background-color: #3b495b; border-top-left-radius: 10px;"
            "border-top-right-radius: 10px;"
        )

        printer_body = QFrame(stage)
        printer_body.setGeometry(10, 110, stage_w - 20, 90)
        printer_body.setStyleSheet(
            "background-color: #263445; border-radius: 12px;"
            "border: 1px solid #1a2430;"
        )

        printer_slot = QFrame(stage)
        printer_slot.setGeometry(26, 108, stage_w - 52, 8)
        printer_slot.setStyleSheet("background-color: #111827; border-radius: 4px;")

        status = QLabel("PRINTING", stage)
        status.setGeometry(stage_w - 98, 128, 74, 18)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet(
            "color: #d1fae5; font-size: 10px; font-weight: 700;"
            "background-color: #14532d; border-radius: 8px;"
        )

        paper = QLabel(stage)
        paper.setText(preview)
        paper.setWordWrap(True)
        paper.setFont(QFont("Courier New", 8))
        paper.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        paper.setStyleSheet(
            "background-color: #fffef5; color: #1f2937;"
            "border: 1px solid #d1d5db; border-radius: 6px; padding: 8px;"
        )
        paper.setGeometry(QRect(28, 112, stage_w - 56, 18))
        paper.raise_()
        stage.raise_()
        stage.show()

        self._print_stage = stage
        self._print_anim = QPropertyAnimation(paper, b"geometry")
        self._print_anim.setDuration(1500)
        self._print_anim.setStartValue(QRect(28, 112, stage_w - 56, 18))
        self._print_anim.setEndValue(QRect(28, 20, stage_w - 56, 130))
        self._print_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_finished():
            stage.deleteLater()
            print_btn.setEnabled(True)
            close_btn.setEnabled(True)
            print_btn.setText("Print on Windows")
            self._open_windows_print_dialog(dialog, receipt_html, receipt_title)

        self._print_anim.finished.connect(on_finished)
        self._print_anim.start()

    def _open_windows_print_dialog(self, parent, receipt_html, receipt_title):
        printers = QPrinterInfo.availablePrinters()
        if not printers:
            self._save_receipt_pdf(parent, receipt_html, receipt_title)
            return

        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
        default_printer = QPrinterInfo.defaultPrinter()
        if not default_printer.isNull():
            printer.setPrinterName(default_printer.printerName())
        elif printers:
            printer.setPrinterName(printers[0].printerName())
        printer.setDocName(receipt_title)

        print_dialog = QPrintDialog(printer, parent)
        print_dialog.setWindowTitle("Print Receipt")
        if print_dialog.exec() != QDialog.DialogCode.Accepted:
            reply = QMessageBox.question(
                parent,
                "Print Cancelled",
                "Printing was cancelled. Save a PDF copy instead?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_receipt_pdf(parent, receipt_html, receipt_title)
            return

        document = QTextDocument()
        document.setDefaultFont(QFont("Segoe UI", 10))
        document.setHtml(receipt_html)
        document.print(printer)
        QMessageBox.information(parent, "Printed", "Receipt sent to selected printer.")

    def _save_receipt_pdf(self, parent, receipt_html, receipt_title):
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save Receipt as PDF",
            f"{receipt_title.replace(' ', '_')}.pdf",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        printer.setDocName(receipt_title)

        document = QTextDocument()
        document.setDefaultFont(QFont("Segoe UI", 10))
        document.setHtml(receipt_html)
        document.print(printer)
        QMessageBox.information(parent, "Saved", f"Receipt saved to:\n{file_path}")

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #borrowPage { background-color: #f0f2f5; }
            QLabel#lbl_header {
                font-size: 20px; font-weight: bold; color: #2c3e50; padding-bottom: 4px;
            }
            QGroupBox {
                background-color: #ffffff; border: none; border-radius: 12px;
                margin-top: 8px; padding-top: 20px;
                font-weight: bold; font-size: 14px; color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 16px; padding: 0 8px;
            }
            QComboBox, QLineEdit, QDateEdit {
                border: 1px solid #d0d4d8; border-radius: 6px; padding: 8px 12px;
                background-color: #ffffff; color: #333333; font-size: 13px;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus { border: 2px solid #3498db; }
            QLabel#lbl_borrow_auto, QLabel#lbl_return_auto, QLabel#lbl_due_auto {
                color: #2c3e50;
                background-color: #eef3fb;
                border: 1px solid #cfd9ea;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#btn_borrow {
                background-color: #3498db; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_borrow:hover { background-color: #2980b9; }
            QPushButton#btn_return {
                background-color: #27ae60; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_return:hover { background-color: #229954; }
            QPushButton#btn_archive {
                background-color: #e67e22; color: #ffffff; border: none;
                border-radius: 8px; padding: 8px 18px; font-weight: bold; font-size: 12px;
            }
            QPushButton#btn_archive:hover { background-color: #d35400; }
            QPushButton#btn_restore {
                background-color: #3498db; color: #ffffff; border: none;
                border-radius: 8px; padding: 8px 18px; font-weight: bold; font-size: 12px;
            }
            QPushButton#btn_restore:hover { background-color: #2980b9; }
            QPushButton#btn_print_receipt {
                background-color: #8e44ad; color: #ffffff; border: none;
                border-radius: 8px; padding: 8px 18px; font-weight: bold; font-size: 12px;
            }
            QPushButton#btn_print_receipt:hover { background-color: #7d3c98; }
            QTabWidget::pane { border: none; background-color: transparent; }
            QTabBar::tab {
                background-color: #dfe6e9; color: #2c3e50; padding: 8px 16px;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
                margin-right: 2px; font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #3498db; color: #ffffff; font-weight: bold;
            }
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
#  Return Condition Assessment Dialog
# ═══════════════════════════════════════════════════════════
class ReturnConditionDialog(QDialog):
    """Dialog for assessing the condition of a returned comic."""

    def __init__(self, parent, record):
        super().__init__(parent)
        self.setWindowTitle("Return — Condition Assessment")
        parent_w = parent.width() if parent else 1200
        parent_h = parent.height() if parent else 800
        dialog_w = max(560, int(parent_w * 0.42))
        dialog_h = max(460, int(parent_h * 0.58))
        self.setFixedSize(dialog_w, dialog_h)
        self.record = record
        self._setup()

    def _setup(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_title = QLabel("Return Assessment")
        self.lbl_title.setObjectName("lbl_return_title")
        layout.addRow(self.lbl_title)

        self.lbl_subtitle = QLabel("Assess product condition before completing return.")
        self.lbl_subtitle.setObjectName("lbl_return_subtitle")
        layout.addRow(self.lbl_subtitle)

        info = QLabel(f"<b>{self.record['comic_title']}</b> — {self.record['borrower_name']}")
        info.setObjectName("lbl_return_info")
        info.setWordWrap(True)
        layout.addRow(info)

        self.cmb_condition = QComboBox()
        self.cmb_condition.addItems(["Good", "Damaged", "Lost"])
        self.cmb_condition.currentTextChanged.connect(self._on_condition_changed)
        layout.addRow("Condition:", self.cmb_condition)

        self.txt_notes = QLineEdit()
        self.txt_notes.setPlaceholderText("Describe damage if applicable...")
        self.txt_notes.setEnabled(False)
        layout.addRow("Notes:", self.txt_notes)

        self.spn_fee = QDoubleSpinBox()
        self.spn_fee.setPrefix("₱ ")
        self.spn_fee.setMaximum(99999.99)
        self.spn_fee.setDecimals(2)
        self.spn_fee.setEnabled(False)
        # Default fee is the comic's price if lost
        self.comic_price = float(self.record.get("price", 0) or 0)
        layout.addRow("Fee:", self.spn_fee)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_confirm = QPushButton("Confirm Return")
        btn_confirm.setObjectName("btn_save")
        btn_confirm.setMinimumHeight(38)
        btn_confirm.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_confirm)
        btn_layout.addWidget(btn_cancel)
        layout.addRow(btn_layout)

        self.setStyleSheet("""
            QDialog { background-color: #edf1f7; color: #1f2937; }
            QLabel#lbl_return_title {
                font-size: 22px;
                font-weight: 800;
                color: #13253f;
            }
            QLabel#lbl_return_subtitle {
                font-size: 12px;
                color: #5f7088;
                padding-bottom: 2px;
            }
            QLabel#lbl_return_info {
                color: #1f2937;
                background-color: #f8fafc;
                border: 1px solid #e5eaf2;
                border-radius: 8px;
                padding: 8px 10px;
            }
            QComboBox, QLineEdit, QDoubleSpinBox {
                border: 1px solid #ccd6e3; border-radius: 8px; padding: 8px 12px;
                min-height: 32px; background-color: #fff; color: #111827; font-size: 13px;
            }
            QComboBox:focus, QLineEdit:focus, QDoubleSpinBox:focus { border: 2px solid #1f7dd6; }
            QPushButton#btn_save {
                background-color: #1f7a45; color: #fff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_save:hover { background-color: #18663a; }
            QPushButton#btn_cancel {
                background-color: #6b7280; color: #fff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_cancel:hover { background-color: #4b5563; }
        """)

    def _on_condition_changed(self, condition):
        is_damaged_lost = condition in ("Damaged", "Lost")
        self.txt_notes.setEnabled(is_damaged_lost)
        self.spn_fee.setEnabled(is_damaged_lost)
        if condition == "Lost":
            self.spn_fee.setValue(self.comic_price)
        elif condition == "Good":
            self.spn_fee.setValue(0)
            self.txt_notes.clear()

    def get_data(self):
        return (
            self.cmb_condition.currentText(),
            self.txt_notes.text().strip(),
            self.spn_fee.value(),
        )
