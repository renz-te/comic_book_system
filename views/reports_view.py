"""
views/reports_view.py
===============================================================
Sales Reports page — generate date-range reports with summary
cards, a bar chart, and a data table.
Follows setupUi / retranslateUi pattern (Qt Designer compatible).

Widget hierarchy:
  QWidget (ReportsView)
    └─ verticalLayout_main
        ├─ lbl_header
        ├─ horizontalLayout_filter
        ├─ horizontalLayout_cards (3 stat cards)
        ├─ chartView
        └─ table
===============================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDateEdit, QFrame, QSizePolicy,
    QSpacerItem, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QPainter

try:
    from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False


class ReportsView(QWidget):
    """Page for generating sales reports."""

    _CLR_PRIMARY = "#3498db"
    _CLR_SUCCESS = "#27ae60"
    _CLR_WARNING = "#e67e22"

    def __init__(self, user):
        super().__init__()
        self.setObjectName("reportsPage")
        self.user = user
        self.setupUi()
        self.retranslateUi()
        self._apply_styles()

    # =============================================================
    #  setupUi
    # =============================================================
    def setupUi(self):
        self.verticalLayout_main = QVBoxLayout(self)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.verticalLayout_main.setSpacing(20)
        self.verticalLayout_main.setContentsMargins(32, 32, 32, 32)

        # Header
        self.lbl_header = QLabel(self)
        self.lbl_header.setObjectName("lbl_header")
        self.verticalLayout_main.addWidget(self.lbl_header)

        # Filter row
        self.horizontalLayout_filter = QHBoxLayout()
        self.horizontalLayout_filter.setObjectName("horizontalLayout_filter")
        self.horizontalLayout_filter.setSpacing(10)

        lbl_from = QLabel("From:")
        lbl_from.setObjectName("lbl_from_reports")
        self.horizontalLayout_filter.addWidget(lbl_from)

        self.date_from = QDateEdit(self)
        self.date_from.setObjectName("date_from")
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(35)
        self.horizontalLayout_filter.addWidget(self.date_from)

        lbl_to = QLabel("To:")
        lbl_to.setObjectName("lbl_to_reports")
        self.horizontalLayout_filter.addWidget(lbl_to)

        self.date_to = QDateEdit(self)
        self.date_to.setObjectName("date_to")
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(35)
        self.horizontalLayout_filter.addWidget(self.date_to)

        self.btn_generate = QPushButton()
        self.btn_generate.setObjectName("btn_generate")
        self.btn_generate.setMinimumHeight(35)
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self._generate_report)
        self.horizontalLayout_filter.addWidget(self.btn_generate)

        self.horizontalLayout_filter.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.verticalLayout_main.addLayout(self.horizontalLayout_filter)

        # Quick-filter row
        self.horizontalLayout_quick = QHBoxLayout()
        self.horizontalLayout_quick.setObjectName("horizontalLayout_quick")
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

        # Summary cards row
        self.horizontalLayout_cards = QHBoxLayout()
        self.horizontalLayout_cards.setObjectName("horizontalLayout_cards")
        self.horizontalLayout_cards.setSpacing(20)

        self.card_total_sales, self.lbl_total_sales_value = self._create_card(
            "cardTotalSales", "Total Sales", self._CLR_PRIMARY
        )
        self.card_transactions, self.lbl_transactions_value = self._create_card(
            "cardTransactions", "Transactions", self._CLR_SUCCESS
        )
        self.card_avg_sale, self.lbl_avg_sale_value = self._create_card(
            "cardAvgSale", "Avg. Sale", self._CLR_WARNING
        )

        self.horizontalLayout_cards.addWidget(self.card_total_sales)
        self.horizontalLayout_cards.addWidget(self.card_transactions)
        self.horizontalLayout_cards.addWidget(self.card_avg_sale)
        self.verticalLayout_main.addLayout(self.horizontalLayout_cards)

        # Chart
        if HAS_CHARTS:
            self.chart_view = QChartView()
            self.chart_view.setObjectName("chartView_reports")
            self.chart_view.setMinimumHeight(220)
            self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.verticalLayout_main.addWidget(self.chart_view)
        else:
            self.chart_view = None

        # Table
        self.table = QTableWidget(self)
        self.table.setObjectName("table")
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Transactions", "Revenue"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.verticalLayout_main.addWidget(self.table)

    def retranslateUi(self):
        self.lbl_header.setText("Sales Reports")
        self.btn_generate.setText("Generate Report")

    # ── Card factory ────────────────────────────────────────
    def _create_card(self, object_name, title, accent_color):
        card = QFrame(self)
        card.setObjectName(object_name)
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setMinimumHeight(110)
        card.setStyleSheet(f"""
            QFrame#{object_name} {{
                background-color: #ffffff;
                border: none;
                border-left: 4px solid {accent_color};
                border-radius: 12px;
            }}
        """)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setObjectName(f"lbl_{object_name}_title")
        lbl_title.setStyleSheet(
            "font-size: 12px; color: #7f8c8d; font-weight: bold; "
            "border: none; letter-spacing: 0.5px;"
        )
        lay.addWidget(lbl_title)

        lbl_value = QLabel("—")
        lbl_value.setObjectName(f"lbl_{object_name}_value")
        lbl_value.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {accent_color}; border: none;"
        )
        lay.addWidget(lbl_value)

        return card, lbl_value

    def _update_card(self, lbl_value, text):
        lbl_value.setText(str(text))

    # ── Data ────────────────────────────────────────────────
    def refresh_data(self):
        self._generate_report()

    def _show_weekly(self):
        today = QDate.currentDate()
        start = today.addDays(-(today.dayOfWeek() - 1))
        self.date_from.setDate(start)
        self.date_to.setDate(today)
        self._generate_report()

    def _show_monthly(self):
        today = QDate.currentDate()
        start = QDate(today.year(), today.month(), 1)
        self.date_from.setDate(start)
        self.date_to.setDate(today)
        self._generate_report()

    def _show_yearly(self):
        today = QDate.currentDate()
        start = QDate(today.year(), 1, 1)
        self.date_from.setDate(start)
        self.date_to.setDate(today)
        self._generate_report()

    def _generate_report(self):
        from controllers.reports_ctrl import get_report_data

        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        # Validate date range
        if self.date_from.date() > self.date_to.date():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Date Range",
                                "'From' date must be before or equal to 'To' date.")
            return

        result = get_report_data(date_from, date_to)

        if not result:
            result = {"sales": [], "total": 0, "count": 0, "average": 0, "daily": []}

        total_sales = float(result.get("total", 0))
        num_transactions = int(result.get("count", 0))
        avg_sale = float(result.get("average", 0))
        daily = result.get("daily", [])

        self._update_card(self.lbl_total_sales_value, f"₱{total_sales:,.2f}")
        self._update_card(self.lbl_transactions_value, str(num_transactions))
        self._update_card(self.lbl_avg_sale_value, f"₱{avg_sale:,.2f}")

        # Fill table with daily breakdown
        self.table.setRowCount(len(daily))
        for r, d in enumerate(daily):
            sd = d.get("sale_day", "")
            if hasattr(sd, "strftime"):
                sd = sd.strftime("%d/%m/%Y")
            self.table.setItem(r, 0, QTableWidgetItem(str(sd)))
            self.table.setItem(r, 1, QTableWidgetItem(str(d.get("txn_count", "—"))))
            self.table.setItem(r, 2, QTableWidgetItem(f"₱{float(d.get('total', 0)):,.2f}"))

        # Build chart
        if HAS_CHARTS and self.chart_view is not None:
            self._build_chart(daily)

    def _build_chart(self, data):
        chart = QChart()
        chart.setTitle("Daily Revenue")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#ffffff"))
        chart.setTitleBrush(QColor("#2c3e50"))
        chart.setTitleFont(QFont("Inter", 12, QFont.Weight.Bold))

        if not data:
            self.chart_view.setChart(chart)
            return

        bar_set = QBarSet("Revenue")
        bar_set.setColor(QColor(self._CLR_PRIMARY))
        categories = []
        max_val = 0

        for d in data:
            revenue = float(d.get("total", 0))
            bar_set.append(revenue)
            if revenue > max_val:
                max_val = revenue
            sd = d.get("sale_day", "")
            if hasattr(sd, "strftime"):
                sd = sd.strftime("%m/%d")
            categories.append(str(sd))

        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max_val * 1.15 if max_val else 100)
        axis_y.setTitleText("₱")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #reportsPage {
                background-color: #f0f2f5;
            }
            QLabel#lbl_header {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 4px;
            }
            QDateEdit {
                border: 1px solid #d0d4d8;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #ffffff;
                color: #333333;
                font-size: 13px;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton#btn_generate {
                background-color: #3498db; color: #ffffff;
                border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_generate:hover { background-color: #2980b9; }
            QPushButton#btn_quick {
                background-color: #8e44ad; color: #ffffff;
                border: none; border-radius: 8px;
                padding: 10px 22px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_quick:hover { background-color: #7d3c98; }
            QChartView {
                background-color: #ffffff;
                border: none;
                border-radius: 12px;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #333333;
                alternate-background-color: #f8f9fa;
                border: none;
                border-radius: 10px;
                gridline-color: #f0f0f0;
                font-size: 13px;
                padding: 4px;
            }
            QTableWidget::item {
                padding: 6px 8px;
            }
            QTableWidget::item:hover {
                background-color: #eaf2fb;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: #ffffff;
                padding: 10px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
