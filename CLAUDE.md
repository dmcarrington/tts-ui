# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Text-to-speech web application that converts user-provided text to MP3 audio files using the Python `edge-tts` library. Can run as a web server or be packaged as a standalone desktop application for Mac, Windows, and Linux.

## Tech Stack

- **Backend**: FastAPI with `edge-tts` for TTS conversion
- **Frontend**: Plain HTML/CSS/JS served as static files
- **Desktop**: pystray for system tray icon, py2app (Mac) / PyInstaller (Windows/Linux)

## Development Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Desktop App (development)
```bash
python launcher.py
```

### Access
Open http://localhost:8000 in your browser

## Building Desktop Apps

### Native builds (on target platform)
```bash
python build.py                    # Auto-detect current platform
python build.py --target linux     # Build Linux executable
python build.py --target windows   # Build Windows exe (on Windows)
python build.py --target macos     # Build macOS app (on macOS)
```

### Cross-platform builds (GitHub Actions)
```bash
gh workflow run build.yml          # Trigger builds for Windows, macOS, Linux
```

### Build Output
- **Linux**: `dist/TTS Converter`
- **macOS**: `dist/TTS Converter.app`
- **Windows**: `dist/TTS Converter.exe`

## Architecture

```
tts-ui/
├── app/
│   └── main.py              # FastAPI application
├── static/
│   ├── index.html           # Main page
│   ├── style.css            # Styling
│   └── script.js            # Frontend logic
├── assets/
│   └── icon.png             # App icon
├── launcher.py              # Desktop app entry point (tray icon)
├── build.py                 # Cross-platform build script
├── setup_mac.py             # py2app configuration
├── tts_converter.spec       # PyInstaller configuration
├── .github/workflows/
│   └── build.yml            # GitHub Actions for CI builds
└── requirements.txt         # Python dependencies
```

## API

- `GET /` - Serves the frontend
- `GET /api/voices` - Lists available TTS voices
- `POST /api/convert` - Converts text to speech
  - `text` (required): Text to convert
  - `voice` (optional): Voice name (default: en-US-ChristopherNeural)
  - `subtitles` (optional): Include SRT file (returns zip)
