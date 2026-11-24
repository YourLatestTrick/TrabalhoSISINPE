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