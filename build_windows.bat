@echo off
echo Building TTS Converter for Windows...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Check if icon.png exists
if not exist assets\icon.png (
    echo Error: assets\icon.png not found
    exit /b 1
)

REM Install build dependencies
pip install pyinstaller

REM Convert PNG to ICO (requires Pillow)
echo Creating icon.ico...
python -c "from PIL import Image; img = Image.open('assets/icon.png'); img.save('assets/icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])"

REM Build the executable
echo Building executable...
pyinstaller tts_converter.spec --clean

echo.
echo Build complete!
echo Executable location: dist\TTS Converter.exe
pause
