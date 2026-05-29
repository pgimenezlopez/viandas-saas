import urllib.parse
import requests
import streamlit as st
import pandas as pd
import logging
import json
from logica import calcular_total_carrito, esta_abierto
from sqlalchemy import text
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Cadalu - Sistema de Viandas",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #fffaf1; }
    .stButton>button {
        background-color: #f9a8b1;
        color: white;
        border-radius: 20px;
        border: none;
        font-weight: bold;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    conn = st.connection("sql")
except Exception:
    st.error("🔴 Error crítico: No se pudo establecer la conexión con la base de datos.")
    st.stop()

if "pedido_confirmado" not in st.session_state:
    st.session_state.pedido_confirmado = False
if "limpiar_carrito" not in st.session_state:
    st.session_state.limpiar_carrito = False

if st.session_state.limpiar_carrito:
    # Se hace list() para no mutar el dict mientras se itera
    keys_a_borrar = [k for k in st.session_state.keys() if k.startswith("item_")]
    for key in keys_a_borrar:
        del st.session_state[key]
    st.session_state.limpiar_carrito = False

col_izq, col_centro, col_der = st.columns([1, 1.5, 1])
with col_centro:
    st.image("assets/logo_cadalu.png", use_container_width=True)

st.info("""
🛵 **Entregas y Logística:**
* **Mediodía:** Exclusivo en oficinas.
* **Noche:** Envíos a domicilio (coordinar por WhatsApp).
""")
st.divider()

if st.session_state.pedido_confirmado:
    st.success("🎉 ¡Tu pedido fue registrado en la cocina con éxito!")
    st.balloons()

    numero_cocina = st.secrets.get("whatsapp_cocina", "")
    mensaje_wa = (
        f"🍱 *Nuevo Pedido Web - Cadalu*\n\n"
        f"👤 *Cliente:* {st.session_state.get('ultimo_nombre', '')}\n"
        f"📞 *Celular:* {st.session_state.get('ultimo_celular', '')}\n"
        f"📍 *Dirección:* {st.session_state.get('ultimo_direccion', '')} ({st.session_state.get('ultimo_barrio', '')})\n"
        f"💰 *Total:* ${st.session_state.get('ultimo_total', 0)}\n"
        f"💳 *Pago:* {st.session_state.get('ultimo_pago', '')}\n\n"
        f"📋 *Detalle:* {st.session_state.get('ultimo_resumen', '')}\n"
        f"💡 *Notas:* {st.session_state.get('ultimo_notas', 'Ninguna')}"
    )
    url_wa = f"https://wa.me/{numero_cocina}?text={urllib.parse.quote(mensaje_wa)}"

    st.link_button("📲 Enviar confirmación por WhatsApp", url_wa, use_container_width=True, type="primary")
    st.caption("Es necesario tocar el botón para coordinar el horario de entrega con la cocina.")

    if st.button("⬅️ Hacer otro pedido"):
        st.session_state.pedido_confirmado = False
        st.rerun()
    st.stop()

@st.cache_data(ttl=15)
def obtener_menu() -> pd.DataFrame:
    return conn.query("SELECT plato, descripcion, precio, stock FROM menu_semanal WHERE disponible = TRUE ORDER BY id ASC", ttl=0)

try:
    df_menu = obtener_menu()
except Exception as e:
    st.error(f"Error al conectar con la cocina: {e}")
    df_menu = pd.DataFrame()

st.divider()

zona_mvd = ZoneInfo("America/Montevideo")
ahora = datetime.now(zona_mvd)
HORA_APERTURA = 8
HORA_CIERRE = 22

pedido_actual = {}

if esta_abierto(ahora, HORA_APERTURA, HORA_CIERRE):
    st.subheader("🍽️ Menú Disponible")

    if df_menu.empty:
        st.info("El menú se está actualizando. ¡Volvé pronto!")
    else:
        for index, row in df_menu.iterrows():
            col_texto, col_boton = st.columns([3, 1])
            with col_texto:
                st.markdown(f"**{row['plato']}** - **${row['precio']}**")
                st.caption(row['descripcion'])
            
            with col_boton:
                stock_actual = int(row['stock']) if pd.notna(row.get('stock')) else 20
                
                if stock_actual > 0:
                    cantidad = st.number_input(
                        "Cant.", 
                        min_value=0, 
                        max_value=stock_actual,
                        value=0,
                        key=f"item_{index}", 
                        label_visibility="collapsed"
                    )
                    if cantidad > 0:
                        pedido_actual[str(row['plato'])] = {"cantidad": cantidad, "subtotal": cantidad * float(row['precio'])}
                else:
                    st.error("Agotado", icon="🚫")
            st.write("")

    st.divider()

    total_pesos = calcular_total_carrito(pedido_actual)

    if total_pesos > 0:
        st.subheader("🛒 Tu Pedido")
        for plato, datos in pedido_actual.items():
            st.write(f"✔️ **{datos['cantidad']}x** {plato} = **${datos['subtotal']}**")

        st.markdown(f"### Total: **${total_pesos}**")

        with st.form("form_pedido"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nombre = st.text_input("Nombre y Apellido").strip()
                celular = st.text_input("Celular").strip()
            with col_f2:
                direccion = st.text_input("Dirección de entrega").strip()
                barrio = st.selectbox("Barrio", ["Centro", "Cordón", "Pocitos", "Buceo", "Malvín", "Oficinas (Centro)", "Otro"])

            forma_pago = st.radio("Forma de Pago:", ["💵 Efectivo", "🏦 Transferencia", "📱 MercadoPago"], horizontal=True)
            notas = st.text_area("Aclaraciones (Ej: Sin sal, timbre no anda, etc.)")

            if st.form_submit_button("🚀 Confirmar Pedido", type="primary", use_container_width=True):
                if nombre and direccion and celular:
                    with st.spinner("Enviando pedido a cocina..."):
                        try:
                            resumen_legible = ", ".join([f"{d['cantidad']}x {p}" for p, d in pedido_actual.items()])
                            detalle_json = json.dumps(
                                [{"plato": p, "cantidad": d["cantidad"], "subtotal": d["subtotal"]}
                                for p, d in pedido_actual.items()],
                                ensure_ascii=False
                            )
                            agotado = None

                            with conn.session as s:
                                platos_ordenados = sorted(pedido_actual.keys())
                                
                                for plato_nombre in platos_ordenados:
                                    datos = pedido_actual[plato_nombre]
                                    resultado = s.execute(
                                        text("SELECT stock FROM menu_semanal WHERE plato = :p FOR UPDATE"),
                                        {"p": plato_nombre}
                                    ).fetchone()

                                    if not resultado or resultado.stock < datos["cantidad"]:
                                        s.rollback()
                                        agotado = plato_nombre
                                        break

                                    s.execute(
                                        text("UPDATE menu_semanal SET stock = stock - :cant WHERE plato = :p"),
                                        {"cant": datos["cantidad"], "p": plato_nombre}
                                    )

                                if agotado is None:
                                    s.execute(
                                        text("""INSERT INTO pedidos (nombre, celular, direccion, barrio, forma_pago, detalle, total, notas)
                                                VALUES (:n, :c, :d, :b, :fp, :det, :t, :not)"""),
                                        {"n": nombre, "c": celular, "d": direccion, "b": barrio,
                                        "fp": forma_pago, "det": detalle_json, "t": total_pesos, "not": notas}
                                    )
                                    s.commit()

                            if agotado is not None:
                                st.error(f"⚠️ '{agotado}' se agotó justo ahora. Actualizá la página.")
                                st.stop()
                                
                            obtener_menu.clear() 

                            try:
                                telegram_token = st.secrets.get("TELEGRAM_TOKEN")
                                telegram_chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
                                if telegram_token and telegram_chat_id:
                                    mensaje_tg = f"🔔 *Nuevo Pedido*\n👤 {nombre}\n📍 {direccion}\n🍽️ {resumen_legible}"
                                    requests.post(
                                        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                                        data={"chat_id": telegram_chat_id, "text": mensaje_tg, "parse_mode": "Markdown"},
                                        timeout=5
                                    )
                            except Exception as e:
                                logger.error("Telegram fallback falló: %s", e)

                            st.session_state.pedido_confirmado = True
                            st.session_state.limpiar_carrito = True
                            st.session_state.ultimo_nombre = nombre
                            st.session_state.ultimo_celular = celular
                            st.session_state.ultimo_direccion = direccion
                            st.session_state.ultimo_barrio = barrio
                            st.session_state.ultimo_resumen = resumen_legible
                            st.session_state.ultimo_total = total_pesos
                            st.session_state.ultimo_pago = forma_pago
                            st.session_state.ultimo_notas = notas

                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar el pedido: {e}")
                else:
                    st.error("⚠️ Completá nombre, celular y dirección.")
    else:
        st.info("Seleccioná tus viandas arriba para armar el pedido.")

else:
    st.warning("🌙 **¡La cocina de Cadalu está descansando!**")
    st.info(f"Nuestro horario para recibir pedidos es de **{HORA_APERTURA}:00 a {HORA_CIERRE}:00 hs**.\n\n¡Te esperamos mañana!")
    with st.expander("Ver menú de la semana"):
        if not df_menu.empty:
            for index, row in df_menu.iterrows():
                st.markdown(f"**{row['plato']}** - ${row['precio']}")