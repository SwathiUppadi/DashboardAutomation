#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create the sample database if it doesn't exist
if [ ! -f "hr_database.db" ]; then
    echo "Creating sample database..."
    python sample_data.py
fi

# Run the application
echo "Starting HR Insights Dashboard..."
streamlit run app.py
