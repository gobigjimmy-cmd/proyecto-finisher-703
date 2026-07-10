import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Proyecto FINISHER 70.3", page_icon="🏅", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; color: #005088; text-align: center; }
    .metric-box { background-color: #f3f0df; padding: 20px; border-radius: 10px; border-left: 5px solid #005088; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">PROYECTO FINISHER 70.3 - PANAMÁ 2027</div>', unsafe_allow_html=True)

# Conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url_secreta = st.secrets["connections"]["gsheets"]["url"]
    
    # Leemos la hoja
    df_plan = conn.read(spreadsheet=url_secreta, worksheet="Proyecto_FINISHER_703_Panama", ttl=10)
    
    # --- CORRECCIÓN CRÍTICA: Usamos 'Fecha' en lugar de 'Fecha_Inicio' ---
    df_plan['Fecha'] = pd.to_datetime(df_plan['Fecha'])
    
    hoy = pd.to_datetime(datetime.now().date())
    
    # Buscamos la fila basándonos en la columna 'Fecha'
    semana_actual_row = df_plan[df_plan['Fecha'] <= hoy].last_valid_index()
    
    if semana_actual_row is not None:
        semana_info = df_plan.loc[semana_actual_row]
        id_semana = int(semana_info['ID_Semana'])
        fase_actual = semana_info['Fase']
        enfoque_actual = semana_info['Enfoque_Semana']
        horas_objetivo = semana_info['Volumen_Objetivo_Hrs']
        kpi_semana = semana_info['KPI_Clave_Semana']
    else:
        # Failsafe si estamos antes de la fecha de inicio
        id_semana = 1
        semana_info = df_plan.iloc[0]
        fase_actual = semana_info['Fase']
        enfoque_actual = semana_info['Enfoque_Semana']
        horas_objetivo = semana_info['Volumen_Objetivo_Hrs']
        kpi_semana = semana_info['KPI_Clave_Semana']

    # --- UI ---
    st.markdown("### 📊 Estado Actual del Proyecto")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="metric-box"><h4>CRONOGRAMA</h4><h2>Semana {id_semana}</h2><p>{fase_actual}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><h4>CONSISTENCIA</h4><h2>100%</h2><p>Objetivo >90%</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><h4>VOLUMEN</h4><h2>{horas_objetivo} Hrs</h2><p>Meta semanal</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-box"><h4>ALERTAS</h4><h2>Salud OK</h2><p>L5-S1 & Codo</p></div>', unsafe_allow_html=True)

    st.info(f"**📌 Hito Crítico:** {kpi_semana}")

    with st.expander("🔍 Ver Plan Completo"):
        df_mostrar = df_plan.copy()
        df_mostrar['Fecha'] = df_mostrar['Fecha'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_mostrar, use_container_width=True)

except Exception as e:
    st.error("⚠️ Error de procesamiento:")
    st.write(e)
