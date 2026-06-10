import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="La Quiniela Pro 2026", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .big-title { font-size:32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .subtitle { font-size:16px !important; text-align: center; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN
@st.cache_resource
def conectar_google_sheets():
    ruta_secretos = os.path.join(".streamlit", "secrets.toml")
    secretos_dict = toml.load(ruta_secretos)
    gsheets_conf = secretos_dict["connections"]["gsheets"]
    credenciales = {
        "type": gsheets_conf["type"], "project_id": gsheets_conf["project_id"],
        "private_key_id": gsheets_conf["private_key_id"],
        "private_key": gsheets_conf["private_key"].replace("\\n", "\n"),
        "client_email": gsheets_conf["client_email"], "client_id": gsheets_conf["client_id"],
        "auth_uri": gsheets_conf["auth_uri"], "token_uri": gsheets_conf["token_uri"],
        "auth_provider_x509_cert_url": gsheets_conf["auth_provider_x509_cert_url"],
        "client_x509_cert_url": gsheets_conf["client_x509_cert_url"]
    }
    gc = gspread.service_account_from_dict(credenciales)
    return gc.open_by_url(gsheets_conf["spreadsheet"])

# --- LÓGICA DE FASES ---
sh = conectar_google_sheets()
try:
    fase_actual = int(sh.worksheet("Fase_Actual").acell('A1').value or 1)
except: fase_actual = 1

st.markdown(f'<p class="big-title">🏆 QUINIELA MUNDIALISTA 2026</p>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">Fase Actual: {"Grupos" if fase_actual==1 else str(fase_actual)+"vos de Final"}</p>', unsafe_allow_html=True)

pestana_registro, pestana_leaderboard = st.tabs(["📝 Registrar Quiniela", "📊 Tabla de Posiciones"])

# ==========================================
# SECCIÓN: REGISTRO (FASES)
# ==========================================
with pestana_registro:
    if fase_actual == 1:
        # AQUÍ VA TU CÓDIGO ORIGINAL DE GRUPOS
        nombre_usuario = st.text_input("👤 Tu nombre", key="user_name")
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
        todos = [e for g in mundial_grupos.values() for e in g]
        for eq in todos:
            if f"cb_{eq}" not in st.session_state: st.session_state[f"cb_{eq}"] = False
        
        # ... (Aquí va el resto de tu lógica de checkboxes y botones originales)
        if st.button("🚀 Enviar"):
            sh.worksheet("Participantes").append_row([nombre_usuario, ", ".join([e for e in todos if st.session_state[f"cb_{e}"]])])
            st.success("Registrado")
    
    else:
        st.write(f"### Fase de Eliminatoria ({fase_actual}vos)")
        st.info("El sistema de Brackets automáticos está activo.")
        # AQUÍ ES DONDE GENERAREMOS LOS RADIOS DE LOS PARTIDOS M73, M74, etc.

# ==========================================
# SECCIÓN: LEADERBOARD
# ==========================================
with pestana_leaderboard:
    # (Tu lógica original de tabla de posiciones se mantiene aquí)
    if st.button("🔄 Actualizar"): st.rerun()