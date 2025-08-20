# PowerShell script to run CiteGraph
Write-Host "Starting CiteGraph..." -ForegroundColor Green
Write-Host ""

# Activate conda environment
Write-Host "Activating conda environment..." -ForegroundColor Yellow
& ".\.conda\Scripts\activate.ps1"

Write-Host ""
Write-Host "Starting CiteGraph application..." -ForegroundColor Yellow
& ".\.conda\Scripts\streamlit.exe" run app.py

Write-Host ""
Write-Host "CiteGraph stopped." -ForegroundColor Yellow
pause
