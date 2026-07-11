from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import database

class SearchTab(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. Header
        title_label = QLabel("Advanced Customer Search")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # 2. Search Filters Panel
        filter_card = QFrame()
        filter_card.setObjectName("KPICard")
        filter_card.setProperty("class", "KPICard")
        
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setSpacing(12)
        
        grid_row1 = QHBoxLayout()
        grid_row1.setSpacing(15)
        
        # Search by Name
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Customer Name:"))
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("Search name...")
        self.search_name.textChanged.connect(self.trigger_search)
        v1.addWidget(self.search_name)
        grid_row1.addLayout(v1)
        
        # Search by Mobile
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Mobile Number:"))
        self.search_mobile = QLineEdit()
        self.search_mobile.setPlaceholderText("Search mobile...")
        self.search_mobile.textChanged.connect(self.trigger_search)
        v2.addWidget(self.search_mobile)
        grid_row1.addLayout(v2)
        
        # Search by Address
        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Address / Location:"))
        self.search_address = QLineEdit()
        self.search_address.setPlaceholderText("Search address...")
        self.search_address.textChanged.connect(self.trigger_search)
        v3.addWidget(self.search_address)
        grid_row1.addLayout(v3)
        
        filter_layout.addLayout(grid_row1)
        
        grid_row2 = QHBoxLayout()
        grid_row2.setSpacing(15)
        
        # Search by Username
        v4 = QVBoxLayout()
        v4.addWidget(QLabel("Credential Username:"))
        self.search_username = QLineEdit()
        self.search_username.setPlaceholderText("Search username...")
        self.search_username.textChanged.connect(self.trigger_search)
        v4.addWidget(self.search_username)
        grid_row2.addLayout(v4)
        
        # Search by Category
        v5 = QVBoxLayout()
        v5.addWidget(QLabel("Customer Category:"))
        self.search_category = QComboBox()
        self.search_category.addItems(["All Categories", "Regular", "VIP", "Prospect", "Inactive"])
        self.search_category.currentIndexChanged.connect(self.trigger_search)
        v5.addWidget(self.search_category)
        grid_row2.addLayout(v5)
        
        # Search by Document name
        v6 = QVBoxLayout()
        v6.addWidget(QLabel("Document File Name:"))
        self.search_doc = QLineEdit()
        self.search_doc.setPlaceholderText("Search file name...")
        self.search_doc.textChanged.connect(self.trigger_search)
        v6.addWidget(self.search_doc)
        grid_row2.addLayout(v6)
        
        filter_layout.addLayout(grid_row2)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.search_btn = QPushButton("Search Now")
        self.search_btn.setProperty("class", "PrimaryButton")
        self.search_btn.clicked.connect(self.trigger_search)
        
        self.reset_btn = QPushButton("Clear Fields")
        self.reset_btn.setProperty("class", "SecondaryButton")
        self.reset_btn.clicked.connect(self.clear_filters)
        
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.search_btn)
        filter_layout.addLayout(btn_layout)
        
        layout.addWidget(filter_card)
        
        # 3. Results Panel
        results_header = QLabel("Search Results")
        results_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(results_header)
        
        self.results_table = QTableWidget(0, 6)
        self.results_table.setHorizontalHeaderLabels(["Code", "Customer Name", "Primary Mobile", "Category", "Address", "Created Date"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.doubleClicked.connect(self.on_row_double_clicked)
        
        layout.addWidget(self.results_table)
        
        # Initial empty search load
        self.trigger_search()

    def get_filters(self):
        cat = self.search_category.currentText()
        return {
            "name": self.search_name.text().strip(),
            "mobile": self.search_mobile.text().strip(),
            "address": self.search_address.text().strip(),
            "username": self.search_username.text().strip(),
            "category": None if cat == "All Categories" else cat,
            "document_name": self.search_doc.text().strip()
        }

    def trigger_search(self):
        filters = self.get_filters()
        try:
            results = database.search_customers(filters)
            self.results_table.setRowCount(len(results))
            for i, r in enumerate(results):
                # Code
                code_item = QTableWidgetItem(r.get('customer_code', ''))
                code_item.setData(Qt.UserRole, r.get('id'))  # store ID for navigation
                self.results_table.setItem(i, 0, code_item)
                
                self.results_table.setItem(i, 1, QTableWidgetItem(r.get('name', '')))
                self.results_table.setItem(i, 2, QTableWidgetItem(r.get('mobile1', '')))
                self.results_table.setItem(i, 3, QTableWidgetItem(r.get('category', '')))
                self.results_table.setItem(i, 4, QTableWidgetItem(r.get('address') or ''))
                self.results_table.setItem(i, 5, QTableWidgetItem(r.get('created_at', '')))
        except Exception as e:
            print(f"Search failed: {e}")

    def clear_filters(self):
        # Temporarily block signals to prevent multiple queries
        self.search_category.blockSignals(True)
        
        self.search_name.clear()
        self.search_mobile.clear()
        self.search_address.clear()
        self.search_username.clear()
        self.search_category.setCurrentIndex(0)
        self.search_doc.clear()
        
        self.search_category.blockSignals(False)
        
        self.trigger_search()

    def on_row_double_clicked(self, model_index):
        row = model_index.row()
        item = self.results_table.item(row, 0)
        if item and self.main_window:
            cust_id = item.data(Qt.UserRole)
            if cust_id:
                self.main_window.navigate_to_customer(cust_id)
