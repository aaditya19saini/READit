"""
ReadIt — Search Bar Widget
Floating search overlay for finding text in the PDF.
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit,
                              QLabel, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut


class SearchBar(QWidget):
    """Floating search bar widget."""

    search_requested = pyqtSignal(str)
    next_match = pyqtSignal()
    prev_match = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setVisible(False)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in document...")
        self.search_input.setMinimumWidth(250)
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self.next_match.emit)
        layout.addWidget(self.search_input)

        # Match count label
        self.match_label = QLabel("")
        self.match_label.setStyleSheet("color: #808099; font-size: 11px; min-width: 60px;")
        layout.addWidget(self.match_label)

        # Prev button
        btn_prev = QPushButton("▲")
        btn_prev.setFixedSize(28, 28)
        btn_prev.setToolTip("Previous Match (Shift+Enter)")
        btn_prev.clicked.connect(self.prev_match.emit)
        layout.addWidget(btn_prev)

        # Next button
        btn_next = QPushButton("▼")
        btn_next.setFixedSize(28, 28)
        btn_next.setToolTip("Next Match (Enter)")
        btn_next.clicked.connect(self.next_match.emit)
        layout.addWidget(btn_next)

        # Close button
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setToolTip("Close (Esc)")
        btn_close.clicked.connect(self.close_search)
        layout.addWidget(btn_close)

    def _on_text_changed(self, text):
        self.search_requested.emit(text)

    def toggle(self):
        if self.isVisible():
            self.close_search()
        else:
            self.setVisible(True)
            self.search_input.setFocus()
            self.search_input.selectAll()

    def close_search(self):
        self.setVisible(False)
        self.search_input.clear()
        self.match_label.setText("")
        self.closed.emit()

    def update_match_count(self, current, total):
        if total == 0:
            self.match_label.setText("No results")
        else:
            self.match_label.setText(f"{current + 1} of {total}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_search()
        elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            self.prev_match.emit()
        else:
            super().keyPressEvent(event)
