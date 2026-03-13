# ReadIt — Free PDF Reader

A modern, fast, and 100% free PDF reader desktop application built with Python. Designed to be completely offline with no subscriptions and no paywalls. It uses `PyQt6` for a native, premium look and feel and `PyMuPDF` for lightning-fast rendering.

## Features

- **Fast Rendering:** Powered by `PyMuPDF` (fitz) with lazy page loading for smooth scrolling, even on large documents.
- **Modern UI:** Clean, intuitive interface with full Dark Mode and Light Mode support.
- **Powerful Search:** Fast in-document text search with visual hit highlighting and navigation.
- **Sidebar Navigation:** Quickly browse documents using the built-in thumbnail sidebar view.
- **Viewing Options:** Flexible zoom controls including Fit Width, Fit Page, mouse-wheel zooming, and custom zoom percentages.
- **100% Offline & Private:** No cloud uploads, no telemetry. Your files stay perfectly secure on your local machine.
- **Drag & Drop:** Simply drag and drop any PDF file onto the application to open it.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [PyQt6](https://pypi.org/project/PyQt6/) (`>=6.6`)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) (`>=1.24`)

## Installation

1. Enter the project directory:
   ```bash
   cd "path/to/project/folder"
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python main.py
```

You can also directly open a PDF file by passing it as an argument:

```bash
python main.py "path/to/document.pdf"
```

## Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl + O` | Open PDF |
| `Ctrl + F`| Open Search / Find |
| `Ctrl + P`| Print Document |
| `Ctrl + +` / `Ctrl + -` | Zoom In / Zoom Out |
| `Ctrl + Mouse Wheel` | Zoom In / Zoom Out |
| `T` | Toggle Sidebar |
| `F11` | Toggle Fullscreen |
| `Left Arrow` / `Right Arrow` | Previous / Next Page |

## Project Structure

- `main.py`: Application entry point, main window logic, toolbars, and welcome screen.
- `pdf_viewer.py`: The core rendering engine handling PyMuPDF integration, scaling, lazy rendering, and search highlights.
- `sidebar.py`: Navigation sidebar containing lazy-loaded page thumbnails.
- `search_bar.py`: UI and logic for the in-document search functionality.
- `theme.py`: Custom QSS (Qt Style Sheets) defining the Dark and Light modes.
