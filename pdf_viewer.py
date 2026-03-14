"""
ReadIt — PDF Viewer Widget
Core rendering engine using PyMuPDF (fitz) with lazy page loading.
"""

from PyQt6.QtWidgets import (QScrollArea, QWidget, QVBoxLayout,
                              QLabel, QSizePolicy, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import (QPixmap, QImage, QPainter, QColor,
                          QPen, QBrush, QWheelEvent)
import fitz


class PageWidget(QLabel):
    """Widget displaying a single rendered PDF page."""

    def __init__(self, page_num, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.rendered = False
        self.search_rects = []  # List of fitz.Rect for search highlights
        self.active_match_index = -1
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setScaledContents(False)
        self.setStyleSheet("background-color: #ffffff; border-radius: 2px;")

    def set_page_pixmap(self, pixmap):
        """Set the rendered page image."""
        self.setPixmap(pixmap)
        self.rendered = True

    def set_placeholder(self, width, height):
        """Set a blank placeholder of the correct size."""
        self.setFixedSize(int(width), int(height))
        self.rendered = False

    def set_search_highlights(self, rects, active_index=-1):
        """Set search highlight rectangles and repaint."""
        self.search_rects = rects
        self.active_match_index = active_index
        self.update()

    def clear_highlights(self):
        self.search_rects = []
        self.active_match_index = -1
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.search_rects:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i, rect in enumerate(self.search_rects):
            if i == self.active_match_index:
                painter.setBrush(QBrush(QColor(255, 140, 0, 120)))
                painter.setPen(QPen(QColor(255, 140, 0), 2))
            else:
                painter.setBrush(QBrush(QColor(255, 213, 0, 80)))
                painter.setPen(QPen(QColor(255, 213, 0), 1))
            painter.drawRect(QRect(
                int(rect.x0), int(rect.y0),
                int(rect.width), int(rect.height)
            ))

        painter.end()


class PDFViewer(QScrollArea):
    """Scrollable PDF page viewer with lazy rendering."""

    page_changed = pyqtSignal(int)  # emits current page (0-indexed)
    zoom_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Container for all page widgets
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._layout.setSpacing(16)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self.setWidget(self._container)

        # State
        self.doc = None
        self.scale = 1.0
        self.page_widgets = []
        self._current_page = 0
        self._rendered_pages = set()
        self._search_matches = []  # List of (page_num, [fitz.Rect])
        self._search_index = -1

        # Lazy render timer
        self._render_timer = QTimer()
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(50)
        self._render_timer.timeout.connect(self._render_visible_pages)

        # Scroll tracking
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def _sync_container_size(self):
        """Resize the scroll-area widget to match the stacked page layout."""
        content_size = self._layout.sizeHint()
        self._container.setFixedSize(content_size)
        self._container.updateGeometry()

    def open_document(self, filepath):
        """Open a PDF file and create page placeholders."""
        if self.doc:
            self.doc.close()

        self.doc = fitz.open(filepath)
        self._current_page = 0
        self._rendered_pages.clear()
        self._search_matches.clear()
        self._search_index = -1

        # Set a reasonable initial scale, then create placeholders
        self.scale = 1.5  # default decent scale
        self._create_page_placeholders()
        # Defer auto_fit_page to allow the viewport to settle after becoming visible
        QTimer.singleShot(200, self.auto_fit_page)

    def _create_page_placeholders(self):
        """Create empty placeholder widgets for all pages."""
        # Clear existing
        for w in self.page_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self.page_widgets.clear()
        self._rendered_pages.clear()

        for i in range(len(self.doc)):
            page = self.doc[i]
            pw = PageWidget(i)
            width = page.rect.width * self.scale
            height = page.rect.height * self.scale
            pw.set_placeholder(width, height)
            self._layout.addWidget(pw)
            self.page_widgets.append(pw)

        QTimer.singleShot(0, self._sync_container_size)

        # Trigger a render after layout settles
        QTimer.singleShot(100, self._render_visible_pages)

    def _render_visible_pages(self):
        """Render only pages that are currently visible (plus a buffer)."""
        if not self.doc:
            return

        viewport = self.viewport().rect()
        viewport_top = self.verticalScrollBar().value()
        viewport_bottom = viewport_top + viewport.height()
        buffer = viewport.height()  # 1 viewport of buffer above and below

        for i, pw in enumerate(self.page_widgets):
            if i in self._rendered_pages:
                continue

            widget_top = pw.y()
            widget_bottom = widget_top + pw.height()

            # Check if page is within visible range + buffer
            if widget_bottom >= (viewport_top - buffer) and \
               widget_top <= (viewport_bottom + buffer):
                self._render_page(i)

    def _render_page(self, page_num):
        """Render a single page and display it."""
        if page_num in self._rendered_pages:
            return

        try:
            page = self.doc[page_num]
            # Use a higher DPI matrix for crisp rendering, then scale the pixmap
            render_scale = self.scale * 2  # render at 2x for sharpness
            mat = fitz.Matrix(render_scale, render_scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Use PPM format for reliable conversion (no raw pointer issues)
            ppm_data = pix.tobytes("ppm")
            qpixmap = QPixmap()
            qpixmap.loadFromData(ppm_data)

            pw = self.page_widgets[page_num]
            display_w = int(page.rect.width * self.scale)
            display_h = int(page.rect.height * self.scale)
            pw.setFixedSize(display_w, display_h)

            # Scale the pixmap to the display size for crisp rendering
            scaled_pixmap = qpixmap.scaled(
                display_w, display_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            pw.set_page_pixmap(scaled_pixmap)

            self._rendered_pages.add(page_num)

            # Re-apply search highlights if any
            self._apply_search_highlights_to_page(page_num)

        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")

    def _on_scroll(self):
        """Track scroll position and update current page."""
        self._render_timer.start()  # Trigger lazy rendering

        if not self.page_widgets:
            return

        viewport_center = self.verticalScrollBar().value() + self.viewport().height() // 3
        closest_page = 0
        closest_dist = float('inf')

        for i, pw in enumerate(self.page_widgets):
            page_center = pw.y() + pw.height() // 2
            dist = abs(page_center - viewport_center)
            if dist < closest_dist:
                closest_dist = dist
                closest_page = i

        if closest_page != self._current_page:
            self._current_page = closest_page
            self.page_changed.emit(closest_page)

    # ========== ZOOM ==========

    def set_zoom(self, scale):
        """Set zoom level and re-render."""
        self.scale = max(0.25, min(5.0, scale))
        self.zoom_changed.emit(self.scale)
        self._re_render()

    def zoom_in(self):
        self.set_zoom(self.scale + 0.25)

    def zoom_out(self):
        self.set_zoom(self.scale - 0.25)

    def auto_fit_page(self):
        """Fit the first page within the viewport."""
        if not self.doc:
            return
        page = self.doc[0]
        vp_width = self.viewport().width() - 60
        vp_height = self.viewport().height() - 60

        # Guard: if viewport isn't laid out yet, defer
        if vp_width < 100 or vp_height < 100:
            QTimer.singleShot(300, self.auto_fit_page)
            return

        scale_w = vp_width / page.rect.width
        scale_h = vp_height / page.rect.height
        new_scale = min(scale_w, scale_h)
        # Ensure a reasonable minimum scale
        new_scale = max(0.3, new_scale)
        self.set_zoom(new_scale)

    def fit_width(self):
        """Fit to viewport width."""
        if not self.doc:
            return
        page = self.doc[self._current_page]
        vp_width = self.viewport().width() - 60
        self.set_zoom(vp_width / page.rect.width)

    def fit_page(self):
        """Fit entire page in viewport."""
        self.auto_fit_page()

    def _re_render(self):
        """Clear all renders and rebuild placeholders."""
        if not self.doc:
            return
        # Remember current page
        current = self._current_page
        self._create_page_placeholders()
        # Scroll back to the page we were on
        QTimer.singleShot(150, lambda: self.go_to_page(current))

    # ========== NAVIGATION ==========

    def go_to_page(self, page_num):
        """Scroll to a specific page (0-indexed)."""
        if 0 <= page_num < len(self.page_widgets):
            self._current_page = page_num
            self.page_widgets[page_num].ensureWidgetVisible = True
            self.ensureWidgetVisible(self.page_widgets[page_num], 0, 20)
            self.page_changed.emit(page_num)

    def next_page(self):
        if self._current_page < len(self.page_widgets) - 1:
            self.go_to_page(self._current_page + 1)

    def prev_page(self):
        if self._current_page > 0:
            self.go_to_page(self._current_page - 1)

    @property
    def current_page(self):
        return self._current_page

    @property
    def total_pages(self):
        return len(self.doc) if self.doc else 0

    # ========== SEARCH ==========

    def search(self, query):
        """Search for text across all pages."""
        self._search_matches.clear()
        self._search_index = -1

        if not query or not self.doc:
            self._clear_all_highlights()
            return 0

        for i in range(len(self.doc)):
            page = self.doc[i]
            rects = page.search_for(query)
            if rects:
                # Scale rects to current zoom
                scaled_rects = []
                for r in rects:
                    scaled_rects.append(fitz.Rect(
                        r.x0 * self.scale,
                        r.y0 * self.scale,
                        r.x1 * self.scale,
                        r.y1 * self.scale
                    ))
                self._search_matches.append((i, scaled_rects))

        # Apply highlights to rendered pages
        self._apply_all_search_highlights()

        total = sum(len(rects) for _, rects in self._search_matches)
        if total > 0:
            self._search_index = 0
            self._update_active_highlight()
        return total

    def next_search_match(self):
        """Navigate to next search match."""
        if not self._search_matches:
            return -1, 0
        total = sum(len(r) for _, r in self._search_matches)
        self._search_index = (self._search_index + 1) % total
        self._update_active_highlight()
        return self._search_index, total

    def prev_search_match(self):
        """Navigate to previous search match."""
        if not self._search_matches:
            return -1, 0
        total = sum(len(r) for _, r in self._search_matches)
        self._search_index = (self._search_index - 1) % total
        self._update_active_highlight()
        return self._search_index, total

    def _update_active_highlight(self):
        """Update which match is highlighted as active and scroll to it."""
        count = 0
        for page_num, rects in self._search_matches:
            for local_idx in range(len(rects)):
                if count == self._search_index:
                    # Highlight this match as active
                    self._apply_all_search_highlights()
                    if page_num < len(self.page_widgets):
                        pw = self.page_widgets[page_num]
                        pw.set_search_highlights(rects, local_idx)
                    self.go_to_page(page_num)
                    return
                count += 1

    def _apply_all_search_highlights(self):
        """Apply search highlights to all rendered pages."""
        # Clear first
        for pw in self.page_widgets:
            pw.clear_highlights()

        for page_num, rects in self._search_matches:
            self._apply_search_highlights_to_page(page_num)

    def _apply_search_highlights_to_page(self, page_num):
        """Apply search highlights to a specific page."""
        for match_page, rects in self._search_matches:
            if match_page == page_num and page_num < len(self.page_widgets):
                self.page_widgets[page_num].set_search_highlights(rects)
                break

    def _clear_all_highlights(self):
        for pw in self.page_widgets:
            pw.clear_highlights()

    def clear_search(self):
        """Clear all search state."""
        self._search_matches.clear()
        self._search_index = -1
        self._clear_all_highlights()

    # ========== MOUSE WHEEL ZOOM ==========

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    # ========== CLEANUP ==========

    def cleanup(self):
        if self.doc:
            self.doc.close()
            self.doc = None
