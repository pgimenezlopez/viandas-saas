from datetime import datetime
from typing import Dict, Any

def calcular_total_carrito(pedido_actual: Dict[str, Dict[str, Any]]) -> float:
    """Calcula la suma total del carrito en base al diccionario de estado."""
    return sum(datos["subtotal"] for datos in pedido_actual.values())

def esta_abierto(hora_actual: datetime, hora_apertura: int, hora_cierre: int) -> bool:
    """Verifica si la hora actual está dentro del rango operativo."""
    return hora_apertura <= hora_actual.hour < hora_cierre