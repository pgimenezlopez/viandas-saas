import streamlit as st
import pandas as pd
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
        if clave == "cocina2026": 
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop() # Si no está logueado, la app se detiene acá.

# --- 2. LÓGICA DEL DASHBOARD ---

# Botón para refrescar datos manualmente
col_title, col_btn = st.columns([8, 2])
with col_btn:
    if st.button("🔄 Refrescar Pedidos", use_container_width=True):
        st.cache_data.clear()

# Función con caché para no saturar Supabase con consultas repetidas
@st.cache_data(ttl=60)
def cargar_pedidos():
    conn = st.connection("sql")
    df = conn.query("SELECT * FROM pedidos ORDER BY fecha DESC", ttl=0)
    return df

try:
    df_pedidos = cargar_pedidos()
    
    if df_pedidos.empty:
        st.warning("Aún no hay pedidos registrados en la base de datos.")
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