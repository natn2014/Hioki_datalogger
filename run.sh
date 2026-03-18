#!/bin/bash

# HIOKI Resistance Meter - Startup Script for Raspberry Pi
# Uses global Python installation (no venv)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting HIOKI Resistance Meter..."
cd "$SCRIPT_DIR"

# Run the application using global Python
python3 main.py
