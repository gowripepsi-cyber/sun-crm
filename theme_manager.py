DARK_QSS = """
/* Dark Theme Style Sheet for SUN CRM */
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Main Window Layout */
QMainWindow {
    background-color: #0f172a;
}

/* Sidebar Styling */
QFrame#Sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}

QLabel#SidebarTitle {
    color: #818cf8;
    font-size: 18px;
    font-weight: bold;
    padding: 15px 5px;
    border-bottom: 1px solid #334155;
}

/* Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 6px;
    padding: 12px 16px;
    text-align: left;
    font-weight: 500;
}

QPushButton.NavButton:hover {
    background-color: #334155;
    color: #f8fafc;
}

QPushButton.NavButton:checked {
    background-color: #4f46e5;
    color: #ffffff;
    font-weight: 600;
}

/* Cards (Dashboard KPIs) */
QFrame.KPICard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 15px;
}

QLabel.KPICardTitle {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    font-weight: 600;
}

QLabel.KPICardValue {
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
}

/* Tables */
QTableWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    gridline-color: #334155;
    border-radius: 8px;
    alternate-background-color: #1e293b;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #334155;
}

QTableWidget::item:selected {
    background-color: #4f46e5;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}

/* Inputs and Text Edits */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #6366f1;
}

/* Primary Action Buttons */
QPushButton.PrimaryButton {
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #6366f1;
}

QPushButton.PrimaryButton:pressed {
    background-color: #4338ca;
}

/* Secondary Action Buttons */
QPushButton.SecondaryButton {
    background-color: #334155;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton.SecondaryButton:hover {
    background-color: #475569;
}

QPushButton.SecondaryButton:pressed {
    background-color: #1e293b;
}

/* Danger Action Buttons */
QPushButton.DangerButton {
    background-color: #b91c1c;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: #dc2626;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1e293b;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #334155;
    border-bottom: none;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #ffffff;
    font-weight: bold;
    border-bottom: 1px solid #1e293b;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #cbd5e1;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #0f172a;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background-color: #0f172a;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/* Dialogs */
QDialog {
    background-color: #0f172a;
    border: 1px solid #334155;
}

/* Status Bar */
QStatusBar {
    background-color: #1e293b;
    color: #64748b;
    border-top: 1px solid #334155;
    font-size: 11px;
}

QToolTip {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 4px;
}
"""

LIGHT_QSS = """
/* Light Theme Style Sheet for SUN CRM */
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Main Window Layout */
QMainWindow {
    background-color: #f8fafc;
}

/* Sidebar Styling */
QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QLabel#SidebarTitle {
    color: #4f46e5;
    font-size: 18px;
    font-weight: bold;
    padding: 15px 5px;
    border-bottom: 1px solid #e2e8f0;
}

/* Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #64748b;
    border: none;
    border-radius: 6px;
    padding: 12px 16px;
    text-align: left;
    font-weight: 500;
}

QPushButton.NavButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QPushButton.NavButton:checked {
    background-color: #4f46e5;
    color: #ffffff;
    font-weight: 600;
}

/* Cards (Dashboard KPIs) */
QFrame.KPICard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 15px;
}

QLabel.KPICardTitle {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    font-weight: 600;
}

QLabel.KPICardValue {
    color: #0f172a;
    font-size: 24px;
    font-weight: bold;
}

/* Tables */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    gridline-color: #e2e8f0;
    border-radius: 8px;
    alternate-background-color: #f8fafc;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #e2e8f0;
}

QTableWidget::item:selected {
    background-color: #6366f1;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}

/* Inputs and Text Edits */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    color: #0f172a;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #4f46e5;
}

/* Primary Action Buttons */
QPushButton.PrimaryButton {
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #6366f1;
}

QPushButton.PrimaryButton:pressed {
    background-color: #4338ca;
}

/* Secondary Action Buttons */
QPushButton.SecondaryButton {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton.SecondaryButton:hover {
    background-color: #e2e8f0;
}

QPushButton.SecondaryButton:pressed {
    background-color: #cbd5e1;
}

/* Danger Action Buttons */
QPushButton.DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: #ef4444;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #f8fafc;
    color: #64748b;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #4f46e5;
    font-weight: bold;
    border-bottom: 1px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
    color: #0f172a;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #f8fafc;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Dialogs */
QDialog {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    font-size: 11px;
}

QToolTip {
    background-color: #f1f5f9;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
}
"""

def get_stylesheet(theme_name):
    if theme_name.lower() == "light":
        return LIGHT_QSS
    return DARK_QSS
