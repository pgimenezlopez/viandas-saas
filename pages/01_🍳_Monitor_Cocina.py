import streamlit as st
import pandas as pd
import datetime
import json
from sqlalchemy import text
from utils.auth import require_auth


st.set_page_config(page_title="Monitor de Cocina", page_icon="🍳", layout="wide")

st.title("🍳 Monitor de Producción - Viandas")

# --- 1. SISTEMA DE LOGIN BÁSICO ---
require_auth()


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
        
    # Tolerancia a fallos por si no existe la columna estado en la BD aún
    if "estado" not in df_pedidos.columns:
        df_pedidos["estado"] = "Pendiente"

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
    
 
    # Recorremos la columna 'detalle' de todos los pedidos

    lista_platos = []
    for detalle in df_pedidos["detalle"]:
        try:
            items = json.loads(detalle)
            for item in items:
                lista_platos.append({
                    "Plato": item["plato"],
                    "Cantidad": item["cantidad"]
                })
        except (json.JSONDecodeError, KeyError):
            # Tolerancia a pedidos históricos con formato "2x Pollo, 1x Milanesa"
            for item in detalle.split(", "):
                if "x " in item:
                    cant_str, nombre_plato = item.split("x ", 1)
                    try:
                        lista_platos.append({"Plato": nombre_plato.strip(), "Cantidad": int(cant_str)})
                    except ValueError:
                        pass
                
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
    
    # Toggle para ocultar los pedidos que ya fueron despachados
    ocultar_completados = st.toggle("Ocultar pedidos completados", value=True)
    
    df_mostrar = df_pedidos.copy()
    if ocultar_completados:
        df_mostrar = df_mostrar[df_mostrar["estado"] != "Completado"]
        
    if df_mostrar.empty:
        st.success("🎉 ¡Excelente trabajo! No hay pedidos pendientes en esta vista.")
    else:
        # Formateamos la fecha para que sea más legible en Uruguay
        df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m %H:%M')
        
        # Iteramos sobre los pedidos para crear "tarjetas" interactivas
        for _, row in df_mostrar.iterrows():
            with st.container(border=True):
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**{row['nombre']}** - 📍 {row['barrio']} 📞 {row['celular']}")
                    st.markdown(f"📦 **Pedido:** {row['detalle']}")
                    if pd.notna(row['notas']) and str(row['notas']).strip() != "":
                        st.warning(f"⚠️ Aclaraciones: {row['notas']}")
                    st.caption(f"🕒 {row['fecha']} | 💰 ${row['total']} | 💳 {row['forma_pago']}")
                
                with col_btn:
                    if row["estado"] != "Completado":
                        if st.button("✔️ Listo", key=f"btn_{row['id']}", use_container_width=True, type="primary"):
                            try:
                                conn = st.connection("sql")
                                with conn.session as s:
                                    s.execute(text("UPDATE pedidos SET estado = 'Completado' WHERE id = :id"), {"id": row['id']})
                                    s.commit()
                                st.cache_data.clear() # Limpiar la caché para que recargue la lista
                                st.rerun()
                            except Exception as e:
                                st.error(f"⚠️ ¿Agregaste la columna 'estado' a tu tabla 'pedidos' en Supabase? Detalle: {e}")
                    else:
                        st.button("✅ Listo", key=f"btn_done_{row['id']}", disabled=True, use_container_width=True)

except Exception as e:
    st.error(f"Error al conectar con la base de datos o procesar la información: {e}")