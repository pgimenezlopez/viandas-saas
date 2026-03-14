import streamlit as st
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Agregamos initial_sidebar_state="collapsed" para esconder el menú izquierdo por defecto
st.set_page_config(
    page_title="Viandas Caseras", 
    page_icon="🍱", 
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# --- 1. MENÚ DE PLATOS DISPONIBLES ---
# Por ahora los platos están fijos en código, pero la venta va a Supabase.
datos_menu = {
    "Plato": [
        "Pollo al Horno con Papas Rústicas", 
        "Tarta de Verdura y Muzzarella", 
        "Ensalada Completa con Pollo", 
        "Milanesa de Carne con Puré",
        "Wok de Vegetales y Fideos"
    ],
    "Descripción": [
        "Pata muslo deshuesada, horneada con hierbas y papas doradas.", 
        "Masa casera, espinaca, muzzarella y huevo duro.", 
        "Lechuga, tomate, zanahoria, huevo, choclo y pollo grillé.", 
        "Clásica milanesa frita o al horno con puré de papas casero.",
        "Fideos de arroz con morrón, cebolla, zapallito y salsa de soja."
    ],
    "Precio": [350, 280, 250, 380, 290]
}
df_menu = pd.DataFrame(datos_menu)

# --- 2. ENCABEZADO DE LA WEB ---
st.title("🍱 Viandas Caseras")
st.markdown("¡Armá tu pedido de la semana! 🚚 Entregas de 12:00 a 14:00 hs.")
st.divider()

# --- 3. EL MENÚ DINÁMICO (El "Carrito") ---
st.subheader("🍽️ Menú Disponible")

# Diccionarios y variables para guardar la selección del usuario
pedido_actual = {}
total_pesos = 0

# Generamos la interfaz leyendo los datos
for index, row in df_menu.iterrows():
    # Usamos columnas para que quede el texto a la izquierda y el botón a la derecha
    col_texto, col_boton = st.columns([3, 1]) 
    
    with col_texto:
        st.markdown(f"**{row['Plato']}** - **${row['Precio']}**")
        st.caption(row['Descripción'])
        
    with col_boton:
        # El botón de + y -
        cantidad = st.number_input(
            "Cant.", 
            min_value=0, 
            max_value=20, 
            value=0, 
            key=f"item_{index}", 
            label_visibility="collapsed"
        )
        
        # Si eligió al menos 1, lo sumamos al carrito y al total
        if cantidad > 0:
            subtotal = cantidad * row['Precio']
            pedido_actual[row['Plato']] = {"cantidad": cantidad, "subtotal": subtotal}
            total_pesos += subtotal

    st.write("") # Espaciador visual entre platos

st.divider()

# --- 4. RESUMEN Y DATOS DEL CLIENTE ---
st.subheader("🛒 Tu Pedido")

if total_pesos == 0:
    st.info("Aún no has seleccionado ninguna vianda. Usá los botones ➕ arriba para agregar platos.")
else:
    # Mostramos el detalle de lo que va comprando
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
        
        st.write("") # Espaciador
        st.markdown("**💳 Forma de Pago**")
        forma_pago = st.radio(
            "Seleccioná cómo vas a abonar:", 
            ["💵 Efectivo (al recibir)", "🏦 Transferencia (BROU/Itaú/Santander)", "📱 MercadoPago"],
            label_visibility="collapsed"
        )
        
        notas = st.text_area("Aclaraciones (Ej: Sin sal, el timbre no anda, pago con $1000)")
        
        # Botón de confirmación gigante
        enviado = st.form_submit_button("🚀 Confirmar Pedido", type="primary", use_container_width=True)
        
        if enviado:
            if nombre and direccion and celular:
                with st.spinner("Procesando pedido y enviando a la base de datos..."):
                    try:
                        # 1. Armamos el string de qué platos eligió
                        resumen_platos = ", ".join([f"{d['cantidad']}x {p}" for p, d in pedido_actual.items()])
                        
                        # 2. Conectamos a la base de datos SQL
                        conn = st.connection("sql")
                        
                        # 3. Ejecutamos el INSERT de forma segura
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
                        
                        # Mensaje de éxito dinámico según forma de pago
                        if "Efectivo" in forma_pago:
                            mensaje_pago = "Abonás en efectivo al recibir."
                        else:
                            mensaje_pago = f"Te contactaremos al {celular} para los datos de pago."

                        st.success(f"¡Excelente {nombre}! Recibimos tu pedido por **${total_pesos}**. Lo llevaremos a {direccion} ({barrio}). {mensaje_pago}")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Hubo un error al conectar con la base de datos: {e}")
            else:
                st.error("⚠️ Por favor, completá tu nombre, celular y dirección para el envío.")