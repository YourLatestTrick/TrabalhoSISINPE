# Sistema Sisinpe

Sistema de monitoramento que utiliza o arduino integrado via USB a uma raspiberrypi para detectar presença de inundação e de lixo em bueiros. Também conta com uma api python para mostrar os alertas em uma interface.

## Visão Geral
- **Arduino:** lê distância usando o sensor ultrassônico e presença de água usando o sensor de água. Quando detecta lixo na faixa de distância menor que **5.0 cm**, executa o ciclo do servomotor **3 vezes**. Ao detectar água, aciona o **LED RGB na cor vermelha** e faz o **buzzer** apitar, além de enviar as leituras pela porta serial.
- **Monitoramento (Python):** lê a porta serial, valida/converte os dados e gera os eventos **flood_alert** e **trash_needs_pickup** para serem usados na api.

## Estrutura do Projeto
```text
trabalho_g2_sisinpe_novo/
├── .venv/
├── bin/
│   └── arduino-cli
├── src/
│   └── trabalho_g2_sisinpe/
│       ├── api/
│       │   ├── router/
│       │   │   └── __init__.py
│       │   ├── services/
│       │   │   └── __init__.py
│       │   └── __init__.py
│       ├── arduino/
│       │   └── arduino.ino
│       ├── monitoring/
│       │   ├── __init__.py
│       │   └── monitor.py
│       ├── web/
│       │   └── index.html
│       ├── __init__.py
│       └── main.py
├── .gitattributes
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── run.sh
└── uv.lock
```

## Como Iniciar

Na pasta inicial do projeto, basta executar o comando: `./run.sh`