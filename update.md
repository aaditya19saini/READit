# This recreates the executable with your newest code.

pyinstaller --name "ReadIt" --windowed --onefile --clean --add-data "C:/path/to/your/python/Lib/site-packages/fitz;fitz" main.py
