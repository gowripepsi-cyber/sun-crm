import os
import hashlib
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QComboBox, QPushButton, 
                             QFileDialog, QMessageBox, QCheckBox, QInputDialog, 
                             QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from settings_manager import settings_mgr

class SettingsTab(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        title_label = QLabel("Settings & Configurations")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # 1. Company Info Section
        company_card = QFrame()
        company_card.setObjectName("KPICard")
        company_card.setProperty("class", "KPICard")
        comp_layout = QVBoxLayout(company_card)
        comp_layout.setSpacing(10)
        
        comp_header = QLabel("Company Information Profile")
        comp_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        comp_header.setStyleSheet("color: #818cf8;")
        comp_layout.addWidget(comp_header)
        
        r1 = QHBoxLayout()
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Company / Organization Name:"))
        self.comp_name = QLineEdit()
        v1.addWidget(self.comp_name)
        r1.addLayout(v1)
        
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Contact Phone Number:"))
        self.comp_phone = QLineEdit()
        v2.addWidget(self.comp_phone)
        r1.addLayout(v2)
        
        comp_layout.addLayout(r1)
        
        r2 = QHBoxLayout()
        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Contact Email Address:"))
        self.comp_email = QLineEdit()
        v3.addWidget(self.comp_email)
        r2.addLayout(v3)
        
        v4 = QVBoxLayout()
        v4.addWidget(QLabel("Company Logo File (.png/.jpg):"))
        logo_picker = QHBoxLayout()
        self.comp_logo = QLineEdit()
        logo_picker.addWidget(self.comp_logo)
        self.logo_btn = QPushButton("Browse")
        self.logo_btn.setProperty("class", "SecondaryButton")
        self.logo_btn.clicked.connect(self.browse_logo)
        logo_picker.addWidget(self.logo_btn)
        v4.addLayout(logo_picker)
        r2.addLayout(v4)
        
        comp_layout.addLayout(r2)
        
        v5 = QVBoxLayout()
        v5.addWidget(QLabel("Company Physical Address:"))
        self.comp_address = QTextEdit()
        self.comp_address.setMaximumHeight(80)
        v5.addWidget(self.comp_address)
        comp_layout.addLayout(v5)
        
        layout.addWidget(company_card)
        
        # 2. File & Directory Setup
        dir_card = QFrame()
        dir_card.setObjectName("KPICard")
        dir_card.setProperty("class", "KPICard")
        dir_layout = QVBoxLayout(dir_card)
        dir_layout.setSpacing(10)
        
        dir_header = QLabel("Database & Storage Locations")
        dir_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        dir_header.setStyleSheet("color: #818cf8;")
        dir_layout.addWidget(dir_header)
        
        # Database Path
        dir_layout.addWidget(QLabel("Active SQLite Database Location (*.db):"))
        db_lay = QHBoxLayout()
        self.db_path = QLineEdit()
        db_lay.addWidget(self.db_path)
        self.db_btn = QPushButton("Select File")
        self.db_btn.setProperty("class", "SecondaryButton")
        self.db_btn.clicked.connect(self.browse_db)
        db_lay.addWidget(self.db_btn)
        dir_layout.addLayout(db_lay)
        
        # Documents Folder
        dir_layout.addWidget(QLabel("Physical Uploaded Documents Directory Folder:"))
        docs_lay = QHBoxLayout()
        self.docs_folder = QLineEdit()
        docs_lay.addWidget(self.docs_folder)
        self.docs_btn = QPushButton("Select Folder")
        self.docs_btn.setProperty("class", "SecondaryButton")
        self.docs_btn.clicked.connect(self.browse_docs)
        docs_lay.addWidget(self.docs_btn)
        dir_layout.addLayout(docs_lay)
        
        # Backup Folder
        dir_layout.addWidget(QLabel("Database Backup Archives Folder:"))
        back_lay = QHBoxLayout()
        self.backup_folder = QLineEdit()
        back_lay.addWidget(self.backup_folder)
        self.back_btn = QPushButton("Select Folder")
        self.back_btn.setProperty("class", "SecondaryButton")
        self.back_btn.clicked.connect(self.browse_backup)
        back_lay.addWidget(self.back_btn)
        dir_layout.addLayout(back_lay)
        
        layout.addWidget(dir_card)
        
        # 3. GUI theme & Security
        opt_card = QFrame()
        opt_card.setObjectName("KPICard")
        opt_card.setProperty("class", "KPICard")
        opt_layout = QVBoxLayout(opt_card)
        opt_layout.setSpacing(10)
        
        opt_header = QLabel("Preferences & Security")
        opt_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        opt_header.setStyleSheet("color: #818cf8;")
        opt_layout.addWidget(opt_header)
        
        h_pref = QHBoxLayout()
        v_theme = QVBoxLayout()
        v_theme.addWidget(QLabel("Visual Application Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        v_theme.addWidget(self.theme_combo)
        h_pref.addLayout(v_theme)
        
        v_sec = QVBoxLayout()
        v_sec.addWidget(QLabel("Security Settings:"))
        self.pwd_enable = QCheckBox("Enable Startup Password Lock Protection")
        v_sec.addWidget(self.pwd_enable)
        h_pref.addLayout(v_sec)
        
        opt_layout.addLayout(h_pref)
        
        # Google Drive Integration
        v_gdrive = QVBoxLayout()
        v_gdrive.addWidget(QLabel("Google Drive Integration:"))
        self.gdrive_enable = QCheckBox("Use Google Drive for Documents (requires credentials.json)")
        v_gdrive.addWidget(self.gdrive_enable)
        
        h_cred = QHBoxLayout()
        self.gdrive_cred_path = QLineEdit()
        self.gdrive_cred_path.setPlaceholderText("Path to credentials.json")
        self.gdrive_cred_btn = QPushButton("Browse")
        self.gdrive_cred_btn.clicked.connect(self.browse_gdrive_cred)
        h_cred.addWidget(self.gdrive_cred_path)
        h_cred.addWidget(self.gdrive_cred_btn)
        v_gdrive.addLayout(h_cred)
        opt_layout.addLayout(v_gdrive)
        
        # Password setting button row
        pwd_row = QHBoxLayout()
        self.set_pwd_btn = QPushButton("Set / Change Lock Password")
        self.set_pwd_btn.setProperty("class", "SecondaryButton")
        self.set_pwd_btn.clicked.connect(self.on_set_password)
        pwd_row.addWidget(self.set_pwd_btn)
        
        self.clear_pwd_btn = QPushButton("Clear Passphrase Hash")
        self.clear_pwd_btn.setProperty("class", "SecondaryButton")
        self.clear_pwd_btn.clicked.connect(self.on_clear_password)
        pwd_row.addWidget(self.clear_pwd_btn)
        pwd_row.addStretch()
        opt_layout.addLayout(pwd_row)
        
        layout.addWidget(opt_card)
        
        # Save Action Button
        self.save_btn = QPushButton("Apply and Save All Changes")
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        
        # Main widget layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)
        
        # Load active values
        self.load_values()

    def load_values(self):
        self.comp_name.setText(settings_mgr.get("company_name", ""))
        self.comp_phone.setText(settings_mgr.get("company_phone", ""))
        self.comp_email.setText(settings_mgr.get("company_email", ""))
        self.comp_logo.setText(settings_mgr.get("company_logo", ""))
        self.comp_address.setPlainText(settings_mgr.get("company_address", ""))
        
        self.db_path.setText(settings_mgr.get("db_location", ""))
        self.docs_folder.setText(settings_mgr.get("documents_folder", ""))
        self.backup_folder.setText(settings_mgr.get("backup_folder", ""))
        self.gdrive_enable.setChecked(settings_mgr.get("use_gdrive", False))
        self.gdrive_cred_path.setText(settings_mgr.get("gdrive_credentials_path", "credentials.json"))
        
        idx = self.theme_combo.findText(settings_mgr.get("theme", "Dark"))
        self.theme_combo.setCurrentIndex(idx if idx >= 0 else 0)
        
        self.pwd_enable.setChecked(settings_mgr.get("password_enabled", False))

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.comp_logo.setText(path)

    def browse_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Database Location", "suncrm.db", "SQLite Database (*.db)")
        if path:
            self.db_path.setText(path)

    def browse_docs(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Documents Folder")
        if folder:
            self.docs_folder.setText(folder)

    def browse_gdrive_cred(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select credentials.json", "", "JSON Files (*.json)")
        if path:
            self.gdrive_cred_path.setText(path)

    def browse_backup(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            self.backup_folder.setText(folder)

    def on_set_password(self):
        pwd, ok = QInputDialog.getText(self, "Set Password", "Enter Startup Password:", QLineEdit.Password)
        if not ok or not pwd:
            return
            
        pwd_confirm, ok_confirm = QInputDialog.getText(self, "Confirm Password", "Re-enter Startup Password:", QLineEdit.Password)
        if not ok_confirm:
            return
            
        if pwd != pwd_confirm:
            QMessageBox.critical(self, "Match Error", "Passwords do not match. Set cancelled.")
            return
            
        # Hash SHA-256
        pwd_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        settings_mgr.set("password_hash", pwd_hash)
        QMessageBox.information(self, "Security Status", "Startup security password hash set successfully.")

    def on_clear_password(self):
        settings_mgr.set("password_hash", "")
        self.pwd_enable.setChecked(False)
        QMessageBox.information(self, "Security Status", "Password protection credentials cleared.")

    def save_settings(self):
        # 1. Validation
        if not self.db_path.text().strip():
            QMessageBox.warning(self, "Path Error", "Database path cannot be empty.")
            return
            
        # If password check box is checked but no password hash exists, prompt
        if self.pwd_enable.isChecked() and not settings_mgr.get("password_hash"):
            QMessageBox.warning(self, "Security Alert", "Please set a password using the 'Set / Change Lock Password' button first before enabling lock screen.")
            return
            
        # Save values in manager
        original_db = settings_mgr.get("db_location")
        original_theme = settings_mgr.get("theme")
        
        settings_mgr.set("company_name", self.comp_name.text().strip())
        settings_mgr.set("company_phone", self.comp_phone.text().strip())
        settings_mgr.set("company_email", self.comp_email.text().strip())
        settings_mgr.set("company_logo", self.comp_logo.text().strip())
        settings_mgr.set("company_address", self.comp_address.toPlainText().strip())
        
        settings_mgr.set("db_location", self.db_path.text().strip())
        settings_mgr.set("documents_folder", self.docs_folder.text().strip())
        settings_mgr.set("backup_folder", self.backup_folder.text().strip())
        
        settings_mgr.set("use_gdrive", self.gdrive_enable.isChecked())
        settings_mgr.set("gdrive_credentials_path", self.gdrive_cred_path.text().strip())
        
        theme_sel = self.theme_combo.currentText()
        settings_mgr.set("theme", theme_sel)
        settings_mgr.set("password_enabled", self.pwd_enable.isChecked())
        
        # Save JSON file
        settings_mgr.save_settings()
        
        # Trigger Theme Apply instantly
        if theme_sel != original_theme and self.main_window:
            self.main_window.apply_theme()
            
        # If DB location changed, trigger reconnect
        if self.db_path.text().strip() != original_db and self.main_window:
            self.main_window.on_database_changed()
            
        QMessageBox.information(self, "Success", "Configurations applied and saved successfully.")
