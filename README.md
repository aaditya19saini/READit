# ReadIt — Free, Fast & Native PDF Reader 📚

![ReadIt Welcome Screen](images/Screenshot%202026-03-14%20160014.png)

A modern, lightning-fast, and 100% free PDF reader desktop application built entirely with Python. Designed to be completely offline with no subscriptions, no ads, and no paywalls. It leverages **PyQt6** for a native, premium look and feel and **PyMuPDF** for high-performance rendering.

## 🌟 Key Features

- **🚀 Lightning-Fast Rendering:** Powered by `PyMuPDF` (fitz) with lazy page loading for smooth, lag-free scrolling, even on massive documents.
- **🎨 Modern, Premium UI:** Clean, intuitive interface featuring fully integrated **Dark Mode** and **Light Mode**.
- **🔍 Powerful Search:** Fast in-document text search with visual hit highlighting and easy navigation between matches.
- **📑 Sidebar Navigation:** Quickly browse through documents using the built-in, lazy-loaded thumbnail sidebar view.
- **👁️ Flexible Viewing Options:** Adaptive zoom controls including Fit Width, Fit Page, mouse-wheel zooming, and custom zoom percentages.
- **🔒 100% Offline & Private:** No cloud uploads, no telemetry. Your files stay perfectly secure on your local machine.
- **🖱️ Drag & Drop Support:** Simply drag and drop any PDF file onto the application window to open it instantly.

## 📸 In Action

![ReadIt PDF Viewer](images/Screenshot%202026-03-14%20160032.png)

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.8+](https://www.python.org/downloads/)
- [PyQt6](https://pypi.org/project/PyQt6/) (`>=6.6`)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) (`>=1.24`)

## 📥 Installation

1. Enter the project directory:
   ```bash
   cd "path/to/project/folder"
   ```

2. Install the required dependencies via `pip`:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

Run the application directly from the terminal:

```bash
python main.py
```

You can also bypass the welcome screen and directly open a PDF file by passing it as a command-line argument:

```bash
python main.py "path/to/document.pdf"
```

## ⌨️ Keyboard Shortcuts

Navigate like a pro with these handy shortcuts:

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + O` | Open PDF |
| `Ctrl + F`| Open Search / Find |
| `Ctrl + P`| Print Document |
| `Ctrl + +` / `Ctrl + -` | Zoom In / Zoom Out |
| `Ctrl + Mouse Wheel` | Zoom In / Zoom Out |
| `T` | Toggle Sidebar |
| `F11` | Toggle Fullscreen |
| `Left Arrow` / `Right Arrow` | Previous / Next Page |

## 📁 Project Structure

- `main.py`: Application entry point, main window logic, toolbars, and welcome screen.
- `pdf_viewer.py`: The core rendering engine handling PyMuPDF integration, scaling, lazy rendering, and search highlights.
- `sidebar.py`: Navigation sidebar containing lazy-loaded page thumbnails.
- `search_bar.py`: UI and logic for the in-document search functionality.
- `theme.py`: Custom QSS (Qt Style Sheets) defining the Dark and Light modes.


## 📦 Deployment (Windows .exe)

To build the application into a standalone, double-clickable Windows `.exe` file (so users don't need Python installed):

1. Install PyInstaller (Note: `v5.13.2` is highly recommended to avoid hook-resolution issues with PyMuPDF on newer Python versions):
   ```bash
   pip install pyinstaller==5.13.2
   ```
2. Run the build command, explicitly giving PyInstaller the path to the PyMuPDF (`fitz`) binaries:
   ```bash
   pyinstaller --name "ReadIt" --windowed --onefile --clean --add-data "C:/path/to/your/python/Lib/site-packages/fitz;fitz" main.py
   ```
   *(Ensure you replace the Python path with your actual local environment python path).*
3. Once the build finishes, look inside the generated `dist` folder. You will find your standalone `ReadIt.exe` inside!



---
*Built with ❤️ in Python*
