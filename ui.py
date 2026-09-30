import streamlit as st
import pandas as pd
from models import auto_generate_tens
from validators import validate_configuration
from optimizer import solve_schedule
from metrics import calculate_metrics, plot_horas_totales, plot_horas_ventanilla
from excel_export import export_schedule_to_excel

def inject_custom_css():
    """Aplica el diseño sobrio en paleta Celeste y Gris."""
    st.markdown("""
        <style>
        .stApp {
            background-color: #F8FAFC;
            font-family: 'Segoe UI', sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #0F172A;
            color: #F8FAFC;
        }
        .stButton>button {
            background-color: #0284C7;
            color: white;
            border-radius: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.title("🏥 Farmacia CAE")
        st.caption("Hospital Clínico Herminda Martín")
        st.markdown("---")
        nav_choice = st.radio("Navegación", ["⚙️ Parámetros", "📅 Planilla", "📊 Métricas"])
        return nav_choice

def render_parametros_tab():
    st.header("⚙️ Configuración de Parámetros")
    
    # Botón de seguridad para resetear memoria
    if st.button("🧹 Restablecer parámetros de fábrica", type="secondary"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    with st.expander("1. Parámetros Generales y Días", expanded=True):
        c1, c2 = st.columns(2)
        params = st.session_state.params
        params["dias_programar"] = c1.number_input("Cantidad de días a programar", value=params["dias_programar"], min_value=1)
        params["dias_rotacion"] = c2.number_input("Cantidad de días hábiles antes de rotar", value=params["dias_rotacion"], min_value=1)
        params["dias_ciclo"] = c1.number_input("Cantidad de días del ciclo", value=params["dias_ciclo"], min_value=1)

    with st.expander("2. Configuración de Personal (TENS)", expanded=True):
        c1, c2, c3 = st.columns(3)
        params["cant_turnos"] = c1.number_input("Cantidad de turnos", value=params["cant_turnos"], min_value=1)
        params["tens_por_turno"] = c2.number_input("TENS por turno", value=params["tens_por_turno"], min_value=1)
        
        # Recalcular TENS automáticamente
        if c3.button("🔄 Auto-dividir TENS por turno"):
            st.session_state.tens_list = auto_generate_tens(params["cant_turnos"], params["tens_por_turno"])
            st.rerun()

        st.markdown("**Lista de TENS asignados:**")
        df_tens = pd.DataFrame(st.session_state.tens_list)
        edited_tens = st.data_editor(df_tens, num_rows="dynamic", use_container_width=True)
        st.session_state.tens_list = edited_tens.to_dict("records")

    with st.expander("3. Bloques de Trabajo y Personas por Función", expanded=True):
        st.caption("Especifique la cantidad de TENS requeridos por bloque para cada función:")
        df_bloques = pd.DataFrame(st.session_state.bloques)
        edited_b = st.data_editor(df_bloques, num_rows="dynamic", use_container_width=True)
        st.session_state.bloques = edited_b.to_dict("records")

    with st.expander("4. Funciones Disponibles (Paleta Celeste y Gris)", expanded=False):
        df_func = pd.DataFrame(st.session_state.funciones)
        edited_f = st.data_editor(df_func, num_rows="dynamic", use_container_width=True)
        st.session_state.funciones = edited_f.to_dict("records")

    with st.expander("5. Restricciones de Compatibilidad", expanded=False):
        df_rest = pd.DataFrame(st.session_state.restricciones)
        edited_r = st.data_editor(df_rest, num_rows="dynamic", use_container_width=True)
        st.session_state.restricciones = edited_r.to_dict("records")
    

def render_planilla_tab():
    st.header("📅 Planilla de Programación de Turnos")
    res = st.session_state.schedule_result
    if not res or not res.get("schedule"):
        st.info("Ejecuta la programación en la pestaña Parámetros.")
        return

    df = pd.DataFrame(res["schedule"])
    st.dataframe(df, use_container_width=True)

def render_metricas_tab():
    st.header("📊 Métricas de Desempeño y Ventanilla")
    res = st.session_state.schedule_result
    if not res or not res.get("schedule"):
        st.info("Ejecuta la programación para visualizar métricas.")
        return

    df = pd.DataFrame(res["schedule"])
    df_m, kpis = calculate_metrics(df, st.session_state.funciones, st.session_state.bloques)
    
    st.plotly_chart(plot_horas_totales(df_m), use_container_width=True)
    st.plotly_chart(plot_horas_ventanilla(df_m), use_container_width=True)