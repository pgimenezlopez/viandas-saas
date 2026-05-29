import json
from datetime import datetime
from typing import Dict, Any, List, Union

def calcular_total_carrito(pedido_actual: Union[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]) -> float:
    """
    Calcula la suma total del carrito. 
    Soporta formato de dict (Streamlit) y formato de lista (Tests/Base de datos).
    Si no encuentra 'subtotal', hace fallback a precio * cantidad.
    """
    total = 0.0
    
    if isinstance(pedido_actual, dict):
        # Para el formato que usa app.py: {"Milanesa": {"cantidad": 2, "subtotal": 980}}
        for datos in pedido_actual.values():
            subtotal = datos.get("subtotal", datos.get("precio", 0) * datos.get("cantidad", 1))
            total += subtotal
            
    elif isinstance(pedido_actual, list):
        # Para el formato que usan los tests o el JSON de la BD: [{"precio": 490, "cantidad": 2}]
        for item in pedido_actual:
            subtotal = item.get("subtotal", item.get("precio", 0) * item.get("cantidad", 1))
            total += subtotal
            
    return total

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