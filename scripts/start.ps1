$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Create venv and install requirements.txt first; see README.md."
}
if (-not (Test-Path "frontend\dist\index.html")) {
    throw "Build frontend first: cd frontend; npm ci; npm run build"
}
& .\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
exit $LASTEXITCODE
