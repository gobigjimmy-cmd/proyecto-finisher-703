import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de página con estilo profesional
st.set_page_config(
    page_title="Proyecto FINISHER 70.3",
    page_icon="🏅",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; color: #005088; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 20px; color: #11caa0; text-align: center; margin-bottom: 30px; font-style: italic; }
    .metric-box { background-color: #f3f0df; padding: 20px; border-radius: 10px; border-left: 5px solid #005088; margin-bottom: 15px; }
    .metric-title { font-size: 16px; color: #475569; font-weight: bold; }
    .metric-value { font-size: 28px; color: #121212; font-weight: bold; }
    .phase-badge { background-color: #005088; color: white; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Títulos Principales
st.markdown('<div class="main-title">PROYECTO FINISHER 70.3 - PANAMÁ 2027</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">"No entrenamos para sobrevivir al IRONMAN. Entrenamos para disfrutar el camino hasta la meta."</div>', unsafe_allow_html=True)

# Conexión con Google Sheets
try:
    # Iniciar conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer la hoja directamente (toma la URL exacta de los Secrets con el gid incluido)
    df_plan = conn.read(ttl=10)
    
    # Asegurar formato de fecha
    df_plan['Fecha_Inicio'] = pd.to_datetime(df_plan['Fecha_Inicio'])
    
    # 1. Determinar Semana Actual Basado en la Fecha Real
    hoy = pd.to_datetime(datetime.now().date())
    
    # Buscar en qué bloque de semana cae la fecha de hoy
    semana_actual_row = df_plan[df_plan['Fecha_Inicio'] <= hoy].last_valid_index()
    
    if semana_actual_row is not None:
        semana_info = df_plan.loc[semana_actual_row]
        id_semana = int(semana_info['ID_Semana'])
        fase_actual = semana_info['Fase']
        enfoque_actual = semana_info['Enfoque_Semana']
        horas_objetivo = semana_info['Volumen_Objetivo_Hrs']
        kpi_semana = semana_info['KPI_Clave_Semana']
    else:
        # Failsafe
        id_semana = 1
        semana_info = df_plan.iloc[0]
        fase_actual = semana_info['Fase']
        enfoque_actual = semana_info['Enfoque_Semana']
        horas_objetivo = semana_info['Volumen_Objetivo_Hrs']
        kpi_semana = semana_info['KPI_Clave_Semana']

    # --- DISEÑO DEL DASHBOARD (PANEL SUPERIOR) ---
    st.markdown("### 📊 Estado Actual del Proyecto")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">📆 CRONOGRAMA</div>
                <div class="metric-value">Semana {id_semana} <span style="font-size:16px; font-weight:normal;">de 34</span></div>
                <span class="phase-badge">{fase_actual}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="metric-box">
                <div class="metric-title">📈 CONSISTENCIA MENSUAL</div>
                <div class="metric-value">100% <span style="color:#11caa0; font-size:18px;">▲</span></div>
                <p style="font-size:12px; margin:0; color:#475569;">Objetivo: >90%</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">⏱️ VOLUMEN PLANIFICADO</div>
                <div class="metric-value">{horas_objetivo} Hrs</div>
                <p style="font-size:12px; margin:0; color:#475569;">Meta de la semana</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
            <div class="metric-box">
                <div class="metric-title">🩺 ALERTAS DE SALUD</div>
                <div class="metric-value" style="color:#11caa0;">0 <span style="font-size:16px; font-weight:normal; color:#475569;">Molestias</span></div>
                <p style="font-size:12px; margin:0; color:#11caa0;">🟢 L5-S1 & Codo OK</p>
            </div>
        """, unsafe_allow_html=True)

    # --- OBJETIVOS E HITOS DE LA SEMANA ---
    st.markdown("---")
    st.markdown(f"### 🎯 Plan de Trabajo Semanal: {enfoque_actual}")
    st.info(f"**📌 Hito Crítico de la Semana (KPI):** {kpi_semana}")

    # --- TABLA DEL PLAN MAESTRO COMPLETO ---
    st.markdown("---")
    with st.expander("🔍 Ver Plan Maestro Completo de 34 Semanas (Ruta Crítica)"):
        df_mostrar = df_plan.copy()
        df_mostrar['Fecha_Inicio'] = df_mostrar['Fecha_Inicio'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("⚠️ Error de conexión.")
    st.exception(e)
