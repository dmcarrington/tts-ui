#!/bin/bash
#
# Build desktop apps using Docker (for cross-compilation from Linux)
#
# Usage:
#   ./build_docker.sh windows    # Build Windows .exe from Linux
#   ./build_docker.sh all        # Build all platforms
#
# Requirements:
#   - Docker installed and running
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

build_windows() {
    echo "========================================"
    echo "Building Windows executable using Docker"
    echo "========================================"

    # Build the Docker image
    docker build -f Dockerfile.windows -t tts-builder-windows .

    # Run the container and extract the build
    mkdir -p dist

    # Create a container, copy the output, then remove it
    CONTAINER_ID=$(docker create tts-builder-windows)
    docker cp "$CONTAINER_ID:/app/dist/TTS Converter.exe" "dist/TTS Converter.exe" 2>/dev/null || \
    docker cp "$CONTAINER_ID:/app/dist/TTS Converter" "dist/" 2>/dev/null || \
    echo "Warning: Could not copy executable. Check Docker build logs."
    docker rm "$CONTAINER_ID"

    echo ""
    echo "Windows build complete!"
    if [ -f "dist/TTS Converter.exe" ]; then
        echo "Output: dist/TTS Converter.exe"
        ls -lh "dist/TTS Converter.exe"
    fi
}

build_linux() {
    echo "========================================"
    echo "Building Linux executable"
    echo "========================================"

    # Install PyInstaller if needed
    pip install pyinstaller

    # Build
    pyinstaller tts_converter.spec --clean

    echo ""
    echo "Linux build complete!"
    echo "Output: dist/TTS Converter"
}

show_usage() {
    echo "Usage: $0 [windows|linux|all]"
    echo ""
    echo "Commands:"
    echo "  windows  - Build Windows .exe using Docker"
    echo "  linux    - Build Linux executable natively"
    echo "  all      - Build for all platforms"
    echo ""
    echo "Note: macOS builds require a macOS host or GitHub Actions."
    echo "      Use 'gh workflow run build.yml' for CI builds."
}

case "${1:-}" in
    windows)
        build_windows
        ;;
    linux)
        build_linux
        ;;
    all)
        build_linux
        build_windows
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
