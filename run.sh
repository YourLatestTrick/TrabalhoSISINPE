#!/bin/bash

echo "1/2 Compilando e enviando para o arduino"
cd src/trabalho_g2_sisinpe/arduino
arduino-cli compile --fqbn arduino:avr:uno .
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno .

echo "2/2 Iniciando o sistema python com uv"
cd ~/trabalho_g2_sisinpe
PYTHONPATH=src uv run uvicorn trabalho_g2_sisinpe.api.app:app --host 0.0.0.0 --port 8000
