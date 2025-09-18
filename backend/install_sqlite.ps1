# Activate virtual environment and install SQLite support
& ".\venv\Scripts\Activate.ps1"
pip install aiosqlite
Write-Host "SQLite support installed successfully!"
