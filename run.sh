#!/bin/bash

echo "1/2 Compilando e Enviando para o Arduino."
cd src/trabalho_g2_sisinpe/arduino
arduino-cli compile --fqbn arduino:avr:uno .
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno .

echo "2/2 Iniciando o sistema Python com uv..."
cd ~/trabalho_g2_sisinpe
uv run python src/trabalho_g2_sisinpe/main.py
