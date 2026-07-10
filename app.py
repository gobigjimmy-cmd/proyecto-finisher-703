import streamlit as st
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
fecha_actual = datetime.datetime.now(colombia_tz)
fecha_carrera = datetime.datetime(2027, 2, 28, 6, 0, 0, tzinfo=colombia_tz) # Asumimos inicio a las 6:00 AM

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
    st.metric(label="📅 Fecha Actual (Bogotá)", value=fecha_actual.strftime("%Y-%m-%d"))

with col2:
    st.metric(label="⏰ Hora Actual", value=fecha_actual.strftime("%I:%M %p"))

with col3:
    st.metric(label="⏳ Días para la meta", value=f"{dias_restantes} días", delta="-1 día más cerca", delta_color="inverse")

st.divider()

# 5. Estructura de los siguientes módulos (Marcadores de posición)
st.subheader("🎯 Tu Hito Semanal")
st.info("Aquí conectaremos con Google Sheets para mostrar tu KPI de la semana actual.")

col4, col5 = st.columns(2)

with col4:
    st.subheader("📊 Cumplimiento de Volumen")
    st.warning("Semáforos de cumplimiento en construcción...")

with col5:
    st.subheader("⚠️ Radar de Salud")
    st.error("Gráfico de molestias L5-S1 y Codo en construcción...")

st.divider()

st.subheader("📝 Registrar Entrenamiento de Hoy")
st.button("Abrir Formulario de Registro")
