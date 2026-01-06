#!/usr/bin/env python3
"""
Cross-platform build script for TTS Converter.

Usage:
    python build.py                 # Build for current platform
    python build.py --target windows  # Cross-compile for Windows (requires Docker)
    python build.py --target macos    # Cross-compile for macOS (requires Docker or CI)
    python build.py --icon            # Only create the icon
    python build.py --clean           # Clean build directories

Cross-compilation from Linux:
    Windows: Uses Docker with Wine (./build_docker.sh windows)
    macOS:   Requires GitHub Actions or macOS host (no Docker solution)
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


def build_windows_docker():
    """Build Windows executable using Docker (from Linux)."""
    print("=" * 50)
    print("Building TTS Converter for Windows (via Docker)")
    print("=" * 50)

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Docker is not installed or not running.")
        print("Please install Docker and try again.")
        sys.exit(1)

    print("\nBuilding Docker image...")
    subprocess.run(
        ["docker", "build", "-f", "Dockerfile.windows", "-t", "tts-builder-windows", "."],
        check=True
    )

    print("\nExtracting build output...")
    os.makedirs("dist", exist_ok=True)

    # Create container and copy output
    result = subprocess.run(
        ["docker", "create", "tts-builder-windows"],
        capture_output=True,
        text=True,
        check=True
    )
    container_id = result.stdout.strip()

    try:
        subprocess.run(
            ["docker", "cp", f"{container_id}:/app/dist/TTS Converter.exe", "dist/"],
            check=True
        )
    finally:
        subprocess.run(["docker", "rm", container_id], check=True)

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
  python build.py --target windows   # Cross-compile for Windows (Linux→Windows via Docker)
  python build.py --target linux     # Build for Linux
  python build.py --target macos     # Build for macOS (requires macOS host)

Cross-compilation notes:
  - Linux → Windows: Uses Docker with Wine. Requires Docker installed.
  - Linux → macOS: Not supported locally. Use GitHub Actions instead.
  - macOS → Windows: Not supported. Use GitHub Actions instead.
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
            # Cross-compile using Docker
            build_windows_docker()

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
