import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QScrollArea, QFrame)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
import database
from settings_manager import settings_mgr

class DonutChartWidget(QWidget):
    """Custom donut chart widget drawn using QPainter."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}  # Format: {"Category": count}
        self.colors = [
            QColor("#4f46e5"), # Indigo
            QColor("#10b981"), # Emerald
            QColor("#f59e0b"), # Amber
            QColor("#a855f7"), # Purple
            QColor("#ef4444")  # Red
        ]
        self.setMinimumSize(200, 200)

    def setData(self, data):
        self.data = {k: v for k, v in data.items() if v > 0}
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 40
        
        # Center of drawing
        rect = QRectF((width - size) / 2, (height - size) / 2, size, size)
        
        total = sum(self.data.values())
        if total == 0:
            # Draw empty gray circle
            painter.setPen(QPen(QColor("#475569"), 2))
            painter.setBrush(QBrush(QColor("#334155")))
            painter.drawEllipse(rect)
            
            # Text inside
            painter.setPen(QColor("#94a3b8"))
            painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, "No Data")
            return

        current_angle = 90 * 16  # Start at top (12 o'clock in QPainter units: 16ths of a degree)
        
        # Draw segments
        for i, (cat, val) in enumerate(self.data.items()):
            span_angle = int((val / total) * 360 * 16)
            
            # Select color
            color = self.colors[i % len(self.colors)]
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            
            # Draw pie slice
            painter.drawPie(rect, current_angle, -span_angle)
            current_angle -= span_angle
            
        # Draw central circle to turn pie into donut
        hole_size = size * 0.6
        hole_rect = QRectF((width - hole_size) / 2, (height - hole_size) / 2, hole_size, hole_size)
        
        # Determine background color based on theme
        theme = settings_mgr.get("theme", "Dark").lower()
        bg_color = QColor("#1e293b") if theme == "dark" else QColor("#ffffff")
        text_color = QColor("#ffffff") if theme == "dark" else QColor("#0f172a")
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(hole_rect)
        
        # Write total count inside donut
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Segoe UI", 20, QFont.Bold))
        painter.drawText(hole_rect, Qt.AlignCenter, str(total))
        
        # Draw label subtext
        subtext_rect = QRectF(hole_rect.left(), hole_rect.top() + (hole_size * 0.6), hole_size, hole_size * 0.3)
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(subtext_rect, Qt.AlignCenter, "CUSTOMERS")

class KPICard(QFrame):
    """Custom dashboard KPI Card widget."""
    def __init__(self, title, value, color_hex="#4f46e5", parent=None):
        super().__init__(parent)
        self.setObjectName("KPICard")
        self.setProperty("class", "KPICard")
        
        # Apply hover visual effects in QSS
        self.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("KPICardTitle")
        self.title_label.setProperty("class", "KPICardTitle")
        
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("KPICardValue")
        self.value_label.setProperty("class", "KPICardValue")
        
        # Optional color accent bar
        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setStyleSheet(f"background-color: {color_hex}; border-radius: 1px;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(accent)
        
    def setValue(self, val):
        self.value_label.setText(str(val))

class DashboardTab(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        # Base scroll layout for dashboard content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 1. Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Dashboard Overview")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # 2. KPI Summary Grid
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        self.kpi_total = KPICard("Total Customers", "0", "#6366f1")
        self.kpi_today = KPICard("Today's Customers", "0", "#10b981")
        self.kpi_month = KPICard("This Month's Customers", "0", "#3b82f6")
        self.kpi_docs = KPICard("Total Documents", "0", "#f59e0b")
        self.kpi_creds = KPICard("Credentials", "0", "#a855f7")
        self.kpi_backup = KPICard("Backup Status", "N/A", "#64748b")
        
        kpi_layout.addWidget(self.kpi_total)
        kpi_layout.addWidget(self.kpi_today)
        kpi_layout.addWidget(self.kpi_month)
        kpi_layout.addWidget(self.kpi_docs)
        kpi_layout.addWidget(self.kpi_creds)
        kpi_layout.addWidget(self.kpi_backup)
        
        main_layout.addLayout(kpi_layout)
        
        # 3. Middle Section: Recent Customers & Category Distribution
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        
        # Recent Customers Card
        recent_card = QFrame()
        recent_card.setObjectName("KPICard")
        recent_card.setProperty("class", "KPICard")
        recent_layout = QVBoxLayout(recent_card)
        
        recent_header = QLabel("Recent Customers")
        recent_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        recent_layout.addWidget(recent_header)
        
        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["Code", "Name", "Mobile", "Category"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recent_table.doubleClicked.connect(self.on_customer_double_click)
        recent_layout.addWidget(self.recent_table)
        
        middle_layout.addWidget(recent_card, stretch=2)
        
        # Category distribution Chart Card
        chart_card = QFrame()
        chart_card.setObjectName("KPICard")
        chart_card.setProperty("class", "KPICard")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setAlignment(Qt.AlignCenter)
        
        chart_header = QLabel("Category Distribution")
        chart_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        chart_layout.addWidget(chart_header, alignment=Qt.AlignLeft)
        
        self.donut_chart = DonutChartWidget()
        chart_layout.addWidget(self.donut_chart, alignment=Qt.AlignCenter)
        
        # Legend layout
        self.legend_layout = QHBoxLayout()
        self.legend_layout.setAlignment(Qt.AlignCenter)
        chart_layout.addLayout(self.legend_layout)
        
        middle_layout.addWidget(chart_card, stretch=1)
        
        main_layout.addLayout(middle_layout)
        
        # 4. Bottom Section: Activity Log
        bottom_card = QFrame()
        bottom_card.setObjectName("KPICard")
        bottom_card.setProperty("class", "KPICard")
        bottom_layout = QVBoxLayout(bottom_card)
        
        bottom_header = QLabel("Recent Activity Logs")
        bottom_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        bottom_layout.addWidget(bottom_header)
        
        self.activity_table = QTableWidget(0, 3)
        self.activity_table.setHorizontalHeaderLabels(["Timestamp", "Action", "Details"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        bottom_layout.addWidget(self.activity_table)
        
        main_layout.addWidget(bottom_card)
        
        # Main widget layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)
        
        # Initial Load
        self.refresh_stats()

    def refresh_stats(self):
        # Fetch stats from db
        try:
            stats = database.get_dashboard_stats()
            self.kpi_total.setValue(stats.get('total_customers', 0))
            self.kpi_today.setValue(stats.get('today_customers', 0))
            self.kpi_month.setValue(stats.get('month_customers', 0))
            self.kpi_docs.setValue(stats.get('total_documents', 0))
            self.kpi_creds.setValue(stats.get('total_credentials', 0))
            self.kpi_backup.setValue(stats.get('backup_status', 'N/A'))
        except Exception as e:
            print(f"Error fetching stats: {e}")
            
        # Refresh Recent Customers Table
        try:
            recent = database.get_recent_customers(8)
            self.recent_table.setRowCount(len(recent))
            for i, r in enumerate(recent):
                # We store the customer dict/ID in the row for selection jumps
                self.recent_table.setItem(i, 0, QTableWidgetItem(r.get('customer_code', '')))
                self.recent_table.setItem(i, 1, QTableWidgetItem(r.get('name', '')))
                self.recent_table.setItem(i, 2, QTableWidgetItem(r.get('mobile1', '')))
                self.recent_table.setItem(i, 3, QTableWidgetItem(r.get('category', '')))
                # Link row items with customer data
                for col in range(4):
                    self.recent_table.item(i, col).setData(Qt.UserRole, r.get('id'))
        except Exception as e:
            print(f"Error listing recent customers: {e}")
            
        # Refresh Donut Chart (Category Distribution)
        try:
            cat_data = database.get_category_report_data()
            chart_dict = {}
            for r in cat_data:
                cat_name = r.get('category') or "Uncategorized"
                chart_dict[cat_name] = r.get('count', 0)
                
            self.donut_chart.setData(chart_dict)
            self.build_chart_legend(chart_dict)
        except Exception as e:
            print(f"Error plotting category donut: {e}")
            
        # Refresh Recent Activity Logs Table
        try:
            logs = database.get_recent_activities(10)
            self.activity_table.setRowCount(len(logs))
            for i, l in enumerate(logs):
                self.activity_table.setItem(i, 0, QTableWidgetItem(l.get('timestamp', '')))
                self.activity_table.setItem(i, 1, QTableWidgetItem(l.get('action', '')))
                self.activity_table.setItem(i, 2, QTableWidgetItem(l.get('details', '')))
        except Exception as e:
            print(f"Error listing activity logs: {e}")

    def build_chart_legend(self, data):
        # Clear existing legends
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Create legend items
        for i, (cat, val) in enumerate(data.items()):
            color = self.donut_chart.colors[i % len(self.donut_chart.colors)].name()
            
            legend_item = QWidget()
            h_layout = QHBoxLayout(legend_item)
            h_layout.setContentsMargins(5, 5, 5, 5)
            h_layout.setSpacing(5)
            
            indicator = QFrame()
            indicator.setFixedSize(10, 10)
            indicator.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
            
            label = QLabel(f"{cat}: {val}")
            label.setFont(QFont("Segoe UI", 9))
            
            h_layout.addWidget(indicator)
            h_layout.addWidget(label)
            
            self.legend_layout.addWidget(legend_item)

    def on_customer_double_click(self, model_index):
        row = model_index.row()
        item = self.recent_table.item(row, 0)
        if item and self.main_window:
            cust_id = item.data(Qt.UserRole)
            if cust_id:
                # Tell main window to navigate to Customer Management tab and focus this customer
                self.main_window.navigate_to_customer(cust_id)
