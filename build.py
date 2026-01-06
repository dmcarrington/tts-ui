#!/usr/bin/env python3
"""
Cross-platform build script for TTS Converter.

Usage:
    python build.py                 # Build for current platform
    python build.py --target linux    # Build Linux executable
    python build.py --target windows  # Build Windows exe (on Windows only)
    python build.py --target macos    # Build macOS app (on macOS only)
    python build.py --icon            # Only create the icon
    python build.py --clean           # Clean build directories

Cross-compilation:
    Windows/macOS builds from Linux require GitHub Actions: gh workflow run build.yml
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path


def create_icon():
    """Create app icon if it doesn't exist."""
    icon_path = Path("assets/icon.png")

    os.makedirs("assets", exist_ok=True)

    if icon_path.exists():
        print(f"Icon already exists at {icon_path}")
        return

    print("Creating default icon...")

    from PIL import Image, ImageDraw

    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a speech bubble
    draw.ellipse([20, 20, 236, 200], fill='#007bff')
    draw.polygon([(60, 180), (100, 180), (40, 240)], fill='#007bff')

    # Add waveform bars
    for i, h in enumerate([40, 70, 100, 70, 40]):
        x = 80 + i * 25
        draw.rectangle([x, 110-h//2, x+15, 110+h//2], fill='white')

    img.save(icon_path)
    print(f"Created {icon_path}")


def create_ico():
    """Create Windows ICO file from PNG."""
    from PIL import Image

    print("Creating icon.ico...")
    img = Image.open("assets/icon.png")
    img.save(
        "assets/icon.ico",
        format='ICO',
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )
    print("Created assets/icon.ico")


def create_icns():
    """Create macOS ICNS file from PNG."""
    from PIL import Image

    print("Creating icon.icns...")

    iconset = Path("assets/icon.iconset")
    iconset.mkdir(exist_ok=True)

    img = Image.open("assets/icon.png")

    # Create all required sizes
    sizes = {
        'icon_16x16.png': 16,
        'icon_16x16@2x.png': 32,
        'icon_32x32.png': 32,
        'icon_32x32@2x.png': 64,
        'icon_128x128.png': 128,
        'icon_128x128@2x.png': 256,
        'icon_256x256.png': 256,
        'icon_256x256@2x.png': 512,
        'icon_512x512.png': 512,
        'icon_512x512@2x.png': 1024,
    }

    for filename, size in sizes.items():
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset / filename)

    # Use iconutil to create icns (macOS only)
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", "assets/icon.icns"],
        check=True
    )

    shutil.rmtree(iconset)
    print("Created assets/icon.icns")


def build_windows_native():
    """Build Windows executable using PyInstaller (on Windows)."""
    print("=" * 50)
    print("Building TTS Converter for Windows")
    print("=" * 50)

    create_ico()

    print("\nInstalling PyInstaller...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        check=True
    )

    print("\nBuilding executable...")
    subprocess.run(
        ["pyinstaller", "tts_converter.spec", "--clean"],
        check=True
    )

    print("\n" + "=" * 50)
    print("Windows build complete!")
    print("Output: dist/TTS Converter.exe")
    print("=" * 50)


def build_mac_native():
    """Build macOS app using py2app (on macOS)."""
    print("=" * 50)
    print("Building TTS Converter for macOS")
    print("=" * 50)

    create_icns()

    print("\nInstalling py2app...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "py2app"],
        check=True
    )

    print("\nBuilding app bundle...")
    subprocess.run(
        [sys.executable, "setup_mac.py", "py2app"],
        check=True
    )

    print("\n" + "=" * 50)
    print("macOS build complete!")
    print("Output: dist/TTS Converter.app")
    print("=" * 50)


def build_linux():
    """Build Linux executable using PyInstaller."""
    print("=" * 50)
    print("Building TTS Converter for Linux")
    print("=" * 50)

    print("\nInstalling PyInstaller...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        check=True
    )

    print("\nBuilding executable...")
    subprocess.run(
        ["pyinstaller", "tts_converter.spec", "--clean"],
        check=True
    )

    print("\n" + "=" * 50)
    print("Linux build complete!")
    print("Output: dist/TTS Converter")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Build TTS Converter for desktop platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build for current platform
  python build.py --target linux     # Build for Linux
  python build.py --target windows   # Build for Windows (requires Windows host)
  python build.py --target macos     # Build for macOS (requires macOS host)

Cross-compilation:
  Use GitHub Actions for cross-platform builds: gh workflow run build.yml
        """
    )
    parser.add_argument(
        "--target",
        choices=["windows", "macos", "linux", "auto"],
        default="auto",
        help="Target platform (default: auto-detect current platform)"
    )
    parser.add_argument("--icon", action="store_true", help="Only create the icon")
    parser.add_argument("--clean", action="store_true", help="Clean build directories")
    args = parser.parse_args()

    if args.clean:
        print("Cleaning build directories...")
        shutil.rmtree("build", ignore_errors=True)
        shutil.rmtree("dist", ignore_errors=True)
        print("Done.")
        return

    if args.icon:
        create_icon()
        return

    # Clean previous builds
    print("Cleaning previous builds...")
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)

    # Create icon
    create_icon()

    # Determine target platform
    target = args.target
    if target == "auto":
        if sys.platform == "darwin":
            target = "macos"
        elif sys.platform == "win32":
            target = "windows"
        else:
            target = "linux"

    # Build for target platform
    current_platform = sys.platform

    if target == "windows":
        if current_platform == "win32":
            build_windows_native()
        else:
            print("Error: Windows builds require a Windows host.")
            print("")
            print("Options:")
            print("  1. Use GitHub Actions: gh workflow run build.yml")
            print("  2. Build on a Windows machine")
            sys.exit(1)

    elif target == "macos":
        if current_platform == "darwin":
            build_mac_native()
        else:
            print("Error: macOS builds require a macOS host.")
            print("")
            print("Options:")
            print("  1. Use GitHub Actions: gh workflow run build.yml")
            print("  2. Build on a macOS machine")
            print("  3. Use a macOS CI service")
            sys.exit(1)

    elif target == "linux":
        if current_platform.startswith("linux"):
            build_linux()
        else:
            print(f"Error: Linux builds require a Linux host (current: {current_platform})")
            sys.exit(1)

    else:
        print(f"Unknown target: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
