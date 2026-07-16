import sys
import os
import hashlib
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
                             QStatusBar, QDialog, QLineEdit, QMessageBox, QFrame,
                             QScrollArea, QGridLayout)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QIcon, QDesktopServices
import database
from settings_manager import settings_mgr
import theme_manager
from utils import backup_engine

# Import Tabs
from widgets.dashboard_tab import DashboardTab
from widgets.customer_tab import CustomerTab
from widgets.search_tab import SearchTab
from widgets.reports_tab import ReportsTab
from widgets.backup_tab import BackupTab
from widgets.settings_tab import SettingsTab
from widgets.names_list_tab import CustomerNamesListTab

class LoginDialog(QDialog):
    """Secure startup login screen styled matching the dark/light QSS."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SUN CRM - Secure Login")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(380, 240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Logo placeholder or Title
        title = QLabel("SUN CRM")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #4f46e5;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        sub = QLabel("Enterprise Customer Database System")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet("color: #64748b; margin-bottom: 10px;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)
        
        # Input
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Enter access password...")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setMinimumHeight(35)
        self.pwd_input.returnPressed.connect(self.check_login)
        layout.addWidget(self.pwd_input)
        
        # Actions
        btn_layout = QHBoxLayout()
        self.exit_btn = QPushButton("Exit Application")
        self.exit_btn.setProperty("class", "SecondaryButton")
        self.exit_btn.setMinimumHeight(35)
        self.exit_btn.clicked.connect(self.reject)
        
        self.login_btn = QPushButton("Authenticate")
        self.login_btn.setProperty("class", "PrimaryButton")
        self.login_btn.setMinimumHeight(35)
        self.login_btn.clicked.connect(self.check_login)
        
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addWidget(self.login_btn)
        layout.addLayout(btn_layout)
        
        self.retries = 3

    def check_login(self):
        entered_pwd = self.pwd_input.text()
        saved_hash = settings_mgr.get("password_hash")
        
        entered_hash = hashlib.sha256(entered_pwd.encode('utf-8')).hexdigest()
        
        if entered_hash == saved_hash:
            self.accept()
        else:
            self.retries -= 1
            if self.retries <= 0:
                QMessageBox.critical(self, "Access Denied", "Too many invalid authentication attempts. Exiting.")
                self.reject()
            else:
                QMessageBox.warning(self, "Invalid Password", f"Incorrect password. {self.retries} attempts remaining.")
                self.pwd_input.clear()
                self.pwd_input.setFocus()

class FutureModulesTab(QWidget):
    """Display information about planned future expansion modules."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("Expansion Roadmap & Future Modules")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        sub = QLabel("Upcoming plugins and integrations. Configure mockups and API endpoints below.")
        sub.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(sub)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        scroll.setWidget(content)
        grid = QGridLayout(content)
        grid.setSpacing(15)
        
        modules = [
            ("🕒 Customer Timeline", "View historic interactive touchpoint milestones automatically synced from emails, calls, and orders.", "In Development"),
            ("📋 Activity Auditing", "Complete user session audit logs and record histories to satisfy compliance criteria.", "Beta Available"),
            ("📱 QR Codes", "Instantly render vector barcodes and business card QR codes containing customer bio cards.", "Ready to Deploy"),
            ("💬 WhatsApp Messaging", "Send templated invoices and follow-ups directly to clients using WhatsApp Business Web links.", "Operational"),
            ("✉️ SMS Gateways", "Bulk-transmit reminders, OTPs, and category announcements through custom Twilio integrations.", "Planned"),
            ("🔔 Reminders & Tasks", "Create callback alarms, subscription expiration notices, and schedule calendars.", "Planned"),
            ("🔒 Roles & Permissions", "Set up fine-grained permission control grids for multiple user logons.", "Planned"),
            ("🌐 Multi-User Server", "Transition SQLite local storage seamlessly into standard cloud PostgreSQL servers.", "Architecture Stage")
        ]
        
        for idx, (name, desc, status) in enumerate(modules):
            card = QFrame()
            card.setObjectName("KPICard")
            card.setProperty("class", "KPICard")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)
            
            lbl_name = QLabel(name)
            lbl_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
            lbl_name.setStyleSheet("color: #818cf8;")
            
            lbl_status = QLabel(status)
            lbl_status.setFont(QFont("Segoe UI", 8, QFont.Bold))
            lbl_status.setStyleSheet("background-color: #334155; color: #10b981; padding: 2px 6px; border-radius: 4px;")
            
            head_lay = QHBoxLayout()
            head_lay.addWidget(lbl_name)
            head_lay.addStretch()
            head_lay.addWidget(lbl_status)
            card_layout.addLayout(head_lay)
            
            lbl_desc = QLabel(desc)
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
            card_layout.addWidget(lbl_desc)
            
            # Place in grid
            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)
            
        layout.addWidget(scroll)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SUN CRM - Enterprise Customer Management")
        self.resize(1150, 750)
        
        # Build core layouts
        self.init_ui()
        self.apply_theme()
        
        # Log session start
        database.log_activity("Application Startup", "Launched SUN CRM and reconnected SQLite engine.")

    def init_ui(self):
        # Master central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        master_layout = QHBoxLayout(central)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)
        
        # 1. Left Sidebar Navigation
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(6)
        
        # Sidebar Logo / Header
        logo_lbl = QLabel("SUN CRM")
        logo_lbl.setObjectName("SidebarTitle")
        logo_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        logo_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_lbl)
        sidebar_layout.addSpacing(15)
        
        # Nav buttons
        self.nav_buttons = []
        navs = [
            ("📊 Dashboard", 0),
            ("👤 Customers", 1),
            ("📋 Names List", 7),
            ("🔍 Search Engine", 2),
            ("📈 Report Hub", 3),
            ("💾 Database Backup", 4),
            ("⚙️ Settings", 5),
            ("🚀 Expansion Suite", 6)
        ]
        
        for name, idx in navs:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("class", "NavButton")
            btn.setProperty("stack_idx", idx)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        # Select first nav by default
        self.nav_buttons[0].setChecked(True)
        
        sidebar_layout.addStretch()
        
        # Light/Dark Theme Switcher at bottom of sidebar
        self.theme_btn = QPushButton("Toggle Color Theme")
        self.theme_btn.setProperty("class", "SecondaryButton")
        self.theme_btn.clicked.connect(self.toggle_theme_action)
        sidebar_layout.addWidget(self.theme_btn)
        
        master_layout.addWidget(self.sidebar)
        
        # 2. Main Page Stack
        self.page_stack = QStackedWidget()
        
        # Instantiate widgets
        self.tab_dashboard = DashboardTab(self)
        self.tab_customer = CustomerTab(self)
        self.tab_search = SearchTab(self)
        self.tab_reports = ReportsTab(self)
        self.tab_backup = BackupTab(self)
        self.tab_settings = SettingsTab(self)
        self.tab_future = FutureModulesTab(self)
        self.tab_names_list = CustomerNamesListTab(self)
        
        # Add to stack
        self.page_stack.addWidget(self.tab_dashboard)    # Index 0
        self.page_stack.addWidget(self.tab_customer)     # Index 1
        self.page_stack.addWidget(self.tab_search)       # Index 2
        self.page_stack.addWidget(self.tab_reports)      # Index 3
        self.page_stack.addWidget(self.tab_backup)       # Index 4
        self.page_stack.addWidget(self.tab_settings)     # Index 5
        self.page_stack.addWidget(self.tab_future)       # Index 6
        self.page_stack.addWidget(self.tab_names_list)   # Index 7
        
        # Wire Names List → navigate to full Customer profile on double-click
        self.tab_names_list.open_customer_profile.connect(self.navigate_to_customer)
        
        master_layout.addWidget(self.page_stack)
        
        # 3. Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready", 3000)
        self.update_status_bar()

    def switch_page(self, index):
        # Set checked state on sidebar buttons matching page
        for btn in self.nav_buttons:
            btn.setChecked(btn.property("stack_idx") == index)
            
        self.page_stack.setCurrentIndex(index)
        
        # Refresh current page contents when navigated
        if index == 0:
            self.tab_dashboard.refresh_stats()
        elif index == 1:
            self.tab_customer.refresh_customer_list()
        elif index == 2:
            self.tab_search.trigger_search()
        elif index == 4:
            self.tab_backup.refresh_backup_info()
            self.tab_backup.refresh_history_table()
        elif index == 7:
            self.tab_names_list.refresh()

    def navigate_to_customer(self, customer_id):
        """Forces dashboard or search results double click to hop to customer profile tab."""
        self.switch_page(1)
        self.tab_customer.select_customer_by_id(customer_id)

    def apply_theme(self):
        theme_name = settings_mgr.get("theme", "Dark")
        stylesheet = theme_manager.get_stylesheet(theme_name)
        QApplication.instance().setStyleSheet(stylesheet)
        self.statusBar().showMessage(f"Applied visual theme: {theme_name} Mode", 2000)

    def toggle_theme_action(self):
        current_theme = settings_mgr.get("theme", "Dark")
        next_theme = "Light" if current_theme == "Dark" else "Dark"
        settings_mgr.set("theme", next_theme)
        settings_mgr.save_settings()
        
        # Reload Settings Tab fields to reflect combo box index
        self.tab_settings.load_values()
        self.apply_theme()

    def update_status_bar(self):
        company = settings_mgr.get("company_name", "SUN CRM Enterprise")
        db_path = settings_mgr.get("db_location", "N/A")
        self.statusBar().showMessage(f"Company: {company} | Database Location: {db_path}")

    def on_database_changed(self):
        """Called if settings DB path is altered or a database backup is restored."""
        try:
            database.init_db()  # Run migrations / verify tables
            # Refresh all interfaces
            self.tab_dashboard.refresh_stats()
            self.tab_customer.refresh_customer_list()
            self.tab_search.clear_filters()
            self.update_status_bar()
            self.statusBar().showMessage("Database reconnected successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Database Reconnect Error", f"Failed to reconnect to database: {e}")

    def closeEvent(self, event):
        # Auto backup on exit
        if settings_mgr.get("auto_backup_on_exit", True):
            self.statusBar().showMessage("Saving database backup snapshots...")
            success, path = backup_engine.perform_backup("Auto-Exit")
            if success:
                print(f"Automatic database exit backup saved to: {path}")
                
        database.log_activity("Application Shutdown", "Terminated application instance cleanly.")
        event.accept()

def main():
    # Setup directories
    settings_mgr.ensure_directories()
    
    # Initialize Database structures
    database.init_db()
    
    app = QApplication(sys.argv)
    
    # Set default fonts
    app.setFont(QFont("Segoe UI", 9))
    
    # Startup Authentication Check
    if settings_mgr.get("password_enabled", False) and settings_mgr.get("password_hash"):
        # Apply style sheets to app first so login modal is styled
        theme_name = settings_mgr.get("theme", "Dark")
        app.setStyleSheet(theme_manager.get_stylesheet(theme_name))
        
        login = LoginDialog()
        if login.exec() != QDialog.Accepted:
            # Quit immediately if login is canceled or fails
            sys.exit(0)
            
    # Launch main dashboard
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
