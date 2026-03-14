#!/bin/bash
# Build script for Linux (Railway deployment)

set -e

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_VERSION_NODOT=$(python3 -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")

echo "Building framework for Python ${PYTHON_VERSION}..."

# Get Python include path
PYTHON_INCLUDE=$(python3 -c "from sysconfig import get_paths; print(get_paths()['include'])")

echo "Python include: $PYTHON_INCLUDE"
echo "Looking for Boost.Python matching Python ${PYTHON_VERSION} (${PYTHON_VERSION_NODOT})"

# Find the actual Boost library files
echo "Available Boost libraries:"
ls -la /usr/lib/x86_64-linux-gnu/libboost_python* || true
ls -la /usr/lib/x86_64-linux-gnu/libboost_numpy* || true

# Try to find the correct Boost Python library FOR THIS PYTHON VERSION
# First try exact match (e.g., libboost_python311 for Python 3.11)
BOOST_PYTHON=$(ls /usr/lib/x86_64-linux-gnu/libboost_python${PYTHON_VERSION_NODOT}*.so 2>/dev/null | head -1)
BOOST_NUMPY=$(ls /usr/lib/x86_64-linux-gnu/libboost_numpy${PYTHON_VERSION_NODOT}*.so 2>/dev/null | head -1)

# If not found, try generic python3
if [ -z "$BOOST_PYTHON" ]; then
    BOOST_PYTHON=$(ls /usr/lib/x86_64-linux-gnu/libboost_python3*.so 2>/dev/null | head -1)
fi

if [ -z "$BOOST_NUMPY" ]; then
    BOOST_NUMPY=$(ls /usr/lib/x86_64-linux-gnu/libboost_numpy3*.so 2>/dev/null | head -1)
fi

if [ -z "$BOOST_PYTHON" ]; then
    echo "ERROR: Boost.Python for Python ${PYTHON_VERSION} not found!"
    echo "Tried: libboost_python${PYTHON_VERSION_NODOT}, libboost_python3*"
    exit 1
fi

if [ -z "$BOOST_NUMPY" ]; then
    echo "ERROR: Boost.NumPy for Python ${PYTHON_VERSION} not found!"  
    echo "Tried: libboost_numpy${PYTHON_VERSION_NODOT}, libboost_numpy3*"
    exit 1
fi

echo "✓ Using Boost.Python: $BOOST_PYTHON"
echo "✓ Using Boost.NumPy: $BOOST_NUMPY"

# Extract library names without path and extension
BOOST_PYTHON_LIB=$(basename "$BOOST_PYTHON" .so | sed 's/^lib//')
BOOST_NUMPY_LIB=$(basename "$BOOST_NUMPY" .so | sed 's/^lib//')

echo "✓ Link flags: -l$BOOST_PYTHON_LIB -l$BOOST_NUMPY_LIB"

echo "Linking with: -l$BOOST_PYTHON_LIB -l$BOOST_NUMPY_LIB"

# Compile all C++ files into a shared library
g++ -O3 -std=c++17 -fPIC -shared \
    -o framework.so \
    *.cpp \
    -I"$PYTHON_INCLUDE" \
    -lpython${PYTHON_VERSION} \
    -l"$BOOST_PYTHON_LIB" \
    -l"$BOOST_NUMPY_LIB"

echo "Build complete: framework.so"
ls -lh framework.so

# Copy to site-packages
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
echo "Installing to: $SITE_PACKAGES"
cp framework.so "$SITE_PACKAGES/"

echo "✅ Framework installed successfully!"

