"""
Customer Names List CRUD Tab
============================
A dedicated, focused panel for managing the Customer Names List with
full Create, Read, Update, and Delete (CRUD) operations.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QComboBox, QMessageBox, QInputDialog,
    QMenu, QFrame, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction, QColor, QBrush

import database


# ---------------------------------------------------------------------------
# Add Customer Dialog (compact, name-focused)
# ---------------------------------------------------------------------------
class AddCustomerDialog(QDialog):
    """Quick-add dialog for creating a new customer entry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("➕  New Customer Entry")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #818cf8; margin-bottom: 6px;")
        layout.addWidget(title)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full customer name (required)")
        self.name_input.setMinimumHeight(34)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Primary mobile number (required)")
        self.mobile_input.setMinimumHeight(34)

        self.mobile2_input = QLineEdit()
        self.mobile2_input.setPlaceholderText("Alternative mobile (optional)")
        self.mobile2_input.setMinimumHeight(34)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Regular", "VIP", "Prospect", "Inactive"])
        self.category_combo.setMinimumHeight(34)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "Male", "Female", "Other"])
        self.gender_combo.setMinimumHeight(34)

        form.addRow("Customer Name *:", self.name_input)
        form.addRow("Primary Mobile *:", self.mobile_input)
        form.addRow("Alt. Mobile:", self.mobile2_input)
        form.addRow("Category:", self.category_combo)
        form.addRow("Gender:", self.gender_combo)

        layout.addLayout(form)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #334155;")
        layout.addWidget(line)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", "SecondaryButton")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("✓  Save Customer")
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self._validate_and_accept)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

        # Enter key triggers save
        self.name_input.returnPressed.connect(self.mobile_input.setFocus)
        self.mobile_input.returnPressed.connect(self._validate_and_accept)

    def _validate_and_accept(self):
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Customer Name is required.")
            self.name_input.setFocus()
            return
        if not mobile:
            QMessageBox.warning(self, "Validation", "Primary Mobile is required.")
            self.mobile_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "mobile1": self.mobile_input.text().strip(),
            "mobile2": self.mobile2_input.text().strip(),
            "category": self.category_combo.currentText(),
            "gender": self.gender_combo.currentText(),
            "address": "",
            "notes": "",
            "age_group": "",
            "tags": ""
        }


# ---------------------------------------------------------------------------
# Edit Customer Name Dialog
# ---------------------------------------------------------------------------
class EditNameDialog(QDialog):
    """Dialog to quickly edit only the customer name and category."""

    def __init__(self, parent=None, name="", category="Regular", mobile1="", mobile2="", gender=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Customer Details")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(380)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("✏️  Edit Customer")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #818cf8; margin-bottom: 4px;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit(name)
        self.name_input.setMinimumHeight(34)

        self.mobile1_input = QLineEdit(mobile1)
        self.mobile1_input.setMinimumHeight(34)

        self.mobile2_input = QLineEdit(mobile2)
        self.mobile2_input.setMinimumHeight(34)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Regular", "VIP", "Prospect", "Inactive"])
        idx = self.category_combo.findText(category, Qt.MatchExactly)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        self.category_combo.setMinimumHeight(34)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "Male", "Female", "Other"])
        gidx = self.gender_combo.findText(gender, Qt.MatchExactly)
        if gidx >= 0:
            self.gender_combo.setCurrentIndex(gidx)
        self.gender_combo.setMinimumHeight(34)

        form.addRow("Name *:", self.name_input)
        form.addRow("Mobile 1 *:", self.mobile1_input)
        form.addRow("Mobile 2:", self.mobile2_input)
        form.addRow("Category:", self.category_combo)
        form.addRow("Gender:", self.gender_combo)

        layout.addLayout(form)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #334155;")
        layout.addWidget(line)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "SecondaryButton")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("✓  Save Changes")
        save_btn.setProperty("class", "PrimaryButton")
        save_btn.setMinimumHeight(36)
        save_btn.clicked.connect(self._validate_and_accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Customer Name cannot be empty.")
            self.name_input.setFocus()
            return
        if not self.mobile1_input.text().strip():
            QMessageBox.warning(self, "Validation", "Primary Mobile is required.")
            self.mobile1_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "mobile1": self.mobile1_input.text().strip(),
            "mobile2": self.mobile2_input.text().strip(),
            "category": self.category_combo.currentText(),
            "gender": self.gender_combo.currentText(),
        }


# ---------------------------------------------------------------------------
# Customer Names List CRUD Tab
# ---------------------------------------------------------------------------
class CustomerNamesListTab(QWidget):
    """
    Dedicated CRUD panel for the Customer Names List.
    Emits `open_customer_profile` signal when user double-clicks a row
    so MainWindow can navigate to the full Customer profile tab.
    """

    # Signal: emit customer_id to open in the full Customer tab
    open_customer_profile = Signal(int)

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._all_customers = []   # cache for filter
        self._init_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ── Header ──────────────────────────────────────────────────────
        header_row = QHBoxLayout()

        title_lbl = QLabel("👥  Customer Names List")
        title_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_row.addWidget(title_lbl)
        header_row.addStretch()

        self.total_lbl = QLabel("Total: 0")
        self.total_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
        header_row.addWidget(self.total_lbl)
        root.addLayout(header_row)

        subtitle = QLabel("Manage your complete customer directory. Add, edit, rename or remove customer records.")
        subtitle.setStyleSheet("color: #64748b; font-size: 11px;")
        root.addWidget(subtitle)

        # ── Toolbar ─────────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search by name, code, mobile or category…")
        self.search_box.setMinimumHeight(36)
        self.search_box.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.search_box, stretch=1)

        self.add_btn = QPushButton("➕  Add Customer")
        self.add_btn.setProperty("class", "PrimaryButton")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.setToolTip("Create a new customer record")
        self.add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️  Edit")
        self.edit_btn.setProperty("class", "SecondaryButton")
        self.edit_btn.setMinimumHeight(36)
        self.edit_btn.setToolTip("Edit selected customer's name / details")
        self.edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑  Delete")
        self.delete_btn.setProperty("class", "DangerButton")
        self.delete_btn.setMinimumHeight(36)
        self.delete_btn.setToolTip("Permanently delete selected customer")
        self.delete_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton("🔄  Refresh")
        self.refresh_btn.setProperty("class", "SecondaryButton")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setToolTip("Reload customer list from database")
        self.refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self.refresh_btn)

        root.addLayout(toolbar)

        # ── Info strip ──────────────────────────────────────────────────
        info_strip = QLabel("💡  Double-click a row to open the full customer profile.  Right-click for quick actions.")
        info_strip.setStyleSheet(
            "background-color: #1e3a5f; color: #93c5fd; border-radius: 6px; "
            "padding: 6px 12px; font-size: 11px;"
        )
        root.addWidget(info_strip)

        # ── Table ───────────────────────────────────────────────────────
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "#", "Customer Code", "Full Name", "Mobile", "Category"
        ])
        self.table.setColumnHidden(0, True)   # hide DB id

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)   # row number
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # code
        hh.setSectionResizeMode(3, QHeaderView.Stretch)             # name
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # mobile
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # category

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSortingEnabled(True)

        # Interactions
        self.table.doubleClicked.connect(self._on_open_profile)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Row height
        self.table.verticalHeader().setDefaultSectionSize(36)

        root.addWidget(self.table, stretch=1)

        # ── Footer stats row ────────────────────────────────────────────
        footer = QHBoxLayout()

        self._stat_regular = self._make_stat_badge("Regular", "#10b981")
        self._stat_vip      = self._make_stat_badge("VIP",     "#f59e0b")
        self._stat_prospect = self._make_stat_badge("Prospect","#818cf8")
        self._stat_inactive = self._make_stat_badge("Inactive","#64748b")

        for w in (self._stat_regular, self._stat_vip, self._stat_prospect, self._stat_inactive):
            footer.addWidget(w)

        footer.addStretch()
        root.addLayout(footer)

    def _make_stat_badge(self, label: str, color: str) -> QLabel:
        lbl = QLabel(f"● {label}: 0")
        lbl.setStyleSheet(
            f"color: {color}; background-color: transparent; "
            f"font-size: 11px; font-weight: 600; padding: 4px 8px;"
        )
        return lbl

    # ------------------------------------------------------------------
    # Data Operations
    # ------------------------------------------------------------------
    def refresh(self):
        """Reload from database and rebuild table."""
        self._all_customers = database.get_all_customers()
        self._apply_filter(self.search_box.text() if hasattr(self, "search_box") else "")
        self._update_stat_badges()

    def _apply_filter(self, text: str):
        """Filter _all_customers by search text and rebuild table rows."""
        text = text.strip().lower()
        if text:
            filtered = [
                c for c in self._all_customers
                if (text in (c.get("name") or "").lower()
                    or text in (c.get("customer_code") or "").lower()
                    or text in (c.get("mobile1") or "").lower()
                    or text in (c.get("mobile2") or "").lower()
                    or text in (c.get("category") or "").lower())
            ]
        else:
            filtered = list(self._all_customers)

        self._populate_table(filtered)
        self.total_lbl.setText(f"Showing {len(filtered)} of {len(self._all_customers)}")

    def _populate_table(self, customers):
        """Fill the QTableWidget with given customer list."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        CATEGORY_COLORS = {
            "VIP":      "#f59e0b",
            "Prospect": "#818cf8",
            "Inactive": "#64748b",
            "Regular":  "#10b981",
        }

        for row_idx, c in enumerate(customers):
            self.table.insertRow(row_idx)

            # Hidden ID
            id_item = QTableWidgetItem(str(c["id"]))
            self.table.setItem(row_idx, 0, id_item)

            # Row number (1-based)
            num_item = QTableWidgetItem(str(row_idx + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, num_item)

            # Code
            code_item = QTableWidgetItem(c.get("customer_code", ""))
            code_item.setForeground(QBrush(QColor("#818cf8")))
            self.table.setItem(row_idx, 2, code_item)

            # Name (bold)
            name_item = QTableWidgetItem(c.get("name", ""))
            font = QFont("Segoe UI", 10, QFont.Bold)
            name_item.setFont(font)
            self.table.setItem(row_idx, 3, name_item)

            # Mobile
            mobile = c.get("mobile1", "") or ""
            if c.get("mobile2"):
                mobile += f"  /  {c['mobile2']}"
            mob_item = QTableWidgetItem(mobile)
            self.table.setItem(row_idx, 4, mob_item)

            # Category (color-coded)
            cat = c.get("category") or "Regular"
            cat_item = QTableWidgetItem(cat)
            cat_item.setTextAlignment(Qt.AlignCenter)
            color = CATEGORY_COLORS.get(cat, "#94a3b8")
            cat_item.setForeground(QBrush(QColor(color)))
            cat_font = QFont("Segoe UI", 9, QFont.Bold)
            cat_item.setFont(cat_font)
            self.table.setItem(row_idx, 5, cat_item)

        self.table.setSortingEnabled(True)

    def _update_stat_badges(self):
        counts = {"Regular": 0, "VIP": 0, "Prospect": 0, "Inactive": 0}
        for c in self._all_customers:
            cat = c.get("category") or "Regular"
            if cat in counts:
                counts[cat] += 1
            else:
                counts["Regular"] += 1

        self._stat_regular.setText(f"● Regular: {counts['Regular']}")
        self._stat_vip.setText(f"● VIP: {counts['VIP']}")
        self._stat_prospect.setText(f"● Prospect: {counts['Prospect']}")
        self._stat_inactive.setText(f"● Inactive: {counts['Inactive']}")

    # ------------------------------------------------------------------
    # CRUD Actions
    # ------------------------------------------------------------------
    def _on_add(self):
        """Open Add Customer dialog and insert into DB."""
        dlg = AddCustomerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                cust_id, code = database.add_customer(data)
                self.refresh()
                # Scroll to and highlight new entry
                self._select_row_by_id(cust_id)
                if self.main_window:
                    self.main_window.statusBar().showMessage(
                        f"✅  Customer '{data['name']}' added — Code: {code}", 4000
                    )
                QMessageBox.information(
                    self, "Customer Added",
                    f"Customer <b>{data['name']}</b> created successfully!<br>"
                    f"Customer Code: <b>{code}</b>"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add customer:\n{e}")

    def _on_edit(self):
        """Open Edit dialog for selected row."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a customer row to edit.")
            return
        self._edit_row(row)

    def _edit_row(self, row: int):
        """Edit the customer in the given table row."""
        cust_id = int(self.table.item(row, 0).text())
        cust = database.get_customer(cust_id)
        if not cust:
            QMessageBox.warning(self, "Error", "Customer record not found.")
            return

        dlg = EditNameDialog(
            self,
            name=cust.get("name", ""),
            category=cust.get("category", "Regular"),
            mobile1=cust.get("mobile1", ""),
            mobile2=cust.get("mobile2", "") or "",
            gender=cust.get("gender", "") or ""
        )
        if dlg.exec() == QDialog.Accepted:
            changes = dlg.get_data()
            # Merge with full existing data so we don't wipe other fields
            update_data = {
                "name":     changes["name"],
                "mobile1":  changes["mobile1"],
                "mobile2":  changes["mobile2"],
                "category": changes["category"],
                "gender":   changes["gender"],
                "address":  cust.get("address", "") or "",
                "notes":    cust.get("notes", "") or "",
                "age_group":cust.get("age_group", "") or "",
                "tags":     cust.get("tags", "") or "",
            }
            try:
                database.update_customer(cust_id, update_data)
                self.refresh()
                self._select_row_by_id(cust_id)
                if self.main_window:
                    self.main_window.statusBar().showMessage(
                        f"✅  Customer '{changes['name']}' updated.", 3000
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update customer:\n{e}")

    def _on_delete(self):
        """Delete selected customer with confirmation."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a customer row to delete.")
            return
        self._delete_row(row)

    def _delete_row(self, row: int):
        cust_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 3).text()
        code = self.table.item(row, 2).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to <b>permanently delete</b> this customer?<br><br>"
            f"<b>Name:</b> {name}<br>"
            f"<b>Code:</b> {code}<br><br>"
            f"⚠️ All credentials, custom fields and documents will be removed.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            # Remove physical document files first
            import os
            docs = database.get_customer_documents(cust_id)
            for d in docs:
                fp = d.get("file_path")
                if fp and os.path.exists(fp):
                    try:
                        os.remove(fp)
                    except Exception as fe:
                        print(f"Could not delete file {fp}: {fe}")

            database.delete_customer(cust_id)
            self.refresh()
            if self.main_window:
                self.main_window.statusBar().showMessage(
                    f"🗑  Customer '{name}' deleted.", 3000
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete customer:\n{e}")

    def _on_open_profile(self):
        """Navigate to the full Customer tab for the double-clicked row."""
        row = self.table.currentRow()
        if row < 0:
            return
        cust_id = int(self.table.item(row, 0).text())
        self.open_customer_profile.emit(cust_id)

    # ------------------------------------------------------------------
    # Context Menu
    # ------------------------------------------------------------------
    def _show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        self.table.selectRow(row)
        name = self.table.item(row, 3).text()

        menu = QMenu(self)

        act_open = QAction(f"👁  Open Full Profile — {name}", self)
        act_open.triggered.connect(self._on_open_profile)

        act_edit = QAction("✏️  Edit Customer Details", self)
        act_edit.triggered.connect(lambda: self._edit_row(row))

        act_rename = QAction("🔤  Rename (Name Only)", self)
        act_rename.triggered.connect(lambda: self._quick_rename(row))

        act_del = QAction("🗑  Delete Customer", self)
        act_del.triggered.connect(lambda: self._delete_row(row))

        menu.addAction(act_open)
        menu.addSeparator()
        menu.addAction(act_edit)
        menu.addAction(act_rename)
        menu.addSeparator()
        menu.addAction(act_del)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _quick_rename(self, row: int):
        """Inline quick rename — only changes the customer's name."""
        cust_id = int(self.table.item(row, 0).text())
        current_name = self.table.item(row, 3).text()

        new_name, ok = QInputDialog.getText(
            self, "Rename Customer",
            "Enter the new customer name:",
            text=current_name
        )
        if not ok or not new_name.strip():
            return

        cust = database.get_customer(cust_id)
        if not cust:
            return

        update_data = {
            "name":     new_name.strip(),
            "mobile1":  cust.get("mobile1", ""),
            "mobile2":  cust.get("mobile2", "") or "",
            "address":  cust.get("address", "") or "",
            "notes":    cust.get("notes", "") or "",
            "age_group":cust.get("age_group", "") or "",
            "gender":   cust.get("gender", "") or "",
            "category": cust.get("category", "Regular") or "Regular",
            "tags":     cust.get("tags", "") or "",
        }
        try:
            database.update_customer(cust_id, update_data)
            self.refresh()
            self._select_row_by_id(cust_id)
            if self.main_window:
                self.main_window.statusBar().showMessage(
                    f"✅  Customer renamed to '{new_name.strip()}'.", 3000
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Rename failed:\n{e}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _select_row_by_id(self, cust_id: int):
        """Select the table row matching the given customer ID."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == cust_id:
                self.table.selectRow(row)
                self.table.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                break
