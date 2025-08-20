# PowerShell script to run the test Streamlit app
Write-Host "Starting Streamlit Test App..." -ForegroundColor Green

# Activate the conda environment and run Streamlit
& ".\.conda\Scripts\streamlit.exe" run test_app.py

Write-Host "Streamlit app stopped." -ForegroundColor Yellow
