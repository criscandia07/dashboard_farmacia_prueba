import streamlit as st
import pandas as pd
from validators import validate_configuration
from optimizer import solve_schedule
from metrics import calculate_metrics, plot_horas_totales, plot_horas_ventanilla
from excel_export import export_schedule_to_excel

def inject_custom_css():
    """Aplica diseño visual sobrio en paleta azul-celeste pastel."""
    st.markdown("""
        <style>
        .stApp {
            background-color: #F8FAFC;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #0F172A;
            color: #F8FAFC;
        }
        .metric-card {
            background-color: #FFFFFF;
            border-left: 5px solid #3B82F6;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        .status-badge-ok {
            background-color: #D1FAE5;
            color: #065F46;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        .status-badge-warn {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Menú lateral permanente con logo y navegación."""
    with st.sidebar:
        st.title("🏥 Farmacia CAE")
        st.caption("Hospital Clínico Herminda Martín")
        st.markdown("---")
        
        nav_choice = st.radio(
            "Navegación Principal",
            ["⚙️ Parámetros", "📅 Planilla", "📊 Métricas"],
            index=0
        )
        
        st.markdown("---")
        st.subheader("Estado del Sistema")
        if st.session_state.schedule_result:
            res = st.session_state.schedule_result
            if res["status"] == "OPTIMAL":
                st.markdown('<span class="status-badge-ok">✅ Solución Óptima</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-badge-warn">⚠️ Solución Relajada</span>', unsafe_allow_html=True)
        else:
            st.info("Programación pendiente.")
            
    return nav_choice

def render_parametros_tab():
    st.header("⚙️ Configuración de Parámetros de Programación")
    
    # 2.1 General
    with st.expander("1. Parámetros Generales y Días", expanded=True):
        c1, c2 = st.columns(2)
        params = st.session_state.params
        params["dias_programar"] = c1.number_input("Días hábiles a programar", value=params["dias_programar"], min_value=1, max_value=60)
        params["dias_rotacion"] = c2.number_input("Días rotación de turno", value=params["dias_rotacion"], min_value=1)
        params["dias_ciclo"] = c1.number_input("Días por ciclo de función", value=params["dias_ciclo"], min_value=1)

    # 3. Personal
    with st.expander("2. Configuración de Personal TENS", expanded=True):
        c1, c2 = st.columns(2)
        params["cant_turnos"] = c1.number_input("Cantidad de turnos", value=params["cant_turnos"], min_value=1)
        params["tens_por_turno"] = c2.number_input("TENS por turno", value=params["tens_por_turno"], min_value=1)
        
        st.subheader("Listado de TENS")
        df_tens = pd.DataFrame(st.session_state.tens_list)
        edited_tens = st.data_editor(df_tens, num_rows="dynamic", use_container_width=True)
        st.session_state.tens_list = edited_tens.to_dict("records")

    # 5. Bloques
    with st.expander("3. Bloques de Trabajo", expanded=False):
        df_bloques = pd.DataFrame(st.session_state.bloques)
        edited_b = st.data_editor(df_bloques, num_rows="dynamic", use_container_width=True)
        st.session_state.bloques = edited_b.to_dict("records")

    # 8. Funciones
    with st.expander("4. Funciones Disponibles", expanded=False):
        df_func = pd.DataFrame(st.session_state.funciones)
        edited_f = st.data_editor(df_func, num_rows="dynamic", use_container_width=True)
        st.session_state.funciones = edited_f.to_dict("records")

    # 9. Restricciones
    with st.expander("5. Restricciones de Compatibilidad (Ventanilla)", expanded=False):
        df_rest = pd.DataFrame(st.session_state.restricciones)
        edited_r = st.data_editor(df_rest, num_rows="dynamic", use_container_width=True)
        st.session_state.restricciones = edited_r.to_dict("records")

    st.markdown("---")
    if st.button("🚀 EJECUTAR PROGRAMACIÓN", type="primary", use_container_width=True):
        is_valid, errors, warnings = validate_configuration(
            st.session_state.params,
            st.session_state.tens_list,
            st.session_state.bloques,
            st.session_state.funciones,
            st.session_state.restricciones
        )
        
        if not is_valid:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            if warnings:
                for w in warnings:
                    st.warning(f"⚠️️ {w}")
                    
            with st.spinner("Ejecutando modelo de optimización OR-Tools..."):
                res = solve_schedule(
                    st.session_state.params,
                    st.session_state.tens_list,
                    st.session_state.bloques,
                    st.session_state.funciones,
                    st.session_state.restricciones
                )
                st.session_state.schedule_result = res
                if res["status"] in ("OPTIMAL", "FEASIBLE"):
                    st.success("¡Programación generada con éxito!")
                else:
                    st.error("No se encontró solución factible.")

def render_planilla_tab():
    st.header("📅 Planilla de Programación de Turnos")
    res = st.session_state.schedule_result
    
    if not res or not res["schedule"]:
        st.info("No hay datos de programación. Ejecuta el modelo en la ventana Parámetros.")
        return

    df = pd.DataFrame(res["schedule"])
    
    # Filtros laterales
    col1, col2 = st.columns(2)
    selected_tens = col1.multiselect("Filtrar TENS", options=df["TENS"].unique(), default=df["TENS"].unique())
    selected_fecha = col2.multiselect("Filtrar Fecha", options=df["Fecha"].unique(), default=df["Fecha"].unique())
    
    filtered_df = df[df["TENS"].isin(selected_tens) & df["Fecha"].isin(selected_fecha)]
    
    # Mostrar Leyenda de Funciones con colores pastel
    st.subheader("Leyenda de Funciones")
    cols = st.columns(len(st.session_state.funciones))
    for idx, f in enumerate(st.session_state.funciones):
        cols[idx].markdown(
            f'<div style="background-color:{f["color"]}; padding:5px; border-radius:5px; text-align:center; font-size:12px; font-weight:bold;">{f["nombre"]}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True)
    
    # Exportación
    df_m, kpis = calculate_metrics(df, st.session_state.funciones, st.session_state.bloques)
    excel_bytes = export_schedule_to_excel(df, st.session_state.params, st.session_state.funciones, kpis)
    
    st.download_button(
        label="📥 EXPORTAR A EXCEL",
        data=excel_bytes,
        file_name="Planilla_TENS_CAE.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

def render_metricas_tab():
    st.header("📊 Métricas y Equidad de Carga")
    res = st.session_state.schedule_result
    
    if not res or not res["schedule"]:
        st.info("Ejecuta la programación para visualizar indicadores.")
        return

    df = pd.DataFrame(res["schedule"])
    df_m, kpis = calculate_metrics(df, st.session_state.funciones, st.session_state.bloques)

    # Tarjetas KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TENS Programados", kpis["tens_programados"])
    k2.metric("Horas Totales", f"{kpis['hrs_totales']:.1f} hrs")
    k3.metric("Prom. Ventanilla", f"{kpis['hrs_vent_prom']:.1f} hrs")
    k4.metric("Brecha Max-Min Vent.", f"{kpis['diff_vent_max_min']:.1f} hrs")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_horas_totales(df_m), use_container_width=True)
    with c2:
        st.plotly_chart(plot_horas_ventanilla(df_m), use_container_width=True)