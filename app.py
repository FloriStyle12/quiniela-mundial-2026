import streamlit as st
import random
import os
import gspread
import toml

# 1. CONEXIÓN (Mantenemos tu configuración actual)
@st.cache_resource
def conectar():
    ruta = os.path.join(".streamlit", "secrets.toml")
    conf = toml.load(ruta)["connections"]["gsheets"]
    creds = {
        "type": conf["type"], "project_id": conf["project_id"],
        "private_key_id": conf["private_key_id"],
        "private_key": conf["private_key"].replace("\\n", "\n"),
        "client_email": conf["client_email"], "client_id": conf["client_id"],
        "auth_uri": conf["auth_uri"], "token_uri": conf["token_uri"],
        "auth_provider_x509_cert_url": conf["auth_provider_x509_cert_url"],
        "client_x509_cert_url": conf["client_x509_cert_url"]
    }
    return gspread.service_account_from_dict(creds).open_by_url(conf["spreadsheet"])

# 2. DEFINICIÓN DE EQUIPOS (Tus grupos originales)
mundial_grupos = {
    "Grupo A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 República Checa"],
    # ... (El resto de tus grupos aquí, como los tenías)
}
todos = [eq for grupo in mundial_grupos.values() for eq in grupo]

# 3. LÓGICA DE FASE (Ajustada a tus nombres de pestañas)
sh = conectar()
try:
    # Lee la fase de la pestaña 'Fase_Actual' celda A1
    fase_valor = sh.worksheet("Fase_Actual").acell('A1').value
    fase_actual = int(fase_valor) if fase_valor and fase_valor.isdigit() else 1
except:
    fase_actual = 1

st.title("🏆 Quiniela Mundial 2026")

if fase_actual == 1:
    st.write("### Fase 1: Selección de 32 equipos")
    nombre = st.text_input("👤 Tu nombre")
    
    # Inicialización de estado
    for eq in todos:
        if f"cb_{eq}" not in st.session_state: st.session_state[f"cb_{eq}"] = False
        
    if st.button("🎲 Aleatorio"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        for eq in random.sample(todos, 32): st.session_state[f"cb_{eq}"] = True
        st.rerun()

    for grupo, equipos in mundial_grupos.items():
        with st.expander(grupo):
            for eq in equipos: st.checkbox(eq, key=f"cb_{eq}")
    
    if st.button("Enviar Registro"):
        sel = [eq for eq in todos if st.session_state[f"cb_{eq}"]]
        # Usa tu pestaña existente 'Participantes'
        sh.worksheet("Participantes").append_row([nombre, ", ".join(sel)])
        st.success("¡Registrado en 'Participantes'!")

elif fase_actual > 1:
    st.write(f"### Fase Eliminatoria (Fase {fase_actual})")
    # Aquí irá tu lógica para registrar en 'Respuestas_Fases'