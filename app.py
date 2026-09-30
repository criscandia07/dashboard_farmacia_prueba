import streamlit as st
from models import init_session_state
from ui import (
    inject_custom_css,
    render_sidebar,
    render_parametros_tab,
    render_planilla_tab,
    render_metricas_tab
)

# Configuración Global de la Página
st.set_page_config(
    page_title="Programación TENS - Farmacia CAE",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # 1. Inicializar session_state
    init_session_state()
    
    # 2. Inyectar estilos institucionales
    inject_custom_css()
    
    # 3. Renderizar barra lateral y obtener pestaña seleccionada
    nav_choice = render_sidebar()
    
    # 4. Enrutamiento de ventanas
    if nav_choice == "⚙️ Parámetros":
        render_parametros_tab()
    elif nav_choice == "📅 Planilla":
        render_planilla_tab()
    elif nav_choice == "📊 Métricas":
        render_metricas_tab()

if __name__ == "__main__":
    main()