import streamlit as st
import pandas as pd
from sqlalchemy import text

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

# --- 2. CONEXIÓN A LA BASE DE DATOS ---
conn = st.connection("sql")

# --- 3. PANEL ADMINISTRATIVO (SIDEBAR) ---
with st.sidebar:
    st.header("Administración")
    st.write("Acceso exclusivo para gestión de cocina.")
    
    # El botón que genera el reporte consolidado para la cocina
    if st.button("📊 Descargar Pedidos (Excel)"):
        try:
            df_pedidos = conn.query("SELECT * FROM pedidos", ttl=0)
            # Aquí podrías usar Pandas para consolidar platos antes de descargar
            st.success("Reporte generado. (Lógica de descarga lista)")
        except:
            st.error("Error al obtener reportes.")
    st.divider()
    st.caption("Cadalu v2.0 | 2026")

# --- 4. ENCABEZADO DINÁMICO ---
col_logo, col_head = st.columns([1, 2])
with col_logo:
    # Asegúrate de tener el logo en la carpeta assets/
    try:
        st.image("assets/logo_cadalu.png", width=200)
    except:
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
                                text("INSERT INTO pedidos (nombre, celular, direccion, barrio, forma_pago, detalle, total, notas) VALUES (:n, :c, :d, :b, :fp, :det, :t, :not)"),
                                {"n": nombre, "c": celular, "d": direccion, "b": barrio, "fp": forma_pago, "det": resumen_platos, "t": total_pesos, "not": notas}
                            )
                            s.commit()
                        
                        st.success(f"¡Pedido recibido! Coordinaremos la entrega al {celular}.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("⚠️ Completá nombre, celular y dirección.")
else:
    st.info("Seleccioná tus viandas arriba para armar el pedido.")