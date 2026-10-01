"""
views/dashboard_view.py
===============================================================
Dashboard page with statistics cards and Qt Charts.
Shows: Total Sales Today, Total Comics, Borrowed Count, Low Stock Count
Charts: Daily Sales, Top Selling Comics, Stock Distribution, Borrow Status

Widget hierarchy:
  QWidget (DashboardView)
    └─ verticalLayout_outer
        └─ scrollArea
            └─ scrollAreaContents
                └─ verticalLayout_main
                    ├─ lbl_header
                    ├─ horizontalLayout_cards
                    │   ├─ card_sales  ├─ card_comics
                    │   ├─ card_borrowed  └─ card_low_stock
                    ├─ horizontalLayout_charts1
                    │   ├─ chartView_daily_sales
                    │   └─ chartView_top_selling
                    ├─ horizontalLayout_charts2
                    │   ├─ chartView_stock_dist
                    │   └─ chartView_borrow
                    ├─ lbl_recent_header
                    └─ table_recent
===============================================================
"""

import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, QBoxLayout
)
from PyQt6.QtCore import Qt, QLocale, QEvent
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet,
    QPieSeries, QBarCategoryAxis, QValueAxis, QHorizontalBarSeries
)

from controllers.dashboard_ctrl import get_dashboard_data


# ── Shared colour palette ───────────────────────────────────
_CLR_PRIMARY   = "#3498db"
_CLR_SUCCESS   = "#27ae60"
_CLR_WARNING   = "#e67e22"
_CLR_DANGER    = "#e74c3c"
_CLR_PURPLE    = "#8e44ad"
_CLR_TEAL      = "#1abc9c"


class DashboardView(QWidget):
    """Dashboard page with stats and charts."""

    def __init__(self):
        super().__init__()
        self.setObjectName("dashboardPage")
        self.setupUi()
        self.retranslateUi()
        self._apply_styles()

    # =============================================================
    #  setupUi
    # =============================================================
    def setupUi(self):
        """Build the dashboard layout."""
        self.verticalLayout_outer = QVBoxLayout(self)
        self.verticalLayout_outer.setObjectName("verticalLayout_outer")
        self.verticalLayout_outer.setContentsMargins(0, 0, 0, 0)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)

        self.scrollAreaContents = QWidget()
        self.scrollAreaContents.setObjectName("scrollAreaContents")

        self.verticalLayout_main = QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.verticalLayout_main.setSpacing(28)
        self.verticalLayout_main.setContentsMargins(32, 32, 32, 32)

        # ── Page Header ────────────────────────────────────
        self.lbl_header = QLabel(self.scrollAreaContents)
        self.lbl_header.setObjectName("lbl_header")
        self.verticalLayout_main.addWidget(self.lbl_header)

        # ── Statistics Cards ────────────────────────────────
        self.horizontalLayout_cards = QHBoxLayout()
        self.horizontalLayout_cards.setObjectName("horizontalLayout_cards")
        self.horizontalLayout_cards.setSpacing(20)

        self.card_sales     = self._create_stat_card("cardSales",    "lbl_sales_title",    "lbl_sales_value",    _CLR_PRIMARY)
        self.card_comics    = self._create_stat_card("cardComics",   "lbl_comics_title",   "lbl_comics_value",   _CLR_SUCCESS)
        self.card_borrowed  = self._create_stat_card("cardBorrowed", "lbl_borrowed_title", "lbl_borrowed_value", _CLR_WARNING)
        self.card_low_stock = self._create_stat_card("cardLowStock", "lbl_lowstock_title", "lbl_lowstock_value", _CLR_DANGER)

        self.horizontalLayout_cards.addWidget(self.card_sales)
        self.horizontalLayout_cards.addWidget(self.card_comics)
        self.horizontalLayout_cards.addWidget(self.card_borrowed)
        self.horizontalLayout_cards.addWidget(self.card_low_stock)
        self.verticalLayout_main.addLayout(self.horizontalLayout_cards)

        # ── Highlights Row ─────────────────────────────────
        self.horizontalLayout_highlights = QHBoxLayout()
        self.horizontalLayout_highlights.setObjectName("horizontalLayout_highlights")
        self.horizontalLayout_highlights.setSpacing(20)

        self.chartView_most_borrowed = QChartView(self.scrollAreaContents)
        self.chartView_most_borrowed.setObjectName("chartView_most_borrowed")
        self.chartView_most_borrowed.setMinimumHeight(180)

        self.chartView_most_sold = QChartView(self.scrollAreaContents)
        self.chartView_most_sold.setObjectName("chartView_most_sold")
        self.chartView_most_sold.setMinimumHeight(180)

        self.horizontalLayout_highlights.addWidget(self.chartView_most_borrowed)
        self.horizontalLayout_highlights.addWidget(self.chartView_most_sold)
        self.verticalLayout_main.addLayout(self.horizontalLayout_highlights)

        # ── Charts Row 1 ────────────────────────────────────
        self.horizontalLayout_charts1 = QHBoxLayout()
        self.horizontalLayout_charts1.setObjectName("horizontalLayout_charts1")
        self.horizontalLayout_charts1.setSpacing(20)

        self.chartView_daily_sales = QChartView(self.scrollAreaContents)
        self.chartView_daily_sales.setObjectName("chartView_daily_sales")
        self.chartView_daily_sales.setMinimumHeight(300)
        self.horizontalLayout_charts1.addWidget(self.chartView_daily_sales)

        self.chartView_top_selling = QChartView(self.scrollAreaContents)
        self.chartView_top_selling.setObjectName("chartView_top_selling")
        self.chartView_top_selling.setMinimumHeight(300)
        self.horizontalLayout_charts1.addWidget(self.chartView_top_selling)

        self.verticalLayout_main.addLayout(self.horizontalLayout_charts1)

        # ── Charts Row 2 ────────────────────────────────────
        self.horizontalLayout_charts2 = QHBoxLayout()
        self.horizontalLayout_charts2.setObjectName("horizontalLayout_charts2")
        self.horizontalLayout_charts2.setSpacing(20)

        self.chartView_stock_dist = QChartView(self.scrollAreaContents)
        self.chartView_stock_dist.setObjectName("chartView_stock_dist")
        self.chartView_stock_dist.setMinimumHeight(300)
        self.horizontalLayout_charts2.addWidget(self.chartView_stock_dist)

        self.chartView_borrow = QChartView(self.scrollAreaContents)
        self.chartView_borrow.setObjectName("chartView_borrow")
        self.chartView_borrow.setMinimumHeight(300)
        self.horizontalLayout_charts2.addWidget(self.chartView_borrow)

        self.verticalLayout_main.addLayout(self.horizontalLayout_charts2)

        # ── Recent Transactions ─────────────────────────────
        self.lbl_recent_header = QLabel(self.scrollAreaContents)
        self.lbl_recent_header.setObjectName("lbl_recent_header")
        self.verticalLayout_main.addWidget(self.lbl_recent_header)

        self.table_recent = QTableWidget(self.scrollAreaContents)
        self.table_recent.setObjectName("table_recent")
        self.table_recent.setColumnCount(4)
        self.table_recent.setHorizontalHeaderLabels(["Sale ID", "Cashier", "Total", "Date"])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_recent.setColumnHidden(0, True)
        self.table_recent.verticalHeader().setVisible(False)
        self.table_recent.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_recent.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_recent.setAlternatingRowColors(True)
        self.table_recent.setMinimumHeight(180)
        self.table_recent.viewport().installEventFilter(self)
        self.verticalLayout_main.addWidget(self.table_recent)

        self.scrollArea.setWidget(self.scrollAreaContents)
        self.verticalLayout_outer.addWidget(self.scrollArea)

    # =============================================================
    #  retranslateUi
    # =============================================================
    def retranslateUi(self):
        self.lbl_header.setText("Dashboard")
        self.lbl_recent_header.setText("Recent Transactions")
        # Card titles
        self.card_sales.findChild(QLabel, "lbl_sales_title").setText("Total Sales Today")
        self.card_comics.findChild(QLabel, "lbl_comics_title").setText("Total Products")
        self.card_borrowed.findChild(QLabel, "lbl_borrowed_title").setText("Borrowed Products")
        self.card_low_stock.findChild(QLabel, "lbl_lowstock_title").setText("Low Stock Products")

    # ── Helper: create a stat card ──────────────────────────
    def _create_stat_card(self, frame_name, title_name, value_name, accent):
        """Create a styled statistics card QFrame."""
        card = QFrame(self.scrollAreaContents)
        card.setObjectName(frame_name)
        card.setMinimumHeight(110)
        card.setStyleSheet(f"""
            QFrame#{frame_name} {{
                background-color: #ffffff;
                border-radius: 12px;
                border: none;
                border-left: 4px solid {accent};
            }}
        """)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        title_lbl = QLabel(card)
        title_lbl.setObjectName(title_name)
        title_lbl.setStyleSheet(
            "color: #7f8c8d; font-size: 12px; font-weight: bold; "
            "border: none; letter-spacing: 0.5px;"
        )

        value_lbl = QLabel("—", card)
        value_lbl.setObjectName(value_name)
        value_lbl.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        value_lbl.setStyleSheet(f"color: {accent}; border: none;")

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        return card

    def _create_highlight_card(self, frame_name, title_name, value_name, accent):
        """Create compact highlight cards for top borrowed/sold titles."""
        card = QFrame(self.scrollAreaContents)
        card.setObjectName(frame_name)
        card.setMinimumHeight(94)
        card.setStyleSheet(f"""
            QFrame#{frame_name} {{
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e6ebf2;
                border-left: 4px solid {accent};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(16)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        title_lbl = QLabel(card)
        title_lbl.setObjectName(title_name)
        title_lbl.setStyleSheet(
            "color: #7f8c8d; font-size: 11px; font-weight: bold; border: none; letter-spacing: 0.4px;"
        )

        value_lbl = QLabel("—", card)
        value_lbl.setObjectName(value_name)
        value_lbl.setWordWrap(True)
        value_lbl.setStyleSheet("color: #1f2d3d; font-size: 14px; font-weight: bold; border: none;")

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        return card

    # ── Refresh dashboard data ──────────────────────────────
    def refresh_data(self):
        """Fetch fresh data from the database and update all widgets."""
        data = get_dashboard_data()

        # Update stat cards
        self._set_card_value("lbl_sales_value",    f"₱{data['today_sales']:,.2f}")
        self._set_card_value("lbl_comics_value",   str(data['total_comics']))
        self._set_card_value("lbl_borrowed_value", str(data['borrowed_count']))
        self._set_card_value("lbl_lowstock_value", str(data['low_stock_count']))

        self._build_most_borrowed_chart(data.get("most_borrowed") or {})
        self._build_most_sold_chart(data.get("most_sold") or {})

        # Build charts
        self._build_daily_sales_chart(data['daily_sales'])
        self._build_top_selling_chart(data['top_selling'])
        self._build_stock_distribution_chart(data['stock_distribution'])
        self._build_borrow_chart(data['borrow_vs_returned'])

        # Recent transactions
        self._fill_recent_table(data['recent_transactions'])

    def _set_card_value(self, obj_name, text):
        lbl = self.findChild(QLabel, obj_name)
        if lbl:
            lbl.setText(text)

    # ── Chart helpers ───────────────────────────────────────
    def _make_chart(self, title):
        """Create a consistently styled QChart."""
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#ffffff"))
        chart.setTitleBrush(QColor("#2c3e50"))
        chart.setTitleFont(QFont("Inter", 12, QFont.Weight.Bold))
        chart.setLocale(QLocale(QLocale.Language.English, QLocale.Country.Philippines))
        from PyQt6.QtCore import QMargins
        chart.setMargins(QMargins(12, 8, 12, 8))
        return chart

    # ── Chart builders ──────────────────────────────────────
    def _build_daily_sales_chart(self, daily_sales):
        chart = self._make_chart("Daily Sales (Last 7 Days)")

        if not daily_sales:
            chart.legend().setVisible(False)
            self.chartView_daily_sales.setChart(chart)
            return

        bar_set = QBarSet("Sales")
        bar_set.setColor(QColor(_CLR_PRIMARY))
        categories = []

        for row in daily_sales:
            day = row["sale_day"]
            categories.append(day.strftime("%m/%d") if hasattr(day, "strftime") else str(day))
            bar_set.append(float(row["total"]))

        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        ax = QBarCategoryAxis()
        ax.append(categories)
        chart.addAxis(ax, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(ax)

        ay = QValueAxis()
        max_total = max(float(row["total"]) for row in daily_sales)
        nice_step = self._compute_nice_step(max_total, target_ticks=6)
        nice_max = math.ceil(max_total / nice_step) * nice_step if max_total > 0 else nice_step
        ay.setRange(0, max(nice_step, nice_max))
        ay.setLabelFormat("PHP %.0f")
        ay.setLabelsFont(QFont("Segoe UI", 9))
        ay.setTickCount(int(max(3, min(8, (max(nice_step, nice_max) / nice_step) + 1))))
        chart.addAxis(ay, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(ay)

        chart.legend().setVisible(False)
        self.chartView_daily_sales.setChart(chart)

    def _compute_nice_step(self, max_value, target_ticks=6):
        """Return a rounded axis step (1/2/5 x 10^n) for cleaner Y-axis labels."""
        if max_value <= 0:
            return 1.0

        rough = max_value / max(2, target_ticks - 1)
        exp = math.floor(math.log10(rough))
        fraction = rough / (10 ** exp)

        if fraction <= 1:
            nice_fraction = 1
        elif fraction <= 2:
            nice_fraction = 2
        elif fraction <= 5:
            nice_fraction = 5
        else:
            nice_fraction = 10

        return nice_fraction * (10 ** exp)

    def _build_top_selling_chart(self, top_selling):
        chart = self._make_chart("Top Selling Products")

        if not top_selling:
            chart.legend().setVisible(False)
            self.chartView_top_selling.setChart(chart)
            return

        bar_set = QBarSet("Units Sold")
        bar_set.setColor(QColor(_CLR_SUCCESS))
        categories = []

        for row in top_selling:
            title = row["title"][:18] + ".." if len(row["title"]) > 18 else row["title"]
            categories.append(title)
            bar_set.append(int(row["total_sold"]))

        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        ax = QBarCategoryAxis()
        ax.append(categories)
        chart.addAxis(ax, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(ax)

        ay = QValueAxis()
        max_units = max(int(row["total_sold"]) for row in top_selling)
        ay.setRange(0, max(1, max_units))
        ay.setLabelFormat("%.0f")
        ay.setTickCount(min(max(2, max_units + 1), 6))
        chart.addAxis(ay, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(ay)

        chart.legend().setVisible(False)
        self.chartView_top_selling.setChart(chart)

    def _build_stock_distribution_chart(self, stock_data):
        chart = self._make_chart("Stock Distribution by Category")

        if not stock_data:
            chart.legend().setVisible(False)
            self.chartView_stock_dist.setChart(chart)
            return

        series = QPieSeries()
        palette = [_CLR_PRIMARY, _CLR_SUCCESS, _CLR_WARNING, _CLR_DANGER, _CLR_PURPLE, _CLR_TEAL]

        for i, row in enumerate(stock_data):
            stock_val = int(row["total_stock"])
            s = series.append(row["category"], stock_val)
            s.setColor(QColor(palette[i % len(palette)]))
            s.setLabelVisible(True)
            s.setLabel(f"{row['category']} ({stock_val})")

        chart.addSeries(series)
        chart.legend().setVisible(False)
        self.chartView_stock_dist.setChart(chart)

    def _build_borrow_chart(self, borrow_data):
        chart = self._make_chart("Borrowed vs Returned")

        borrowed = borrow_data.get("borrowed", 0) or 0
        returned = borrow_data.get("returned", 0) or 0

        if borrowed == 0 and returned == 0:
            chart.legend().setVisible(False)
            self.chartView_borrow.setChart(chart)
            return

        series = QPieSeries()
        s1 = series.append("Borrowed", borrowed)
        s1.setColor(QColor(_CLR_WARNING))
        s1.setLabelVisible(True)
        s1.setLabel(f"Borrowed ({borrowed})")

        s2 = series.append("Returned", returned)
        s2.setColor(QColor(_CLR_SUCCESS))
        s2.setLabelVisible(True)
        s2.setLabel(f"Returned ({returned})")

        chart.addSeries(series)
        chart.legend().setVisible(False)
        self.chartView_borrow.setChart(chart)

    def _build_most_borrowed_chart(self, most_borrowed):
        chart = self._make_chart("Most Borrowed Book")

        count = int(most_borrowed.get("borrow_count") or 0)
        title = (most_borrowed.get("title") or "No records")
        if count <= 0:
            chart.legend().setVisible(False)
            self.chartView_most_borrowed.setChart(chart)
            return

        title = title[:34] + ".." if len(title) > 34 else title
        bar_set = QBarSet("Borrows")
        bar_set.setColor(QColor(_CLR_WARNING))
        bar_set.append(count)

        series = QHorizontalBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        ax = QBarCategoryAxis()
        ax.append([title])
        chart.addAxis(ax, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(ax)

        ay = QValueAxis()
        ay.setRange(0, max(1, count))
        ay.setLabelFormat("%.0f")
        ay.setTickCount(min(max(2, count + 1), 6))
        chart.addAxis(ay, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(ay)

        chart.legend().setVisible(False)
        self.chartView_most_borrowed.setChart(chart)

    def _build_most_sold_chart(self, most_sold):
        chart = self._make_chart("Most Sold Book")

        count = int(most_sold.get("total_sold") or 0)
        title = (most_sold.get("title") or "No records")
        if count <= 0:
            chart.legend().setVisible(False)
            self.chartView_most_sold.setChart(chart)
            return

        title = title[:34] + ".." if len(title) > 34 else title
        bar_set = QBarSet("Units")
        bar_set.setColor(QColor(_CLR_PRIMARY))
        bar_set.append(count)

        series = QHorizontalBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        ax = QBarCategoryAxis()
        ax.append([title])
        chart.addAxis(ax, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(ax)

        ay = QValueAxis()
        ay.setRange(0, max(1, count))
        ay.setLabelFormat("%.0f")
        ay.setTickCount(min(max(2, count + 1), 6))
        chart.addAxis(ay, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(ay)

        chart.legend().setVisible(False)
        self.chartView_most_sold.setChart(chart)

    # ── Fill recent transactions table ──────────────────────
    def _fill_recent_table(self, transactions):
        self.table_recent.setRowCount(len(transactions))

        for r, txn in enumerate(transactions):
            self.table_recent.setItem(r, 0, QTableWidgetItem(str(txn["sale_id"])))
            self.table_recent.setItem(r, 1, QTableWidgetItem(txn["cashier"]))
            self.table_recent.setItem(r, 2, QTableWidgetItem(f"₱{txn['total_amount']:,.2f}"))

            if hasattr(txn["sale_date"], "strftime"):
                d = txn["sale_date"].strftime("%d/%m/%Y %I:%M %p")
            else:
                d = str(txn["sale_date"])
            self.table_recent.setItem(r, 3, QTableWidgetItem(d))

    # ── Styles ──────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            #dashboardPage {
                background-color: #f0f2f5;
            }
            #scrollArea, #scrollAreaContents {
                background-color: transparent;
                border: none;
            }
            QLabel#lbl_header {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 4px;
            }
            QLabel#lbl_recent_header {
                font-size: 15px;
                font-weight: bold;
                color: #2c3e50;
                padding-top: 4px;
            }
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

    def resizeEvent(self, event):
        super().resizeEvent(event)

        content_w = self.scrollArea.viewport().width()
        compact = content_w < 1300

        if content_w >= 1800:
            margin = 42
            spacing = 32
            chart_h = 360
        elif content_w >= 1400:
            margin = 32
            spacing = 24
            chart_h = 320
        elif content_w >= 1100:
            margin = 22
            spacing = 18
            chart_h = 280
        else:
            margin = 14
            spacing = 14
            chart_h = 240

        self.verticalLayout_main.setContentsMargins(margin, margin, margin, margin)
        self.verticalLayout_main.setSpacing(spacing)
        self.horizontalLayout_cards.setSpacing(spacing)
        self.horizontalLayout_highlights.setSpacing(spacing)
        self.horizontalLayout_charts1.setSpacing(spacing)
        self.horizontalLayout_charts2.setSpacing(spacing)

        self.horizontalLayout_cards.setDirection(
            QBoxLayout.Direction.TopToBottom if compact else QBoxLayout.Direction.LeftToRight
        )
        self.horizontalLayout_highlights.setDirection(
            QBoxLayout.Direction.TopToBottom if compact else QBoxLayout.Direction.LeftToRight
        )
        self.horizontalLayout_charts1.setDirection(
            QBoxLayout.Direction.TopToBottom if compact else QBoxLayout.Direction.LeftToRight
        )
        self.horizontalLayout_charts2.setDirection(
            QBoxLayout.Direction.TopToBottom if compact else QBoxLayout.Direction.LeftToRight
        )

        self.chartView_daily_sales.setMinimumHeight(chart_h)
        self.chartView_top_selling.setMinimumHeight(chart_h)
        self.chartView_stock_dist.setMinimumHeight(chart_h)
        self.chartView_borrow.setMinimumHeight(chart_h)
        highlight_h = max(170, chart_h - 110)
        self.chartView_most_borrowed.setMinimumHeight(highlight_h)
        self.chartView_most_sold.setMinimumHeight(highlight_h)

        if content_w >= 1800:
            header_size = 22
            recent_size = 16
            card_title_size = 13
            card_value_size = 30
        elif content_w >= 1400:
            header_size = 20
            recent_size = 15
            card_title_size = 12
            card_value_size = 27
        elif content_w >= 1100:
            header_size = 19
            recent_size = 14
            card_title_size = 11
            card_value_size = 24
        else:
            header_size = 17
            recent_size = 13
            card_title_size = 10
            card_value_size = 21

        self.lbl_header.setFont(QFont("Inter", header_size, QFont.Weight.Bold))
        self.lbl_recent_header.setFont(QFont("Inter", recent_size, QFont.Weight.Bold))

        for name in ("lbl_sales_title", "lbl_comics_title", "lbl_borrowed_title", "lbl_lowstock_title"):
            label = self.findChild(QLabel, name)
            if label:
                label.setFont(QFont("Inter", card_title_size, QFont.Weight.Bold))

        for name in ("lbl_most_borrowed_title", "lbl_most_sold_title"):
            label = self.findChild(QLabel, name)
            if label:
                label.setFont(QFont("Inter", max(9, card_title_size - 1), QFont.Weight.Bold))

        for name in ("lbl_sales_value", "lbl_comics_value", "lbl_borrowed_value", "lbl_lowstock_value"):
            label = self.findChild(QLabel, name)
            if label:
                label.setFont(QFont("Inter", card_value_size, QFont.Weight.Bold))

        highlight_value_size = max(11, card_value_size - 10)
        for name in ("lbl_most_borrowed_value", "lbl_most_sold_value"):
            label = self.findChild(QLabel, name)
            if label:
                label.setFont(QFont("Inter", highlight_value_size, QFont.Weight.Bold))

    def eventFilter(self, watched, event):
        if watched is self.table_recent.viewport() and event.type() == QEvent.Type.Wheel:
            vbar = self.table_recent.verticalScrollBar()
            if vbar.maximum() > vbar.minimum():
                delta_y = event.angleDelta().y()
                if delta_y != 0:
                    steps = delta_y / 120.0
                    new_value = int(round(vbar.value() - (steps * max(1, vbar.singleStep()))))
                    new_value = max(vbar.minimum(), min(vbar.maximum(), new_value))
                    vbar.setValue(new_value)
            event.accept()
            return True
        return super().eventFilter(watched, event)
