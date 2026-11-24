import pytest

from trabalho_g2_sisinpe.api.services.risk_service import (
    classificar_risco,
)


def test_situacao_normal():

    resultado = classificar_risco(
        distance_cm=25,
        water_detected=False,
    )

    assert resultado["nivel"] == "NORMAL"

    assert resultado["lixo_detectado"] is False

    assert resultado["agua_detectada"] is False

    assert resultado["acionar_alerta"] is False

    assert resultado["acionar_mecanismo"] is False


def test_detecta_lixo_a_20_cm():

    resultado = classificar_risco(
        distance_cm=20,
        water_detected=False,
    )

    assert resultado["nivel"] == "OBSTRUCAO"

    assert resultado["lixo_detectado"] is True

    assert resultado["acionar_mecanismo"] is True


def test_detecta_lixo_a_15_cm():

    resultado = classificar_risco(
        distance_cm=15,
        water_detected=False,
    )

    assert resultado["lixo_detectado"] is True

    assert resultado["nivel"] == "OBSTRUCAO"


def test_detecta_lixo_a_5_cm():

    resultado = classificar_risco(
        distance_cm=5,
        water_detected=False,
    )

    assert resultado["lixo_detectado"] is True

    assert resultado["acionar_mecanismo"] is True


def test_nao_detecta_lixo_acima_de_20_cm():

    resultado = classificar_risco(
        distance_cm=21,
        water_detected=False,
    )

    assert resultado["lixo_detectado"] is False

    assert resultado["nivel"] == "NORMAL"


def test_distancia_acima_do_alcance():

    resultado = classificar_risco(
        distance_cm=35,
        water_detected=False,
    )

    assert resultado["nivel"] == "NORMAL"

    assert resultado["lixo_detectado"] is False


def test_detecta_agua():

    resultado = classificar_risco(
        distance_cm=25,
        water_detected=True,
    )

    assert resultado["nivel"] == "ALERTA_AGUA"

    assert resultado["agua_detectada"] is True

    assert resultado["acionar_alerta"] is True

    assert resultado["acionar_mecanismo"] is False


def test_detecta_lixo_e_agua():

    resultado = classificar_risco(
        distance_cm=15,
        water_detected=True,
    )

    assert resultado["nivel"] == "CRITICO"

    assert resultado["lixo_detectado"] is True

    assert resultado["agua_detectada"] is True

    assert resultado["acionar_alerta"] is True

    assert resultado["acionar_mecanismo"] is True


def test_sensor_sem_leitura():

    resultado = classificar_risco(
        distance_cm=None,
        water_detected=False,
    )

    assert resultado["nivel"] == "INDETERMINADO"

    assert resultado["lixo_detectado"] is None

    assert resultado["acionar_alerta"] is True

    assert resultado["acionar_mecanismo"] is False


def test_leitura_negativa():

    resultado = classificar_risco(
        distance_cm=-1,
        water_detected=False,
    )

    assert resultado["nivel"] == "INDETERMINADO"

    assert resultado["acionar_alerta"] is True


@pytest.mark.parametrize(
    "distance",
    [
        0,
        1,
        5,
        10,
        15,
        19,
        20,
    ],
)
def test_distancias_que_detectam_lixo(distance):

    resultado = classificar_risco(
        distance_cm=distance,
        water_detected=False,
    )

    assert resultado["lixo_detectado"] is True


@pytest.mark.parametrize(
    "distance",
    [
        20.1,
        21,
        25,
        30,
        30.1,
        50,
        100,
    ],
)
def test_distancias_que_nao_detectam_lixo(distance):

    resultado = classificar_risco(
        distance_cm=distance,
        water_detected=False,
    )

    assert resultado["lixo_detectado"] is False