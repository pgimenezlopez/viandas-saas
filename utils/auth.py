import hmac
import streamlit as st

def verificar_password(ingresada: str) -> bool:
    """Comparación de strings resistente a timing attacks."""
    esperada = st.secrets.get("admin_password", "")
    if not esperada:
        return False  # Falla segura si olvidaste configurar el secret
    return hmac.compare_digest(ingresada.encode(), esperada.encode())

def require_auth() -> None:
    """Guard de autenticación reutilizable para todas las páginas admin."""
    if not st.session_state.get("autenticado", False):
        st.info("🔒 Acceso exclusivo para el equipo de cocina.")
        clave = st.text_input("Contraseña:", type="password", key="login_input")
        if st.button("Entrar", type="primary"):
            if verificar_password(clave):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        st.stop()