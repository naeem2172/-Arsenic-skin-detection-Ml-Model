@echo off
cd /d "%~dp0"
echo ========================================
echo  Arsenic Detection - Full Setup and Run
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Create placeholder model only if no trained model in models/
python -c "from pathlib import Path; m=Path('models'); exit(0 if m.exists() and any(m.glob('*'+e) for e in ['.h5','.keras','.pkl']) else 1)" 2>nul || (
    echo No model in models/. Creating placeholder...
    python train_model.py --placeholder
    echo.
)

REM Start the app
echo Starting Arsenic Detection app...
echo.
echo Open http://localhost:5000 in your browser
echo - Dashboard, Prediction, Chatbot
echo.
python app.py
pause
