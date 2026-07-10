import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Proyecto FINISHER 70.3", layout="wide")

st.title("PROYECTO FINISHER 70.3")

try:
    # Conexión simplificada
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer sin forzar el nombre de la hoja primero
    df_plan = conn.read(ttl=10)
    
    # Depuración: mostrar las columnas encontradas para saber qué está leyendo realmente
    st.write("Columnas encontradas:", df_plan.columns.tolist())
    
    # Procesamiento basado en la columna 'Fecha' (que confirmaste existe)
    df_plan['Fecha'] = pd.to_datetime(df_plan['Fecha'])
    
    st.dataframe(df_plan)

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.write("Por favor, asegúrate de que la URL en 'Secrets' sea la URL pública del navegador y que el archivo esté compartido como Lector.")
