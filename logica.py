import json
from datetime import datetime
from typing import Dict, Any, List, Union

def calcular_total_carrito(pedido_actual: Dict[str, Dict[str, Any]]) -> float:
    """Calcula la suma total del carrito en base al diccionario de estado."""
    return sum(datos["subtotal"] for datos in pedido_actual.values())

def esta_abierto(hora_actual: datetime, hora_apertura: int, hora_cierre: int) -> bool:
    """Verifica si la hora actual está dentro del rango operativo."""
    return hora_apertura <= hora_actual.hour < hora_cierre

def parsear_detalle_pedido(detalle: Union[str, Any]) -> List[Dict[str, Union[str, int]]]:
    """
    Parsea el detalle del pedido. Soporta formato JSON actual 
    y hace fallback seguro a texto plano separado por comas (legacy).
    """
    lista_platos = []
    try:
        # Intento como JSON
        items = json.loads(detalle)
        for item in items:
            lista_platos.append({
                "Plato": str(item.get("plato", "")), 
                "Cantidad": int(item.get("cantidad", 0))
            })
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback para pedidos viejos en formato texto
        if isinstance(detalle, str):
            for item in detalle.split(", "):
                if "x " in item:
                    try:
                        cant_str, nombre_plato = item.split("x ", 1)
                        lista_platos.append({
                            "Plato": nombre_plato.strip(), 
                            "Cantidad": int(cant_str)
                        })
                    except ValueError:
                        pass
    return lista_platos