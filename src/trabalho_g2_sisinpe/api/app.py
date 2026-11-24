from contextlib import asynccontextmanager
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parents[1] / "web"

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers import health
from .routers import telemetry
from .routers import alerts
from .routers import control

from .services.database import inicializar_banco

from trabalho_g2_sisinpe.monitoring.monitor import (
    iniciar_monitor,
    parar_monitor,
)


# Caminho correto da pasta web
WEB_DIR = (
    Path(__file__).resolve().parent.parent
    / "web"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    inicializar_banco()
    iniciar_monitor()

    print("SISINPE API iniciada.")

    try:
        yield
    finally:
        parar_monitor()
        print("SISINPE API encerrada.")


app = FastAPI(
    title="SISINPE API",
    description=(
        "API de monitoramento do Sistema Inteligente "
        "de Prevenção de Enchentes."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# Arquivos estáticos do frontend
app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR),
    name="static",
)


# Registro das rotas
app.include_router(health.router)
app.include_router(telemetry.router)
app.include_router(alerts.router)
app.include_router(control.router)


@app.get("/")
def raiz():

    return {
        "sistema": "SISINPE",
        "status": "online",
        "message": "API funcionando.",
        "dashboard": "/dashboard",
        "documentation": "/docs",
    }


@app.get("/dashboard")
def dashboard():
    return FileResponse(WEB_DIR / "index.html")