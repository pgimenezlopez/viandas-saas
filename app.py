import streamlit as st
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Viandas Caseras", 
    page_icon="🍱", 
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# --- CONEXIÓN A LA BASE DE DATOS ---
conn = st.connection("sql")

# --- 1. OBTENER MENÚ ACTIVO DESDE SUPABASE ---
# Traemos solo los platos que tienen 'disponible = TRUE' (o Activo)
try:
    df_menu = conn.query("SELECT plato, descripcion, precio FROM menu_semanal WHERE disponible = TRUE ORDER BY id ASC", ttl=0)
except Exception as e:
    st.error("Error al conectar con la cocina. Por favor, intentá de nuevo en unos minutos.")
    df_menu = pd.DataFrame() # DataFrame vacío por si falla la red, para que no explote la app

# --- 2. ENCABEZADO DE LA WEB ---
st.title("🍱 Viandas Caseras")
st.markdown("¡Armá tu pedido de la semana! 🚚 Entregas de 12:00 a 14:00 hs.")
st.divider()

# --- 3. EL MENÚ DINÁMICO (El "Carrito") ---
st.subheader("🍽️ Menú Disponible")

pedido_actual = {}
total_pesos = 0

if df_menu.empty:
    st.info("El menú de esta semana se está actualizando. ¡Volvé pronto!")
else:
    # Generamos la interfaz leyendo los datos reales de la base
    for index, row in df_menu.iterrows():
        col_texto, col_boton = st.columns([3, 1]) 
        
        with col_texto:
            # Los nombres de las columnas ahora van en minúscula, tal cual están en PostgreSQL
            st.markdown(f"**{row['plato']}** - **${row['precio']}**")
            st.caption(row['descripcion'])
            
        with col_boton:
            cantidad = st.number_input(
                "Cant.", 
                min_value=0, 
                max_value=20, 
                value=0, 
                key=f"item_{index}", 
                label_visibility="collapsed"
            )
            
            if cantidad > 0:
                subtotal = cantidad * row['precio']
                pedido_actual[row['plato']] = {"cantidad": cantidad, "subtotal": subtotal}
                total_pesos += subtotal

        st.write("") # Espaciador visual

st.divider()

# --- 4. RESUMEN Y DATOS DEL CLIENTE ---
st.subheader("🛒 Tu Pedido")

if total_pesos == 0 and not df_menu.empty:
    st.info("Aún no has seleccionado ninguna vianda. Usá los botones ➕ arriba para agregar platos.")
elif total_pesos > 0:
    for plato, datos in pedido_actual.items():
        st.write(f"✔️ **{datos['cantidad']}x** {plato} = **${datos['subtotal']}**")
    
    st.markdown(f"### Total a pagar: **${total_pesos}**")
    
    st.write("")
    
    # --- 5. FORMULARIO DE ENVÍO Y PAGO ---
    st.markdown("#### 📍 Datos de Envío y Pago")
    
    with st.form("form_pedido"):
        nombre = st.text_input("Tu Nombre y Apellido")
        celular = st.text_input("Celular de contacto")
        direccion = st.text_input("Dirección de entrega (Ej: 18 de Julio 1234, Apto 5)")
        barrio = st.selectbox("Barrio", ["Centro", "Cordón", "Pocitos", "Buceo", "Malvín", "Otro"])
        
        st.write("") 
        st.markdown("**💳 Forma de Pago**")
        forma_pago = st.radio(
            "Seleccioná cómo vas a abonar:", 
            ["💵 Efectivo (al recibir)", "🏦 Transferencia (BROU/Itaú/Santander)", "📱 MercadoPago"],
            label_visibility="collapsed"
        )
        
        notas = st.text_area("Aclaraciones (Ej: Sin sal, el timbre no anda, pago con $1000)")
        
        enviado = st.form_submit_button("🚀 Confirmar Pedido", type="primary", use_container_width=True)
        
        if enviado:
            if nombre and direccion and celular:
                with st.spinner("Procesando pedido y enviando a la base de datos..."):
                    try:
                        resumen_platos = ", ".join([f"{d['cantidad']}x {p}" for p, d in pedido_actual.items()])
                        
                        # Usamos la conexión que abrimos al principio
                        with conn.session as s:
                            s.execute(
                                text("""
                                    INSERT INTO pedidos 
                                    (nombre, celular, direccion, barrio, forma_pago, detalle, total, notas)
                                    VALUES 
                                    (:nombre, :celular, :direccion, :barrio, :forma_pago, :detalle, :total, :notas)
                                """),
                                {
                                    "nombre": nombre,
                                    "celular": celular,
                                    "direccion": direccion,
                                    "barrio": barrio,
                                    "forma_pago": forma_pago,
                                    "detalle": resumen_platos,
                                    "total": total_pesos,
                                    "notas": notas
                                }
                            )
                            s.commit() 
                        
                        if "Efectivo" in forma_pago:
                            mensaje_pago = "Abonás en efectivo al recibir."
                        else:
                            mensaje_pago = f"Te contactaremos al {celular} para los datos de pago."

                        st.success(f"¡Excelente {nombre}! Recibimos tu pedido por **${total_pesos}**. Lo llevaremos a {direccion} ({barrio}). {mensaje_pago}")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Hubo un error al guardar tu pedido: {e}")
            else:
                st.error("⚠️ Por favor, completá tu nombre, celular y dirección para el envío.")