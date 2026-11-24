# SISINPE — Sistema Inteligente de Prevenção de Enchentes

Sistema de monitoramento que utiliza o arduino integrado via USB a uma raspberry pi para detectar enchentes e a presença de lixo em bueiros. Também conta com uma api python para mostrar os alertas em uma interface web.

## Visão Geral
- **Arduino:** lê distância usando o sensor ultrassônico e presença de água usando o sensor de humidade do solo (higrômetro). Quando o sensor ultrassônico detecta lixo na faixa de distância menor que **5.0 cm**, o arduino executa o ciclo do servomotor **3 vezes**. Quando o higrômetro detecta água, o arduino aciona o **LED RGB na cor vermelha** e faz o **buzzer** apitar. Além disso, o arduino envia as leituras pela porta serial.

- **Monitoramento (Python):** lê a porta serial, valida/converte os dados e gera os eventos **flood_alert** e **trash_needs_pickup** para serem usados na api.

## Componentes físicos
- Raspberry Pi
- Arduino Uno
- Sensor ultrassônico
- Sensor de umidade do solo (higrômetro)
- Servomotor
- Led RGB
- Buzzer

## Estrutura do Projeto
```text
trabalho_g2_sisinpe/
├── .venv/
├── bin/
│   └── arduino-cli
├── src/
│   └── trabalho_g2_sisinpe/
│       ├── api/
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   └── router.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── service.py
│       │   └── __init__.py
│       ├── arduino/
│       │   └── arduino.ino
│       ├── monitoring/
│       │   ├── __init__.py
│       │   └── monitor.py
│       ├── web/
│       │   ├── index.html
│       │   ├── script.js
│       │   └── style.css
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── __init__.py
├── .gitattributes
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── run.sh
└── uv.lock
```

## Testes
```
colocar os testes
```

## Como Iniciar
Na pasta inicial do projeto, basta executar o comando: `./run.sh`
