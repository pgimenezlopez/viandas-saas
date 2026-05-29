import streamlit as st
import pandas as pd
from sqlalchemy import text
from utils.auth import require_auth

st.set_page_config(page_title="Administrar Menú", page_icon="⚙️", layout="wide")

require_auth()

st.title("⚙️ Administrar Menú y Stock")
st.info("Editá los precios, modificá el stock o agregá platos nuevos. Los cambios se guardan todos juntos en una sola transacción.")

try:
    conn = st.connection("sql")
    df_menu = conn.query("SELECT id, plato, descripcion, precio, stock, disponible FROM menu_semanal ORDER BY id ASC", ttl=0)
    # SEGURIDAD: Alineamos el index nativo para que coincida exactamente con las filas del editor
    df_menu = df_menu.reset_index(drop=True)
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()

df_editado = st.data_editor(
    df_menu, 
    key="editor_menu_cambios", 
    num_rows="dynamic",        
    hide_index=True, 
    use_container_width=True,
    disabled=["id"], 
    column_config={
        "id": None, 
        "plato": st.column_config.TextColumn("Plato", required=True),
        "descripcion": "Descripción",
        "precio": st.column_config.NumberColumn("Precio ($)", format="%d", min_value=0),
        "stock": st.column_config.NumberColumn("Stock", format="%d", min_value=0),
        "disponible": "Activo"
    }
)

if st.button("💾 Guardar Cambios Masivos", type="primary"):
    cambios = st.session_state.editor_menu_cambios
    agregados = cambios.get("added_rows", [])
    editados = cambios.get("edited_rows", {})
    borrados = cambios.get("deleted_rows", [])

    if not agregados and not editados and not borrados:
        st.warning("No se detectaron cambios para guardar.")
        st.stop()

    with st.spinner("Sincronizando con la base de datos..."):
        try:
            with conn.session as s:
                # 1. Bajas
                if borrados:
                    for i in borrados:
                        id_real = int(df_menu.iloc[i]['id'])
                        s.execute(text("DELETE FROM menu_semanal WHERE id = :id"), {"id": id_real})

                # 2. Modificaciones
                if editados:
                    for i, modificaciones in editados.items():
                        id_real = int(df_menu.iloc[int(i)]['id'])
                        fila_original = df_menu.iloc[int(i)].to_dict()
                        for col, val in modificaciones.items():
                            fila_original[col] = val
                        
                        s.execute(
                            text("""
                                UPDATE menu_semanal 
                                SET plato = :p, descripcion = :d, precio = :pr, stock = :stk, disponible = :disp
                                WHERE id = :id
                            """),
                            {
                                "p": fila_original["plato"], 
                                "d": fila_original["descripcion"], 
                                "pr": int(fila_original["precio"]), 
                                "stk": int(fila_original["stock"]), 
                                "disp": bool(fila_original["disponible"]), 
                                "id": id_real
                            }
                        )

                # 3. Altas
                if agregados:
                    for fila in agregados:
                        s.execute(
                            text("""
                                INSERT INTO menu_semanal (plato, descripcion, precio, stock, disponible) 
                                VALUES (:p, :d, :pr, :stk, :disp)
                            """),
                            {
                                "p": fila.get("plato", "Nuevo Plato"), 
                                "d": fila.get("descripcion", ""), 
                                "pr": int(fila.get("precio", 0)), 
                                "stk": int(fila.get("stock", 20)), 
                                "disp": bool(fila.get("disponible", True))
                            }
                        )
                s.commit()
            
            st.success("✅ ¡Menú y stock actualizados correctamente!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error durante la transacción: {e}")