#!/bin/bash

# HIOKI Resistance Meter - Startup Script for Raspberry Pi
# This script sets up the Python virtual environment and runs the application

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_EXEC="$VENV_DIR/bin/python"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install requirements if needed
if [ ! -f "$VENV_DIR/bin/pip" ]; then
    echo "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

echo "Installing dependencies..."
pip install -q -r "$SCRIPT_DIR/requirements.txt"

# Run the application
echo "Starting HIOKI Resistance Meter..."
python "$SCRIPT_DIR/main.py"

# Deactivate virtual environment on exit
deactivate
