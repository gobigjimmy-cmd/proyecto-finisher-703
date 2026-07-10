# Conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Forzamos la lectura directa usando la URL de tus Secrets y tu pestaña real
    df_plan = conn.read(
        spreadsheet=st.secrets["connections"]["gsheets"]["url"],
        worksheet="Proyecto_FINISHER_703_Panama"
    )
    
    # Asegurar formato de fecha
    df_plan['Fecha_Inicio'] = pd.to_datetime(df_plan['Fecha_Inicio'])
