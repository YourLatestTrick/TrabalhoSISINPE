#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
uv run uvicorn trabalho_g2_sisinpe.api.app:app --host 0.0.0.0 --port 8000
