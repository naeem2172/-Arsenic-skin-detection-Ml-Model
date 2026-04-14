@echo off
REM Run Arsenic Detection app - ensures correct working directory
cd /d "%~dp0"

echo Starting Arsenic Detection...
echo Model path: %CD%\models\arsenic_skin_detection_advanced_model.h5
if exist "models\arsenic_skin_detection_advanced_model.h5" (
    echo Model file found.
) else (
    echo WARNING: Model file not found! Place arsenic_skin_detection_advanced_model.h5 in models/
    pause
)

call venv\Scripts\activate.bat
python app.py
pause
