# logica.py
from datetime import datetime
from zoneinfo import ZoneInfo

def calcular_total_carrito(carrito):
    """Calcula la suma total del carrito."""
    return sum(item["cantidad"] * item["precio"] for item in carrito)

def esta_abierto(hora_actual, hora_apertura, hora_cierre):
    """Verifica si la hora actual está dentro del rango operativo."""
    return hora_apertura <= hora_actual.hour < hora_cierre