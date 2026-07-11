import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import database
from settings_manager import settings_mgr
from utils import exporter

class ReportsTab(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_headers = []
        self.current_rows = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. Header
        title_label = QLabel("Reports Center")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # 2. Settings Panel
        settings_card = QFrame()
        settings_card.setObjectName("KPICard")
        settings_card.setProperty("class", "KPICard")
        settings_layout = QHBoxLayout(settings_card)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(20)
        
        settings_layout.addWidget(QLabel("Select Report Template:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Customer List",
            "Category Wise Summary",
            "Age Group Summary",
            "Gender Summary",
            "Recent Customers (Last 30 Days)",
            "Document Attachment Registry"
        ])
        settings_layout.addWidget(self.report_type_combo, stretch=1)
        
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setProperty("class", "PrimaryButton")
        self.generate_btn.clicked.connect(self.on_generate_report)
        settings_layout.addWidget(self.generate_btn)
        
        layout.addWidget(settings_card)
        
        # 3. Export Controls Bar
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Export options:"))
        
        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.setProperty("class", "SecondaryButton")
        self.export_csv_btn.clicked.connect(lambda: self.on_export("csv"))
        export_layout.addWidget(self.export_csv_btn)
        
        self.export_xls_btn = QPushButton("Export to Excel")
        self.export_xls_btn.setProperty("class", "SecondaryButton")
        self.export_xls_btn.clicked.connect(lambda: self.on_export("excel"))
        export_layout.addWidget(self.export_xls_btn)
        
        self.export_pdf_btn = QPushButton("Export to PDF")
        self.export_pdf_btn.setProperty("class", "SecondaryButton")
        self.export_pdf_btn.clicked.connect(lambda: self.on_export("pdf"))
        export_layout.addWidget(self.export_pdf_btn)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        # Disable export buttons initially
        self.toggle_export_buttons(False)
        
        # 4. Display Table
        self.report_table = QTableWidget(0, 0)
        self.report_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.report_table.setSelectionMode(QTableWidget.SingleSelection)
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.report_table)

    def toggle_export_buttons(self, enabled):
        self.export_csv_btn.setEnabled(enabled)
        self.export_xls_btn.setEnabled(enabled)
        self.export_pdf_btn.setEnabled(enabled)

    def on_generate_report(self):
        template = self.report_type_combo.currentText()
        self.current_rows.clear()
        
        try:
            if template == "Customer List":
                self.current_headers = ["Code", "Name", "Mobile 1", "Mobile 2", "Category", "Age Group", "Gender", "Created Date"]
                customers = database.get_all_customers()
                for c in customers:
                    self.current_rows.append([
                        c.get('customer_code', ''),
                        c.get('name', ''),
                        c.get('mobile1', ''),
                        c.get('mobile2') or '',
                        c.get('category', ''),
                        c.get('age_group') or '',
                        c.get('gender') or '',
                        c.get('created_at', '')
                    ])
                    
            elif template == "Category Wise Summary":
                self.current_headers = ["Customer Category", "Count"]
                data = database.get_category_report_data()
                for r in data:
                    self.current_rows.append([r.get('category') or 'Uncategorized', r.get('count', 0)])
                    
            elif template == "Age Group Summary":
                self.current_headers = ["Age Group", "Count"]
                data = database.get_age_group_report_data()
                for r in data:
                    self.current_rows.append([r.get('age_group') or 'Uncategorized', r.get('count', 0)])
                    
            elif template == "Gender Summary":
                self.current_headers = ["Gender", "Count"]
                data = database.get_gender_report_data()
                for r in data:
                    self.current_rows.append([r.get('gender') or 'Unspecified', r.get('count', 0)])
                    
            elif template == "Recent Customers (Last 30 Days)":
                self.current_headers = ["Code", "Name", "Mobile", "Category", "Created Date"]
                # For summary, grab all but filter dynamically in python
                customers = database.get_all_customers()
                for c in customers:
                    try:
                        created_dt = datetime.strptime(c['created_at'], "%Y-%m-%d %H:%M:%S")
                        delta = datetime.now() - created_dt
                        if delta.days <= 30:
                            self.current_rows.append([
                                c.get('customer_code', ''),
                                c.get('name', ''),
                                c.get('mobile1', ''),
                                c.get('category', ''),
                                c.get('created_at', '')
                            ])
                    except Exception:
                        # Fallback: include all in recent list if date parsing fails
                        self.current_rows.append([
                            c.get('customer_code', ''),
                            c.get('name', ''),
                            c.get('mobile1', ''),
                            c.get('category', ''),
                            c.get('created_at', '')
                        ])
                        
            elif template == "Document Attachment Registry":
                self.current_headers = ["File Name", "File Type", "Remarks", "Attached To (Code)", "Uploaded Date"]
                data = database.get_document_report_data()
                for r in data:
                    self.current_rows.append([
                        r.get('filename', ''),
                        r.get('file_type', ''),
                        r.get('remarks') or '',
                        f"{r.get('customer_name')} ({r.get('customer_code')})",
                        r.get('created_at', '')
                    ])
            
            # Update GUI Table
            self.report_table.setColumnCount(len(self.current_headers))
            self.report_table.setHorizontalHeaderLabels(self.current_headers)
            self.report_table.setRowCount(len(self.current_rows))
            
            for row_idx, row_data in enumerate(self.current_rows):
                for col_idx, cell_data in enumerate(row_data):
                    self.report_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
            
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            # Make the last column fill the remaining space
            if len(self.current_headers) > 0:
                self.report_table.horizontalHeader().setSectionResizeMode(len(self.current_headers) - 1, QHeaderView.Stretch)
                
            self.toggle_export_buttons(len(self.current_rows) > 0)
            
            if self.main_window:
                self.main_window.statusBar().showMessage(f"Generated {template} with {len(self.current_rows)} records.", 3000)
                
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"Could not compile report data: {e}")

    def on_export(self, fmt):
        if not self.current_rows:
            return
            
        template_name = self.report_type_combo.currentText().replace(" ", "_").replace("(", "").replace(")", "").lower()
        
        if fmt == "csv":
            filepath, _ = QFileDialog.getSaveFileName(self, "Save CSV Report", f"{template_name}.csv", "CSV Files (*.csv)")
            if filepath:
                success, msg = exporter.export_to_csv(self.current_headers, self.current_rows, filepath)
                self.show_export_feedback(success, msg, filepath)
                
        elif fmt == "excel":
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", f"{template_name}.xls", "Excel Files (*.xls)")
            if filepath:
                success, msg = exporter.export_to_excel(self.current_headers, self.current_rows, filepath)
                self.show_export_feedback(success, msg, filepath)
                
        elif fmt == "pdf":
            filepath, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", f"{template_name}.pdf", "PDF Files (*.pdf)")
            if filepath:
                # Gather company profile information from settings
                company_info = {
                    "company_name": settings_mgr.get("company_name"),
                    "company_address": settings_mgr.get("company_address"),
                    "company_phone": settings_mgr.get("company_phone"),
                    "company_email": settings_mgr.get("company_email")
                }
                
                title = self.report_type_combo.currentText()
                success, msg = exporter.export_to_pdf(title, self.current_headers, self.current_rows, filepath, company_info)
                self.show_export_feedback(success, msg, filepath)

    def show_export_feedback(self, success, msg, path):
        if success:
            QMessageBox.information(self, "Export Success", f"Report successfully saved to:\n{path}")
            database.log_activity("Export Report", f"Exported report to: {os.path.basename(path)}")
        else:
            QMessageBox.critical(self, "Export Failed", f"An error occurred during export:\n{msg}")
from datetime import datetime
