import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Proyecto FINISHER 70.3", layout="wide")
st.title("PROYECTO FINISHER 70.3")

# URL base limpia (sin el #gid)
URL_LIMPIA = "https://docs.google.com/spreadsheets/d/1LI8NZtEa9KTZVWf53uAW3y2E4yoT9ToVRHY8ZCbAan0"

try:
    # Iniciar conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer la hoja por nombre
    df_plan = conn.read(spreadsheet=URL_LIMPIA, worksheet="Proyecto_FINISHER_703_Panama", ttl=10)
    
    st.write("¡Conexión establecida con éxito!")
    st.dataframe(df_plan)

except Exception as e:
    st.error(f"Error técnico encontrado: {e}")
    st.markdown("""
    **Posibles causas de este error:**
    1. **Nombre de la pestaña:** Asegúrate de que en tu Google Sheet, la pestaña se llame *exactamente* `Proyecto_FINISHER_703_Panama`.
    2. **Permisos:** Confirma que al dar clic en 'Compartir', diga: 'Cualquier persona con el enlace puede ser Lector'.
    3. **URL:** La URL debe ser la dirección que aparece en la barra de navegación del navegador al abrir la hoja.
    """)
