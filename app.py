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
# Creamos una versión sin zona horaria para poder compararla con las fechas de Excel
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

# 5. Conexión a Google Sheets y Lógica de Fechas
try:
    # Crear la conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer la hoja maestra
    df_plan = conn.read(ttl=10)
    
    # CONVERSIÓN DE FECHAS: Le decimos a Pandas que lea en formato Día/Mes/Año[cite: 1]
    df_plan['Fecha_Inicio'] = pd.to_datetime(df_plan['Fecha_Inicio'], format='%d/%m/%Y', errors='coerce')
    
    # EXTRAER LA SEMANA ACTUAL[cite: 1]
    # Filtramos las semanas que ya empezaron (Fecha_Inicio <= fecha_actual)
    semanas_iniciadas = df_plan[df_plan['Fecha_Inicio'] <= fecha_actual]
    
    if not semanas_iniciadas.empty:
        # La semana actual es la última de esa lista
        semana_actual_data = semanas_iniciadas.iloc[-1]
        hito_actual = semana_actual_data['KPI_Clave_Semana']
        fase_actual = semana_actual_data['Fase']
        enfoque_actual = semana_actual_data['Enfoque_Semana']
    else:
        hito_actual = "El plan aún no ha comenzado."
        fase_actual = "-"
        enfoque_actual = "-"

    # 6. Mostrar el Hito Semanal Automatizado
    st.subheader("🎯 Tu Hito Semanal")
    st.info(f"**Fase:** {fase_actual} | **Enfoque:** {enfoque_actual}")
    st.success(f"**Misión de esta semana:** {hito_actual}")
    
    with st.expander("Ver el plan maestro completo"):
        # Mostramos el dataframe pero volvemos a poner la fecha en texto para que se vea bonita
        df_mostrar = df_plan.copy()
        df_mostrar['Fecha_Inicio'] = df_mostrar['Fecha_Inicio'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_mostrar)

except Exception as e:
    st.error(f"Error técnico conectando a Google Sheets: {e}")

st.divider()

# 7. Estructura de los siguientes módulos
col4, col5 = st.columns(2)

with col4:
    st.subheader("📊 Cumplimiento de Volumen")
    st.warning("Semáforos de cumplimiento en construcción...")

with col5:
    st.subheader("⚠️ Radar de Salud")
    st.error("Gráfico de molestias L5-S1 y Codo en construcción...")
