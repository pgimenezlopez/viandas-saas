import streamlit as st
import pandas as pd
from sqlalchemy import text

st.set_page_config(page_title="Admin Menú", page_icon="⚙️", layout="centered")

st.title("⚙️ Administrador de Menú")
st.markdown("Agregá platos nuevos o editá los datos de los existentes.")

password = st.text_input("Ingresá la clave de administrador:", type="password")

if password == "cocina2026":
    conn = st.connection("sql")
    
    # --- 1. FORMULARIO PARA AGREGAR PLATOS NUEVOS ---
    st.subheader("➕ Agregar Nuevo Plato")
    with st.form("nuevo_plato", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            plato = st.text_input("Nombre del Plato (Ej: Milanesa con Puré)")
        with col2:
            precio = st.number_input("Precio ($)", min_value=0, step=10)
            
        descripcion = st.text_input("Descripción corta o ingredientes")
        submit = st.form_submit_button("Guardar Plato Nuevo")
        
        if submit and plato:
            with conn.session as s:
                s.execute(
                    text("INSERT INTO menu_semanal (plato, descripcion, precio) VALUES (:plato, :desc, :precio)"),
                    {"plato": plato, "desc": descripcion, "precio": precio}
                )
                s.commit()
            st.success(f"¡'{plato}' agregado exitosamente!")
            st.rerun()

    st.divider()
    
    # --- 2. EDITOR INTERACTIVO DEL MENÚ EXISTENTE ---
    st.subheader("📋 Editar Menú Actual")
    st.markdown("Hacé doble clic en las celdas para modificar precios o nombres. Destildá la casilla **Activo** para ocultar un plato agotado.")
    
    # Traemos los datos frescos de la base
    df_menu = conn.query("SELECT id, plato, descripcion, precio, disponible FROM menu_semanal ORDER BY id ASC", ttl=0)
    
    # Convertimos el DataFrame en un editor interactivo
    df_editado = st.data_editor(
        df_menu, 
        hide_index=True, 
        use_container_width=True,
        disabled=["id"], # Bloqueamos el ID para que no se rompa la base de datos
        column_config={
            "id": None, # Ocultamos la columna visualmente
            "plato": st.column_config.TextColumn("Plato", required=True),
            "descripcion": "Descripción",
            "precio": st.column_config.NumberColumn("Precio ($)", format="%d", min_value=0),
            "disponible": "Activo"
        }
    )
    
    # Botón para impactar los cambios en Supabase
    if st.button("💾 Guardar Cambios en la Base de Datos", type="primary", use_container_width=True):
        with st.spinner("Actualizando menú..."):
            with conn.session as s:
                # Recorremos la tabla editada y actualizamos fila por fila
                for index, row in df_editado.iterrows():
                    s.execute(
                        text("""
                            UPDATE menu_semanal 
                            SET plato = :plato, descripcion = :desc, precio = :precio, disponible = :disp
                            WHERE id = :id
                        """),
                        {
                            "plato": row["plato"], 
                            "desc": row["descripcion"], 
                            "precio": row["precio"], 
                            "disp": row["disponible"],
                            "id": row["id"]
                        }
                    )
                s.commit()
            st.success("¡Menú actualizado! Los clientes ya ven los nuevos datos.")
            st.rerun()
            
elif password:
    st.error("Clave incorrecta.")