#!/bin/bash

# Script to set up virtual environment and continuously run the Python program
# located at ./src/main.py, restarting it upon exit.
#
# This script:
# 1. Detects available Python command (python or python3)
# 2. Creates a virtual environment (.venv) if it doesn't exist
# 3. Activates the virtual environment
# 4. Installs dependencies from requirements.txt if needed
# 5. Enters an infinite loop where it starts the specified Python program
#
# If the program exits, the script waits for 2 seconds and then restarts it.
# The loop can be interrupted by pressing Ctrl+C.
#
# Requirements:
# - Python 3.x installed and accessible via "python" or "python3" command
# - Intended for streaming or testing scenarios where automatic restarts are useful
# - Automatically manages virtual environment and dependencies

set -e  # Exit on any error

# Function to detect Python command
detect_python() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        # Check if python is Python 3
        if python -c "import sys; exit(0 if sys.version_info.major == 3 else 1)" &> /dev/null; then
            echo "python"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Function to check if dependencies are installed
check_dependencies_installed() {
    if [ ! -f "./requirements.txt" ]; then
        echo "requirements.txt not found, skipping dependency check"
        return 0
    fi

    local venv_python=".venv/bin/python"

    # Read requirements.txt and check each package
    while IFS= read -r requirement; do
        # Skip comments and empty lines
        if [[ "$requirement" =~ ^[[:space:]]*# ]] || [[ -z "${requirement// }" ]]; then
            continue
        fi

        # Extract package name (before ==)
        package_name=$(echo "$requirement" | cut -d'=' -f1 | xargs)

        # Check if package is installed
        if ! "$venv_python" -m pip show "$package_name" &> /dev/null; then
            return 1
        fi
    done < "./requirements.txt"

    return 0
}

# Function to handle cleanup on script exit
cleanup() {
    echo -e "\nStopped by user."
    exit 0
}

# Set up signal handler
trap cleanup SIGINT SIGTERM

# Detect Python command
PYTHON_CMD=$(detect_python)

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3 is not installed or not accessible via 'python' or 'python3' command."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_CMD" -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies need to be installed
if ! check_dependencies_installed; then
    echo "Installing dependencies..."
    .venv/bin/python -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully."
else
    echo "Dependencies already installed."
fi

# Run the application in a loop
while true; do
    echo "Starting program..."
    .venv/bin/python ./src/main.py
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "Program was closed by user. Exiting..."
        break
    else
        echo "Program exited with error code $exit_code. Restarting in 2 seconds... Press Ctrl+C to stop."
        sleep 2
    fi
done