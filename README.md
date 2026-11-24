# SISINPE — Sistema Inteligente de Prevenção de Enchentes

Protótipo de monitoramento de boca de lobo com Arduino conectado por USB a um computador/Raspberry Pi que executa a API Python, banco SQLite e dashboard web.

## Componentes
- Arduino Uno/Nano (firmware em `src/trabalho_g2_sisinpe/arduino/arduino.ino`)
- Sensor ultrassônico (TRIG 12, ECHO 13)
- Sensor de umidade/água (analógico A0 e digital D9)
- Servo (D10), buzzer (D11), LED RGB (D5, D6, D7)
- API FastAPI, SQLite e dashboard

## Regras de funcionamento
- Faixa de percepção do ultrassônico: 30 cm.
- Possível obstrução: distância até 20 cm.
- Até três ciclos do servo para tentar remover a obstrução.
- Após cada ciclo, nova leitura ultrassônica verifica se o objeto deixou a faixa de detecção.
- Água detectada gera alerta.
- Obstrução persistente após três ciclos gera evento `TRASH_REMOVAL_REQUIRED` e alerta crítico.
- Distância inválida gera estado `INDETERMINADO` e alerta de falha do sensor.

**Limitação:** o servo não possui sensor de posição/torque. O firmware considera a tentativa bem-sucedida somente se a leitura ultrassônica indicar que o objeto saiu da faixa de detecção; isso não comprova mecanicamente a rotação ou a remoção do lixo. O valor percentual do sensor de umidade é estimado e precisa de calibração com o componente real.

## Instalação (Windows PowerShell)
Na raiz do projeto:
```powershell
uv sync
```

## Modo simulação (sem Arduino)
```powershell
uv run uvicorn trabalho_g2_sisinpe.api.app:app --reload
```
Acesse:
- Dashboard: http://127.0.0.1:8000/dashboard
- Documentação: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Use a seção **Simulação de sensores** do dashboard ou `POST /telemetry/simulate`.

## Modo hardware
1. Faça upload do firmware para o Arduino.
2. Conecte o Arduino via USB.
3. Identifique a porta no Windows (ex.: `COM5`) ou Linux/Raspberry Pi (ex.: `/dev/ttyACM0`).
4. Configure a variável de ambiente para a porta antes de iniciar a API:

Windows PowerShell:
```powershell
$env:SISINPE_SERIAL_PORT = "COM5"
uv run uvicorn trabalho_g2_sisinpe.api.app:app --reload
```
Linux/Raspberry Pi:
```bash
export SISINPE_SERIAL_PORT=/dev/ttyACM0
uv run uvicorn trabalho_g2_sisinpe.api.app:app --reload
```
Baud rate: 9600. O Arduino envia uma linha JSON por ciclo. Não abra a mesma porta serial no Serial Monitor enquanto a API estiver conectada.

## Testes
```powershell
uv run pytest -v
uv run pytest --cov=trabalho_g2_sisinpe --cov-report=term-missing
uv run pytest --cov=trabalho_g2_sisinpe --cov-report=html
```
Relatório HTML: `htmlcov/index.html`.

## Protocolo serial
Exemplo:
```json
{"distance_cm":12.5,"water_detected":true,"humidity_percent":55,"rotation_attempts":3,"rotation_success":false,"event_code":"TRASH_REMOVAL_REQUIRED"}
```
Campos `distance_cm` e `rotation_success` podem ser `null` quando não aplicáveis/sem leitura. O serviço também aceita temporariamente o protocolo legado `DIST:12.50|WATER:1`.
