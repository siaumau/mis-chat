@echo off
echo Creating virtual environment...
python -m venv app

echo Activating virtual environment...
call app\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required packages...
pip install -r requirements.txt

echo Running application...
python app.py

pause
