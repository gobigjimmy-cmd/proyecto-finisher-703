import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Proyecto FINISHER 70.3", layout="wide")
st.title("PROYECTO FINISHER 70.3")

# URL Limpia (sin parámetros adicionales ni #gid)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1LI8NZtEa9KTZVWf53uAW3y2E4yoT9ToVRHY8ZCbAan0"

try:
    # Crear la conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer la hoja (cambia 'Hoja1' si decidiste renombrarla así en Google Sheets)
    df_plan = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=10)
    
    st.success("¡Conexión exitosa!")
    st.dataframe(df_plan)

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.write("---")
    st.write("### Pasos para arreglarlo:")
    st.markdown("""
    1. Asegúrate de que la pestaña en tu Google Sheet se llame **exactamente** `Hoja1` (sin espacios extra).
    2. Verifica que el archivo esté compartido: **Compartir** -> **Cualquier persona con el enlace** -> **Lector**.
    3. Si el error persiste, el mensaje de arriba nos dará la clave final.
    """)
