#!/bin/bash
# GenoScene - Unix/Linux/macOS Startup Script
# ===========================================

echo ""
echo "========================================"
echo "  GenoScene - Forensic Phenotype Prediction"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
if ! python3 -c "import pandas, numpy, matplotlib, scipy" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install packages"
        exit 1
    fi
fi

# Create output directory if it doesn't exist
mkdir -p output

# Function to open web interface
open_web() {
    echo "Opening web interface..."
    if command -v xdg-open &> /dev/null; then
        xdg-open index.html
    elif command -v open &> /dev/null; then
        open index.html
    else
        echo "Please open index.html in your web browser"
    fi
}

# Function to run demo
run_demo() {
    echo "Running demo analysis..."
    python3 run_genoscene.py --demo
}

# Function to run custom analysis
run_custom() {
    read -p "Enter Sample ID: " sample_id
    read -p "Enter path to CSV file: " data_file
    python3 run_genoscene.py "$sample_id" "$data_file"
}

# Function to install packages
install_packages() {
    echo "Installing/updating packages..."
    python3 run_genoscene.py --install
}

# Main menu
while true; do
    echo ""
    echo "What would you like to do?"
    echo "1. Open Web Interface"
    echo "2. Run Demo Analysis"
    echo "3. Run Custom Analysis"
    echo "4. Install/Update Packages"
    echo "5. Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice

    case $choice in
        1)
            open_web
            break
            ;;
        2)
            run_demo
            break
            ;;
        3)
            run_custom
            break
            ;;
        4)
            install_packages
            break
            ;;
        5)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done

echo ""
echo "Operation completed!"
