"""
Serviço de classificação das condições do SISINPE.
"""

DISTANCIA_MAXIMA_PERCEPCAO_CM = 30.0
DISTANCIA_DETECCAO_LIXO_CM = 20.0

MAX_TENTATIVAS_DESOBSTRUCA = 3


def classificar_risco(distance_cm=None, water_detected=False):
    """
    Classifica as condições detectadas pelos sensores.

    Ultrassônico:
        <= 20 cm: possível lixo
        > 20 cm: lixo não identificado
        > 30 cm: fora da faixa de percepção

    Sensor de umidade:
        True: água detectada
        False: sensor seco

    """

    agua_detectada = bool(water_detected)

    # Falha ou ausência de leitura
    if distance_cm is None:

        return {
            "nivel": "INDETERMINADO",
            "descricao": "Sensor ultrassônico sem leitura.",
            "lixo_detectado": None,
            "agua_detectada": agua_detectada,
            "acionar_alerta": True,
            "acionar_mecanismo": False,
        }

    # Leitura inválida
    if distance_cm < 0:

        return {
            "nivel": "INDETERMINADO",
            "descricao": "Leitura inválida do sensor ultrassônico.",
            "lixo_detectado": None,
            "agua_detectada": agua_detectada,
            "acionar_alerta": True,
            "acionar_mecanismo": False,
        }

    # Distância fora do alcance esperado
    if distance_cm > DISTANCIA_MAXIMA_PERCEPCAO_CM:

        lixo_detectado = False

    else:

        lixo_detectado = (
            distance_cm <= DISTANCIA_DETECCAO_LIXO_CM
        )

    # Lixo e água detectados simultaneamente
    if lixo_detectado and agua_detectada:

        return {
            "nivel": "CRITICO",
            "descricao": (
                "Lixo detectado próximo à boca de lobo "
                "e presença de água na galeria."
            ),
            "lixo_detectado": True,
            "agua_detectada": True,
            "acionar_alerta": True,
            "acionar_mecanismo": True,
        }

    # Lixo detectado
    if lixo_detectado:

        return {
            "nivel": "OBSTRUCAO",
            "descricao": (
                "Possível acúmulo de lixo detectado. "
                "Desobstrução necessária."
            ),
            "lixo_detectado": True,
            "agua_detectada": False,
            "acionar_alerta": False,
            "acionar_mecanismo": True,
        }

    # Água detectada
    if agua_detectada:

        return {
            "nivel": "ALERTA_AGUA",
            "descricao": (
                "Sensor de umidade detectou contato com água."
            ),
            "lixo_detectado": False,
            "agua_detectada": True,
            "acionar_alerta": True,
            "acionar_mecanismo": False,
        }

    # Nenhuma condição de risco
    return {
        "nivel": "NORMAL",
        "descricao": (
            "Nenhum lixo detectado e sensor de umidade seco."
        ),
        "lixo_detectado": False,
        "agua_detectada": False,
        "acionar_alerta": False,
        "acionar_mecanismo": False,
    }