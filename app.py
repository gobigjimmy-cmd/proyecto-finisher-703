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

tiempo_restante = fecha_carrera - fecha_actual
dias_restantes = tiempo_restante.days

# 3. Interfaz de Usuario: Cabecera
st.title("🏃‍♂️ Proyecto FINISHER 70.3 - Panamá 2027")
st.markdown("*No entrenamos para sobrevivir al IRONMAN. Entrenamos para disfrutar el camino hasta la meta.*")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📅 Fecha Actual (Bogotá)", value=fecha_actual_completa.strftime("%d/%m/%Y"))
with col2:
    st.metric(label="⏰ Hora Actual", value=fecha_actual_completa.strftime("%I:%M %p"))
with col3:
    st.metric(label="⏳ Días para la meta", value=f"{dias_restantes} días", delta="-1 día más cerca", delta_color="inverse")

st.divider()

# 4. Conexión a Google Sheets (Múltiples GIDs)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_plan = conn.read(ttl=10)
except Exception as e:
    st.error(f"❌ Error leyendo la hoja principal del Plan. Detalle: {e}")
    st.stop()

try:
    url_registro = "https://docs.google.com/spreadsheets/d/1LI8NZtEa9KTZVWf53uAW3y2E4yoT9ToVRHY8ZCbAan0/edit?gid=1045035074"
    df_registro = conn.read(spreadsheet=url_registro, ttl=10)
except Exception as e:
    st.error(f"❌ Error leyendo el Registro Diario. Detalle: {e}")
    st.stop()

try:
    url_metricas = "https://docs.google.com/spreadsheets/d/1LI8NZtEa9KTZVWf53uAW3y2E4yoT9ToVRHY8ZCbAan0/edit?gid=125851459"
    df_metricas = conn.read(spreadsheet=url_metricas, ttl=10)
except Exception as e:
    st.error(f"❌ Error leyendo las Métricas Corporales. Detalle: {e}")
    st.stop()

try:
    url_restricciones = "https://docs.google.com/spreadsheets/d/1LI8NZtEa9KTZVWf53uAW3y2E4yoT9ToVRHY8ZCbAan0/edit?gid=1711597699"
    df_restricciones = conn.read(spreadsheet=url_restricciones, ttl=10)
except Exception as e:
    st.error(f"❌ Error leyendo el Calendario de Restricciones. Detalle: {e}")
    st.stop()

# 5. Lógica de Datos - Plan Maestro
df_plan['Fecha_Inicio'] = pd.to_datetime(df_plan['Fecha_Inicio'], format='%d/%m/%Y', errors='coerce')
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

st.subheader("🎯 Tu Hito Semanal")
st.info(f"**Fase:** {fase_actual} | **Enfoque:** {enfoque_actual}")
st.success(f"**Misión de esta semana:** {hito_actual}")

with st.expander("Ver el plan maestro completo"):
    df_mostrar = df_plan.copy()
    df_mostrar['Fecha_Inicio'] = df_mostrar['Fecha_Inicio'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_mostrar)

st.divider()

# 6. Módulos V2.0: Registro y Salud
df_registro = df_registro.dropna(subset=['Fecha'])
df_registro['Fecha'] = pd.to_datetime(df_registro['Fecha'], format='%d/%m/%Y', errors='coerce')
df_registro['Duración_Real_Min'] = pd.to_numeric(df_registro['Duración_Real_Min'], errors='coerce').fillna(0)
df_registro['Dolor_Lumbar'] = pd.to_numeric(df_registro['Dolor_Lumbar'], errors='coerce').fillna(0)
df_registro['Dolor_Codo'] = pd.to_numeric(df_registro['Dolor_Codo'], errors='coerce').fillna(0)

df_semana_actual = df_registro[df_registro['ID_Semana'] == id_semana_actual]
minutos_totales = df_semana_actual['Duración_Real_Min'].sum()
horas_totales = minutos_totales / 60.0

porcentaje_cumplimiento = (horas_totales / volumen_objetivo_hrs * 100) if volumen_objetivo_hrs > 0 else 0.0

col4, col5 = st.columns(2)

with col4:
    st.subheader("📊 Cumplimiento de Volumen")
    st.write(f"**Objetivo de la semana:** {volumen_objetivo_hrs:.1f} hrs")
    st.write(f"**Realizado hasta hoy:** {horas_totales:.1f} hrs")
    
    if porcentaje_cumplimiento >= 90:
        st.success(f"🟢 Excelente ritmo ({porcentaje_cumplimiento:.0f}%). Vas alineado al KPI de éxito.")
    elif porcentaje_cumplimiento >= 70:
        st.warning(f"🟠 Ritmo medio ({porcentaje_cumplimiento:.0f}%). Revisa tu agenda para completar el volumen.")
    else:
        st.error(f"🔴 Ritmo bajo ({porcentaje_cumplimiento:.0f}%). ¡Es hora de ajustar el plan o recuperar sesiones!")
        
    st.progress(min(porcentaje_cumplimiento / 100.0, 1.0))

with col5:
    st.subheader("⚠️ Radar de Salud")
    if not df_registro.empty:
        df_chart = df_registro[['Fecha', 'Dolor_Lumbar', 'Dolor_Codo']].set_index('Fecha')
        st.line_chart(df_chart, color=["#FF0000", "#FFA500"])
        
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

st.divider()

# 7. Módulos V3.1: Métricas Corporales Completas y Restricciones
col6, col7 = st.columns(2)

with col6:
    st.subheader("⚖️ Métricas Corporales")
    df_metricas = df_metricas.dropna(subset=['Fecha'])
    if not df_metricas.empty:
        df_metricas['Fecha'] = pd.to_datetime(df_metricas['Fecha'], format='%d/%m/%Y', errors='coerce')
        # Convertimos todas las columnas relevantes a formato numérico
        df_metricas['Peso_Kg'] = pd.to_numeric(df_metricas['Peso_Kg'], errors='coerce')
        df_metricas['Porcentaje_Grasa'] = pd.to_numeric(df_metricas['Porcentaje_Grasa'], errors='coerce')
        df_metricas['Perimetro_Cintura_Cm'] = pd.to_numeric(df_metricas['Perimetro_Cintura_Cm'], errors='coerce')
        df_metricas['FC_Reposo'] = pd.to_numeric(df_metricas['FC_Reposo'], errors='coerce')
        
        # Gráfica combinada de las 4 variables
        df_metricas_chart = df_metricas[['Fecha', 'Peso_Kg', 'Porcentaje_Grasa', 'Perimetro_Cintura_Cm', 'FC_Reposo']].set_index('Fecha').dropna()
        
        st.write("**Evolución de Variables Físicas**")
        if not df_metricas_chart.empty:
            # Mostramos las 4 líneas al mismo tiempo
            st.line_chart(df_metricas_chart)
        else:
            st.info("Agrega datos numéricos a todas las columnas para ver la tendencia.")
            
        # Tabla siempre visible (sin expander) para lectura directa en móvil
        st.write("**Detalle Numérico Fijo:**")
        df_metricas_show = df_metricas.copy()
        df_metricas_show['Fecha'] = df_metricas_show['Fecha'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_metricas_show, use_container_width=True)
    else:
        st.info("Aún no has registrado métricas corporales.")

with col7:
    st.subheader("🚧 Próximas Restricciones")
    df_restricciones = df_restricciones.dropna(subset=['Fecha'])
    if not df_restricciones.empty:
        df_restricciones['Fecha'] = pd.to_datetime(df_restricciones['Fecha'], format='%d/%m/%Y', errors='coerce')
        
        # Filtrar solo eventos de hoy en adelante
        df_futuras = df_restricciones[df_restricciones['Fecha'] >= pd.to_datetime(fecha_actual.date())]
        
        if not df_futuras.empty:
            for index, row in df_futuras.iterrows():
                fecha_str = row['Fecha'].strftime('%d/%m/%Y')
                tipo = row.get('Tipo_Restriccion', 'Evento')
                severidad = row.get('Severidad', 'Baja')
                desc = row.get('Descripcion', '')
                
                # Asignar color visual según severidad
                if severidad == 'Alta':
                    st.error(f"**{fecha_str} | {tipo} (Severidad {severidad})**: {desc}")
                elif severidad == 'Medio':
                    st.warning(f"**{fecha_str} | {tipo} (Severidad {severidad})**: {desc}")
                else:
                    st.info(f"**{fecha_str} | {tipo} (Severidad {severidad})**: {desc}")
        else:
            st.success("✅ Ruta despejada: No tienes restricciones o eventos próximos registrados.")
    else:
        st.info("Tu calendario de restricciones está vacío.")
