import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Quiniela Mundial 2026", layout="centered")

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

# 2. EQUIPOS
mundial_grupos = {
    "Grupo A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 República Checa"],
    "Grupo B": ["🇨🇦 Canadá", "🇧🇦 Bosnia y Herzegovina", "🇶🇦 Catar", "🇨🇭 Suiza"],
    "Grupo C": ["🇧🇷 Brasil", "🇲🇦 Marruecos", "🇭🇹 Haití", "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"],
    "Grupo D": ["🇺🇸 Estados Unidos", "🇵🇾 Paraguay", "🇦🇺 Australia", "🇹🇷 Turquía"],
    "Grupo E": ["🇩🇪 Alemania", "🇨🇼 Curazao", "🇨🇮 Costa de Marfil", "🇪🇨 Ecuador"],
    "Grupo F": ["🇳🇱 Países Bajos", "🇯🇵 Japón", "🇸🇪 Suecia", "🇹🇳 Túnez"],
    "Grupo G": ["🇧🇪 Bélgica", "🇪🇬 Egipto", "🇮🇷 Irán", "🇳🇿 Nueva Zelanda"],
    "Grupo H": ["🇪🇸 España", "🇨🇻 Cabo Verde", "🇸🇦 Arabia Saudita", "🇺🇾 Uruguay"],
    "Grupo I": ["🇫🇷 Francia", "🇸🇳 Senegal", "🇮🇶 Irak", "🇳🇴 Noruega"],
    "Grupo J": ["🇦🇷 Argentina", "🇩🇿 Argelia", "🇦🇹 Austria", "🇯🇴 Jordania"],
    "Grupo K": ["🇵🇹 Portugal", "🇨🇩 RD Congo", "🇺🇿 Uzbekistán", "🇨🇴 Colombia"],
    "Grupo L": ["🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "🇭🇷 Croacia", "🇬🇭 Ghana", "🇵🇦 Panamá"]
}
todos = [eq for grupo in mundial_grupos.values() for eq in grupo]

# 3. LÓGICA DE FASE
sh = conectar()
try:
    fase_actual = int(sh.worksheet("Control_Fase").acell('A1').value or 1)
except: fase_actual = 1

st.title("🏆 Quiniela Mundial 2026")

if fase_actual == 1:
    st.write("### Fase 1: Selección de 32 equipos")
    nombre = st.text_input("👤 Tu nombre")
    
    # Inicializar estado para botones
    for eq in todos:
        if f"cb_{eq}" not in st.session_state: st.session_state[f"cb_{eq}"] = False
        
    col1, col2 = st.columns(2)
    if col1.button("🎲 Aleatorio"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        for eq in random.sample(todos, 32): st.session_state[f"cb_{eq}"] = True
        st.rerun()
    if col2.button("🧹 Limpiar"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        st.rerun()

    for grupo, equipos in mundial_grupos.items():
        with st.expander(grupo):
            for eq in equipos:
                st.checkbox(eq, key=f"cb_{eq}")
    
    if st.button("Enviar Registro"):
        sel = [eq for eq in todos if st.session_state[f"cb_{eq}"]]
        sh.worksheet("Participantes_Grupos").append_row([nombre, ", ".join(sel)])
        st.success("¡Registrado!")

elif fase_actual > 1:
    st.write(f"### Eliminatoria: {fase_actual}vos de Final")
    st.info("Ya puedes votar por los clasificados.")

st.write("---")
if st.button("🔄 Actualizar"): st.rerun()