"""
views/pos_view.py
===============================================================
Point of Sale (POS) page — select comics, add to cart, complete sale.
Includes printable receipts and refund processing.
===============================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QSpinBox, QComboBox,
    QTextEdit, QDialog, QFormLayout, QDoubleSpinBox,
    QLineEdit, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, QPoint
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter, QPrinterInfo
from datetime import datetime
from html import escape
import re


class POSView(QWidget):
    """POS page for selling comics."""

    def __init__(self, user):
        super().__init__()
        self.setObjectName("posPage")
        self.user = user
        self.cart = []
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

        # Selection row
        self.horizontalLayout_selection = QHBoxLayout()
        self.horizontalLayout_selection.setObjectName("horizontalLayout_selection")
        self.horizontalLayout_selection.setSpacing(10)

        self.lbl_comic = QLabel(self)
        self.lbl_comic.setObjectName("lbl_comic")
        self.horizontalLayout_selection.addWidget(self.lbl_comic)

        self.cmb_comic = QComboBox(self)
        self.cmb_comic.setObjectName("cmb_comic")
        self.cmb_comic.setMinimumHeight(38)
        self.cmb_comic.setMinimumWidth(300)
        self.cmb_comic.currentIndexChanged.connect(self._on_comic_selected)
        self.horizontalLayout_selection.addWidget(self.cmb_comic)

        self.lbl_price_label = QLabel(self)
        self.lbl_price_label.setObjectName("lbl_price_label")
        self.horizontalLayout_selection.addWidget(self.lbl_price_label)

        self.lbl_price_value = QLabel(self)
        self.lbl_price_value.setObjectName("lbl_price_value")
        self.lbl_price_value.setMinimumWidth(100)
        self.horizontalLayout_selection.addWidget(self.lbl_price_value)

        self.lbl_stock_label = QLabel(self)
        self.lbl_stock_label.setObjectName("lbl_stock_label")
        self.horizontalLayout_selection.addWidget(self.lbl_stock_label)

        self.lbl_stock_value = QLabel(self)
        self.lbl_stock_value.setObjectName("lbl_stock_value")
        self.horizontalLayout_selection.addWidget(self.lbl_stock_value)

        self.lbl_qty = QLabel(self)
        self.lbl_qty.setObjectName("lbl_qty")
        self.horizontalLayout_selection.addWidget(self.lbl_qty)

        self.spn_qty = QSpinBox(self)
        self.spn_qty.setObjectName("spn_qty")
        self.spn_qty.setMinimum(1)
        self.spn_qty.setMaximum(999)
        self.spn_qty.setMinimumHeight(38)
        self.horizontalLayout_selection.addWidget(self.spn_qty)

        self.btn_add_cart = QPushButton(self)
        self.btn_add_cart.setObjectName("btn_add_cart")
        self.btn_add_cart.setMinimumHeight(38)
        self.btn_add_cart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_cart.clicked.connect(self._add_to_cart)
        self.horizontalLayout_selection.addWidget(self.btn_add_cart)

        self.verticalLayout_main.addLayout(self.horizontalLayout_selection)

        # Cart header
        self.lbl_cart_header = QLabel(self)
        self.lbl_cart_header.setObjectName("lbl_cart_header")
        self.verticalLayout_main.addWidget(self.lbl_cart_header)

        # Cart table
        self.table_cart = QTableWidget(self)
        self.table_cart.setObjectName("table_cart")
        self.table_cart.setColumnCount(5)
        self.table_cart.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal", "Action"])
        self.table_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cart.verticalHeader().setVisible(False)
        self.table_cart.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalLayout_main.addWidget(self.table_cart)

        # Bottom bar
        self.horizontalLayout_bottom = QHBoxLayout()
        self.horizontalLayout_bottom.setObjectName("horizontalLayout_bottom")
        self.horizontalLayout_bottom.setSpacing(12)

        self.lbl_total = QLabel(self)
        self.lbl_total.setObjectName("lbl_total")
        self.horizontalLayout_bottom.addWidget(self.lbl_total)

        self.horizontalLayout_bottom.addStretch()

        self.btn_refund = QPushButton(self)
        self.btn_refund.setObjectName("btn_refund")
        self.btn_refund.setMinimumHeight(42)
        self.btn_refund.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refund.clicked.connect(self._open_refund_dialog)
        self.horizontalLayout_bottom.addWidget(self.btn_refund)
        self.btn_refund.hide()

        self.btn_clear = QPushButton(self)
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setMinimumHeight(42)
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_cart)
        self.horizontalLayout_bottom.addWidget(self.btn_clear)

        self.btn_complete = QPushButton(self)
        self.btn_complete.setObjectName("btn_complete")
        self.btn_complete.setMinimumHeight(42)
        self.btn_complete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_complete.clicked.connect(self._complete_sale)
        self.horizontalLayout_bottom.addWidget(self.btn_complete)

        self.verticalLayout_main.addLayout(self.horizontalLayout_bottom)

    def retranslateUi(self):
        self.lbl_header.setText("Point of Sale")
        self.lbl_comic.setText("Product:")
        self.lbl_price_label.setText("Price:")
        self.lbl_price_value.setText("₱0.00")
        self.lbl_stock_label.setText("Stock:")
        self.lbl_stock_value.setText("0")
        self.lbl_qty.setText("Qty:")
        self.btn_add_cart.setText("Add to Cart")
        self.lbl_cart_header.setText("Cart Items")
        self.lbl_total.setText("Total: ₱0.00")
        self.btn_refund.setText("Process Refund")
        self.btn_clear.setText("Clear Cart")
        self.btn_complete.setText("Complete Sale")

    def _normalize_title(self, title):
        """Insert missing spaces in CamelCase-like titles for cleaner display."""
        text = str(title or "").strip()
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ── Data ────────────────────────────────────────────────
    def refresh_data(self):
        from controllers.pos_ctrl import get_available_comics_list
        comics = get_available_comics_list()

        self.cmb_comic.blockSignals(True)
        self.cmb_comic.clear()
        self.cmb_comic.addItem("-- Select a product --", None)
        for comic in comics:
            clean_title = self._normalize_title(comic.get("title", "Product"))
            display = f"{clean_title} (Issue {comic.get('issue_number', 'N/A')})"
            self.cmb_comic.addItem(display, comic)
        self.cmb_comic.blockSignals(False)
        self._on_comic_selected(0)

    def _on_comic_selected(self, index):
        comic = self.cmb_comic.currentData()
        if comic:
            self.lbl_price_value.setText(f"₱{comic['price']:,.2f}")
            self.lbl_stock_value.setText(str(comic["stock_quantity"]))
            self.spn_qty.setMaximum(comic["stock_quantity"])
        else:
            self.lbl_price_value.setText("₱0.00")
            self.lbl_stock_value.setText("0")
            self.spn_qty.setMaximum(1)

    # ── Cart operations ─────────────────────────────────────
    def _add_to_cart(self):
        comic = self.cmb_comic.currentData()
        if not comic:
            QMessageBox.warning(self, "No Product", "Please select a product to add.")
            return

        qty = self.spn_qty.value()
        if qty <= 0:
            QMessageBox.warning(self, "Invalid Quantity", "Quantity must be at least 1.")
            return

        available = int(comic["stock_quantity"])

        for item in self.cart:
            if item["comic_id"] == comic["comic_id"]:
                new_qty = item["quantity"] + qty
                if new_qty > available:
                    QMessageBox.warning(
                        self, "Insufficient Stock",
                        f"Only {available} available in stock.\n"
                        f"You already have {item['quantity']} in the cart.")
                    return
                item["quantity"] = new_qty
                item["subtotal"] = item["unit_price"] * new_qty
                self._update_cart_table()
                return

        if qty > available:
            QMessageBox.warning(
                self, "Insufficient Stock",
                f"Only {available} available in stock.")
            return

        subtotal = float(comic["price"]) * qty
        self.cart.append({
            "comic_id": comic["comic_id"],
            "title": self._normalize_title(comic.get("title", "Product")),
            "quantity": qty,
            "unit_price": float(comic["price"]),
            "subtotal": subtotal,
        })
        self._update_cart_table()

    def _update_cart_table(self):
        self.table_cart.setRowCount(len(self.cart))
        for r, item in enumerate(self.cart):
            self.table_cart.setItem(r, 0, QTableWidgetItem(item["title"]))
            self.table_cart.setItem(r, 1, QTableWidgetItem(f"₱{item['unit_price']:,.2f}"))
            self.table_cart.setItem(r, 2, QTableWidgetItem(str(item["quantity"])))
            self.table_cart.setItem(r, 3, QTableWidgetItem(f"₱{item['subtotal']:,.2f}"))

            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("btn_remove")
            remove_btn.setStyleSheet(
                "background-color:#c0392b; color:#fff; border:none; padding:4px 8px; border-radius:3px;")
            remove_btn.clicked.connect(lambda checked, idx=r: self._remove_from_cart(idx))
            self.table_cart.setCellWidget(r, 4, remove_btn)

        total = sum(i["subtotal"] for i in self.cart)
        self.lbl_total.setText(f"Total: ₱{total:,.2f}")

    def _remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self._update_cart_table()

    def _clear_cart(self):
        if not self.cart:
            return
        reply = QMessageBox.question(
            self, "Clear Cart",
            "Are you sure you want to clear all items from the cart?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cart.clear()
            self._update_cart_table()

    # ── Complete sale ───────────────────────────────────────
    def _complete_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "Please add items to the cart first.")
            return

        total = sum(i["subtotal"] for i in self.cart)
        reply = QMessageBox.question(
            self, "Confirm Sale",
            f"Complete this sale for ₱{total:,.2f}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from controllers.pos_ctrl import process_sale
            sale_id = process_sale(self.user["user_id"], self.cart)
            if sale_id:
                self._show_receipt(sale_id, total)
                self.cart.clear()
                self._update_cart_table()
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to process sale.")

    def _show_receipt(self, sale_id, total):
        now = datetime.now()
        lines = [
            "=" * 40,
            "     PRODUCT POS — RECEIPT",
            "=" * 40,
            f"  Sale ID:    #{sale_id}",
            f"  Date:       {now.strftime('%d/%m/%Y')}",
            f"  Time:       {now.strftime('%I:%M %p')}",
            f"  Cashier:    {self.user['full_name']}",
            "-" * 40,
        ]
        for item in self.cart:
            lines.append(f"  {item['title']}")
            lines.append(f"    {item['quantity']} x ₱{item['unit_price']:,.2f} = ₱{item['subtotal']:,.2f}")
        lines += [
            "-" * 40,
            f"  TOTAL:      ₱{total:,.2f}",
            "=" * 40,
            "     Thank you for your purchase!",
            "=" * 40,
        ]

        receipt_html = self._build_receipt_html("POS Receipt", lines)

        dialog = QDialog(self)
        dialog.setWindowTitle("Receipt")
        dialog_w = max(420, int(self.width() * 0.5))
        dialog_h = max(400, int(self.height() * 0.62))
        dialog.setFixedSize(dialog_w, dialog_h)
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        caption = QLabel("Preview before printing")
        caption.setObjectName("receipt_preview_caption")
        layout.addWidget(caption)

        receipt = QTextEdit()
        receipt.setHtml(receipt_html)
        receipt.setReadOnly(True)
        receipt.setFont(QFont("Segoe UI", 10))
        layout.addWidget(receipt)

        btn_row = QHBoxLayout()
        print_btn = QPushButton("Print on Windows")
        print_btn.setObjectName("btn_print_action")
        btn_row.addWidget(print_btn)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("btn_close_receipt")
        close_btn.clicked.connect(dialog.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)
        dialog.setLayout(layout)
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
            QPushButton#btn_print_action {
                background-color: #1f7a45; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_print_action:hover { background-color: #18663a; }
            QPushButton#btn_close_receipt {
                background-color: #6b7280; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_close_receipt:hover { background-color: #4b5563; }
        """)

        print_btn.clicked.connect(
            lambda: self._simulate_print(dialog, receipt, print_btn, close_btn, "POS Receipt", receipt_html)
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

    # ── Refund ──────────────────────────────────────────────
    def _open_refund_dialog(self):
        QMessageBox.information(
            self,
            "Refund Moved",
            "Refund processing is now handled in Sales History and linked to a selected sale."
        )

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #posPage { background-color: #f0f2f5; }
            QLabel#lbl_header {
                font-size: 20px; font-weight: bold; color: #2c3e50; padding-bottom: 4px;
            }
            QLabel#lbl_cart_header {
                font-size: 15px; font-weight: bold; color: #2c3e50; padding-top: 4px;
            }
            QLabel#lbl_comic, QLabel#lbl_price_label,
            QLabel#lbl_stock_label, QLabel#lbl_qty {
                font-size: 13px; color: #555555;
            }
            QLabel#lbl_price_value { font-size: 13px; font-weight: bold; color: #2c3e50; }
            QLabel#lbl_stock_value { font-size: 13px; color: #2c3e50; }
            QLabel#lbl_total { font-size: 20px; font-weight: bold; color: #27ae60; }
            QComboBox, QSpinBox {
                border: 1px solid #d0d4d8; border-radius: 8px; padding: 8px 12px;
                background-color: #ffffff; color: #333333; font-size: 13px;
            }
            QPushButton#btn_add_cart {
                background-color: #3498db; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_add_cart:hover { background-color: #2980b9; }
            QPushButton#btn_refund {
                background-color: #e67e22; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_refund:hover { background-color: #d35400; }
            QPushButton#btn_clear {
                background-color: #c0392b; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_clear:hover { background-color: #a93226; }
            QPushButton#btn_complete {
                background-color: #27ae60; color: #ffffff; border: none;
                border-radius: 8px; padding: 10px 32px; font-size: 14px; font-weight: bold;
            }
            QPushButton#btn_complete:hover { background-color: #229954; }
            QTableWidget {
                background-color: #ffffff; color: #333333; border: none;
                border-radius: 10px; gridline-color: #f0f0f0;
                font-size: 13px; padding: 4px;
            }
            QTableWidget::item { padding: 6px 8px; }
            QTableWidget::item:hover { background-color: #eaf2fb; }
            QHeaderView::section {
                background-color: #2c3e50; color: #ffffff; padding: 10px 8px;
                border: none; font-weight: bold; font-size: 12px;
            }
        """)


# ═══════════════════════════════════════════════════════════
#  Refund Dialog
# ═══════════════════════════════════════════════════════════
class RefundDialog(QDialog):
    """Dialog for processing a refund on a past sale."""

    def __init__(self, parent, user):
        super().__init__(parent)
        self.setWindowTitle("Process Refund")
        parent_w = parent.width() if parent else 1200
        parent_h = parent.height() if parent else 800
        dialog_w = max(560, int(parent_w * 0.45))
        dialog_h = max(500, int(parent_h * 0.62))
        self.setFixedSize(dialog_w, dialog_h)
        self.user = user
        self._setup()

    def _setup(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_title = QLabel("Refund Transaction")
        self.lbl_title.setObjectName("lbl_refund_title")
        layout.addRow(self.lbl_title)

        self.lbl_subtitle = QLabel("Verify sale details before processing the refund.")
        self.lbl_subtitle.setObjectName("lbl_refund_subtitle")
        layout.addRow(self.lbl_subtitle)

        self.spn_sale_id = QSpinBox()
        self.spn_sale_id.setMinimum(1)
        self.spn_sale_id.setMaximum(999999)
        self.spn_sale_id.setPrefix("Sale #")
        layout.addRow("Sale ID:", self.spn_sale_id)

        self.cmb_comic = QComboBox()
        self.cmb_comic.setMinimumHeight(34)
        self.cmb_comic.currentIndexChanged.connect(self._on_comic_selected)
        self._load_comics()
        layout.addRow("Product:", self.cmb_comic)

        self.spn_quantity = QSpinBox()
        self.spn_quantity.setMinimum(1)
        self.spn_quantity.setMaximum(999)
        layout.addRow("Quantity:", self.spn_quantity)

        self.spn_refund_amount = QDoubleSpinBox()
        self.spn_refund_amount.setPrefix("₱ ")
        self.spn_refund_amount.setMaximum(99999.99)
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

    def _load_comics(self):
        from controllers.pos_ctrl import get_available_comics_list
        from models.comic_model import get_all_comics
        comics = get_all_comics()
        self.cmb_comic.clear()
        self.cmb_comic.addItem("-- Select product --", None)
        for c in comics:
            self.cmb_comic.addItem(
                f"{c['title']} (₱{c['price']:,.2f})", c
            )

    def _on_comic_selected(self, index):
        comic = self.cmb_comic.currentData()
        if comic:
            self.spn_refund_amount.setValue(float(comic["price"]))

    def _process(self):
        sale_id = self.spn_sale_id.value()
        comic = self.cmb_comic.currentData()
        if not comic:
            QMessageBox.warning(self, "No Product", "Please select a product.")
            return

        reason = self.txt_reason.text().strip()
        if not reason:
            QMessageBox.warning(self, "No Reason", "Please enter a reason for the refund.")
            self.txt_reason.setFocus()
            return

        qty = self.spn_quantity.value()
        amount = self.spn_refund_amount.value()
        condition = self.cmb_condition.currentText()

        reply = QMessageBox.question(
            self, "Confirm Refund",
            f"Process refund of ₱{amount:,.2f} for {qty}x {comic['title']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from controllers.pos_ctrl import process_refund
            result = process_refund(sale_id, comic["comic_id"], qty, amount,
                                    reason, condition, self.user["user_id"])
            if result:
                QMessageBox.information(self, "Success", "Refund processed successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to process refund.")
