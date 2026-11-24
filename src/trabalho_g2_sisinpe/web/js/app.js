
const API_URL = "";

let apiOnline = false;

function formatarData(data) {
    if (!data) return "--";

    const date = new Date(data);

    return Number.isNaN(date.getTime())
        ? data
        : date.toLocaleString("pt-BR");
}

function atualizarTexto(id, texto) {
    const elemento = document.getElementById(id);

    if (elemento) {
        elemento.textContent = texto;
    }
}

async function requisicaoJson(url) {
    const response = await fetch(url, {
        cache: "no-store"
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}

async function carregarStatus() {
    try {
        const data = await requisicaoJson(
            `${API_URL}/health`
        );

        apiOnline = true;

        atualizarTexto(
            "connection-status",
            `API: ${data.status.toUpperCase()}`
        );

    } catch (error) {
        apiOnline = false;

        atualizarTexto(
            "connection-status",
            "API: OFFLINE"
        );

        atualizarTexto(
            "serial-status",
            "Arduino: indisponível (API offline)"
        );
    }
}

async function carregarStatusSerial() {
    try {
        const data = await requisicaoJson(
            `${API_URL}/serial/status`
        );

        const status = data.connected
            ? "CONECTADO"
            : "DESCONECTADO";

        atualizarTexto(
            "serial-status",
            `Arduino: ${status} (${data.port || "porta não definida"})`
        );

    } catch (error) {
        atualizarTexto(
            "serial-status",
            "Arduino: status indisponível"
        );
    }
}

async function carregarTelemetria() {
    try {
        const resultado = await requisicaoJson(
            `${API_URL}/telemetry/latest`
        );

        const medicao = resultado.data;

        if (!medicao) {
            [
                "distance",
                "water",
                "risk",
                "attempts",
                "mechanism"
            ].forEach(id => atualizarTexto(id, "--"));

            atualizarTexto(
                "measurement-time",
                "Nenhuma medição registrada."
            );

            atualizarTexto("measurement-details", "--");

            return;
        }

        atualizarTexto(
            "distance",
            medicao.distance_cm == null
                ? "Sem leitura"
                : `${Number(medicao.distance_cm).toFixed(2)} cm`
        );

        atualizarTexto(
            "water",
            medicao.water_detected
                ? "ÁGUA DETECTADA"
                : "SECO"
        );

        atualizarTexto(
            "risk",
            medicao.risk_level || "--"
        );

        atualizarTexto(
            "attempts",
            `${medicao.rotation_attempts ?? 0} / 3`
        );

        const mechanism =
            medicao.rotation_success === true
                ? "Sucesso (objeto fora da faixa)"
                : medicao.rotation_success === false
                    ? "Falha após tentativas"
                    : "Não acionado nesta leitura";

        atualizarTexto("mechanism", mechanism);

        atualizarTexto(
            "measurement-time",
            formatarData(medicao.created_at)
        );

        atualizarTexto(
            "measurement-details",
            `Medição #${medicao.id} | Evento: ${medicao.event_code || "nenhum"}`
        );

    } catch (error) {
        console.error(
            "Erro ao carregar telemetria:",
            error
        );
    }
}

function preencherLista(
    containerId,
    items,
    formatter,
    emptyText
) {
    const container = document.getElementById(containerId);

    if (!container) return;

    container.replaceChildren();

    if (!items || items.length === 0) {
        container.textContent = emptyText;
        return;
    }

    items.forEach(itemData => {
        const item = document.createElement("div");

        item.className = "item";

        formatter(item, itemData);

        container.appendChild(item);
    });
}

async function carregarAlertas() {
    try {
        const resultado = await requisicaoJson(
            `${API_URL}/alerts`
        );

        preencherLista(
            "alerts",
            resultado.data,
            (item, alerta) => {
                if (alerta.severity === "CRITICAL") {
                    item.classList.add("critical");
                } else if (
                    alerta.severity === "WARNING" ||
                    alerta.severity === "HIGH"
                ) {
                    item.classList.add("warning");
                }

                const title = document.createElement("strong");

                title.textContent =
                    `${alerta.alert_type} — ${alerta.severity}`;

                const description = document.createElement("p");

                description.textContent = alerta.description;

                const status = document.createElement("small");

                status.textContent =
                    `Status: ${alerta.status} | ${formatarData(alerta.created_at)}`;

                item.append(title, description, status);
            },
            "Nenhum alerta registrado."
        );

    } catch (error) {
        console.error("Erro ao carregar alertas:", error);
    }
}

async function carregarEventos() {
    try {
        const resultado = await requisicaoJson(
            `${API_URL}/events`
        );

        preencherLista(
            "events",
            resultado.data,
            (item, evento) => {
                const title = document.createElement("strong");

                title.textContent = evento.event_type;

                const description = document.createElement("p");

                description.textContent = evento.description;

                const date = document.createElement("small");

                date.textContent = formatarData(evento.created_at);

                item.append(title, description, date);
            },
            "Nenhum evento registrado."
        );

    } catch (error) {
        console.error("Erro ao carregar eventos:", error);
    }
}

async function atualizarDashboard() {
    await carregarStatus();

    if (!apiOnline) return;

    await Promise.all([
        carregarStatusSerial(),
        carregarTelemetria(),
        carregarAlertas(),
        carregarEventos()
    ]);
}

// Simulação manual.
const simulationForm = document.getElementById("simulation-form");

if (simulationForm) {
    simulationForm.addEventListener("submit", async event => {
        event.preventDefault();

        const form = event.currentTarget;

        const payload = {
            distance_cm: Number(form.elements.distance_cm.value),

            water_detected:
                form.elements.water_detected.value === "true",

            rotation_attempts:
                Number(form.elements.rotation_attempts.value),

            rotation_success:
                form.elements.rotation_success.value === ""
                    ? null
                    : form.elements.rotation_success.value === "true",

            event_code:
                Number(form.elements.rotation_attempts.value) === 3 &&
                form.elements.rotation_success.value === "false"
                    ? "TRASH_REMOVAL_REQUIRED"
                    : null
        };

        const resultElement = document.getElementById(
            "simulation-result"
        );

        resultElement.textContent = "Enviando...";

        try {
            const response = await fetch(
                `${API_URL}/telemetry/simulate`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(payload)
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.detail || "Erro na simulação"
                );
            }

            resultElement.textContent =
                "Medição simulada e registrada com sucesso.";

            await atualizarDashboard();

        } catch (error) {
            resultElement.textContent =
                `Erro: ${error.message}`;
        }
    });
}

atualizarDashboard();

setInterval(atualizarDashboard, 5000);
