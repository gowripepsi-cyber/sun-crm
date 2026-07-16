import os
import shutil
import hashlib
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QTextEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QSplitter, QListWidget, QListWidgetItem, QTabWidget, 
                             QFileDialog, QDialog, QFormLayout, QMessageBox, 
                             QInputDialog, QFrame)
from PySide6.QtCore import Qt, QUrl, QRectF
from PySide6.QtGui import QFont, QIcon, QDesktopServices, QPainter, QColor, QPen, QBrush
import database
from settings_manager import settings_mgr
from google_drive import gdrive_mgr

class QRCodeWidget(QWidget):
    """Custom widget that draws a deterministic QR code mock based on customer code."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.code_str = ""
        self.setMinimumSize(120, 120)
        self.setMaximumSize(120, 120)

    def setCode(self, code_str):
        self.code_str = code_str
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background white square with light border
        width = self.width()
        height = self.height()
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#cbd5e1"), 2))
        painter.drawRect(0, 0, width, height)
        
        if not self.code_str:
            return
            
        # Seed md5 for deterministic blocks
        h = hashlib.md5(self.code_str.encode('utf-8')).hexdigest()
        grid_size = 12
        cell_size = (width - 16) / grid_size
        
        # Brush for blocks
        painter.setBrush(QBrush(QColor("#000000")))
        painter.setPen(Qt.NoPen)
        
        # QR Finder Patterns (Corners)
        # Top-Left finder
        painter.drawRect(8, 8, cell_size * 3, cell_size * 3)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRect(8 + cell_size, 8 + cell_size, cell_size, cell_size)
        
        # Top-Right finder
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawRect(width - 8 - cell_size * 3, 8, cell_size * 3, cell_size * 3)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRect(width - 8 - cell_size * 2, 8 + cell_size, cell_size, cell_size)
        
        # Bottom-Left finder
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawRect(8, height - 8 - cell_size * 3, cell_size * 3, cell_size * 3)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRect(8 + cell_size, height - 8 - cell_size * 2, cell_size, cell_size)
        
        # Draw random-looking but deterministic grid pixels
        painter.setBrush(QBrush(QColor("#000000")))
        hash_idx = 0
        for r in range(grid_size):
            for c in range(grid_size):
                # Skip finder pattern zones
                if (r < 3 and c < 3) or (r < 3 and c >= grid_size - 3) or (r >= grid_size - 3 and c < 3):
                    continue
                    
                char = h[hash_idx % len(h)]
                hash_idx += 1
                
                # Turn on pixels if character matches condition
                if char in "02458acf":
                    x = 8 + c * cell_size
                    y = 8 + r * cell_size
                    painter.drawRect(QRectF(x, y, cell_size, cell_size))


class CredentialDialog(QDialog):
    """Popup to add or edit a credential."""
    def __init__(self, parent=None, service="", username="", password="", remarks=""):
        super().__init__(parent)
        self.setWindowTitle("Credential Details")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.service_input = QLineEdit(service)
        self.username_input = QLineEdit(username)
        self.password_input = QLineEdit(password)
        self.remarks_input = QTextEdit(remarks)
        self.remarks_input.setMaximumHeight(80)
        
        form_layout.addRow("Service Name:", self.service_input)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Remarks:", self.remarks_input)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", "SecondaryButton")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "service_name": self.service_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
            "remarks": self.remarks_input.toPlainText().strip()
        }

class CustomerTab(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_customer_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter to separate list and workspaces
        splitter = QSplitter(Qt.Horizontal)
        
        # 1. Left Section: Customer List Manager
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        search_layout = QHBoxLayout()
        self.quick_search = QLineEdit()
        self.quick_search.setPlaceholderText("Filter customers...")
        self.quick_search.textChanged.connect(self.filter_customer_list)
        search_layout.addWidget(self.quick_search)
        
        self.new_cust_btn = QPushButton("+ New")
        self.new_cust_btn.setProperty("class", "PrimaryButton")
        self.new_cust_btn.clicked.connect(self.create_new_customer_flow)
        search_layout.addWidget(self.new_cust_btn)
        
        left_layout.addLayout(search_layout)
        
        self.customer_list = QListWidget()
        self.customer_list.itemSelectionChanged.connect(self.on_customer_selected)
        left_layout.addWidget(self.customer_list)
        
        splitter.addWidget(left_panel)
        
        # 2. Right Section: Detail Workspace Tabs
        self.right_workspace = QWidget()
        self.right_layout = QVBoxLayout(self.right_workspace)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(10)
        
        # Header bar showing active selection
        self.header_bar = QWidget()
        self.header_bar.setStyleSheet("background-color: #1e293b; border-radius: 8px; padding: 10px;")
        header_layout = QHBoxLayout(self.header_bar)
        
        self.header_title = QLabel("Select a Customer")
        self.header_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.header_title.setStyleSheet("color: #ffffff;")
        
        self.header_category = QLabel("")
        self.header_category.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.header_category.setStyleSheet("color: #818cf8; background-color: #334155; padding: 4px 8px; border-radius: 4px;")
        self.header_category.setVisible(False)
        
        header_layout.addWidget(self.header_title)
        header_layout.addWidget(self.header_category)
        header_layout.addStretch()
        
        # Delete active customer button
        self.delete_cust_btn = QPushButton("Delete Customer")
        self.delete_cust_btn.setProperty("class", "DangerButton")
        self.delete_cust_btn.clicked.connect(self.delete_active_customer)
        self.delete_cust_btn.setVisible(False)
        header_layout.addWidget(self.delete_cust_btn)
        
        self.right_layout.addWidget(self.header_bar)
        
        # Workspace tabs
        self.tabs = QTabWidget()
        self.tabs.setEnabled(False)  # Disabled until a customer is chosen
        
        self.setup_biodata_tab()
        self.setup_credentials_tab()
        self.setup_custominfo_tab()
        self.setup_documents_tab()
        self.setup_tools_tab()
        
        self.right_layout.addWidget(self.tabs)
        
        splitter.addWidget(self.right_workspace)
        
        # Distribute proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Initial list load
        self.refresh_customer_list()

    # --- Setup Tab Layouts ---
    def setup_biodata_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.biodata_code = QLineEdit()
        self.biodata_code.setReadOnly(True)
        self.biodata_code.setPlaceholderText("Will be generated automatically")
        self.biodata_code.setStyleSheet("background-color: #334155; color: #94a3b8;")
        
        self.biodata_name = QLineEdit()
        self.biodata_mobile1 = QLineEdit()
        self.biodata_mobile2 = QLineEdit()
        
        self.biodata_address = QTextEdit()
        self.biodata_address.setMaximumHeight(80)
        
        self.biodata_notes = QTextEdit()
        self.biodata_notes.setMaximumHeight(80)
        
        # Age group combo box
        self.biodata_age = QComboBox()
        self.biodata_age.addItems(["", "Kids (0-12)", "Teens (13-19)", "Young Adult (20-29)", "Adult (30-59)", "Senior (60+)"])
        
        # Gender combo
        self.biodata_gender = QComboBox()
        self.biodata_gender.addItems(["", "Male", "Female", "Other"])
        
        # Category combo
        self.biodata_category = QComboBox()
        self.biodata_category.addItems(["Regular", "VIP", "Prospect", "Inactive"])
        
        # Tags line edit
        self.biodata_tags = QLineEdit()
        self.biodata_tags.setPlaceholderText("Comma-separated values (e.g. Lead, Software, Corporate)")
        
        # Date & Time display
        self.biodata_date = QLabel("N/A")
        self.biodata_date.setStyleSheet("color: #94a3b8;")
        
        form_layout.addRow("Customer Code:", self.biodata_code)
        form_layout.addRow("Customer Name *:", self.biodata_name)
        form_layout.addRow("Primary Mobile *:", self.biodata_mobile1)
        form_layout.addRow("Alternative Mobile:", self.biodata_mobile2)
        form_layout.addRow("Address:", self.biodata_address)
        form_layout.addRow("Age Group:", self.biodata_age)
        form_layout.addRow("Gender:", self.biodata_gender)
        form_layout.addRow("Customer Category:", self.biodata_category)
        form_layout.addRow("Tags / Labels:", self.biodata_tags)
        form_layout.addRow("Notes:", self.biodata_notes)
        form_layout.addRow("Created Date & Time:", self.biodata_date)
        
        layout.addLayout(form_layout)
        
        # Save button
        self.save_bio_btn = QPushButton("Save Customer Profile")
        self.save_bio_btn.setProperty("class", "PrimaryButton")
        self.save_bio_btn.clicked.connect(self.save_customer_profile)
        layout.addWidget(self.save_bio_btn)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Bio Data & Profile")

    def setup_credentials_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        tbl_controls = QHBoxLayout()
        self.add_cred_btn = QPushButton("+ Add Account")
        self.add_cred_btn.setProperty("class", "PrimaryButton")
        self.add_cred_btn.clicked.connect(self.on_add_credential)
        
        self.edit_cred_btn = QPushButton("Edit")
        self.edit_cred_btn.setProperty("class", "SecondaryButton")
        self.edit_cred_btn.clicked.connect(self.on_edit_credential)
        
        self.delete_cred_btn = QPushButton("Delete")
        self.delete_cred_btn.setProperty("class", "SecondaryButton")
        self.delete_cred_btn.clicked.connect(self.on_delete_credential)
        
        self.copy_pass_btn = QPushButton("Copy Password")
        self.copy_pass_btn.setProperty("class", "SecondaryButton")
        self.copy_pass_btn.clicked.connect(self.on_copy_password)
        
        self.toggle_pass_btn = QPushButton("Show/Hide Password")
        self.toggle_pass_btn.setProperty("class", "SecondaryButton")
        self.toggle_pass_btn.clicked.connect(self.on_toggle_password_visibility)
        
        tbl_controls.addWidget(self.add_cred_btn)
        tbl_controls.addWidget(self.edit_cred_btn)
        tbl_controls.addWidget(self.delete_cred_btn)
        tbl_controls.addWidget(self.copy_pass_btn)
        tbl_controls.addWidget(self.toggle_pass_btn)
        tbl_controls.addStretch()
        
        layout.addLayout(tbl_controls)
        
        # Credentials table
        self.creds_table = QTableWidget(0, 5)
        self.creds_table.setHorizontalHeaderLabels(["ID", "Website / Service Name", "Username", "Password", "Remarks"])
        self.creds_table.setColumnHidden(0, True)  # Hide ID
        self.creds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.creds_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.creds_table.setSelectionMode(QTableWidget.SingleSelection)
        self.creds_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.creds_table.doubleClicked.connect(self.on_edit_credential)
        
        layout.addWidget(self.creds_table)
        self.tabs.addTab(tab, "Saved Credentials")
        self.passwords_visible = False

    def setup_custominfo_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        controls = QHBoxLayout()
        self.add_field_btn = QPushButton("+ Add Custom Field")
        self.add_field_btn.setProperty("class", "PrimaryButton")
        self.add_field_btn.clicked.connect(self.on_add_custom_field)
        
        self.delete_field_btn = QPushButton("Remove Field")
        self.delete_field_btn.setProperty("class", "SecondaryButton")
        self.delete_field_btn.clicked.connect(self.on_delete_custom_field)
        
        controls.addWidget(self.add_field_btn)
        controls.addWidget(self.delete_field_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        self.fields_table = QTableWidget(0, 3)
        self.fields_table.setHorizontalHeaderLabels(["ID", "Title / Label", "Value"])
        self.fields_table.setColumnHidden(0, True)
        self.fields_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fields_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fields_table.setSelectionMode(QTableWidget.SingleSelection)
        self.fields_table.doubleClicked.connect(self.on_edit_custom_field)
        
        layout.addWidget(self.fields_table)
        self.tabs.addTab(tab, "Other Information")

    def setup_documents_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        controls = QHBoxLayout()
        self.upload_doc_btn = QPushButton("+ Upload Document")
        self.upload_doc_btn.setProperty("class", "PrimaryButton")
        self.upload_doc_btn.clicked.connect(self.on_upload_document)
        
        self.view_doc_btn = QPushButton("View/Open")
        self.view_doc_btn.setProperty("class", "SecondaryButton")
        self.view_doc_btn.clicked.connect(self.on_view_document)
        
        self.open_doc_folder_btn = QPushButton("Open Folder")
        self.open_doc_folder_btn.setProperty("class", "SecondaryButton")
        self.open_doc_folder_btn.clicked.connect(self.on_open_document_folder)
        
        self.edit_doc_remark_btn = QPushButton("Edit Remarks")
        self.edit_doc_remark_btn.setProperty("class", "SecondaryButton")
        self.edit_doc_remark_btn.clicked.connect(self.on_edit_document_remarks)
        
        self.delete_doc_btn = QPushButton("Delete")
        self.delete_doc_btn.setProperty("class", "SecondaryButton")
        self.delete_doc_btn.clicked.connect(self.on_delete_document)
        
        controls.addWidget(self.upload_doc_btn)
        controls.addWidget(self.view_doc_btn)
        controls.addWidget(self.open_doc_folder_btn)
        controls.addWidget(self.edit_doc_remark_btn)
        controls.addWidget(self.delete_doc_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        self.docs_table = QTableWidget(0, 5)
        self.docs_table.setHorizontalHeaderLabels(["ID", "File Name", "File Type", "Remarks", "Created Date"])
        self.docs_table.setColumnHidden(0, True)
        self.docs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.docs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.docs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.docs_table.setSelectionMode(QTableWidget.SingleSelection)
        self.docs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.docs_table.doubleClicked.connect(self.on_view_document)
        
        layout.addWidget(self.docs_table)
        self.tabs.addTab(tab, "Documents")

    # --- Loading & Filtering Customers ---
    def refresh_customer_list(self):
        self.customer_list.clear()
        customers = database.get_all_customers()
        for c in customers:
            item = QListWidgetItem(f"{c['customer_code']} - {c['name']}")
            item.setData(Qt.UserRole, c['id'])
            self.customer_list.addItem(item)
            
        if self.current_customer_id:
            # Re-select original customer if still valid
            for index in range(self.customer_list.count()):
                item = self.customer_list.item(index)
                if item.data(Qt.UserRole) == self.current_customer_id:
                    self.customer_list.setCurrentItem(item)
                    break
        else:
            self.clear_detail_workspace()

    def filter_customer_list(self, text):
        for index in range(self.customer_list.count()):
            item = self.customer_list.item(index)
            item.setHidden(text.lower() not in item.text().lower())

    def on_customer_selected(self):
        items = self.customer_list.selectedItems()
        if not items:
            self.clear_detail_workspace()
            return
            
        customer_id = items[0].data(Qt.UserRole)
        self.load_customer_data(customer_id)

    def load_customer_data(self, customer_id):
        self.current_customer_id = customer_id
        cust = database.get_customer(customer_id)
        if not cust:
            self.clear_detail_workspace()
            return
            
        # Update Header
        self.header_title.setText(f"{cust['name']} ({cust['customer_code']})")
        self.header_category.setText(cust['category'] or "Regular")
        self.header_category.setVisible(True)
        self.delete_cust_btn.setVisible(True)
        
        # Load Bio Data Forms
        self.biodata_code.setText(cust['customer_code'])
        self.biodata_name.setText(cust['name'])
        self.biodata_mobile1.setText(cust['mobile1'])
        self.biodata_mobile2.setText(cust['mobile2'] or "")
        self.biodata_address.setPlainText(cust['address'] or "")
        self.biodata_notes.setPlainText(cust['notes'] or "")
        self.biodata_tags.setText(cust['tags'] or "")
        
        # Combos
        idx_age = self.biodata_age.findText(cust['age_group'] or "", Qt.MatchContains)
        self.biodata_age.setCurrentIndex(idx_age if idx_age >= 0 else 0)
        
        idx_gen = self.biodata_gender.findText(cust['gender'] or "", Qt.MatchExactly)
        self.biodata_gender.setCurrentIndex(idx_gen if idx_gen >= 0 else 0)
        
        idx_cat = self.biodata_category.findText(cust['category'] or "Regular", Qt.MatchExactly)
        self.biodata_category.setCurrentIndex(idx_cat if idx_cat >= 0 else 0)
        
        self.biodata_date.setText(cust['created_at'])
        
        # Load Credentials Tab
        self.refresh_credentials()
        
        # Load Custom Fields
        self.refresh_custom_fields()
        
        # Load Documents
        self.refresh_documents()
        
        # Load Tools & Timeline
        self.refresh_tools_tab(cust)
        
        self.tabs.setEnabled(True)

    def select_customer_by_id(self, customer_id):
        """Used externally to force selection (e.g. from Dashboard click)."""
        self.current_customer_id = customer_id
        for idx in range(self.customer_list.count()):
            item = self.customer_list.item(idx)
            if item.data(Qt.UserRole) == customer_id:
                self.customer_list.setCurrentItem(item)
                item.setSelected(True)
                self.load_customer_data(customer_id)
                break

    def clear_detail_workspace(self):
        self.current_customer_id = None
        self.header_title.setText("Select a Customer")
        self.header_category.setVisible(False)
        self.delete_cust_btn.setVisible(False)
        
        # Clear forms
        self.biodata_code.clear()
        self.biodata_name.clear()
        self.biodata_mobile1.clear()
        self.biodata_mobile2.clear()
        self.biodata_address.clear()
        self.biodata_notes.clear()
        self.biodata_tags.clear()
        self.biodata_age.setCurrentIndex(0)
        self.biodata_gender.setCurrentIndex(0)
        self.biodata_category.setCurrentIndex(0)
        self.biodata_date.setText("N/A")
        
        # Clear Tables
        self.creds_table.setRowCount(0)
        self.fields_table.setRowCount(0)
        self.docs_table.setRowCount(0)
        self.timeline_list.clear()
        self.qr_code_widget.setCode("")
        self.wa_msg_input.setPlainText("Hello {name},\n\nThis is SUN CRM. We are reaching out regarding...")
        
        self.tabs.setEnabled(False)

    # --- Customer CRUD ---
    def create_new_customer_flow(self):
        # Quick input for new customer name & mobile
        name, ok1 = QInputDialog.getText(self, "New Customer", "Enter Customer Name *:")
        if not ok1 or not name.strip():
            return
            
        mobile, ok2 = QInputDialog.getText(self, "New Customer", "Enter Mobile Number *:")
        if not ok2 or not mobile.strip():
            return
            
        new_cust_data = {
            "name": name.strip(),
            "mobile1": mobile.strip(),
            "mobile2": "",
            "address": "",
            "notes": "",
            "age_group": "",
            "gender": "",
            "category": "Regular",
            "tags": ""
        }
        
        try:
            cust_id, code = database.add_customer(new_cust_data)
            self.current_customer_id = cust_id
            self.refresh_customer_list()
            self.select_customer_by_id(cust_id)
            QMessageBox.information(self, "Success", f"Customer {name} created with Code: {code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create customer: {e}")

    def save_customer_profile(self):
        if not self.current_customer_id:
            return
            
        name = self.biodata_name.text().strip()
        mobile = self.biodata_mobile1.text().strip()
        
        if not name or not mobile:
            QMessageBox.warning(self, "Validation Alert", "Name and Mobile fields are required.")
            return
            
        data = {
            "name": name,
            "mobile1": mobile,
            "mobile2": self.biodata_mobile2.text().strip(),
            "address": self.biodata_address.toPlainText().strip(),
            "notes": self.biodata_notes.toPlainText().strip(),
            "age_group": self.biodata_age.currentText(),
            "gender": self.biodata_gender.currentText(),
            "category": self.biodata_category.currentText(),
            "tags": self.biodata_tags.text().strip()
        }
        
        try:
            database.update_customer(self.current_customer_id, data)
            self.refresh_customer_list()
            QMessageBox.information(self, "Success", "Customer profile updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer profile: {e}")

    def delete_active_customer(self):
        if not self.current_customer_id:
            return
            
        confirm = QMessageBox.question(
            self, 
            "Delete Confirmation", 
            "Are you sure you want to permanently delete this customer?\nAll credentials, dynamic data, and uploaded documents will be deleted.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Retrieve files to delete from disk
                docs = database.get_customer_documents(self.current_customer_id)
                for d in docs:
                    full_path = d.get('file_path')
                    if full_path and os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                        except Exception as ex:
                            print(f"Error removing file {full_path}: {ex}")
                            
                database.delete_customer(self.current_customer_id)
                self.current_customer_id = None
                self.refresh_customer_list()
                QMessageBox.information(self, "Success", "Customer record deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customer: {e}")

    # --- Credentials Management ---
    def refresh_credentials(self):
        self.creds_table.setRowCount(0)
        if not self.current_customer_id:
            return
            
        creds = database.get_customer_credentials(self.current_customer_id)
        self.creds_table.setRowCount(len(creds))
        for i, c in enumerate(creds):
            self.creds_table.setItem(i, 0, QTableWidgetItem(str(c['id'])))
            self.creds_table.setItem(i, 1, QTableWidgetItem(c['service_name']))
            self.creds_table.setItem(i, 2, QTableWidgetItem(c['username'] or ''))
            
            pwd_display = c['password'] if self.passwords_visible else "••••••••"
            pwd_item = QTableWidgetItem(pwd_display)
            # Stash actual password for visibility switches
            pwd_item.setData(Qt.UserRole, c['password'])
            self.creds_table.setItem(i, 3, pwd_item)
            
            self.creds_table.setItem(i, 4, QTableWidgetItem(c['remarks'] or ''))

    def on_add_credential(self):
        if not self.current_customer_id:
            return
            
        dialog = CredentialDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['service_name']:
                QMessageBox.warning(self, "Input Error", "Service Name is required.")
                return
                
            try:
                database.add_credential(
                    self.current_customer_id,
                    data['service_name'],
                    data['username'],
                    data['password'],
                    data['remarks']
                )
                self.refresh_credentials()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save credential: {e}")

    def on_edit_credential(self):
        row = self.creds_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Alert", "Please select a credential row to edit.")
            return
            
        cred_id = int(self.creds_table.item(row, 0).text())
        service = self.creds_table.item(row, 1).text()
        username = self.creds_table.item(row, 2).text()
        password = self.creds_table.item(row, 3).data(Qt.UserRole)
        remarks = self.creds_table.item(row, 4).text()
        
        dialog = CredentialDialog(self, service, username, password, remarks)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['service_name']:
                QMessageBox.warning(self, "Input Error", "Service Name is required.")
                return
                
            try:
                database.update_credential(
                    cred_id,
                    data['service_name'],
                    data['username'],
                    data['password'],
                    data['remarks']
                )
                self.refresh_credentials()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update credential: {e}")

    def on_delete_credential(self):
        row = self.creds_table.currentRow()
        if row < 0:
            return
            
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this credential?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            cred_id = int(self.creds_table.item(row, 0).text())
            try:
                database.delete_credential(cred_id)
                self.refresh_credentials()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete credential: {e}")

    def on_copy_password(self):
        row = self.creds_table.currentRow()
        if row < 0:
            return
            
        pwd = self.creds_table.item(row, 3).data(Qt.UserRole)
        if pwd:
            clipboard = self.main_window.screen().clipboard() if self.main_window else QWidget.find(self.winId()).screen().clipboard()
            clipboard.setText(pwd)
            if self.main_window:
                self.main_window.statusBar().showMessage("Password copied to clipboard!", 2000)

    def on_toggle_password_visibility(self):
        self.passwords_visible = not self.passwords_visible
        self.refresh_credentials()

    # --- Custom Fields Management ---
    def refresh_custom_fields(self):
        self.fields_table.setRowCount(0)
        if not self.current_customer_id:
            return
            
        fields = database.get_customer_other_info(self.current_customer_id)
        self.fields_table.setRowCount(len(fields))
        self.fields_table.setWordWrap(True)
        for i, f in enumerate(fields):
            self.fields_table.setItem(i, 0, QTableWidgetItem(str(f['id'])))
            self.fields_table.setItem(i, 1, QTableWidgetItem(f['title']))
            self.fields_table.setItem(i, 2, QTableWidgetItem(f['value'] or ''))
        
        self.fields_table.resizeRowsToContents()

    def on_add_custom_field(self):
        if not self.current_customer_id:
            return
            
        title, ok1 = QInputDialog.getText(self, "Custom Field", "Enter Field Label / Title:")
        if not ok1 or not title.strip():
            return
            
        value, ok2 = QInputDialog.getMultiLineText(self, "Custom Field", f"Enter Value for '{title}':")
        if not ok2:
            return
            
        try:
            database.add_other_info(self.current_customer_id, title.strip(), value.strip())
            self.refresh_custom_fields()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add field: {e}")

    def on_edit_custom_field(self):
        row = self.fields_table.currentRow()
        if row < 0:
            return
            
        field_id = int(self.fields_table.item(row, 0).text())
        title = self.fields_table.item(row, 1).text()
        value = self.fields_table.item(row, 2).text()
        
        new_val, ok = QInputDialog.getMultiLineText(self, "Edit Field", f"Edit Value for '{title}':", value)
        if ok:
            try:
                database.update_other_info(field_id, title, new_val.strip())
                self.refresh_custom_fields()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to edit field: {e}")

    def on_delete_custom_field(self):
        row = self.fields_table.currentRow()
        if row < 0:
            return
            
        field_id = int(self.fields_table.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirm Delete", "Remove this custom field?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                database.delete_other_info(field_id)
                self.refresh_custom_fields()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove custom field: {e}")

    # --- Document Upload & Management ---
    def refresh_documents(self):
        self.docs_table.setRowCount(0)
        if not self.current_customer_id:
            return
            
        docs = database.get_customer_documents(self.current_customer_id)
        self.docs_table.setRowCount(len(docs))
        for i, d in enumerate(docs):
            self.docs_table.setItem(i, 0, QTableWidgetItem(str(d['id'])))
            
            # Save absolute file path inside the item for opening
            fn_item = QTableWidgetItem(d['filename'])
            fn_item.setData(Qt.UserRole, d['file_path'])
            self.docs_table.setItem(i, 1, fn_item)
            
            self.docs_table.setItem(i, 2, QTableWidgetItem(d['file_type'] or ''))
            self.docs_table.setItem(i, 3, QTableWidgetItem(d['remarks'] or ''))
            self.docs_table.setItem(i, 4, QTableWidgetItem(d['created_at']))

    def on_upload_document(self):
        if not self.current_customer_id:
            return
            
        filepaths, _ = QFileDialog.getOpenFileNames(
            self, "Select Documents to Upload", "", 
            "All Document Files (*.pdf *.png *.jpg *.jpeg);;PDF Documents (*.pdf);;Images (*.png *.jpg *.jpeg)"
        )
        
        if not filepaths:
            return
            
        remarks, ok = QInputDialog.getText(self, "Document Remarks", "Enter document remarks / comments:")
            
        try:
            use_gdrive = settings_mgr.get("use_gdrive", False)
            cust = database.get_customer(self.current_customer_id)
            code = cust['customer_code']
            
            if not use_gdrive:
                # Physical directory details from settings
                dest_dir_root = settings_mgr.get("documents_folder")
                # Separate by customer code subdirectory for integrity
                dest_dir = os.path.join(dest_dir_root, code)
                os.makedirs(dest_dir, exist_ok=True)
            
            uploaded_count = 0
            for filepath in filepaths:
                filename = os.path.basename(filepath)
                # If no remarks provided or cancelled, use filename
                doc_remarks = remarks.strip() if ok and remarks.strip() else filename
                
                # Resolve extension
                _, ext = os.path.splitext(filename)
                file_type = ext.replace(".", "").upper()
                
                if use_gdrive:
                    file_id, web_link = gdrive_mgr.upload_file(filepath, code)
                    dest_path = f"gdrive://{web_link}"
                else:
                    # Avoid collisions by adding timestamp prefix
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    dest_path = os.path.join(dest_dir, unique_filename)
                    # Copy file
                    shutil.copy2(filepath, dest_path)
                
                # DB save
                database.add_document(self.current_customer_id, filename, dest_path, file_type, doc_remarks)
                uploaded_count += 1
                
            self.refresh_documents()
            
            if uploaded_count == 1:
                QMessageBox.information(self, "Success", f"Document '{os.path.basename(filepaths[0])}' uploaded successfully.")
            else:
                QMessageBox.information(self, "Success", f"{uploaded_count} documents uploaded successfully.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload document(s): {e}")

    def on_view_document(self):
        row = self.docs_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Alert", "Select a document row to view.")
            return
            
        filepath = self.docs_table.item(row, 1).data(Qt.UserRole)
        if not filepath:
            QMessageBox.critical(self, "File Error", "The file path is missing.")
            return
            
        if filepath.startswith("gdrive://"):
            web_link = filepath.replace("gdrive://", "")
            webbrowser.open(web_link)
            return
            
        if not os.path.exists(filepath):
            QMessageBox.critical(self, "File Error", "The file does not exist on disk or path is corrupt.")
            return
            
        try:
            # Cross-platform / Windows launch native file editor/viewer
            os.startfile(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not launch native document viewer: {e}")

    def on_open_document_folder(self):
        row = self.docs_table.currentRow()
        filepath = None
        if row >= 0:
            filepath = self.docs_table.item(row, 1).data(Qt.UserRole)
            
        if filepath and filepath.startswith("gdrive://"):
            QMessageBox.information(self, "Cloud Storage", "This file is stored in Google Drive. Please use the View/Open button to open it in your browser.")
            return
            
        if filepath and os.path.exists(filepath):
            folder = os.path.dirname(filepath)
        else:
            # Fallback to configured root documents folder
            folder = settings_mgr.get("documents_folder")
            
        if os.path.exists(folder):
            try:
                os.startfile(folder)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open directory: {e}")
        else:
            QMessageBox.warning(self, "Error", "Directory does not exist.")

    def on_edit_document_remarks(self):
        row = self.docs_table.currentRow()
        if row < 0:
            return
            
        doc_id = int(self.docs_table.item(row, 0).text())
        old_remarks = self.docs_table.item(row, 3).text()
        
        new_remarks, ok = QInputDialog.getText(self, "Edit Remarks", "Enter document remarks:", QLineEdit.Normal, old_remarks)
        if ok:
            try:
                database.update_document_remarks(doc_id, new_remarks.strip())
                self.refresh_documents()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update remarks: {e}")

    def on_delete_document(self):
        row = self.docs_table.currentRow()
        if row < 0:
            return
            
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to permanently delete this document from disk?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            doc_id = int(self.docs_table.item(row, 0).text())
            filepath = self.docs_table.item(row, 1).data(Qt.UserRole)
            
            try:
                # Remove file from disk
                if filepath and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as fe:
                        print(f"Failed to delete disk file: {fe}")
                        
                database.delete_document(doc_id)
                self.refresh_documents()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete document: {e}")

    # --- Timeline, SMS & WhatsApp Integrations ---
    def setup_tools_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Left side: Timeline Logs
        v_left = QVBoxLayout()
        v_left.addWidget(QLabel("<b>Customer Touchpoint Timeline:</b>"))
        self.timeline_list = QListWidget()
        v_left.addWidget(self.timeline_list)
        layout.addLayout(v_left, stretch=1)
        
        # Right side: QR Code and messaging
        v_right = QVBoxLayout()
        v_right.setSpacing(12)
        
        # QR Code Card
        qr_card = QFrame()
        qr_card.setObjectName("KPICard")
        qr_card.setProperty("class", "KPICard")
        qr_lay = QVBoxLayout(qr_card)
        qr_lay.setAlignment(Qt.AlignCenter)
        qr_lay.addWidget(QLabel("<b>Customer Code QR Identifier:</b>"), alignment=Qt.AlignCenter)
        
        self.qr_code_widget = QRCodeWidget()
        qr_lay.addWidget(self.qr_code_widget, alignment=Qt.AlignCenter)
        
        self.qr_lbl = QLabel("")
        self.qr_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        qr_lay.addWidget(self.qr_lbl, alignment=Qt.AlignCenter)
        
        v_right.addWidget(qr_card)
        
        # WhatsApp Card
        wa_card = QFrame()
        wa_card.setObjectName("KPICard")
        wa_card.setProperty("class", "KPICard")
        wa_lay = QVBoxLayout(wa_card)
        wa_lay.addWidget(QLabel("<b>WhatsApp & SMS Gateway:</b>"))
        
        self.wa_msg_input = QTextEdit()
        self.wa_msg_input.setMaximumHeight(80)
        self.wa_msg_input.setPlainText("Hello {name},\n\nThis is SUN CRM. We are reaching out regarding...")
        wa_lay.addWidget(self.wa_msg_input)
        
        self.send_wa_btn = QPushButton("Send WhatsApp Message")
        self.send_wa_btn.setProperty("class", "PrimaryButton")
        self.send_wa_btn.clicked.connect(self.on_send_whatsapp)
        wa_lay.addWidget(self.send_wa_btn)
        
        self.send_sms_btn = QPushButton("Simulate SMS Transmission")
        self.send_sms_btn.setProperty("class", "SecondaryButton")
        self.send_sms_btn.clicked.connect(self.on_simulate_sms)
        wa_lay.addWidget(self.send_sms_btn)
        
        v_right.addWidget(wa_card)
        v_right.addStretch()
        
        layout.addLayout(v_right, stretch=1)
        self.tabs.addTab(tab, "Timeline & Tools")

    def refresh_tools_tab(self, cust):
        self.qr_code_widget.setCode(cust['customer_code'])
        self.qr_lbl.setText(cust['customer_code'])
        
        # Build customer timeline dynamically from related items
        self.timeline_list.clear()
        
        # 1. Created timeline node
        self.timeline_list.addItem(f"📅 Profile Created: {cust['created_at']}")
        
        # 2. Add document count node
        docs = database.get_customer_documents(self.current_customer_id)
        if docs:
            self.timeline_list.addItem(f"📁 Documents Attached: {len(docs)} files uploaded.")
            for d in docs:
                self.timeline_list.addItem(f"  └─ File: {d['filename']} ({d['created_at']})")
        else:
            self.timeline_list.addItem("📁 Documents: No attachments linked.")
            
        # 3. Add credential node
        creds = database.get_customer_credentials(self.current_customer_id)
        if creds:
            self.timeline_list.addItem(f"🔑 Credentials: {len(creds)} service passwords stored.")
            for c in creds:
                self.timeline_list.addItem(f"  └─ Service: {c['service_name']} ({c['created_at']})")
        else:
            self.timeline_list.addItem("🔑 Credentials: No passwords saved.")
            
        # Customize message with name
        msg_template = f"Hello {cust['name']},\n\nWe appreciate doing business with you! Please let us know if you need any assistance."
        self.wa_msg_input.setPlainText(msg_template)

    def on_send_whatsapp(self):
        if not self.current_customer_id:
            return
            
        phone = self.biodata_mobile1.text().strip()
        clean_phone = "".join(filter(str.isdigit, phone))
        
        if not clean_phone:
            QMessageBox.warning(self, "Invalid Phone", "This customer does not have a valid mobile number.")
            return
            
        # Format mobile to international (default 91 if length is 10 digits)
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
            
        msg = self.wa_msg_input.toPlainText().strip()
        encoded_msg = urllib.parse.quote(msg)
        
        wa_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
        try:
            QDesktopServices.openUrl(QUrl(wa_url))
            database.log_activity("WhatsApp Trigger", f"Opened WhatsApp web draft to: {clean_phone}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open web browser: {e}")

    def on_simulate_sms(self):
        phone = self.biodata_mobile1.text().strip()
        if not phone:
            QMessageBox.warning(self, "Invalid Phone", "This customer does not have a valid mobile number.")
            return
            
        msg = self.wa_msg_input.toPlainText().strip()
        QMessageBox.information(
            self, 
            "SMS Gateway Simulator", 
            f"SMS dispatch simulated successfully!\n\n"
            f"<b>Recipient:</b> {phone}\n"
            f"<b>Message:</b> {msg}\n\n"
            f"<i>Twilio API response: Status: Queued, SID: SM{hashlib.md5(phone.encode()).hexdigest()[:16]}</i>"
        )
        database.log_activity("SMS Simulation", f"Simulated SMS transmission to: {phone}")
