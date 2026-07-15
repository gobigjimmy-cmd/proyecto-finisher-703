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

# 4. Creación de Pestañas (Tabs)
tab_dashboard, tab_registro = st.tabs(["📊 Dashboard de Control", "📝 Registrar Entrenamiento"])

# ==========================================
# PESTAÑA 1: DASHBOARD DE CONTROL
# ==========================================
with tab_dashboard:
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Lectura de datos por nombre de pestaña (usando la conexión con Service Account)
    try:
        df_plan = conn.read(worksheet="Proyecto_FINISHER_703_Panama", ttl=10)
    except Exception as e:
        st.error(f"❌ Error leyendo la hoja principal del Plan. Detalle: {e}")
        st.stop()

    try:
        df_registro = conn.read(worksheet="Registro_Diario", ttl=10)
    except Exception as e:
        st.error(f"❌ Error leyendo el Registro Diario. Detalle: {e}")
        st.stop()

    try:
        df_metricas = conn.read(worksheet="Metricas_Corporales", ttl=10)
    except Exception as e:
        st.error(f"❌ Error leyendo las Métricas Corporales. Detalle: {e}")
        st.stop()

    try:
        df_restricciones = conn.read(worksheet="Calendario_Restricciones", ttl=10)
    except Exception as e:
        st.error(f"❌ Error leyendo el Calendario de Restricciones. Detalle: {e}")
        st.stop()

    # Lógica de Datos - Plan Maestro
    df_plan_fecha = df_plan.copy()
    df_plan_fecha['Fecha_Inicio_dt'] = pd.to_datetime(df_plan_fecha['Fecha_Inicio'], format='%d/%m/%Y', errors='coerce')
    semanas_iniciadas = df_plan_fecha[df_plan_fecha['Fecha_Inicio_dt'] <= fecha_actual]

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
        st.dataframe(df_plan)

    st.divider()

    # Módulos V2.0: Registro y Salud
    df_registro_clean = df_registro.dropna(subset=['Fecha']).copy()
    df_registro_clean['Fecha_dt'] = pd.to_datetime(df_registro_clean['Fecha'], format='%d/%m/%Y', errors='coerce')
    df_registro_clean['Duración_Real_Min'] = pd.to_numeric(df_registro_clean['Duración_Real_Min'], errors='coerce').fillna(0)
    df_registro_clean['Dolor_Lumbar'] = pd.to_numeric(df_registro_clean['Dolor_Lumbar'], errors='coerce').fillna(0)
    df_registro_clean['Dolor_Codo'] = pd.to_numeric(df_registro_clean['Dolor_Codo'], errors='coerce').fillna(0)

    df_semana_actual = df_registro_clean[df_registro_clean['ID_Semana'] == id_semana_actual]
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
        if not df_registro_clean.empty:
            df_chart = df_registro_clean[['Fecha', 'Dolor_Lumbar', 'Dolor_Codo']].set_index('Fecha')
            st.line_chart(df_chart, color=["#FF0000", "#FFA500"])
            
            ultimo_lumbar = df_registro_clean.iloc[-1]['Dolor_Lumbar']
            ultimo_codo = df_registro_clean.iloc[-1]['Dolor_Codo']
            
            if ultimo_lumbar >= 3:
                st.error(f"🚨 Alerta L5-S1: El último registro de dolor lumbar fue de {ultimo_lumbar}. PRIORIDAD: Movilidad y técnica.")
            elif ultimo_codo >= 3:
                st.error(f"🚨 Alerta Epicondilitis: El dolor de codo está en {ultimo_codo}. Vigilar vibraciones en la bici y agarre al nadar.")
            else:
                st.success("✅ Sistema físico en verde: Sin molestias preocupantes.")
        else:
            st.info("No hay datos de salud registrados aún.")

    st.divider()

    # Módulos V3.1: Métricas Corporales y Restricciones
    col6, col7 = st.columns(2)

    with col6:
        st.subheader("⚖️ Métricas Corporales")
        df_metricas_clean = df_metricas.dropna(subset=['Fecha']).copy()
        if not df_metricas_clean.empty:
            df_metricas_clean['Peso_Kg'] = pd.to_numeric(df_metricas_clean['Peso_Kg'], errors='coerce')
            df_metricas_clean['Porcentaje_Grasa'] = pd.to_numeric(df_metricas_clean['Porcentaje_Grasa'], errors='coerce')
            df_metricas_clean['Perimetro_Cintura_Cm'] = pd.to_numeric(df_metricas_clean['Perimetro_Cintura_Cm'], errors='coerce')
            df_metricas_clean['FC_Reposo'] = pd.to_numeric(df_metricas_clean['FC_Reposo'], errors='coerce')
            
            df_metricas_chart = df_metricas_clean[['Fecha', 'Peso_Kg', 'Porcentaje_Grasa', 'Perimetro_Cintura_Cm', 'FC_Reposo']].set_index('Fecha').dropna()
            
            st.write("**Evolución de Variables Físicas**")
            if not df_metricas_chart.empty:
                st.line_chart(df_metricas_chart)
            else:
                st.info("Agrega datos numéricos a todas las columnas para ver la tendencia.")
                
            st.write("**Detalle Numérico Fijo:**")
            st.dataframe(df_metricas_clean, use_container_width=True)
        else:
            st.info("Aún no has registrado métricas corporales.")

    with col7:
        st.subheader("🚧 Próximas Restricciones")
        df_restricciones_clean = df_restricciones.dropna(subset=['Fecha']).copy()
        if not df_restricciones_clean.empty:
            df_restricciones_clean['Fecha_dt'] = pd.to_datetime(df_restricciones_clean['Fecha'], format='%d/%m/%Y', errors='coerce')
            df_futuras = df_restricciones_clean[df_restricciones_clean['Fecha_dt'] >= pd.to_datetime(fecha_actual.date())]
            
            if not df_futuras.empty:
                for index, row in df_futuras.iterrows():
                    fecha_str = row['Fecha']
                    tipo = row.get('Tipo_Restriccion', 'Evento')
                    severidad = row.get('Severidad', 'Baja')
                    desc = row.get('Descripcion', '')
                    
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

# ==========================================
# PESTAÑA 2: REGISTRAR ENTRENAMIENTO
# ==========================================
with tab_registro:
    st.header("📝 Nuevo Entrenamiento")
    st.write("Registra tu sesión al terminar. Los datos se sincronizarán automáticamente con tu plan maestro.")
    
    with st.form("form_registro", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        f_fecha = col_f1.date_input("Fecha del entrenamiento", value=fecha_actual_completa.date())
        f_disciplina = col_f2.selectbox("Disciplina", ["Natación", "Ciclismo MTB", "Carrera", "Fuerza / Core", "Movilidad", "Descanso Activo"])
        
        col_f3, col_f4 = st.columns(2)
        f_duracion = col_f3.number_input("Duración Real (minutos)", min_value=0, value=45, step=5)
        f_distancia = col_f4.number_input("Distancia (km) - Deja en 0 para Fuerza/Movilidad", min_value=0.0, value=0.0, step=0.1)
        
        st.divider()
        st.write("**Métricas de Esfuerzo y Salud (Escala 1 a 10)**")
        col_f5, col_f6, col_f7 = st.columns(3)
        f_rpe = col_f5.slider("RPE (Esfuerzo Percibido)", 1, 10, 5)
        f_lumbar = col_f6.slider("Dolor Lumbar (L5-S1)", 0, 10, 0)
        f_codo = col_f7.slider("Dolor Codo (Epicondilitis)", 0, 10, 0)
        
        st.divider()
        f_cumplimiento = st.slider("Porcentaje de Cumplimiento (%)", 0, 100, 100, step=5)
        f_comentarios = st.text_area("Comentarios y Sensaciones", placeholder="Ej: Me sentí muy fuerte en las subidas, leve tensión lumbar al final...")
        
        submitted = st.form_submit_button("Guardar Entrenamiento 💾")
        
        if submitted:
            # 1. Calcular el ID_Semana basado en la fecha seleccionada
            fecha_seleccionada_dt = pd.to_datetime(f_fecha)
            semanas_coincidentes = df_plan_fecha[df_plan_fecha['Fecha_Inicio_dt'] <= fecha_seleccionada_dt]
            
            id_semana_calculado = 0
            if not semanas_coincidentes.empty:
                id_semana_calculado = semanas_coincidentes.iloc[-1]['ID_Semana']
                
            # 2. Crear la nueva fila de datos
            nueva_fila = pd.DataFrame([{
                'Fecha': f_fecha.strftime("%d/%m/%Y"),
                'ID_Semana': id_semana_calculado,
                'Disciplina': f_disciplina,
                'Duración_Real_Min': f_duracion,
                'Distancia_Km': f_distancia,
                'RPE_Esfuerzo': f_rpe,
                'Dolor_Lumbar': f_lumbar,
                'Dolor_Codo': f_codo,
                'Cumplimiento': f_cumplimiento,
                'Comentarios': f_comentarios
            }])
            
            # 3. Concatenar y subir a Google Sheets
            try:
                # Nos aseguramos de mantener el formato original
                df_actualizado = pd.concat([df_registro, nueva_fila], ignore_index=True)
                # Forzamos la actualización explícita a la hoja Registro_Diario
                conn.update(worksheet="Registro_Diario", data=df_actualizado)
                
                st.success("✅ ¡Entrenamiento guardado con éxito en tu base de datos!")
                # Limpiamos caché para que el dashboard recargue la información fresca de inmediato
                st.cache_data.clear()
            except Exception as e:
                st.error(f"❌ Error al guardar en Google Sheets: {e}")
                st.info("Asegúrate de que tu archivo de Google Sheets tenga permisos de 'Editor'.")
