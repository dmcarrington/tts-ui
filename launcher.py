#!/usr/bin/env python3
"""
TTS Converter Desktop Launcher

Starts the FastAPI server, opens the browser, and displays a system tray icon.
"""

import sys
import os
import threading
import webbrowser
import time

# Handle frozen app paths (PyInstaller/py2app)
if getattr(sys, 'frozen', False):
    # Running as compiled
    if hasattr(sys, '_MEIPASS'):
        BASE_DIR = sys._MEIPASS  # PyInstaller
    else:
        BASE_DIR = os.path.dirname(sys.executable)  # py2app
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the base directory to path for imports
sys.path.insert(0, BASE_DIR)

import uvicorn
from pystray import Icon, Menu, MenuItem
from PIL import Image

PORT = 8000
URL = f"http://localhost:{PORT}"


class TTSApp:
    def __init__(self):
        self.server_thread = None
        self.server = None
        self.icon = None

    def start_server(self):
        """Start the uvicorn server in a background thread."""
        # Change to the correct directory for static files
        os.chdir(BASE_DIR)

        config = uvicorn.Config(
            "app.main:app",
            host="127.0.0.1",
            port=PORT,
            log_level="warning"
        )
        self.server = uvicorn.Server(config)
        self.server.run()

    def open_browser(self):
        """Open the default browser after a short delay."""
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(URL)

    def on_open_browser(self, icon, item):
        """Menu callback to open browser."""
        webbrowser.open(URL)

    def on_quit(self, icon, item):
        """Quit the application."""
        if self.server:
            self.server.should_exit = True
        icon.stop()

    def load_icon(self):
        """Load the app icon."""
        icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        else:
            # Create a simple default icon if none exists
            img = Image.new('RGB', (64, 64), color='#007bff')
            return img

    def run(self):
        """Run the application."""
        # Start server in background thread
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

        # Open browser in background thread
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()

        # Create system tray icon
        image = self.load_icon()
        menu = Menu(
            MenuItem("Open Browser", self.on_open_browser),
            Menu.SEPARATOR,
            MenuItem("Quit", self.on_quit)
        )

        self.icon = Icon("TTS Converter", image, "TTS Converter", menu)
        self.icon.run()


def main():
    app = TTSApp()
    app.run()


if __name__ == "__main__":
    main()
