import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la ventana del navegador
st.set_page_config(page_title="Dashboard Farmacia CAE", layout="wide")

# 2. Título principal
st.title("💊 Panel de Control: Flujo de Farmacia CAE")
st.markdown("Monitoreo de tiempos de espera y atención de pacientes.")

# 3. Creación de datos de prueba
datos = pd.DataFrame({
    'Día': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
    'Pacientes Atendidos': [180, 220, 250, 210, 190, 280, 240],
    'Tiempo Medio Espera (min)': [25, 30, 40, 20, 15, 35, 28]
})

# 4. Indicadores clave (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Total Pacientes (Semana)", "1,570")
col2.metric("Promedio Espera", "27.5 min")
col3.metric("TENS Activos en Turno", "4")

st.divider()

# 5. Gráficos interactivos
st.subheader("📊 Evolución de Pacientes Atendidos")
st.bar_chart(data=datos, x='Día', y='Pacientes Atendidos')

st.subheader("⏱️ Tendencia de Tiempos de Espera")
st.line_chart(data=datos, x='Día', y='Tiempo Medio Espera (min)')