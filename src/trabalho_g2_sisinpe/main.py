import uvicorn


def main():
    """Ponto de entrada para executar a API e dashboard do SISINPE."""
    uvicorn.run(
        "trabalho_g2_sisinpe.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
