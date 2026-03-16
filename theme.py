"""
ReadIt — Theme Module
Dark/Light QSS stylesheets for native look.
"""

DARK_THEME = """
/* ========== GLOBAL ========== */
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #e0e0ef;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}

/* ========== MENU BAR ========== */
QMenuBar {
    background-color: #12121f;
    color: #c0c0d5;
    border-bottom: 1px solid #2a2a44;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #2a2a50;
    border-radius: 4px;
}
QMenu {
    background-color: #1a1a30;
    color: #d0d0e5;
    border: 1px solid #2a2a44;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item:selected {
    background-color: #7c3aed;
    border-radius: 4px;
}
QMenu::separator {
    height: 1px;
    background: #2a2a44;
    margin: 4px 8px;
}

/* ========== TOOLBAR ========== */
QToolBar {
    background-color: #12121f;
    border-bottom: 1px solid #2a2a44;
    spacing: 4px;
    padding: 4px 8px;
}
QToolBar::separator {
    width: 1px;
    background: #2a2a44;
    margin: 4px 6px;
}
QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px;
    color: #a0a0c0;
}
QToolButton:hover {
    background-color: #2a2a50;
    color: #e0e0ef;
}
QToolButton:pressed {
    background-color: #3a3a60;
}
QToolButton:disabled {
    color: #404060;
}

/* ========== SPINBOX / COMBOBOX ========== */
QSpinBox, QComboBox {
    background-color: #22223a;
    border: 1px solid #2a2a44;
    border-radius: 6px;
    padding: 4px 8px;
    color: #d0d0e5;
    min-height: 24px;
}
QSpinBox:focus, QComboBox:focus {
    border-color: #7c3aed;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 18px;
    border: none;
    background: transparent;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #1a1a30;
    color: #d0d0e5;
    border: 1px solid #2a2a44;
    border-radius: 6px;
    selection-background-color: #7c3aed;
}

/* ========== SCROLLBAR ========== */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a3a60;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #5a5a80;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #3a3a60;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #5a5a80;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}

/* ========== DOCK WIDGET (SIDEBAR) ========== */
QDockWidget {
    color: #a0a0c0;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}
QDockWidget::title {
    background-color: #12121f;
    padding: 8px;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
    border-bottom: 1px solid #2a2a44;
}

/* ========== LIST WIDGET (THUMBNAILS) ========== */
QListWidget {
    background-color: #16162a;
    border: none;
    outline: none;
}
QListWidget::item {
    padding: 8px;
    border-radius: 6px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: rgba(124, 58, 237, 0.2);
    border: 2px solid #7c3aed;
}
QListWidget::item:hover:!selected {
    background-color: #22223a;
}

/* ========== LABELS ========== */
QLabel {
    color: #d0d0e5;
}

/* ========== LINE EDIT (SEARCH) ========== */
QLineEdit {
    background-color: #22223a;
    border: 1px solid #2a2a44;
    border-radius: 8px;
    padding: 6px 12px;
    color: #e0e0ef;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #7c3aed;
}

/* ========== PUSH BUTTON ========== */
QPushButton {
    background-color: #22223a;
    border: 1px solid #2a2a44;
    border-radius: 6px;
    padding: 6px 12px;
    color: #c0c0d5;
}
QPushButton:hover {
    background-color: #2a2a50;
    border-color: #7c3aed;
    color: #e0e0ef;
}
QPushButton:pressed {
    background-color: #3a3a60;
}

/* ========== STATUS BAR ========== */
QStatusBar {
    background-color: #12121f;
    color: #808099;
    border-top: 1px solid #2a2a44;
    font-size: 11px;
}

/* ========== PROGRESS BAR ========== */
QProgressBar {
    background-color: #22223a;
    border: none;
    border-radius: 2px;
    height: 3px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #06b6d4);
    border-radius: 2px;
}

/* ========== TOOLTIP ========== */
QToolTip {
    background-color: #1a1a30;
    color: #e0e0ef;
    border: 1px solid #2a2a44;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f5f5fa;
    color: #1a1a2e;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}
QMenuBar {
    background-color: #ffffff;
    color: #3a3a5c;
    border-bottom: 1px solid #e0e0ee;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #e8e8f5;
    border-radius: 4px;
}
QMenu {
    background-color: #ffffff;
    color: #2a2a4a;
    border: 1px solid #d0d0e0;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item:selected {
    background-color: #7c3aed;
    color: white;
    border-radius: 4px;
}
QMenu::separator {
    height: 1px;
    background: #e0e0ee;
    margin: 4px 8px;
}
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0ee;
    spacing: 4px;
    padding: 4px 8px;
}
QToolBar::separator {
    width: 1px;
    background: #e0e0ee;
    margin: 4px 6px;
}
QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px;
    color: #5a5a7a;
}
QToolButton:hover {
    background-color: #e8e8f5;
    color: #1a1a2e;
}
QToolButton:pressed {
    background-color: #d0d0e5;
}
QToolButton:disabled {
    color: #b0b0c5;
}
QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0e0;
    border-radius: 6px;
    padding: 4px 8px;
    color: #2a2a4a;
    min-height: 24px;
}
QSpinBox:focus, QComboBox:focus {
    border-color: #7c3aed;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 18px;
    border: none;
    background: transparent;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #2a2a4a;
    border: 1px solid #d0d0e0;
    selection-background-color: #7c3aed;
    selection-color: white;
}
QScrollBar:vertical {
    background: transparent;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #c0c0d5;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #a0a0b5;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #c0c0d5;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #a0a0b5;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QDockWidget {
    color: #5a5a7a;
}
QDockWidget::title {
    background-color: #ffffff;
    padding: 8px;
    font-weight: bold;
    font-size: 11px;
    border-bottom: 1px solid #e0e0ee;
}
QListWidget {
    background-color: #fafafe;
    border: none;
    outline: none;
}
QListWidget::item {
    padding: 8px;
    border-radius: 6px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: rgba(124, 58, 237, 0.1);
    border: 2px solid #7c3aed;
}
QListWidget::item:hover:!selected {
    background-color: #eeeef5;
}
QLabel { color: #2a2a4a; }
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0e0;
    border-radius: 8px;
    padding: 6px 12px;
    color: #1a1a2e;
}
QLineEdit:focus {
    border-color: #7c3aed;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #d0d0e0;
    border-radius: 6px;
    padding: 6px 12px;
    color: #3a3a5c;
}
QPushButton:hover {
    background-color: #e8e8f5;
    border-color: #7c3aed;
}
QPushButton:pressed {
    background-color: #d0d0e5;
}
QStatusBar {
    background-color: #ffffff;
    color: #8a8aa5;
    border-top: 1px solid #e0e0ee;
    font-size: 11px;
}
QProgressBar {
    background-color: #e0e0ee;
    border: none;
    border-radius: 2px;
    height: 3px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #06b6d4);
    border-radius: 2px;
}
QToolTip {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1px solid #d0d0e0;
    border-radius: 6px;
    padding: 6px 10px;
}
"""
