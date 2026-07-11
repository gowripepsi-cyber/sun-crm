import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import database
from settings_manager import settings_mgr
from utils import backup_engine

class BackupTab(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. Header
        title_label = QLabel("Backup & Recovery Manager")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # Info Box
        info_frame = QFrame()
        info_frame.setObjectName("KPICard")
        info_frame.setProperty("class", "KPICard")
        info_layout = QVBoxLayout(info_frame)
        
        self.info_lbl = QLabel()
        self.info_lbl.setFont(QFont("Segoe UI", 10))
        self.info_lbl.setWordWrap(True)
        info_layout.addWidget(self.info_lbl)
        layout.addWidget(info_frame)
        
        # 2. Main Actions
        btn_layout = QHBoxLayout()
        
        self.backup_now_btn = QPushButton("Create Manual Backup")
        self.backup_now_btn.setProperty("class", "PrimaryButton")
        self.backup_now_btn.clicked.connect(self.on_create_backup)
        btn_layout.addWidget(self.backup_now_btn)
        
        self.restore_btn = QPushButton("Restore Backup File (.zip)")
        self.restore_btn.setProperty("class", "SecondaryButton")
        self.restore_btn.clicked.connect(self.on_restore_file)
        btn_layout.addWidget(self.restore_btn)
        
        self.restore_selected_btn = QPushButton("Restore Selected Snapshot")
        self.restore_selected_btn.setProperty("class", "SecondaryButton")
        self.restore_selected_btn.clicked.connect(self.on_restore_selected)
        btn_layout.addWidget(self.restore_selected_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 3. Backup History Table
        history_header = QLabel("Database Backup History")
        history_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(history_header)
        
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Backup Type", "Status", "Archive Path"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.history_table)
        
        # Refresh info & table
        self.refresh_backup_info()
        self.refresh_history_table()

    def refresh_backup_info(self):
        backup_folder = settings_mgr.get("backup_folder")
        db_path = settings_mgr.get("db_location")
        self.info_lbl.setText(
            f"<b>Database File:</b> {db_path}<br>"
            f"<b>Backup Destination:</b> {backup_folder}<br><br>"
            f"<i>Note: Standard automatic backups are completed based on settings when exiting. "
            f"Restoring backups will overwrite the existing active database immediately. A pre-restore snapshot "
            f"of the current database will be saved in the database directory for emergency undo capabilities.</i>"
        )

    def refresh_history_table(self):
        try:
            history = database.get_backup_history()
            self.history_table.setRowCount(len(history))
            for i, h in enumerate(history):
                self.history_table.setItem(i, 0, QTableWidgetItem(h.get('timestamp', '')))
                self.history_table.setItem(i, 1, QTableWidgetItem(h.get('backup_type', '')))
                self.history_table.setItem(i, 2, QTableWidgetItem(h.get('status', '')))
                
                path_item = QTableWidgetItem(h.get('backup_path', ''))
                # Stash path inside column for restoration
                path_item.setData(Qt.UserRole, h.get('backup_path'))
                self.history_table.setItem(i, 3, path_item)
        except Exception as e:
            print(f"Error listing backup history: {e}")

    def on_create_backup(self):
        success, result = backup_engine.perform_backup("Manual")
        if success:
            QMessageBox.information(self, "Backup Status", f"Database successfully backed up!\nArchive saved to: {result}")
            self.refresh_history_table()
        else:
            QMessageBox.critical(self, "Backup Error", f"Backup failed: {result}")
            self.refresh_history_table()

    def on_restore_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Backup Archive", "", "ZIP Backup Files (*.zip)")
        if not filepath:
            return
            
        self.trigger_restoration(filepath)

    def on_restore_selected(self):
        row = self.history_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Alert", "Please select a backup log entry from the table below.")
            return
            
        filepath = self.history_table.item(row, 3).data(Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            QMessageBox.critical(self, "Error", "The backup file record does not exist on disk.")
            return
            
        self.trigger_restoration(filepath)

    def trigger_restoration(self, filepath):
        confirm = QMessageBox.warning(
            self, 
            "Restore Database Warning", 
            "WARNING: Restoring will overwrite all current customer records, credentials, and attachments in the active database!\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # We must disconnect database connection to release file lock during copy
            success, msg = backup_engine.restore_backup(filepath)
            if success:
                QMessageBox.information(self, "Success", "Database restore completed successfully!\nThe application database will reconnect immediately.")
                
                # Signal main window to reload data
                if self.main_window:
                    self.main_window.on_database_changed()
                    
                self.refresh_history_table()
            else:
                QMessageBox.critical(self, "Restore Failed", f"An error occurred: {msg}")
