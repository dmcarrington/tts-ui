"""
py2app build configuration for TTS Converter on macOS.

Usage:
    python setup_mac.py py2app
"""

from setuptools import setup

APP = ['launcher.py']
DATA_FILES = [
    ('static', ['static/index.html', 'static/style.css', 'static/script.js']),
    ('app', ['app/main.py']),
    ('assets', ['assets/icon.png']),
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icon.icns',
    'plist': {
        'CFBundleName': 'TTS Converter',
        'CFBundleDisplayName': 'TTS Converter',
        'CFBundleIdentifier': 'com.tts.converter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Hide from dock (tray app)
    },
    'packages': [
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.protocols',
        'uvicorn.lifespan',
        'fastapi',
        'starlette',
        'anyio',
        'edge_tts',
        'pystray',
        'PIL',
        'aiohttp',
        'multidict',
        'yarl',
    ],
    'includes': [
        'app.main',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
    ],
}

setup(
    app=APP,
    name='TTS Converter',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
