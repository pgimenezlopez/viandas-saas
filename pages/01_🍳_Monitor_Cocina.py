import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

st.set_page_config(page_title="Monitor de Cocina", page_icon="🍳", layout="wide")

st.title("🍳 Monitor de Producción - Viandas")

# --- 1. SISTEMA DE LOGIN BÁSICO ---
# Usamos session_state para recordar si el usuario ya puso la clave
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.info("🔒 Acceso exclusivo para el equipo de cocina.")
    clave = st.text_input("Ingresá la contraseña:", type="password")
    if st.button("Entrar", type="primary"):
        # Contraseña quemada en código para este MVP
        if clave == st.secrets["admin_password"]: 
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop() # Si no está logueado, la app se detiene acá.


# --- 2. LÓGICA DEL DASHBOARD Y FILTROS ---

# Interfaz para el filtro de fechas
col_rango, col_btn = st.columns([8, 2])

with col_rango:
    # Por defecto mostramos los últimos 7 días para no mezclar métricas históricas
    hoy = datetime.date.today()
    hace_una_semana = hoy - datetime.timedelta(days=7)
    
    fechas_seleccionadas = st.date_input(
        "📅 Filtrar por fecha de pedido:",
        value=(hace_una_semana, hoy),
        max_value=hoy,
        format="DD/MM/YYYY"
    )

with col_btn:
    st.write("") # Espaciador para alinear el botón verticalmente con el input
    if st.button("🔄 Refrescar", use_container_width=True):
        st.cache_data.clear()

# st.date_input devuelve una tupla. Nos aseguramos de que el usuario haya seleccionado inicio y fin
if len(fechas_seleccionadas) != 2:
    st.warning("Seleccioná el rango completo (fecha de inicio y fin) en el calendario.")
    st.stop()

fecha_inicio, fecha_fin = fechas_seleccionadas

# Función con caché que invalida los datos si cambian las fechas solicitadas
@st.cache_data(ttl=60)
def cargar_pedidos(f_inicio, f_fin):
    conn = st.connection("sql")
    
    # Le sumamos 1 día a la fecha fin para que el SQL incluya los pedidos de hoy hasta las 23:59:59
    f_fin_mas_uno = f_fin + datetime.timedelta(days=1)
    
    # Inyección segura de parámetros usando la API de Streamlit connections
    query = "SELECT * FROM pedidos WHERE fecha >= :inicio AND fecha < :fin ORDER BY fecha DESC"
    df = conn.query(query, params={"inicio": f_inicio, "fin": f_fin_mas_uno}, ttl=0)
    return df

try:
    df_pedidos = cargar_pedidos(fecha_inicio, fecha_fin)
    
    if df_pedidos.empty:
        st.info("No hay pedidos registrados en este rango de fechas.")
        st.stop()

    # --- 3. MÉTRICAS GENERALES (Facturación) ---
    st.subheader("📊 Resumen Financiero")
    
    total_recaudado = df_pedidos['total'].sum()
    cantidad_pedidos = len(df_pedidos)
    ticket_promedio = total_recaudado / cantidad_pedidos if cantidad_pedidos > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Recaudado", f"${total_recaudado:,.0f}")
    c2.metric("📦 Cantidad de Pedidos", cantidad_pedidos)
    c3.metric("🎫 Ticket Promedio", f"${ticket_promedio:,.0f}")
    
    st.divider()

    # --- 4. CONSOLIDADOR DE OLLAS (Pandas Magic) ---
    st.subheader("🔥 Consolidado para la Cocina")
    st.caption("Total exacto de porciones a cocinar para evitar mermas.")
    
    lista_platos = []
    
    # Recorremos la columna 'detalle' de todos los pedidos
    for detalle in df_pedidos['detalle']:
        # Separamos los platos de un mismo pedido por la coma
        items = detalle.split(", ")
        for item in items:
            if "x " in item:
                # Separamos "2x Pollo" en "2" y "Pollo"
                cant_str, nombre_plato = item.split("x ", 1)
                lista_platos.append({
                    "Plato": nombre_plato.strip(),
                    "Cantidad": int(cant_str)
                })
                
    if lista_platos:
        df_platos = pd.DataFrame(lista_platos)
        # Agrupamos por plato y sumamos las cantidades
        df_consolidado = df_platos.groupby("Plato")["Cantidad"].sum().reset_index()
        # Ordenamos para que los que más salen queden arriba
        df_consolidado = df_consolidado.sort_values(by="Cantidad", ascending=False)
        
        col_tabla, col_grafico = st.columns([1, 2])
        with col_tabla:
            st.dataframe(df_consolidado, use_container_width=True, hide_index=True)
        with col_grafico:
            st.bar_chart(df_consolidado.set_index("Plato"))
            
    st.divider()

    # --- 5. DETALLE CLIENTE POR CLIENTE ---
    st.subheader("📋 Planilla de Despacho")
    st.caption("Detalle para armado de bolsas y cobranza.")
    
    # Filtramos columnas para no mostrar el ID interno
    df_mostrar = df_pedidos[['fecha', 'nombre', 'celular', 'barrio', 'forma_pago', 'detalle', 'total', 'notas']].copy()
    
    # Formateamos la fecha para que sea más legible en Uruguay
    df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m %H:%M')
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al conectar con la base de datos o procesar la información: {e}")