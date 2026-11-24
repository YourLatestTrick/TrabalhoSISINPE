from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def verificar_saude():
    """
    Verifica se a API está funcionando.
    """

    return {
        "status": "online",
        "sistema": "SISINPE",
        "mensagem": "API funcionando corretamente.",
    }

@router.get("/serial/status")
def status_serial():
    from ..services.serial_service import verificar_disponibilidade

    return verificar_disponibilidade()


@router.post("/serial/status")
def atualizar_status_serial(payload: dict):
    from ..services.serial_service import atualizar_estado_conexao

    return atualizar_estado_conexao(
        payload.get("connected", False),
        payload.get("message"),
        payload.get("port"),
    )