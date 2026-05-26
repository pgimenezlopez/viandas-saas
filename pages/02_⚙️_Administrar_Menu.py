import streamlit as st
import pandas as pd
from sqlalchemy import text

st.set_page_config(page_title="Admin Menú", page_icon="⚙️", layout="centered")

st.title("⚙️ Administrador de Menú")
st.markdown("Agregá platos nuevos o editá los datos de los existentes.")

password = st.text_input("Ingresá la clave de administrador:", type="password")

if password == st.secrets["admin_password"]:
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
    
    # 1. PRIMERO traemos los datos frescos de la base y creamos la variable df_menu
    df_menu = conn.query("SELECT id, plato, descripcion, precio, disponible FROM menu_semanal ORDER BY id ASC", ttl=0)
    
    # 2. DESPUÉS le pasamos esa variable al editor interactivo
    df_editado = st.data_editor(
        df_menu, 
        key="editor_menu_cambios", # <-- Clave fundamental para leer los deltas
        num_rows="dynamic",        # <-- Permite agregar (+) y borrar filas
        hide_index=True, 
        use_container_width=True,
        disabled=["id"], 
        column_config={
            "id": None, 
            "plato": st.column_config.TextColumn("Plato", required=True),
            "descripcion": "Descripción",
            "precio": st.column_config.NumberColumn("Precio ($)", format="%d", min_value=0),
            "disponible": "Activo"
        }
    )
    
    # Botón para impactar los cambios en Supabase
    if st.button("💾 Guardar Cambios en la Base de Datos", type="primary", use_container_width=True):
        cambios = st.session_state["editor_menu_cambios"]
        
        with st.spinner("Sincronizando con Supabase..."):
            try:
                with conn.session as s:
                    # 1. Modificaciones (UPDATES)
                    for idx_str, fila_modificada in cambios.get("edited_rows", {}).items():
                        idx = int(idx_str)
                        id_real = int(df_menu.iloc[idx]["id"])
                        # Armamos un diccionario con los valores actuales y los pisamos con los editados
                        valores_actuales = df_menu.iloc[idx].to_dict()
                        valores_actuales.update(fila_modificada)
                        
                        s.execute(
                            text("""
                                UPDATE menu_semanal 
                                SET plato = :p, descripcion = :d, precio = :pr, disponible = :disp
                                WHERE id = :id
                            """),
                            {"p": valores_actuales["plato"], "d": valores_actuales["descripcion"], 
                             "pr": int(valores_actuales["precio"]), "disp": bool(valores_actuales["disponible"]), 
                             "id": id_real}
                        )

                    # 2. Altas Nuevas (INSERTS SIN ID)
                    for nueva_fila in cambios.get("added_rows", []):
                        s.execute(
                            text("""
                                INSERT INTO menu_semanal (plato, descripcion, precio, disponible) 
                                VALUES (:p, :d, :pr, :disp)
                            """),
                            {"p": nueva_fila.get("plato", "Nuevo Plato"), 
                             "d": nueva_fila.get("descripcion", ""), 
                             "pr": int(nueva_fila.get("precio", 0)), 
                             "disp": bool(nueva_fila.get("disponible", True))}
                        )
                    
                    # 3. Bajas (DELETES)
                    for idx in cambios.get("deleted_rows", []):
                        id_borrar = int(df_menu.iloc[idx]["id"])
                        s.execute(text("DELETE FROM menu_semanal WHERE id = :id"), {"id": id_borrar})

                    s.commit()
                    
                st.success("¡Operación exitosa! Menú sincronizado.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error crítico en la transacción SQL: {e}")
            
elif password:
    st.error("Clave incorrecta.")