import urllib.parse
import requests
import streamlit as st
import pandas as pd
# app.py (al inicio)
import streamlit as st
from logica import calcular_total_carrito, esta_abierto
from sqlalchemy import text
from datetime import datetime
from zoneinfo import ZoneInfo

# --- 1. CONFIGURACIÓN DE LA PÁGINA (BRANDING OFICIAL) ---
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

# --- 2. CONEXIÓN A LA BASE DE DATOS (SUPABASE) ---
try:
    conn = st.connection("sql")
except Exception:
    st.error("🔴 Error crítico: No se pudo establecer la conexión con la base de datos de Supabase. Verificá los secrets.")
    st.stop()

# --- 3. INICIALIZACIÓN TEMPRANA DE session_state ---
if "pedido_confirmado" not in st.session_state:
    st.session_state.pedido_confirmado = False
if "limpiar_carrito" not in st.session_state:
    st.session_state.limpiar_carrito = False

# Limpieza preventiva del carrito para evitar duplicaciones de keys
if st.session_state.limpiar_carrito:
    for key in list(st.session_state.keys()):
        if key.startswith("item_"):
            del st.session_state[key]
    st.session_state.limpiar_carrito = False

# --- 4. ENCABEZADO DINÁMICO ---
col_logo, col_head = st.columns([1, 2])
with col_logo:
    try:
        st.image("assets/logo_cadalu.png", width=220)
    except Exception:
        st.write("### 🍱 Cadalu")

with col_head:
    st.title("Cadalu")
    st.markdown("**Comidas hechas con amor**")
    st.info("""
    **🛵 Entregas y Logística:**
    * **Mediodía:** Exclusivo en oficinas.
    * **Noche:** Envíos a domicilio (coordinar por WhatsApp).
    """)

st.divider()

# --- 5. PANTALLA DE CONFIRMACIÓN POST-PEDIDO ---
if st.session_state.pedido_confirmado:
    nombre_ok    = st.session_state.get("ultimo_nombre", "")
    resumen_ok   = st.session_state.get("ultimo_resumen", "")
    total_ok     = st.session_state.get("ultimo_total", 0)
    celular_ok   = st.session_state.get("ultimo_celular", "")
    direccion_ok = st.session_state.get("ultimo_direccion", "")
    barrio_ok    = st.session_state.get("ultimo_barrio", "")
    pago_ok      = st.session_state.get("ultimo_pago", "")
    notas_ok     = st.session_state.get("ultimo_notas", "")

    st.success("🎉 ¡Tu pedido fue registrado en la cocina con éxito!")
    st.balloons()

    # Lectura segura del número desde la bóveda de secrets
    numero_cocina = st.secrets.get("whatsapp_cocina", "")

    mensaje_wa = (
        f"🍱 *Nuevo Pedido Web - Cadalu*\n\n"
        f"👤 *Cliente:* {nombre_ok}\n"
        f"📞 *Celular:* {celular_ok}\n"
        f"📍 *Dirección:* {direccion_ok} ({barrio_ok})\n"
        f"💰 *Total:* ${total_ok}\n"
        f"💳 *Pago:* {pago_ok}\n\n"
        f"📋 *Detalle:* {resumen_ok}\n"
        f"💡 *Notas:* {notas_ok if notas_ok else 'Ninguna'}"
    )

    url_wa = f"https://wa.me/{numero_cocina}?text={urllib.parse.quote(mensaje_wa)}"

    st.link_button("📲 Enviar confirmación por WhatsApp", url_wa, use_container_width=True, type="primary")
    st.caption("Es necesario tocar el botón para coordinar el horario de entrega con la cocina.")

    if st.button("⬅️ Hacer otro pedido"):
        st.session_state.pedido_confirmado = False
        st.rerun()

    st.stop()

# --- 6. OBTENER MENÚ ACTIVO CON STOCK ---
try:
    df_menu = conn.query(
        "SELECT plato, descripcion, precio, stock FROM menu_semanal WHERE disponible = TRUE ORDER BY id ASC",
        ttl=0
    )
except Exception as e:
    # AHORA IMPRIMIMOS EL ERROR REAL DE POSTGRESQL
    st.error(f"Error al conectar con la cocina: {e}")
    df_menu = pd.DataFrame()

st.divider()

# --- 7. CONTROL DE HORARIO OPERATIVO ---
zona_mvd = ZoneInfo("America/Montevideo")
ahora = datetime.now(zona_mvd)

HORA_APERTURA = 8   # 08:00 AM
HORA_CIERRE = 22    # 22:00 PM

# Inicialización global para evitar NameError fuera del horario comercial
pedido_actual = {}
total_pesos = 0

if HORA_APERTURA <= ahora.hour < HORA_CIERRE:

    # --- 8. CARRITO DINÁMICO ---
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
                # Validamos si hay unidades disponibles en la cocina, previniendo errores por nulos
                if 'stock' in row and pd.notna(row['stock']):
                    stock_actual = int(row['stock'])
                else:
                    stock_actual = 20
                
                if stock_actual > 0:
                    cantidad = st.number_input(
                        "Cant.", 
                        min_value=0, 
                        max_value=stock_actual,  # El tope máximo ahora es el stock real
                        value=0,
                        key=f"item_{index}", 
                        label_visibility="collapsed"
                    )
                    if cantidad > 0:
                        subtotal = cantidad * row['precio']
                        pedido_actual[row['plato']] = {"cantidad": cantidad, "subtotal": subtotal}
                        total_pesos += subtotal
                else:
                    st.error("Agotado", icon="🚫")
            st.write("")

    st.divider()

    # --- 9. RESUMEN Y FORMULARIO DE CHECKOUT ---
    if total_pesos > 0:
        st.subheader("🛒 Tu Pedido")
        for plato, datos in pedido_actual.items():
            st.write(f"✔️ **{datos['cantidad']}x** {plato} = **${datos['subtotal']}**")

        st.markdown(f"### Total: **${total_pesos}**")

        with st.form("form_pedido"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nombre = st.text_input("Nombre y Apellido")
                celular = st.text_input("Celular")
            with col_f2:
                direccion = st.text_input("Dirección de entrega")
                barrio = st.selectbox("Barrio", ["Centro", "Cordón", "Pocitos", "Buceo", "Malvín", "Oficinas (Centro)", "Otro"])

            forma_pago = st.radio("Forma de Pago:", ["💵 Efectivo", "🏦 Transferencia", "📱 MercadoPago"], horizontal=True)
            notas = st.text_area("Aclaraciones (Ej: Sin sal, timbre no anda, etc.)")

            enviado = st.form_submit_button("🚀 Confirmar Pedido", type="primary", use_container_width=True)

            if enviado:
                if nombre and direccion and celular:
                    with st.spinner("Enviando pedido a cocina..."):
                        try:
                            resumen_platos = ", ".join([f"{d['cantidad']}x {p}" for p, d in pedido_actual.items()])

                            with conn.session as s:
                                s.execute(
                                    text("""
                                        INSERT INTO pedidos (nombre, celular, direccion, barrio, forma_pago, detalle, total, notas)
                                        VALUES (:n, :c, :d, :b, :fp, :det, :t, :not)
                                    """),
                                    {
                                        "n": nombre, "c": celular, "d": direccion, "b": barrio,
                                        "fp": forma_pago, "det": resumen_platos, "t": total_pesos, "not": notas
                                    }
                                )
                                s.commit()

                            # Notificación Push a Telegram
                            try:
                                telegram_token = st.secrets.get("TELEGRAM_TOKEN")
                                telegram_chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
                                
                                if telegram_token and telegram_chat_id:
                                    mensaje_tg = f"🔔 *Nuevo Pedido*\n👤 Nombre: {nombre}\n📍 Dirección: {direccion}\n🍽️ Resumen: {resumen_platos}"
                                    tg_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                                    requests.post(
                                        tg_url, 
                                        data={"chat_id": telegram_chat_id, "text": mensaje_tg, "parse_mode": "Markdown"}, 
                                        timeout=5
                                    )
                            except Exception:
                                # Fallo silencioso para no interrumpir el flujo del pedido web
                                pass

                            # Respaldar datos en el estado para el renderizado del botón de WhatsApp
                            st.session_state.pedido_confirmado = True
                            st.session_state.limpiar_carrito = True
                            st.session_state.ultimo_nombre = nombre
                            st.session_state.ultimo_celular = celular
                            st.session_state.ultimo_direccion = direccion
                            st.session_state.ultimo_barrio = barrio
                            st.session_state.ultimo_resumen = resumen_platos
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
    # --- PANTALLA DE CIERRE ---
    st.warning("🌙 **¡La cocina de Cadalu está descansando!**")
    st.info(
        f"Nuestro horario para recibir pedidos es de **{HORA_APERTURA}:00 a {HORA_CIERRE}:00 hs**."
        f"\n\n¡Te esperamos mañana para prepararte algo rico!"
    )
    with st.expander("Ver menú de la semana"):
        if not df_menu.empty:
            for index, row in df_menu.iterrows():
                st.markdown(f"**{row['plato']}** - ${row['precio']}")
        else:
            st.write("Menú no disponible por el momento.")