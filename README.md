# SISINPE — Sistema Inteligente de Prevenção de Enchentes

Sistema de monitoramento que utiliza o arduino integrado via USB a uma raspberry pi para detectar enchentes e a presença de lixo em bueiros. Também conta com uma api python para mostrar os alertas em uma interface web.

## Visão Geral
- **Arduino:** lê distância usando o sensor ultrassônico e presença de água usando o sensor de humidade do solo (higrômetro). Quando o sensor ultrassônico detecta lixo na faixa de distância menor que **5.0 cm**, o arduino executa o ciclo do servomotor **3 vezes**. Quando o higrômetro detecta água, o arduino aciona o **LED RGB na cor vermelha** e faz o **buzzer** apitar. Além disso, o arduino envia as leituras pela porta serial.

- **Monitoramento (Python):** executa a leitura contínua dos dados enviados pelo Arduino por meio da porta serial. As informações recebidas são validadas, convertidas para os formatos esperados e encaminhadas para a API, que realiza o processamento das medições, a classificação dos riscos e a geração de alertas quando necessário. Esse processo é executado em uma thread separada, permitindo que o monitoramento aconteça continuamente sem bloquear o funcionamento da API e das demais funcionalidades do sistema. Também permite o funcionamento em modo de simulação quando o Arduino não está conectado.

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
├── bin/
│   └── arduino-cli
├── data/
│   └── sisinpe.db
├── src/
│   └── trabalho_g2_sisinpe/
│       ├── api/
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   ├── alerts.py
│       │   │   ├── control.py
│       │   │   ├── health.py
│       │   │   └── telemetry.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── database.py
│       │   │   ├── monitoring_service.py
│       │   │   ├── risk_service.py
│       │   │   └── serial_service.py
│       │   ├── __init__.py
│       │   └── app.py
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
│   ├── test_api_serial.py
│   ├── test_database_migration.py
│   ├── test_risk_service.py
│   └── test_serial_service.py
├── .coverage
├── .gitattributes
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── run.sh
└── uv.lock
```

## Testes
- Executar os testes automatizados: `uv run pytest -v`

- Executar com relatório de cobertura: `uv run pytest --cov=trabalho_g2_sisinpe --cov-report= team-missing`

## Como Iniciar
Na pasta inicial do projeto, basta executar o comando: `./run.sh`
