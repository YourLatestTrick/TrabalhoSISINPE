const API_URL = "";

let apiOnline = false;


function formatarData(data) {

    if (!data) {
        return "--";
    }

    const date = new Date(data);

    return date.toLocaleString("pt-BR");
}


function atualizarTexto(id, texto) {

    const elemento = document.getElementById(id);

    if (elemento) {
        elemento.textContent = texto;
    }

}


async function carregarStatus() {

    try {

        const response = await fetch(
            `${API_URL}/health`
        );

        if (!response.ok) {
            throw new Error("API indisponível");
        }

        const data = await response.json();

        apiOnline = true;

        atualizarTexto(
            "connection-status",
            `API: ${data.status.toUpperCase()} | SERIAL: SIMULAÇÃO`
        );

        const serialResponse = await fetch(`${API_URL}/control/status`);
        if (serialResponse.ok) {
            const control = await serialResponse.json();
            const serial = control.serial || {};
            atualizarTexto(
                "connection-status",
                `API: ONLINE | SERIAL: ${serial.connected ? "CONECTADA" : serial.mode || "SIMULAÇÃO"}`
            );
        }

    } catch (error) {

        apiOnline = false;

        atualizarTexto(
            "connection-status",
            "API: OFFLINE"
        );

    }

}


async function carregarTelemetria() {

    try {

        const response = await fetch(
            `${API_URL}/telemetry/latest`
        );

        if (!response.ok) {
            throw new Error("Erro na telemetria");
        }

        const resultado = await response.json();

        const medicao = resultado.data;

        if (!medicao) {

            atualizarTexto("distance", "-- cm");
            atualizarTexto("water", "--");
            atualizarTexto("risk", "--");
            atualizarTexto("attempts", "--");
            atualizarTexto("mechanism", "--");

            atualizarTexto(
                "measurement-time",
                "Nenhuma medição registrada."
            );

            return;
        }

        atualizarTexto(
            "distance",
            `${medicao.distance_cm ?? "--"} cm`
        );

        atualizarTexto(
            "water",
            medicao.water_detected
                ? "ÁGUA DETECTADA"
                : "SECO"
        );

        atualizarTexto(
            "risk",
            medicao.risk_level ?? "--"
        );

        atualizarTexto(
            "attempts",
            medicao.rotation_attempts ?? "--"
        );

        atualizarTexto(
            "mechanism",
            medicao.rotation_success === true
                ? "Desobstruído"
                : medicao.rotation_success === false
                    ? "Falha"
                    : "Aguardando"
        );

        atualizarTexto(
            "measurement-time",
            formatarData(medicao.created_at)
        );

        atualizarTexto(
            "measurement-details",
            `ID da medição: ${medicao.id}`
        );

    } catch (error) {

        console.error(
            "Erro ao carregar telemetria:",
            error
        );

    }

}


async function carregarAlertas() {

    try {

        const response = await fetch(
            `${API_URL}/alerts`
        );

        if (!response.ok) {
            throw new Error("Erro ao carregar alertas");
        }

        const resultado = await response.json();

        const container = document.getElementById(
            "alerts"
        );

        container.innerHTML = "";

        if (!resultado.data || resultado.data.length === 0) {

            container.textContent = "Nenhum alerta registrado.";

            return;

        }

        resultado.data.forEach(alerta => {

            const item = document.createElement("div");

            item.className = "item";

            if (alerta.severity === "CRITICAL") {
                item.classList.add("critical");
            }

            if (alerta.severity === "WARNING") {
                item.classList.add("warning");
            }

            const texto = document.createElement("p");

            texto.textContent = (
                `${alerta.alert_type}: ${alerta.description}`
            );

            item.appendChild(texto);

            const status = document.createElement("small");

            status.textContent = `Status: ${alerta.status}`;

            item.appendChild(status);

            container.appendChild(item);

        });

    } catch (error) {

        console.error(
            "Erro ao carregar alertas:",
            error
        );

    }

}


async function carregarEventos() {

    try {

        const response = await fetch(
            `${API_URL}/events`
        );

        if (!response.ok) {
            throw new Error("Erro ao carregar eventos");
        }

        const resultado = await response.json();

        const container = document.getElementById(
            "events"
        );

        container.innerHTML = "";

        if (!resultado.data || resultado.data.length === 0) {

            container.textContent = "Nenhum evento registrado.";

            return;

        }

        resultado.data.forEach(evento => {

            const item = document.createElement("div");

            item.className = "item";

            item.textContent = (
                `${evento.event_type}: ${evento.description}`
            );

            container.appendChild(item);

        });

    } catch (error) {

        console.error(
            "Erro ao carregar eventos:",
            error
        );

    }

}


async function atualizarDashboard() {

    await carregarStatus();

    if (!apiOnline) {
        return;
    }

    await Promise.all([
        carregarTelemetria(),
        carregarAlertas(),
        carregarEventos(),
    ]);

}


document.getElementById(
    "simulation-form"
).addEventListener("submit", async function(event) {

    event.preventDefault();

    const form = event.target;

    const payload = {

        distance_cm: Number(
            form.elements["distance_cm"].value
        ),

        water_detected:
            form.elements["water_detected"].value === "true",

        rotation_attempts: Number(
            form.elements["rotation_attempts"].value
        ),

        rotation_success:
            form.elements["rotation_success"].value === ""
                ? null
                : form.elements["rotation_success"].value === "true",

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
                    "Content-Type": "application/json",
                },

                body: JSON.stringify(payload),
            }
        );

        const resultado = await response.json();

        if (!response.ok) {

            throw new Error(
                resultado.detail || "Erro na simulação"
            );

        }

        resultElement.textContent = (
            resultado.message
        );

        await atualizarDashboard();

    } catch (error) {

        resultElement.textContent = (
            `Erro: ${error.message}`
        );

        console.error(error);

    }

});


atualizarDashboard();


// Atualização automática a cada 5 segundos
setInterval(
    atualizarDashboard,
    5000
);