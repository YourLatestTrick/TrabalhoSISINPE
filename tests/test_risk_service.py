
import pytest

from trabalho_g2_sisinpe.api.services.risk_service import (
    classificar_risco
)


def test_situacao_normal():
    result = classificar_risco(25, False)

    assert result["nivel"] == "NORMAL"
    assert result["lixo_detectado"] is False
    assert result["acionar_mecanismo"] is False


@pytest.mark.parametrize(
    "distance",
    [0.1, 1, 2.5, 5.0]
)
def test_detecta_objeto_dentro_do_limite_arduino(distance):
    result = classificar_risco(distance, False)

    assert result["nivel"] == "OBSTRUCAO"
    assert result["lixo_detectado"] is True
    assert result["acionar_mecanismo"] is True


@pytest.mark.parametrize(
    "distance",
    [5.01, 6, 15, 20, 30, 35, 100]
)
def test_nao_aciona_mecanismo_acima_do_limite_arduino(distance):
    result = classificar_risco(distance, False)

    assert result["lixo_detectado"] is False
    assert result["acionar_mecanismo"] is False


def test_detecta_agua():
    result = classificar_risco(25, True)

    assert result["nivel"] == "ALERTA_AGUA"
    assert result["agua_detectada"] is True
    assert result["acionar_alerta"] is True


def test_detecta_objeto_e_agua():
    result = classificar_risco(5, True)

    assert result["nivel"] == "CRITICO"
    assert result["lixo_detectado"] is True
    assert result["agua_detectada"] is True


def test_sensor_sem_leitura():
    result = classificar_risco(None, False)

    assert result["nivel"] == "INDETERMINADO"
    assert result["lixo_detectado"] is None
    assert result["acionar_alerta"] is True
    assert result["acionar_mecanismo"] is False


def test_leitura_negativa():
    result = classificar_risco(-1, False)

    assert result["nivel"] == "INDETERMINADO"
