# ReadIt Desktop — Native Python PDF Reader

Rebuild ReadIt as a **native Windows desktop app** using PyQt6 (GUI) + PyMuPDF (PDF engine). Looks like a system app, runs as a standalone `.exe`.

## Tech Stack

| Component | Library | Why |
|---|---|---|
| GUI | **PyQt6** | Qt widgets = native OS look. Same C++ engine as Qt, but callable from Python |
| PDF Engine | **PyMuPDF (fitz)** | Fastest Python PDF lib. Renders pages, annotations, forms, links, text extraction — all built-in |
| Packaging | **PyInstaller** | Bundles Python + deps into a single `.exe` for distribution |

## Project Structure

```
c:\Users\Aaditya Saini\Desktop\New folder\
├── main.py              ← Entry point / window setup
├── pdf_viewer.py        ← Core PDF rendering widget
├── toolbar.py           ← Toolbar with all controls
├── sidebar.py           ← Thumbnail sidebar
├── search_bar.py        ← Search overlay widget
├── theme.py             ← Dark/light theme QSS stylesheets
├── requirements.txt     ← PyQt6, PyMuPDF
└── assets/
    └── icon.png         ← App icon
```

---

## Proposed Changes

### [NEW] [requirements.txt](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/requirements.txt)

```
PyQt6>=6.6
PyMuPDF>=1.24
```

---

### [NEW] [main.py](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/main.py)

Application entry point:
- Create `QApplication` with the app name "ReadIt"
- Create and show the main `QMainWindow`
- Set app icon, window title, default size (1200×800)
- Apply dark theme stylesheet on startup
- Accept command-line argument to open a PDF directly (e.g., `readit.exe myfile.pdf`)
- Show a welcome/landing widget when no file is open

---

### [NEW] [pdf_viewer.py](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/pdf_viewer.py)

Core rendering widget (`QScrollArea` containing page images):
- **Open PDF**: `fitz.open(filepath)` → store the `Document` object
- **Render pages**: `page.get_pixmap(matrix=zoom_matrix)` → convert to `QPixmap` → display in `QLabel` widgets
- **Lazy rendering**: Only render visible pages + 2 above/below (using scroll position tracking)
- **Annotations**: `page.get_pixmap(annots=True)` renders all annotations (highlights, notes, stamps) directly into the image
- **Text layer**: `page.get_text("dict")` extracts text with positions for search highlighting
- **Text selection & copy**: Track mouse drag over text spans, copy selected text to clipboard
- **Scroll tracking**: Update current page number as user scrolls through pages

---

### [NEW] [toolbar.py](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/toolbar.py)

Native `QToolBar` with:
- **Open button** → `QFileDialog.getOpenFileName(filter="PDF Files (*.pdf)")`
- **Page navigation** → prev/next `QAction` + `QSpinBox` for page jump
- **Zoom controls** → zoom in/out `QAction` + `QComboBox` with presets (50%, 75%, 100%, 125%, 150%, 200%, Fit Width, Fit Page)
- **Search toggle** → opens/closes the search bar
- **Print** → `QPrinter` + `QPrintDialog`
- **Fullscreen** → `showFullScreen()` / `showNormal()`
- **Dark mode toggle** → swaps QSS stylesheet

All buttons use Qt's built-in `QStyle.StandardPixmap` icons for native OS look, with fallback SVG icons.

---

### [NEW] [sidebar.py](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/sidebar.py)

Thumbnail panel (`QDockWidget` containing a `QListWidget`):
- Render each page as a small thumbnail (200px wide) using `page.get_pixmap(matrix=thumb_matrix)`
- Display thumbnails in a vertical `QListWidget` with page numbers
- Click thumbnail → scroll main viewer to that page
- Highlight current page's thumbnail
- Lazy-load thumbnails in a background `QThread` to avoid blocking the UI
- Collapsible via toolbar button or `T` shortcut

---

### [NEW] [search_bar.py](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/search_bar.py)

Floating search widget:
- `QLineEdit` for query input
- Match count label ("3 of 17")
- Prev/Next match buttons
- Uses `page.search_for(query)` which returns exact `Rect` positions of each match
- Draws highlight rectangles over matches on the rendered page image
- Active match gets a different highlight color
- Auto-scrolls to the active match's page

---

### [NEW] [theme.py](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/theme.py)

Qt StyleSheet (QSS) definitions:
- **Dark theme** (default): dark backgrounds, light text, accent colors matching our web version (violet/cyan gradient accents)
- **Light theme**: standard light OS colors
- Styled scrollbars, buttons, toolbars, combo boxes, spin boxes
- Theme preference saved to `QSettings` (persists across app restarts)

---

### [DELETE] Web files (optional cleanup)

The old web files ([index.html](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/index.html), [style.css](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/style.css), [app.js](file:///c:/Users/Aaditya%20Saini/Desktop/New%20folder/app.js), `test.pdf`) can be removed once the Python app is working.

---

## Feature Parity with Web Version

| Feature | How It's Done in Python |
|---|---|
| Open PDFs | `QFileDialog` + drag & drop via `dragEnterEvent`/`dropEvent` |
| Page rendering | `fitz.Page.get_pixmap(annots=True)` → `QPixmap` |
| Annotations | Built-in — `annots=True` renders them automatically |
| Navigation | `QSpinBox` + prev/next buttons + scroll tracking |
| Zoom | Matrix scaling on `get_pixmap()` + combo box presets |
| Text search | `page.search_for(query)` → highlight rects |
| Thumbnails | Background `QThread` renders small pixmaps |
| Dark mode | QSS stylesheet swap + `QSettings` persistence |
| Keyboard shortcuts | `QShortcut` bindings |
| Text selection | Mouse tracking over `page.get_text("dict")` positions |
| Fullscreen | `showFullScreen()` / `showNormal()` |
| Print | `QPrinter` + `QPrintDialog` |
| Progress bar | `QProgressBar` in status bar |

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl+O` | Open file |
| `←` / `→` | Prev / Next page |
| `Ctrl+F` | Search |
| `Escape` | Close search |
| `Ctrl++` / `Ctrl+-` | Zoom in / out |
| `Ctrl+P` | Print |
| `F11` | Fullscreen |
| `T` | Toggle sidebar |

---

## Verification Plan

### Automated
1. Run `main.py` and verify the window opens with the welcome screen
2. Open a sample PDF via file dialog
3. Verify pages render correctly with annotations visible
4. Test zoom, navigation, search, thumbnails
5. Test dark/light mode toggle

### Manual
1. User tests with their own annotated PDFs
2. User verifies it "feels native" (window chrome, file dialogs, keyboard shortcuts)
3. (Later) Package with PyInstaller and test the `.exe`
