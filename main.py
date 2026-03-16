"""
ReadIt — Free PDF Reader
Native Python desktop app using PyQt6 + PyMuPDF.
No subscriptions. No paywalls. Ever.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                              QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QToolBar, QSpinBox,
                              QComboBox, QFileDialog, QStatusBar,
                              QProgressBar, QSizePolicy)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import (QAction, QIcon, QKeySequence, QFont,
                          QDragEnterEvent, QDropEvent, QPalette, QColor)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

from pdf_viewer import PDFViewer
from sidebar import Sidebar
from search_bar import SearchBar
from theme import DARK_THEME, LIGHT_THEME


class WelcomeWidget(QWidget):
    """Welcome screen shown when no PDF is open."""

    file_requested = None  # will be set to a callback

    def __init__(self, open_callback, parent=None):
        super().__init__(parent)
        self.file_requested = open_callback
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Logo / Title
        title = QLabel("ReadIt")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        title.setStyleSheet("color: #7c3aed;")
        layout.addWidget(title)

        subtitle = QLabel("Your free, premium PDF reader. No fees. Ever.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #808099;")
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # Drop zone hint
        drop_label = QLabel("Drag & drop a PDF here")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_label.setFont(QFont("Segoe UI", 13))
        drop_label.setStyleSheet("""
            color: #606080;
            border: 2px dashed #3a3a60;
            border-radius: 16px;
            padding: 40px 60px;
        """)
        layout.addWidget(drop_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(8)

        or_label = QLabel("or")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_label.setStyleSheet("color: #505070;")
        layout.addWidget(or_label)

        layout.addSpacing(8)

        # Browse button
        btn_open = QPushButton("  Browse Files")
        btn_open.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setFixedSize(200, 48)
        btn_open.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c3aed, stop:1 #06b6d4);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6d28d9, stop:1 #0891b2);
            }
        """)
        btn_open.clicked.connect(self.file_requested)
        layout.addWidget(btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(30)

        footer = QLabel("100% offline • No uploads • Your files stay private")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #505070; font-size: 11px;")
        layout.addWidget(footer)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.lower().endswith('.pdf'):
                self.parent().parent().open_file(filepath)
                return


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReadIt — PDF Reader")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        self.setAcceptDrops(True)

        # Settings
        self.settings = QSettings("ReadIt", "PDFReader")
        self.is_dark = self.settings.value("dark_mode", True, type=bool)

        # Core widgets
        self.viewer = PDFViewer()
        self.sidebar = Sidebar()
        self.search_bar = SearchBar()

        # Welcome screen
        self.welcome = WelcomeWidget(self.open_file_dialog)

        # Setup UI
        self._setup_central_widget()
        self._setup_toolbar()
        self._setup_sidebar()
        self._setup_search_bar()
        self._setup_statusbar()
        self._setup_shortcuts()
        self._connect_signals()

        # Apply theme
        self._apply_theme()

        # Show welcome screen initially
        self._show_welcome()

        # Restore window geometry
        geom = self.settings.value("geometry")
        if geom:
            self.restoreGeometry(geom)

    def _setup_central_widget(self):
        """Stack the welcome screen and viewer."""
        central = QWidget()
        self._central_layout = QVBoxLayout(central)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)

        # Search bar goes at top
        self._central_layout.addWidget(self.search_bar)

        # Viewer
        self._central_layout.addWidget(self.viewer)
        self._central_layout.addWidget(self.welcome)

        self.setCentralWidget(central)

    def _setup_toolbar(self):
        """Create the main toolbar."""
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)

        # Open
        self.act_open = QAction("📂 Open", self)
        self.act_open.setToolTip("Open PDF (Ctrl+O)")
        self.act_open.triggered.connect(self.open_file_dialog)
        tb.addAction(self.act_open)

        tb.addSeparator()

        # Navigation
        self.act_prev = QAction("◀", self)
        self.act_prev.setToolTip("Previous Page (←)")
        self.act_prev.setEnabled(False)
        self.act_prev.triggered.connect(self._prev_page)
        tb.addAction(self.act_prev)

        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(1)
        self.page_spinbox.setFixedWidth(60)
        self.page_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_spinbox.valueChanged.connect(self._on_page_spin)
        tb.addWidget(self.page_spinbox)

        self.page_count_label = QLabel(" / 0  ")
        self.page_count_label.setStyleSheet("font-size: 12px;")
        tb.addWidget(self.page_count_label)

        self.act_next = QAction("▶", self)
        self.act_next.setToolTip("Next Page (→)")
        self.act_next.setEnabled(False)
        self.act_next.triggered.connect(self._next_page)
        tb.addAction(self.act_next)

        tb.addSeparator()

        # Zoom
        self.act_zoom_out = QAction("➖", self)
        self.act_zoom_out.setToolTip("Zoom Out (Ctrl+-)")
        self.act_zoom_out.triggered.connect(self.viewer.zoom_out)
        tb.addAction(self.act_zoom_out)

        self.zoom_label = QLabel(" 100% ")
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setStyleSheet("font-size: 12px; font-weight: 500;")
        tb.addWidget(self.zoom_label)

        self.act_zoom_in = QAction("➕", self)
        self.act_zoom_in.setToolTip("Zoom In (Ctrl++)")
        self.act_zoom_in.triggered.connect(self.viewer.zoom_in)
        tb.addAction(self.act_zoom_in)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%",
                                   "Fit Width", "Fit Page"])
        self.zoom_combo.setCurrentText("Fit Page")
        self.zoom_combo.setFixedWidth(100)
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_combo)
        tb.addWidget(self.zoom_combo)

        tb.addSeparator()

        # Tools
        from PyQt6.QtGui import QActionGroup
        self.tool_group = QActionGroup(self)
        
        self.act_hand = QAction("✋ Hand", self)
        self.act_hand.setCheckable(True)
        self.act_hand.setChecked(True)
        self.act_hand.triggered.connect(lambda: self.viewer.set_tool("Hand"))
        self.tool_group.addAction(self.act_hand)
        tb.addAction(self.act_hand)

        self.act_select = QAction("🔤 Select", self)
        self.act_select.setCheckable(True)
        self.act_select.triggered.connect(lambda: self.viewer.set_tool("Select"))
        self.tool_group.addAction(self.act_select)
        tb.addAction(self.act_select)

        self.act_highlight = QAction("🖍️ Highlight", self)
        self.act_highlight.setCheckable(True)
        self.act_highlight.triggered.connect(lambda: self.viewer.set_tool("Highlight"))
        self.tool_group.addAction(self.act_highlight)
        tb.addAction(self.act_highlight)

        self.act_eraser = QAction("🧹 Eraser", self)
        self.act_eraser.setCheckable(True)
        self.act_eraser.triggered.connect(lambda: self.viewer.set_tool("Eraser"))
        self.tool_group.addAction(self.act_eraser)
        tb.addAction(self.act_eraser)

        tb.addSeparator()

        self.act_save = QAction("💾 Save", self)
        self.act_save.setToolTip("Save Changes (Ctrl+S)")
        self.act_save.setEnabled(False)
        self.act_save.triggered.connect(self._save_changes)
        tb.addAction(self.act_save)

        tb.addSeparator()

        # Right side actions
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self.act_search = QAction("🔍 Search", self)
        self.act_search.setToolTip("Search (Ctrl+F)")
        self.act_search.triggered.connect(self.search_bar.toggle)
        tb.addAction(self.act_search)

        self.act_print = QAction("🖨️ Print", self)
        self.act_print.setToolTip("Print (Ctrl+P)")
        self.act_print.triggered.connect(self._print)
        tb.addAction(self.act_print)

        self.act_fullscreen = QAction("⛶ Fullscreen", self)
        self.act_fullscreen.setToolTip("Fullscreen (F11)")
        self.act_fullscreen.triggered.connect(self._toggle_fullscreen)
        tb.addAction(self.act_fullscreen)

        self.act_theme = QAction("🌙 Theme", self)
        self.act_theme.setToolTip("Toggle Dark/Light Mode")
        self.act_theme.triggered.connect(self._toggle_theme)
        tb.addAction(self.act_theme)

        # Sidebar toggle
        self.act_sidebar = QAction("📑 Sidebar", self)
        self.act_sidebar.setToolTip("Toggle Sidebar (T)")
        self.act_sidebar.triggered.connect(self._toggle_sidebar)
        tb.addAction(self.act_sidebar)

    def _setup_sidebar(self):
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        self.sidebar.setVisible(False)

    def _setup_search_bar(self):
        self.search_bar.search_requested.connect(self._on_search)
        self.search_bar.next_match.connect(self._on_next_match)
        self.search_bar.prev_match.connect(self._on_prev_match)
        self.search_bar.closed.connect(self.viewer.clear_search)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def _setup_shortcuts(self):
        """Bind keyboard shortcuts."""
        from PyQt6.QtGui import QShortcut

        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_file_dialog)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.search_bar.toggle)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self._print)
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(self.viewer.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(self.viewer.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(self.viewer.zoom_out)
        QShortcut(QKeySequence("Left"), self).activated.connect(self._prev_page)
        QShortcut(QKeySequence("Right"), self).activated.connect(self._next_page)
        QShortcut(QKeySequence("Home"), self).activated.connect(lambda: self.viewer.go_to_page(0))
        QShortcut(QKeySequence("End"), self).activated.connect(
            lambda: self.viewer.go_to_page(self.viewer.total_pages - 1) if self.viewer.total_pages else None)
        QShortcut(QKeySequence("F11"), self).activated.connect(self._toggle_fullscreen)
        QShortcut(QKeySequence("T"), self).activated.connect(self._toggle_sidebar)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.search_bar.close_search)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_changes)

    def _connect_signals(self):
        """Wire up signals between components."""
        self.viewer.page_changed.connect(self._on_page_changed)
        self.viewer.zoom_changed.connect(self._on_zoom_changed)
        self.viewer.unsaved_changes_state_changed.connect(self._on_unsaved_changes)
        self.sidebar.page_clicked.connect(self.viewer.go_to_page)

    def _on_unsaved_changes(self, has_unsaved):
        self.act_save.setEnabled(has_unsaved)
        title = self.windowTitle()
        if has_unsaved and not title.endswith("*"):
            self.setWindowTitle(title + "*")
        elif not has_unsaved and title.endswith("*"):
            self.setWindowTitle(title[:-1])

    def _save_changes(self):
        self.viewer.save_changes()
        self.status_label.setText("Changes saved")

    # ========== FILE HANDLING ==========

    def open_file_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if filepath:
            self.open_file(filepath)

    def open_file(self, filepath):
        """Open a PDF file."""
        self.status_label.setText(f"Loading {os.path.basename(filepath)}...")
        QApplication.processEvents()

        try:
            self.viewer.open_document(filepath)
            self.sidebar.load_document(self.viewer.doc)

            # Update UI
            total = self.viewer.total_pages
            self.page_spinbox.setMaximum(total)
            self.page_spinbox.setValue(1)
            self.page_count_label.setText(f" / {total}  ")
            self.act_prev.setEnabled(True)
            self.act_next.setEnabled(True)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(1)

            self.setWindowTitle(f"{os.path.basename(filepath)} — ReadIt")
            self.status_label.setText(f"Loaded — {total} pages")

            self._show_viewer()

        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def _show_welcome(self):
        self.viewer.setVisible(False)
        self.welcome.setVisible(True)
        self.sidebar.setVisible(False)

    def _show_viewer(self):
        self.welcome.setVisible(False)
        self.viewer.setVisible(True)
        self.sidebar.setVisible(True)

    # ========== PAGE NAVIGATION ==========

    def _prev_page(self):
        self.viewer.prev_page()

    def _next_page(self):
        self.viewer.next_page()

    def _on_page_spin(self, val):
        self.viewer.go_to_page(val - 1)  # spinbox is 1-indexed

    def _on_page_changed(self, page_num):
        """Called when the viewer's current page changes."""
        self.page_spinbox.blockSignals(True)
        self.page_spinbox.setValue(page_num + 1)
        self.page_spinbox.blockSignals(False)
        self.sidebar.set_current_page(page_num)
        self.progress_bar.setValue(page_num + 1)
        self.act_prev.setEnabled(page_num > 0)
        self.act_next.setEnabled(page_num < self.viewer.total_pages - 1)

    # ========== ZOOM ==========

    def _on_zoom_changed(self, scale):
        self.zoom_label.setText(f" {int(scale * 100)}% ")

    def _on_zoom_combo(self, text):
        if text == "Fit Width":
            self.viewer.fit_width()
        elif text == "Fit Page":
            self.viewer.fit_page()
        else:
            try:
                val = int(text.replace("%", ""))
                self.viewer.set_zoom(val / 100)
            except ValueError:
                pass

    # ========== SEARCH ==========

    def _on_search(self, query):
        total = self.viewer.search(query)
        if total > 0:
            self.search_bar.update_match_count(0, total)
        else:
            self.search_bar.update_match_count(0, 0)

    def _on_next_match(self):
        idx, total = self.viewer.next_search_match()
        self.search_bar.update_match_count(idx, total)

    def _on_prev_match(self):
        idx, total = self.viewer.prev_search_match()
        self.search_bar.update_match_count(idx, total)

    # ========== THEME ==========

    def _toggle_theme(self):
        self.is_dark = not self.is_dark
        self._apply_theme()
        self.settings.setValue("dark_mode", self.is_dark)
        self.act_theme.setText("☀️ Theme" if self.is_dark else "🌙 Theme")

    def _apply_theme(self):
        qss = DARK_THEME if self.is_dark else LIGHT_THEME
        QApplication.instance().setStyleSheet(qss)

    # ========== FULLSCREEN ==========

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # ========== SIDEBAR ==========

    def _toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    # ========== PRINT ==========

    def _print(self):
        if not self.viewer.doc:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            from PyQt6.QtGui import QPainter
            import fitz
            painter = QPainter(printer)
            for i in range(len(self.viewer.doc)):
                if i > 0:
                    printer.newPage()
                page = self.viewer.doc[i]
                # Render at high DPI
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
                from PyQt6.QtGui import QImage
                img = QImage(pix.samples, pix.width, pix.height,
                             pix.stride, QImage.Format.Format_RGB888)
                rect = painter.viewport()
                img_scaled = img.scaled(rect.size(),
                                         Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
                painter.drawImage(0, 0, img_scaled)
            painter.end()

    # ========== DRAG & DROP ==========

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.lower().endswith('.pdf'):
                self.open_file(filepath)
                return

    # ========== CLEANUP ==========

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.sidebar.cleanup()
        self.viewer.cleanup()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ReadIt")
    app.setOrganizationName("ReadIt")

    window = MainWindow()
    window.show()

    # Open file from command line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.isfile(filepath) and filepath.lower().endswith('.pdf'):
            window.open_file(filepath)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
