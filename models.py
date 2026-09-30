import streamlit as st

def init_session_state():
    """Inicializa todas las estructuras de datos dentro de st.session_state con el nuevo esquema."""
    if "params" not in st.session_state:
        st.session_state.params = {
            "dias_programar": 10,
            "feriados": ["2026-09-18", "2026-09-19"],
            "dias_rotacion": 5,
            "dias_ciclo": 5,
            "cant_turnos": 2,
            "tens_por_turno": 4,
        }

    # Generación inicial: 8 TENS divididos automáticamente en 2 turnos de 4
    if "tens_list" not in st.session_state:
        st.session_state.tens_list = auto_generate_tens(2, 4)

    if "funciones" not in st.session_state:
        # Paleta Institucional Celeste y Gris
        st.session_state.funciones = [
            {"id": "FUNC_01", "nombre": "RECEPCIÓN", "color": "#7DD3FC", "ventanilla": True, "es_colacion": False},
            {"id": "FUNC_02", "nombre": "PREPARACIÓN", "color": "#BAE6FD", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_03", "nombre": "REVISIÓN", "color": "#CBD5E1", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_04", "nombre": "ENTREGA", "color": "#38BDF8", "ventanilla": True, "es_colacion": False},
            {"id": "FUNC_05", "nombre": "VOLANTE", "color": "#E2E8F0", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_06", "nombre": "ANFITRIÓN", "color": "#94A3B8", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_07", "nombre": "DIGITACIÓN", "color": "#0284C7", "ventanilla": False, "es_colacion": False},
            {"id": "FUNC_08", "nombre": "COLACIÓN", "color": "#F1F5F9", "ventanilla": False, "es_colacion": True},
        ]

    if "bloques" not in st.session_state:
        # 8 bloques con requerimientos específicos por función
        st.session_state.bloques = [
            {"num": 1, "inicio": "08:00", "fin": "09:30", "colacion": False, "req_RECEPCIÓN": 1, "req_PREPARACIÓN": 1, "req_REVISIÓN": 1, "req_ENTREGA": 1},
            {"num": 2, "inicio": "09:30", "fin": "10:45", "colacion": False, "req_RECEPCIÓN": 1, "req_PREPARACIÓN": 1, "req_REVISIÓN": 1, "req_ENTREGA": 1},
            {"num": 3, "inicio": "10:45", "fin": "12:00", "colacion": False, "req_RECEPCIÓN": 1, "req_PREPARACIÓN": 1, "req_REVISIÓN": 1, "req_ENTREGA": 1},
            {"num": 4, "inicio": "12:00", "fin": "13:15", "colacion": True,  "req_COLACIÓN": 2, "req_RECEPCIÓN": 1, "req_ENTREGA": 1},
            {"num": 5, "inicio": "13:15", "fin": "14:30", "colacion": True,  "req_COLACIÓN": 2, "req_RECEPCIÓN": 1, "req_ENTREGA": 1},
            {"num": 6, "inicio": "14:30", "fin": "15:45", "colacion": False, "req_RECEPCIÓN": 1, "req_PREPARACIÓN": 1, "req_REVISIÓN": 1, "req_ENTREGA": 1},
            {"num": 7, "inicio": "15:45", "fin": "16:00", "colacion": False, "req_RECEPCIÓN": 1, "req_PREPARACIÓN": 1, "req_REVISIÓN": 1, "req_ENTREGA": 1},
            {"num": 8, "inicio": "16:00", "fin": "17:00", "colacion": False, "req_RECEPCIÓN": 1, "req_PREPARACIÓN": 1, "req_REVISIÓN": 1, "req_ENTREGA": 1},
        ]

    if "restricciones" not in st.session_state:
        st.session_state.restricciones = [
            {"tens1": "001", "tens2": "004", "tipo": "No coincidir en ventanilla"},
        ]

    if "schedule_result" not in st.session_state:
        st.session_state.schedule_result = None

def auto_generate_tens(cant_turnos, tens_por_turno):
    """Genera automáticamente IDs de TENS y los reparte de manera equitativa por turno."""
    lista = []
    idx = 1
    for turno in range(1, cant_turnos + 1):
        for _ in range(tens_por_turno):
            lista.append({
                "id": f"{idx:03d}",
                "turno": turno
            })
            idx += 1
    return lista