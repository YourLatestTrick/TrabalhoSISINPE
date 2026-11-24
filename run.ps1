$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
uv run uvicorn trabalho_g2_sisinpe.api.app:app --host 0.0.0.0 --port 8000
