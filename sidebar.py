"""
ReadIt — Thumbnail Sidebar
Renders page thumbnails in a dockable sidebar panel.
"""

from PyQt6.QtWidgets import (QDockWidget, QListWidget, QListWidgetItem,
                              QWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage
import fitz


class ThumbnailRenderer(QThread):
    """Background thread that renders page thumbnails."""
    thumbnail_ready = pyqtSignal(int, QPixmap)  # (page_num, pixmap)

    def __init__(self, doc, thumb_width=180):
        super().__init__()
        self.doc = doc
        self.thumb_width = thumb_width
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        for i in range(len(self.doc)):
            if self._stop:
                return
            try:
                page = self.doc[i]
                # Calculate scale to fit thumb_width
                zoom = self.thumb_width / page.rect.width
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # Convert to QPixmap
                img = QImage(pix.samples, pix.width, pix.height,
                             pix.stride, QImage.Format.Format_RGB888)
                qpixmap = QPixmap.fromImage(img)
                self.thumbnail_ready.emit(i, qpixmap)
            except Exception as e:
                print(f"Thumbnail error page {i}: {e}")


class Sidebar(QDockWidget):
    """Thumbnail sidebar panel."""

    page_clicked = pyqtSignal(int)  # emits 0-indexed page number

    def __init__(self, parent=None):
        super().__init__("Pages", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                             Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                         QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)

        # Thumbnail list
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(170, 240))
        self.list_widget.setSpacing(4)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.currentRowChanged.connect(self._on_item_clicked)
        self.setWidget(self.list_widget)

        self._renderer = None
        self._updating = False

    def load_document(self, doc):
        """Load thumbnails for a new document."""
        self.list_widget.clear()

        # Stop previous renderer if running
        if self._renderer and self._renderer.isRunning():
            self._renderer.stop()
            self._renderer.wait()

        # Add placeholder items
        for i in range(len(doc)):
            item = QListWidgetItem(f"Page {i + 1}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(QSize(190, 260))
            self.list_widget.addItem(item)

        # Start background thumbnail rendering
        self._renderer = ThumbnailRenderer(doc)
        self._renderer.thumbnail_ready.connect(self._on_thumbnail_ready)
        self._renderer.start()

    def _on_thumbnail_ready(self, page_num, pixmap):
        """Slot called when a thumbnail is rendered."""
        if page_num < self.list_widget.count():
            item = self.list_widget.item(page_num)
            from PyQt6.QtGui import QIcon
            item.setIcon(QIcon(pixmap))
            item.setText(str(page_num + 1))

    def _on_item_clicked(self, row):
        if row >= 0 and not self._updating:
            self.page_clicked.emit(row)

    def set_current_page(self, page_num):
        """Highlight the current page's thumbnail (0-indexed)."""
        self._updating = True
        if 0 <= page_num < self.list_widget.count():
            self.list_widget.setCurrentRow(page_num)
        self._updating = False

    def cleanup(self):
        """Stop background thread."""
        if self._renderer and self._renderer.isRunning():
            self._renderer.stop()
            self._renderer.wait()
