#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv app

echo "Activating virtual environment..."
source app/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing required packages..."
pip install -r requirements.txt

echo "Running application..."
python app.py
