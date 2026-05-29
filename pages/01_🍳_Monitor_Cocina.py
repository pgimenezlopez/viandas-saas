import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text
from utils.auth import require_auth
from logica import parsear_detalle_pedido # Importamos la nueva lógica

st.set_page_config(page_title="Monitor de Cocina", page_icon="🍳", layout="wide")
st.title("🍳 Monitor de Producción - Viandas")

require_auth()

col_rango, col_btn = st.columns([8, 2])

with col_rango:
    hoy = datetime.date.today()
    hace_una_semana = hoy - datetime.timedelta(days=7)
    fechas_seleccionadas = st.date_input(
        "📅 Filtrar por fecha de pedido:",
        value=(hace_una_semana, hoy),
        max_value=hoy,
        format="DD/MM/YYYY"
    )

@st.cache_data(ttl=60)
def cargar_pedidos(f_inicio: datetime.date, f_fin: datetime.date) -> pd.DataFrame:
    conn = st.connection("sql")
    f_fin_mas_uno = f_fin + datetime.timedelta(days=1)
    query = "SELECT * FROM pedidos WHERE fecha >= :inicio AND fecha < :fin ORDER BY fecha DESC"
    return conn.query(query, params={"inicio": f_inicio, "fin": f_fin_mas_uno}, ttl=0)

with col_btn:
    st.write("")
    if st.button("🔄 Refrescar", use_container_width=True):
        cargar_pedidos.clear()

if len(fechas_seleccionadas) != 2:
    st.warning("Seleccioná el rango completo en el calendario.")
    st.stop()

fecha_inicio, fecha_fin = fechas_seleccionadas

try:
    df_pedidos = cargar_pedidos(fecha_inicio, fecha_fin)
    
    if df_pedidos.empty:
        st.info("No hay pedidos registrados en este rango de fechas.")
        st.stop()
        
    if "estado" not in df_pedidos.columns:
        df_pedidos["estado"] = "Pendiente"

    st.subheader("📊 Resumen Financiero")
    total_recaudado = float(df_pedidos['total'].sum())
    cantidad_pedidos = len(df_pedidos)
    ticket_promedio = total_recaudado / cantidad_pedidos if cantidad_pedidos > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Recaudado", f"${total_recaudado:,.0f}")
    c2.metric("📦 Cantidad de Pedidos", cantidad_pedidos)
    c3.metric("🎫 Ticket Promedio", f"${ticket_promedio:,.0f}")
    st.divider()

    st.subheader("🔥 Consolidado para la Cocina")
    st.caption("Total exacto de porciones a cocinar para evitar mermas.")
    
    # Uso de la lógica extraída, código mucho más DRY
    lista_platos = []
    for detalle in df_pedidos["detalle"]:
        lista_platos.extend(parsear_detalle_pedido(detalle))
                
    if lista_platos:
        df_platos = pd.DataFrame(lista_platos)
        df_consolidado = df_platos.groupby("Plato")["Cantidad"].sum().reset_index()
        df_consolidado = df_consolidado.sort_values(by="Cantidad", ascending=False)
        
        col_tabla, col_grafico = st.columns([1, 2])
        with col_tabla:
            st.dataframe(df_consolidado, use_container_width=True, hide_index=True)
        with col_grafico:
            st.bar_chart(df_consolidado.set_index("Plato"))
            
    st.divider()

    st.subheader("📋 Planilla de Despacho")
    ocultar_completados = st.toggle("Ocultar pedidos completados", value=True)
    
    df_mostrar = df_pedidos.copy()
    if ocultar_completados:
        df_mostrar = df_mostrar[df_mostrar["estado"] != "Completado"]
        
    if df_mostrar.empty:
        st.success("🎉 ¡Excelente trabajo! No hay pedidos pendientes en esta vista.")
    else:
        df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m %H:%M')
        
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
                                    s.execute(text("UPDATE pedidos SET estado = 'Completado' WHERE id = :id"), {"id": int(row['id'])})
                                    s.commit()
                                cargar_pedidos.clear() 
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar estado: {e}")
                    else:
                        st.button("✅ Listo", key=f"btn_done_{row['id']}", disabled=True, use_container_width=True)

except Exception as e:
    st.error(f"Error procesando la información: {e}")