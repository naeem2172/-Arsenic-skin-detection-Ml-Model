# Run Arsenic Detection app - ensures correct working directory
Set-Location $PSScriptRoot

Write-Host "Starting Arsenic Detection..."
$modelPath = Join-Path $PSScriptRoot "models\arsenic_skin_detection_advanced_model.h5"
Write-Host "Model path: $modelPath"
if (Test-Path $modelPath) {
    Write-Host "Model file found."
} else {
    Write-Host "WARNING: Model file not found! Place arsenic_skin_detection_advanced_model.h5 in models/" -ForegroundColor Yellow
}

& .\venv\Scripts\Activate.ps1
python app.py
