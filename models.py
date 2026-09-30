import streamlit as st

def init_session_state():
    """Inicializa todas las estructuras de datos dentro de st.session_state."""
    if "params" not in st.session_state:
        st.session_state.params = {
            "dias_programar": 10,
            "feriados": ["2026-09-18", "2026-09-19"],
            "dias_rotacion": 5,
            "dias_ciclo": 5,
            "cant_turnos": 2,
            "tens_por_turno": 4,
        }

    if "tens_list" not in st.session_state:
        st.session_state.tens_list = [
            {"id": "001", "turno": 1},
            {"id": "002", "turno": 1},
            {"id": "003", "turno": 1},
            {"id": "004", "turno": 1},
            {"id": "005", "turno": 2},
            {"id": "006", "turno": 2},
            {"id": "007", "turno": 2},
            {"id": "008", "turno": 2},
        ]

    if "bloques" not in st.session_state:
        st.session_state.bloques = [
            {"num": 1, "inicio": "08:00", "fin": "09:30", "colacion": False, "req": 3},
            {"num": 2, "inicio": "09:30", "fin": "11:00", "colacion": False, "req": 3},
            {"num": 3, "inicio": "11:00", "fin": "12:30", "colacion": False, "req": 3},
            {"num": 4, "inicio": "12:30", "fin": "13:30", "colacion": True, "req": 2},
            {"num": 5, "inicio": "13:30", "fin": "14:30", "colacion": True, "req": 2},
            {"num": 6, "inicio": "14:30", "fin": "16:00", "colacion": False, "req": 3},
            {"num": 7, "inicio": "16:00", "fin": "17:00", "colacion": False, "req": 3},
        ]

    if "funciones" not in st.session_state:
        st.session_state.funciones = [
            {"id": "FUNC_01", "nombre": "RECEPCIÓN", "color": "#7FA9C7", "ventanilla": True, "es_colacion": False},
            {"id": "FUNC_02", "nombre": "PREPARACIÓN", "color": "#B2C9AB", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_03", "nombre": "REVISIÓN", "color": "#C9BBC8", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_04", "nombre": "ENTREGA", "color": "#94B0DA", "ventanilla": True, "es_colacion": False},
            {"id": "FUNC_05", "nombre": "VOLANTE", "color": "#E3C9A8", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_06", "nombre": "ANFITRIÓN", "color": "#A2D2FF", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_07", "nombre": "DIGITACIÓN", "color": "#CBD5E1", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_08", "nombre": "COLACIÓN", "color": "#FDE2E4", "ventanilla": False, "es_colacion": True},
        ]

    if "restricciones" not in st.session_state:
        st.session_state.restricciones = [
            {"tens1": "001", "tens2": "004", "tipo": "No coincidir en ventanilla"},
        ]

    if "schedule_result" not in st.session_state:
        st.session_state.schedule_result = None
    
    if "execution_meta" not in st.session_state:
        st.session_state.execution_meta = None