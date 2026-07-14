import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import pytz

# 1. Configuración principal de la aplicación
st.set_page_config(
    page_title="FINISHER 70.3 Panamá",
    page_icon="🇵🇦",
    layout="wide"
)

# 2. Configuración de Zona Horaria (Colombia) y Fechas
colombia_tz = pytz.timezone('America/Bogota')
fecha_actual_completa = datetime.datetime.now(colombia_tz)
fecha_actual = fecha_actual_completa.replace(tzinfo=None) 
fecha_carrera = datetime.datetime(2027, 2, 28, 6, 0, 0)

# Cálculo de la cuenta regresiva
tiempo_restante = fecha_carrera - fecha_actual
dias_restantes = tiempo_restante.days

# 3. Interfaz de Usuario: Cabecera
st.title("🏃‍♂️ Proyecto FINISHER 70.3 - Panamá 2027")
st.markdown("*No entrenamos para sobrevivir al IRONMAN. Entrenamos para disfrutar el camino hasta la meta.*")
st.divider()

# 4. Panel Superior: Reloj, Fecha y Cuenta Regresiva
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="📅 Fecha Actual (Bogotá)", value=fecha_actual_completa.strftime("%d/%m/%Y"))

with col2:
    st.metric(label="⏰ Hora Actual", value=fecha_actual_completa.strftime("%I:%M %p"))

with col3:
    st.metric(label="⏳ Días para la meta", value=f"{dias_restantes} días", delta="-1 día más cerca", delta_color="inverse")

st.divider()

# 5. Conexión a Google Sheets y Lógica de Datos
try:
    # Crear la conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer las hojas (La primera por defecto para el plan, y nombramos la de registro)
    df_plan = conn.read(ttl=10)
    df_registro = conn.read(worksheet="Registro_Diario", ttl=10)
    
    # Formateo de fechas y limpieza de datos vacíos en el Plan
    df_plan['Fecha_Inicio'] = pd.to_datetime(df_plan['Fecha_Inicio'], format='%d/%m/%Y', errors='coerce')
    
    # Identificar la semana actual
    semanas_iniciadas = df_plan[df_plan['Fecha_Inicio'] <= fecha_actual]
    
    if not semanas_iniciadas.empty:
        semana_actual_data = semanas_iniciadas.iloc[-1]
        id_semana_actual = semana_actual_data['ID_Semana']
        hito_actual = semana_actual_data['KPI_Clave_Semana']
        fase_actual = semana_actual_data['Fase']
        enfoque_actual = semana_actual_data['Enfoque_Semana']
        volumen_objetivo_hrs = float(semana_actual_data['Volumen_Objetivo_Hrs'])
    else:
        id_semana_actual = 0
        hito_actual = "El plan aún no ha comenzado."
        fase_actual = "-"
        enfoque_actual = "-"
        volumen_objetivo_hrs = 0.0

    # Mostrar el Hito Semanal
    st.subheader("🎯 Tu Hito Semanal")
    st.info(f"**Fase:** {fase_actual} | **Enfoque:** {enfoque_actual}")
    st.success(f"**Misión de esta semana:** {hito_actual}")
    
    with st.expander("Ver el plan maestro completo"):
        df_mostrar = df_plan.copy()
        df_mostrar['Fecha_Inicio'] = df_mostrar['Fecha_Inicio'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_mostrar)

    st.divider()

    # --- PROCESAMIENTO DE LA VERSIÓN 2.0 (REGISTRO Y SALUD) ---
    
    # Limpiar y preparar los datos del registro diario
    df_registro = df_registro.dropna(subset=['Fecha']) # Elimina filas vacías
    df_registro['Fecha'] = pd.to_datetime(df_registro['Fecha'], format='%d/%m/%Y', errors='coerce')
    df_registro['Duración_Real_Min'] = pd.to_numeric(df_registro['Duración_Real_Min'], errors='coerce').fillna(0)
    df_registro['Dolor_Lumbar'] = pd.to_numeric(df_registro['Dolor_Lumbar'], errors='coerce').fillna(0)
    df_registro['Dolor_Codo'] = pd.to_numeric(df_registro['Dolor_Codo'], errors='coerce').fillna(0)
    
    # Filtrar solo los entrenamientos de la semana actual
    df_semana_actual = df_registro[df_registro['ID_Semana'] == id_semana_actual]
    
    # Calcular horas reales sumando los minutos y dividiendo
    minutos_totales = df_semana_actual['Duración_Real_Min'].sum()
    horas_totales = minutos_totales / 60.0
    
    # Calcular el porcentaje de cumplimiento
    if volumen_objetivo_hrs > 0:
        porcentaje_cumplimiento = (horas_totales / volumen_objetivo_hrs) * 100
    else:
        porcentaje_cumplimiento = 0.0

    # Desplegar los Módulos Visuales V2.0
    col4, col5 = st.columns(2)

    with col4:
        st.subheader("📊 Cumplimiento de Volumen")
        st.write(f"**Objetivo de la semana:** {volumen_objetivo_hrs:.1f} hrs")
        st.write(f"**Realizado hasta hoy:** {horas_totales:.1f} hrs")
        
        # Lógica de Semáforos
        if porcentaje_cumplimiento >= 90:
            st.success(f"🟢 Excelente ritmo ({porcentaje_cumplimiento:.0f}%). Vas alineado al KPI de éxito.")
        elif porcentaje_cumplimiento >= 70:
            st.warning(f"🟠 Ritmo medio ({porcentaje_cumplimiento:.0f}%). Revisa tu agenda para completar el volumen.")
        else:
            st.error(f"🔴 Ritmo bajo ({porcentaje_cumplimiento:.0f}%). ¡Es hora de ajustar el plan o recuperar sesiones!")
            
        # Barra de progreso visual (se bloquea en 100% / 1.0 para que no falle si haces de más)
        st.progress(min(porcentaje_cumplimiento / 100.0, 1.0))

    with col5:
        st.subheader("⚠️ Radar de Salud")
        if not df_registro.empty:
            # Preparar la gráfica de molestias
            df_chart = df_registro[['Fecha', 'Dolor_Lumbar', 'Dolor_Codo']].set_index('Fecha')
            st.line_chart(df_chart, color=["#FF0000", "#FFA500"])
            
            # Detectar el último registro de salud para alertas preventivas
            ultimo_lumbar = df_registro.iloc[-1]['Dolor_Lumbar']
            ultimo_codo = df_registro.iloc[-1]['Dolor_Codo']
            
            if ultimo_lumbar >= 3:
                st.error(f"🚨 Alerta L5-S1: El último registro de dolor lumbar fue de {ultimo_lumbar}. PRIORIDAD: Movilidad y técnica.")
            elif ultimo_codo >= 3:
                st.error(f"🚨 Alerta Epicondilitis: El dolor de codo está en {ultimo_codo}. Vigilar vibraciones en la bici y agarre al nadar.")
            else:
                st.success("✅ Sistema físico en verde: Sin molestias preocupantes.")
        else:
            st.info("No hay datos de salud registrados aún.")

except Exception as e:
    st.error(f"Error técnico conectando a Google Sheets: {e}")
