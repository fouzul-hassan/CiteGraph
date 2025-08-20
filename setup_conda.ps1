# PowerShell script to set up CiteGraph in .conda environment
Write-Host "Setting up CiteGraph in .conda environment..." -ForegroundColor Green
Write-Host ""

# Activate conda environment
Write-Host "Activating conda environment..." -ForegroundColor Yellow
& ".\.conda\Scripts\activate.ps1"

Write-Host ""
Write-Host "Installing CiteGraph dependencies..." -ForegroundColor Yellow
& ".\.conda\Scripts\pip.exe" install -r requirements.txt

Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "To run CiteGraph:" -ForegroundColor Cyan
Write-Host "1. Activate the environment: .\.conda\Scripts\activate.ps1" -ForegroundColor White
Write-Host "2. Run: .\.conda\Scripts\streamlit.exe run app.py" -ForegroundColor White
Write-Host "3. Open browser to: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Or use the run script: .\run_citegraph.ps1" -ForegroundColor Cyan
Write-Host ""
pause
