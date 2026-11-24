from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers import health, telemetry, alerts, control
from .services.database import inicializar_banco
from .services.serial_service import iniciar_monitor_serial, parar_monitor_serial

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_banco()
    iniciar_monitor_serial()
    print("SISINPE API iniciada.")
    yield
    parar_monitor_serial()
    print("SISINPE API encerrada.")


app = FastAPI(
    title="SISINPE API",
    description="API de monitoramento do Sistema Inteligente de Prevenção de Enchentes.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
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
