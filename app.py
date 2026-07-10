import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración básica
st.set_page_config(page_title="Proyecto FINISHER 70.3", layout="wide")
st.title("PROYECTO FINISHER 70.3")

# URL de tu hoja (copiada de tu configuración)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1LI8NZtEa9KTZVWf53uAW3y2E4yoT9ToVRHY8ZCbAan0/edit#gid=1711597699"

try:
    # Iniciar conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer la hoja especificando la URL y el nombre de la pestaña
    df_plan = conn.read(spreadsheet=URL_HOJA, worksheet="Proyecto_FINISHER_703_Panama", ttl=10)
    
    # Mostrar resultados
    st.write("¡Conexión exitosa! Datos cargados:")
    st.dataframe(df_plan)

except Exception as e:
    st.error(f"Error detectado: {e}")
