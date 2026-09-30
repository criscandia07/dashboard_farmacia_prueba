import streamlit as st

# Versión del esquema de datos (cambiar esta clave fuerza la actualización inmediata)
DATA_SCHEMA_VERSION = "v2.0_celeste_gris_req_funciones"

def auto_generate_tens(cant_turnos, tens_por_turno):
    """Genera automáticamente IDs de TENS y los reparte de manera equitativa por turno."""
    lista = []
    idx = 1
    for turno in range(1, cant_turnos + 1):
        for _ in range(tens_por_turno):
            lista.append({
                "id": f"{idx:03d}",
                "turno": f"Turno {turno}"
            })
            idx += 1
    return lista

def init_session_state():
    """Inicializa la sesión. Si detecta una versión antigua, borra la memoria y carga el nuevo modelo."""
    if st.session_state.get("schema_version") != DATA_SCHEMA_VERSION:
        st.session_state.clear()
        st.session_state.schema_version = DATA_SCHEMA_VERSION

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
        # Estructura requerida según el nuevo prompt: requerimiento por función individual
        st.session_state.bloques = [
            {"Bloque": 1, "Inicio": "08:00", "Fin": "09:30", "Colación": False, "RECEPCIÓN": 1, "PREPARACIÓN": 1, "REVISIÓN": 1, "ENTREGA": 1},
            {"Bloque": 2, "Inicio": "09:30", "Fin": "10:45", "Colación": False, "RECEPCIÓN": 1, "PREPARACIÓN": 1, "REVISIÓN": 1, "ENTREGA": 1},
            {"Bloque": 3, "Inicio": "10:45", "Fin": "12:00", "Colación": False, "RECEPCIÓN": 1, "PREPARACIÓN": 1, "REVISIÓN": 1, "ENTREGA": 1},
            {"Bloque": 4, "Inicio": "12:00", "Fin": "13:15", "Colación": True,  "COLACIÓN": 2, "RECEPCIÓN": 1, "ENTREGA": 1},
            {"Bloque": 5, "Inicio": "13:15", "Fin": "14:30", "Colación": True,  "COLACIÓN": 2, "RECEPCIÓN": 1, "ENTREGA": 1},
            {"Bloque": 6, "Inicio": "14:30", "Fin": "15:45", "Colación": False, "RECEPCIÓN": 1, "PREPARACIÓN": 1, "REVISIÓN": 1, "ENTREGA": 1},
            {"Bloque": 7, "Inicio": "15:45", "Fin": "16:00", "Colación": False, "RECEPCIÓN": 1, "PREPARACIÓN": 1, "REVISIÓN": 1, "ENTREGA": 1},
            {"Bloque": 8, "Inicio": "16:00", "Fin": "17:00", "Colación": False, "RECEPCIÓN": 1, "PREPARACIÓN": 1, "REVISIÓN": 1, "ENTREGA": 1},
        ]

    if "restricciones" not in st.session_state:
        st.session_state.restricciones = [
            {"TENS 1": "001", "TENS 2": "004", "Tipo de restricción": "No coincidir en ventanilla"},
        ]

    if "schedule_result" not in st.session_state:
        st.session_state.schedule_result = None