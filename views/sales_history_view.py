"""
views/sales_history_view.py
===============================================================
Sales History page — browse, filter, and inspect past sales.
Includes This Week / This Month / This Year quick-filter buttons.
===============================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDateEdit, QDialog,
    QFormLayout, QSizePolicy, QSpacerItem, QTextEdit, QFileDialog, QFrame,
    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt, QDate, QEasingCurve, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter, QPrinterInfo
from datetime import datetime
from html import escape
import re


class SalesHistoryView(QWidget):
    """Page for viewing and filtering sales history."""

    def __init__(self, user):
        super().__init__()
        self.setObjectName("salesHistoryPage")
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

        # Filter row
        self.horizontalLayout_filter = QHBoxLayout()
        self.horizontalLayout_filter.setObjectName("horizontalLayout_filter")
        self.horizontalLayout_filter.setSpacing(10)

        lbl_from = QLabel("From:")
        lbl_from.setObjectName("lbl_from")
        self.horizontalLayout_filter.addWidget(lbl_from)

        self.date_from = QDateEdit(self)
        self.date_from.setObjectName("date_from")
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(35)
        self.horizontalLayout_filter.addWidget(self.date_from)

        lbl_to = QLabel("To:")
        lbl_to.setObjectName("lbl_to")
        self.horizontalLayout_filter.addWidget(lbl_to)

        self.date_to = QDateEdit(self)
        self.date_to.setObjectName("date_to")
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(35)
        self.horizontalLayout_filter.addWidget(self.date_to)

        self.btn_filter = QPushButton()
        self.btn_filter.setObjectName("btn_filter")
        self.btn_filter.setMinimumHeight(35)
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.clicked.connect(self._filter_sales)
        self.horizontalLayout_filter.addWidget(self.btn_filter)

        self.btn_all = QPushButton()
        self.btn_all.setObjectName("btn_all")
        self.btn_all.setMinimumHeight(35)
        self.btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_all.clicked.connect(self._show_all)
        self.horizontalLayout_filter.addWidget(self.btn_all)

        self.horizontalLayout_filter.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.verticalLayout_main.addLayout(self.horizontalLayout_filter)

        # Quick-filter row
        self.horizontalLayout_quick = QHBoxLayout()
        self.horizontalLayout_quick.setSpacing(10)

        self.btn_week = QPushButton("This Week")
        self.btn_week.setObjectName("btn_quick")
        self.btn_week.setMinimumHeight(35)
        self.btn_week.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_week.clicked.connect(self._show_weekly)
        self.horizontalLayout_quick.addWidget(self.btn_week)

        self.btn_month = QPushButton("This Month")
        self.btn_month.setObjectName("btn_quick")
        self.btn_month.setMinimumHeight(35)
        self.btn_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_month.clicked.connect(self._show_monthly)
        self.horizontalLayout_quick.addWidget(self.btn_month)

        self.btn_year = QPushButton("This Year")
        self.btn_year.setObjectName("btn_quick")
        self.btn_year.setMinimumHeight(35)
        self.btn_year.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_year.clicked.connect(self._show_yearly)
        self.horizontalLayout_quick.addWidget(self.btn_year)

        self.horizontalLayout_quick.addStretch()
        self.verticalLayout_main.addLayout(self.horizontalLayout_quick)

        # Hint
        self.lbl_hint = QLabel(self)
        self.lbl_hint.setObjectName("lbl_hint")
        self.verticalLayout_main.addWidget(self.lbl_hint)

        # Table
        self.table = QTableWidget(self)
        self.table.setObjectName("table")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Sale ID", "Date", "Total Amount", "Cashier"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self._view_sale_details)
        self.verticalLayout_main.addWidget(self.table)

        self.horizontalLayout_actions = QHBoxLayout()
        self.horizontalLayout_actions.setSpacing(10)

        self.btn_view_receipt = QPushButton("View Receipt")
        self.btn_view_receipt.setObjectName("btn_view_receipt")
        self.btn_view_receipt.setMinimumHeight(35)
        self.btn_view_receipt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_receipt.clicked.connect(self._view_sale_receipt)
        self.horizontalLayout_actions.addWidget(self.btn_view_receipt)

        self.btn_refund = QPushButton("Process Refund")
        self.btn_refund.setObjectName("btn_refund")
        self.btn_refund.setMinimumHeight(35)
        self.btn_refund.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refund.clicked.connect(self._process_refund_for_selected_sale)
        self.horizontalLayout_actions.addWidget(self.btn_refund)

        self.horizontalLayout_actions.addStretch()
        self.verticalLayout_main.addLayout(self.horizontalLayout_actions)

        # Total label
        self.lbl_total = QLabel(self)
        self.lbl_total.setObjectName("lbl_total")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.verticalLayout_main.addWidget(self.lbl_total)

    def retranslateUi(self):
        self.lbl_header.setText("Sales History")
        self.btn_filter.setText("Filter")
        self.btn_all.setText("Show All")
        self.lbl_hint.setText("Double-click a row to view sale details.")
        self.lbl_total.setText("Total: ₱0.00")

    def _normalize_title(self, title):
        """Insert missing spaces in CamelCase-like titles for cleaner display."""
        text = str(title or "").strip()
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ── Data ────────────────────────────────────────────────
    def refresh_data(self):
        self._show_all()

    def _filter_sales(self):
        from controllers.sales_history_ctrl import get_filtered_sales

        if self.date_from.date() > self.date_to.date():
            QMessageBox.warning(self, "Invalid Date Range",
                                "'From' date must be before or equal to 'To' date.")
            return

        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        sales = get_filtered_sales(date_from, date_to)
        self._fill_table(sales)

    def _show_all(self):
        from controllers.sales_history_ctrl import get_all_sales
        sales = get_all_sales()
        self._fill_table(sales)

    def _show_weekly(self):
        from controllers.sales_history_ctrl import get_weekly_sales_ctrl
        sales = get_weekly_sales_ctrl()
        self._fill_table(sales)

    def _show_monthly(self):
        from controllers.sales_history_ctrl import get_monthly_sales_ctrl
        sales = get_monthly_sales_ctrl()
        self._fill_table(sales)

    def _show_yearly(self):
        from controllers.sales_history_ctrl import get_yearly_sales_ctrl
        sales = get_yearly_sales_ctrl()
        self._fill_table(sales)

    def _fill_table(self, sales):
        self.table.setRowCount(len(sales))
        total = 0.0
        for r, sale in enumerate(sales):
            self.table.setItem(r, 0, QTableWidgetItem(str(sale["sale_id"])))
            sd = sale["sale_date"]
            if hasattr(sd, "strftime"):
                sd = sd.strftime("%d/%m/%Y")
            self.table.setItem(r, 1, QTableWidgetItem(str(sd)))
            amount = float(sale["total_amount"])
            total += amount
            self.table.setItem(r, 2, QTableWidgetItem(f"₱{amount:,.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(sale.get("cashier", "—")))

        self.lbl_total.setText(f"Total: ₱{total:,.2f}")

    def _view_sale_details(self):
        row = self.table.currentRow()
        if row < 0:
            return

        sale_id = int(self.table.item(row, 0).text())
        from controllers.sales_history_ctrl import get_sale_detail
        details = get_sale_detail(sale_id)

        if not details:
            QMessageBox.information(self, "No Details", "No detail data found for this sale.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Sale #{sale_id} — Details")
        dialog_w = max(500, int(self.width() * 0.58))
        dialog_h = max(320, int(self.height() * 0.54))
        dlg.setFixedSize(dialog_w, dialog_h)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl_title = QLabel(f"Sale #{sale_id} Details")
        lbl_title.setObjectName("lbl_sale_detail_title")
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Products included in this transaction")
        lbl_sub.setObjectName("lbl_sale_detail_sub")
        layout.addWidget(lbl_sub)

        detail_table = QTableWidget()
        detail_table.setObjectName("detailTable")
        detail_table.setColumnCount(4)
        detail_table.setHorizontalHeaderLabels(["Product", "Qty", "Unit Price", "Subtotal"])
        detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        detail_table.verticalHeader().setVisible(False)
        detail_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        detail_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        detail_table.setAlternatingRowColors(True)
        detail_table.setRowCount(len(details))

        for i, d in enumerate(details):
            detail_table.setItem(i, 0, QTableWidgetItem(self._normalize_title(d.get("comic_title", d.get("title", "")))))
            qty = int(d["quantity"])
            price = float(d["unit_price"])
            detail_table.setItem(i, 1, QTableWidgetItem(str(qty)))
            detail_table.setItem(i, 2, QTableWidgetItem(f"₱{price:,.2f}"))
            detail_table.setItem(i, 3, QTableWidgetItem(f"₱{qty * price:,.2f}"))

        layout.addWidget(detail_table)

        btn_close = QPushButton("Close")
        btn_close.setObjectName("btn_close_detail")
        btn_close.setMinimumHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignRight)

        dlg.setStyleSheet("""
            QDialog { background-color: #edf1f7; color: #1f2937; }
            QLabel#lbl_sale_detail_title {
                font-size: 21px;
                font-weight: 800;
                color: #13253f;
            }
            QLabel#lbl_sale_detail_sub {
                font-size: 12px;
                color: #5f7088;
            }
            QTableWidget {
                background-color: #ffffff; color: #333333; alternate-background-color: #f8f9fa;
                border: none; border-radius: 10px; gridline-color: #f0f0f0;
                font-size: 13px; padding: 4px;
            }
            QTableWidget::item { padding: 6px 8px; }
            QTableWidget::item:hover { background-color: #eaf2fb; }
            QHeaderView::section {
                background-color: #2c3e50; color: #ffffff; padding: 10px 8px;
                border: none; font-weight: bold; font-size: 12px;
            }
            QPushButton#btn_close_detail {
                                background-color: #6b7280; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
                        QPushButton#btn_close_detail:hover { background-color: #4b5563; }
        """)
        dlg.exec()

    def _build_receipt_html(self, sale_id, sale_date, cashier, details, total):
        item_rows = ""
        for item in details:
            title = self._normalize_title(item.get("comic_title", item.get("title", "Product")))
            qty = int(item.get("quantity", 0) or 0)
            price = float(item.get("unit_price", 0) or 0)
            subtotal = qty * price
            item_rows += (
                "<tr>"
                f"<td class='item'>{escape(title)}</td>"
                f"<td>{qty}</td>"
                f"<td>₱{price:,.2f}</td>"
                f"<td class='amount'>₱{subtotal:,.2f}</td>"
                "</tr>"
            )

        return f"""
        <html>
          <head>
            <style>
                            @page {{ size: A4; margin: 12mm; }}
                            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; color: #1f2937; }}
                            .sheet {{ border: 1px solid #dbe1ea; border-radius: 12px; padding: 16px; background: #fff; max-width: 740px; margin: 0 auto; }}
              .title {{ font-size: 21px; font-weight: 800; color: #13253f; }}
              .meta {{ margin-top: 8px; margin-bottom: 12px; font-size: 12px; color: #4b5563; }}
              table {{ width: 100%; border-collapse: collapse; }}
              th, td {{ padding: 8px 6px; border-bottom: 1px solid #eef2f7; font-size: 12px; }}
              th {{ text-align: left; color: #334155; }}
              td.amount {{ font-weight: 700; color: #111827; }}
              .total {{ margin-top: 12px; text-align: right; font-size: 15px; font-weight: 800; color: #13253f; }}
            </style>
          </head>
          <body>
            <div class='sheet'>
              <div class='title'>POS Receipt</div>
              <div class='meta'>Sale ID: #{sale_id} | Date: {escape(sale_date)} | Cashier: {escape(cashier)}</div>
              <table>
                <thead>
                  <tr><th>Product</th><th>Qty</th><th>Unit Price</th><th>Subtotal</th></tr>
                </thead>
                <tbody>{item_rows}</tbody>
              </table>
              <div class='total'>TOTAL: ₱{total:,.2f}</div>
            </div>
          </body>
        </html>
        """

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

    def _view_sale_receipt(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "No Records", "There are no sales records to view.")
            return

        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "No Selection", "Please click a sale record first.")
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please click a sale record first.")
            return

        sale_id = int(self.table.item(row, 0).text())
        sale_date = self.table.item(row, 1).text()
        cashier = self.table.item(row, 3).text()

        from controllers.sales_history_ctrl import get_sale_detail
        details = get_sale_detail(sale_id)
        if not details:
            QMessageBox.information(self, "No Details", "No detail data found for this sale.")
            return

        total = 0.0

        for item in details:
            qty = int(item.get("quantity", 0) or 0)
            price = float(item.get("unit_price", 0) or 0)
            total += qty * price

        receipt_html = self._build_receipt_html(sale_id, sale_date, cashier, details, total)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Receipt - Sale #{sale_id}")
        dialog_w = max(420, int(self.width() * 0.5))
        dialog_h = max(380, int(self.height() * 0.62))
        dialog.setFixedSize(dialog_w, dialog_h)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl_caption = QLabel("Preview before printing")
        lbl_caption.setObjectName("receipt_preview_caption")
        layout.addWidget(lbl_caption)

        receipt = QTextEdit()
        receipt.setHtml(receipt_html)
        receipt.setReadOnly(True)
        receipt.setFont(QFont("Segoe UI", 10))
        layout.addWidget(receipt)

        btn_row = QHBoxLayout()
        btn_print = QPushButton("Print on Windows")
        btn_print.setObjectName("btn_print_receipt")
        btn_print.setMinimumHeight(38)
        btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_print.clicked.connect(
            lambda: self._simulate_print(
                dialog, receipt, btn_print, btn_close,
                f"Sale Receipt #{sale_id}", receipt_html
            )
        )
        btn_row.addWidget(btn_print)

        btn_close = QPushButton("Close")
        btn_close.setObjectName("btn_close_receipt")
        btn_close.setMinimumHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(dialog.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        dialog.setStyleSheet("""
            QDialog { background-color: #eef2f7; color: #1f2937; }
            QLabel#receipt_preview_caption {
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
                color: #4b5563;
                padding-left: 4px;
            }
            QTextEdit {
                background-color: #f7f9fc; color: #1f2937;
                border: 1px solid #d4dbe5; border-radius: 10px; padding: 8px;
            }
            QPushButton#btn_print_receipt {
                background-color: #1f7a45; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_print_receipt:hover { background-color: #18663a; }
            QPushButton#btn_print_receipt:disabled { background-color: #9aa4b2; }
            QPushButton#btn_close_receipt {
                background-color: #6b7280; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_close_receipt:hover { background-color: #4b5563; }
        """)
        dialog.exec()

    def _process_refund_for_selected_sale(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "No Records", "There are no sales records to refund.")
            return

        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "No Selection", "Please click a sale record first.")
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please click a sale record first.")
            return

        sale_id = int(self.table.item(row, 0).text())

        from controllers.sales_history_ctrl import get_refundable_items_ctrl
        refundable_items = get_refundable_items_ctrl(sale_id)
        if not refundable_items:
            QMessageBox.information(
                self,
                "No Refundable Items",
                "This sale has no remaining refundable products."
            )
            return

        dlg = SaleRefundDialog(self, self.user, sale_id, refundable_items)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()


    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #salesHistoryPage { background-color: #f0f2f5; }
            QLabel#lbl_header {
                font-size: 20px; font-weight: bold; color: #2c3e50; padding-bottom: 4px;
            }
            QLabel#lbl_hint { font-size: 12px; color: #7f8c8d; padding: 0; }
            QLabel#lbl_total {
                font-size: 15px; font-weight: bold; color: #2c3e50; padding-top: 4px;
            }
            QDateEdit {
                border: 1px solid #d0d4d8; border-radius: 6px; padding: 8px 12px;
                background-color: #ffffff; color: #333333; font-size: 13px;
            }
            QDateEdit:focus { border: 2px solid #3498db; }
            QPushButton#btn_filter {
                background-color: #3498db; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_filter:hover { background-color: #2980b9; }
            QPushButton#btn_all {
                background-color: #95a5a6; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_all:hover { background-color: #7f8c8d; }
            QPushButton#btn_quick {
                background-color: #8e44ad; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_quick:hover { background-color: #7d3c98; }
            QPushButton#btn_view_receipt {
                background-color: #3498db; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_view_receipt:hover { background-color: #2980b9; }
            QPushButton#btn_refund {
                background-color: #b45309; color: #ffffff; border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_refund:hover { background-color: #92400e; }
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


class SaleRefundDialog(QDialog):
    """Refund dialog strictly linked to one selected sale."""

    def __init__(self, parent, user, sale_id, refundable_items):
        super().__init__(parent)
        self.user = user
        self.sale_id = sale_id
        self.refundable_items = refundable_items

        self.setWindowTitle(f"Process Refund - Sale #{sale_id}")
        parent_w = parent.width() if parent else 1200
        parent_h = parent.height() if parent else 800
        dialog_w = max(560, int(parent_w * 0.46))
        dialog_h = max(500, int(parent_h * 0.64))
        self.setFixedSize(dialog_w, dialog_h)
        self._setup()

    def _setup(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"Refund for Sale #{self.sale_id}")
        title.setObjectName("lbl_refund_title")
        layout.addRow(title)

        subtitle = QLabel("Only products from this transaction can be refunded.")
        subtitle.setObjectName("lbl_refund_subtitle")
        layout.addRow(subtitle)

        self.lbl_sale = QLabel(f"Sale #{self.sale_id}")
        self.lbl_sale.setObjectName("lbl_sale_id")
        layout.addRow("Sale ID:", self.lbl_sale)

        self.cmb_comic = QComboBox()
        self.cmb_comic.setMinimumHeight(34)
        self.cmb_comic.currentIndexChanged.connect(self._on_item_selected)
        layout.addRow("Product:", self.cmb_comic)

        self.lbl_remaining = QLabel("0")
        self.lbl_remaining.setObjectName("lbl_remaining")
        layout.addRow("Refundable Qty:", self.lbl_remaining)

        self.spn_quantity = QSpinBox()
        self.spn_quantity.setMinimum(1)
        self.spn_quantity.setMaximum(1)
        self.spn_quantity.valueChanged.connect(self._update_amount_from_qty)
        layout.addRow("Quantity:", self.spn_quantity)

        self.spn_refund_amount = QDoubleSpinBox()
        self.spn_refund_amount.setPrefix("₱ ")
        self.spn_refund_amount.setMaximum(999999.99)
        self.spn_refund_amount.setDecimals(2)
        layout.addRow("Refund Amount:", self.spn_refund_amount)

        self.cmb_condition = QComboBox()
        self.cmb_condition.addItems(["Good", "Damaged", "Lost"])
        layout.addRow("Item Condition:", self.cmb_condition)

        self.txt_reason = QLineEdit()
        self.txt_reason.setPlaceholderText("Reason for refund...")
        layout.addRow("Reason:", self.txt_reason)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        btn_process = QPushButton("Process Refund")
        btn_process.setObjectName("btn_save")
        btn_process.setMinimumHeight(38)
        btn_process.clicked.connect(self._process)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_process)
        btn_layout.addWidget(btn_cancel)
        layout.addRow(btn_layout)

        self._load_items()

        self.setStyleSheet("""
            QDialog { background-color: #edf1f7; color: #1f2937; }
            QLabel#lbl_refund_title {
                font-size: 22px;
                font-weight: 800;
                color: #13253f;
            }
            QLabel#lbl_refund_subtitle {
                font-size: 12px;
                color: #5f7088;
                padding-bottom: 2px;
            }
            QLabel#lbl_sale_id, QLabel#lbl_remaining {
                color: #1f2937;
                background-color: #eef3fb;
                border: 1px solid #cfd9ea;
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 16px;
                font-weight: 600;
            }
            QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
                border: 1px solid #ccd6e3; border-radius: 8px; padding: 8px 12px;
                min-height: 32px; background-color: #fff; color: #111827; font-size: 13px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border: 2px solid #1f7dd6;
            }
            QPushButton#btn_save {
                background-color: #b45309; color: #fff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_save:hover { background-color: #92400e; }
            QPushButton#btn_cancel {
                background-color: #6b7280; color: #fff; border: none; border-radius: 8px;
                padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_cancel:hover { background-color: #4b5563; }
        """)

    def _load_items(self):
        self.cmb_comic.clear()
        for item in self.refundable_items:
            title = str(item.get("comic_title", "Product"))
            price = float(item.get("unit_price", 0) or 0)
            qty = int(item.get("refundable_qty", 0) or 0)
            label = f"{title} (Max {qty}, ₱{price:,.2f})"
            self.cmb_comic.addItem(label, item)
        self._on_item_selected(0)

    def _on_item_selected(self, index):
        item = self.cmb_comic.currentData()
        if not item:
            self.lbl_remaining.setText("0")
            self.spn_quantity.setMaximum(1)
            self.spn_refund_amount.setValue(0)
            return

        max_qty = int(item.get("refundable_qty", 1) or 1)
        price = float(item.get("unit_price", 0) or 0)
        self.lbl_remaining.setText(str(max_qty))
        self.spn_quantity.setMaximum(max_qty)
        self.spn_quantity.setValue(1)
        self.spn_refund_amount.setValue(price)

    def _update_amount_from_qty(self):
        item = self.cmb_comic.currentData()
        if not item:
            return
        price = float(item.get("unit_price", 0) or 0)
        self.spn_refund_amount.setValue(price * self.spn_quantity.value())

    def _process(self):
        item = self.cmb_comic.currentData()
        if not item:
            QMessageBox.warning(self, "No Product", "Please select a product.")
            return

        reason = self.txt_reason.text().strip()
        if not reason:
            QMessageBox.warning(self, "No Reason", "Please enter a reason for the refund.")
            self.txt_reason.setFocus()
            return

        qty = int(self.spn_quantity.value())
        amount = float(self.spn_refund_amount.value())
        condition = self.cmb_condition.currentText()
        title = str(item.get("comic_title", "Product"))

        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Refund amount must be greater than zero.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Refund",
            f"Process refund of ₱{amount:,.2f} for {qty}x {title}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        from controllers.sales_history_ctrl import process_sale_refund_ctrl
        result = process_sale_refund_ctrl(
            self.sale_id,
            int(item["comic_id"]),
            qty,
            amount,
            reason,
            condition,
            self.user["user_id"],
        )
        if result:
            QMessageBox.information(self, "Success", "Refund processed successfully!")
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Refund Failed",
                "Unable to process refund. Check quantity/amount and sale linkage."
            )
