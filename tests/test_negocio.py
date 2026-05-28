# tests/test_negocio.py
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
# Importación real de tu lógica de negocio
from logica import calcular_total_carrito, esta_abierto

def test_calculo_carrito_con_varios_items():
    carrito = [
        {"nombre": "Pastel de papa", "cantidad": 2, "precio": 350},
        {"nombre": "Milanesa de soja", "cantidad": 1, "precio": 280}
    ]
    total = calcular_total_carrito(carrito)
    assert total == 980

def test_calculo_carrito_vacio_da_cero():
    assert calcular_total_carrito([]) == 0

def test_barrera_horaria_apertura_permitida():
    hora_pedido = datetime(2026, 5, 28, 11, 30, tzinfo=ZoneInfo("America/Montevideo"))
    assert esta_abierto(hora_pedido, 10, 23) is True

def test_barrera_horaria_madrugada_bloqueada():
    hora_pedido = datetime(2026, 5, 28, 2, 15, tzinfo=ZoneInfo("America/Montevideo"))
    assert esta_abierto(hora_pedido, 10, 23) is False

def test_barrera_horaria_limite_cierre():
    hora_pedido = datetime(2026, 5, 28, 23, 0, tzinfo=ZoneInfo("America/Montevideo"))
    assert esta_abierto(hora_pedido, 10, 23) is False