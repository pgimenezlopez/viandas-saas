import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from zoneinfo import ZoneInfo  # Módulo nativo para zonas horarias

# --- 1. CONFIGURACIÓN DE LA PÁGINA (BRANDING OFICIAL) ---
st.set_page_config(
    page_title="Cadalu - Sistema de Viandas", 
    page_icon="🍱", 
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# Inyección de CSS para tunear la interfaz con los colores de la marca
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
except Exception as e:
    st.error("🔴 Error crítico: No se pudo establecer la conexión con la base de datos de Supabase. Verificá los secrets.")
    st.stop()  # Detiene la ejecución de la app de forma limpia para evitar cascada de errores

# --- 4. ENCABEZADO DINÁMICO ---
col_logo, col_head = st.columns([1, 2])
with col_logo:
    # Intenta levantar el logo de la carpeta assets/ de forma segura capturando la excepción correcta
    try:
        st.image("assets/logo_cadalu.png", width=220)
    except Exception as e:
        # Silenciamos visualmente el error para el usuario, pero lo manejamos correctamente
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

# --- 5. OBTENER MENÚ ACTIVO ---
try:
    df_menu = conn.query("SELECT plato, descripcion, precio FROM menu_semanal WHERE disponible = TRUE ORDER BY id ASC", ttl=0)
except Exception as e:
    st.error("Error al conectar con la cocina. Por favor, intentá de nuevo en unos minutos.")
    df_menu = pd.DataFrame()

st.divider()

# --- 5. CONTROL DE HORARIO OPERATIVO ---
zona_mvd = ZoneInfo("America/Montevideo")
ahora = datetime.now(zona_mvd)

HORA_APERTURA = 8   # 08:00 AM
HORA_CIERRE = 22    # 22:00 PM

# Evaluamos si estamos en horario de atención
if HORA_APERTURA <= ahora.hour < HORA_CIERRE:
    
    # --- 6. EL CARRITO DINÁMICO ---
    st.subheader("🍽️ Menú Disponible")
    pedido_actual = {}
    total_pesos = 0

    if df_menu.empty:
        st.info("El menú se está actualizando. ¡Volvé pronto!")
    else:
        for index, row in df_menu.iterrows():
            col_texto, col_boton = st.columns([3, 1]) 
            with col_texto:
                st.markdown(f"**{row['plato']}** - **${row['precio']}**")
                st.caption(row['descripcion'])
            with col_boton:
                cantidad = st.number_input("Cant.", min_value=0, max_value=20, value=0, key=f"item_{index}", label_visibility="collapsed")
                if cantidad > 0:
                    subtotal = cantidad * row['precio']
                    pedido_actual[row['plato']] = {"cantidad": cantidad, "subtotal": subtotal}
                    total_pesos += subtotal
            st.write("")

    st.divider()

    # --- 7. RESUMEN Y FORMULARIO ---
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
                            
                            # Guardar datos para WhatsApp y limpiar
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
                            st.error(f"Error: {e}")
                else:
                    st.error("⚠️ Completá nombre, celular y dirección.")
    else:
        st.info("Seleccioná tus viandas arriba para armar el pedido.")

# Fijate que este else está alineado exactamente con el if HORA_APERTURA (sin sangría)
else:
    # --- PANTALLA DE CIERRE ---
    st.warning("🌙 **¡La cocina de Cadalu está descansando!**")
    st.info(f"Nuestro horario para recibir pedidos es de **{HORA_APERTURA}:00 a {HORA_CIERRE}:00 hs**. \n\n¡Te esperamos mañana para prepararte algo rico!")
    
    with st.expander("Ver menú de la semana"):
        for index, row in df_menu.iterrows():
            st.markdown(f"**{row['plato']}** - ${row['precio']}")
# --- 7. RESUMEN Y FORMULARIO ---

# Inicializar flags de session_state
# Inicializar flags de session_state
if "pedido_confirmado" not in st.session_state:
    st.session_state.pedido_confirmado = False
if "limpiar_carrito" not in st.session_state:
    st.session_state.limpiar_carrito = False

# Si hay que limpiar el carrito, eliminar las keys ANTES de renderizar widgets
if st.session_state.limpiar_carrito:
    for key in list(st.session_state.keys()):
        if key.startswith("item_"):
            del st.session_state[key]
    st.session_state.limpiar_carrito = False

# Mostrar confirmación si el pedido fue enviado exitosamente
if st.session_state.pedido_confirmado:
    import urllib.parse
    
    # Extraemos los datos guardados en la sesión
    nombre_ok = st.session_state.get("ultimo_nombre", "")
    resumen_ok = st.session_state.get("ultimo_resumen", "")
    total_ok = st.session_state.get("ultimo_total", 0)
    celular_ok = st.session_state.get("ultimo_celular", "")
    direccion_ok = st.session_state.get("ultimo_direccion", "")
    barrio_ok = st.session_state.get("ultimo_barrio", "")
    pago_ok = st.session_state.get("ultimo_pago", "")
    notas_ok = st.session_state.get("ultimo_notas", "") # Agregamos notas si existen

    st.success("🎉 ¡Tu pedido fue registrado en la cocina con éxito!")
    st.balloons()

    # Formateo limpio del mensaje con saltos de línea reales para WhatsApp
    numero_cocina = "59899000000" # <-- REEMPLAZAR POR EL NÚMERO OFICIAL DE CADALU
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

    # Limpiamos el flag para que el cartel desaparezca si el usuario sigue navegando
    st.session_state.pedido_confirmado = False
    st.stop()

if total_pesos > 0:
    st.subheader("🛒 Tu Pedido")
    for plato, datos in pedido_actual.items():
        st.write(f"✔️ **{datos['cantidad']}x** {plato} = **${datos['subtotal']}**")
    
    st.markdown(f"### Total: **${total_pesos}**")