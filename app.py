import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread

# 1. CONFIGURACIÓN
st.set_page_config(page_title="La Quiniela Pro 2026", page_icon="⚽", layout="centered")

# Estilos para asegurar que se vea bien en celular
st.markdown("""
    <style>
    .big-title { font-size:28px !important; font-weight: bold; color: #1E3A8A; text-align: center; }
    .stCheckbox { font-size: 16px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN
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

# 3. EQUIPOS
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

# 4. LÓGICA DE FASE
sh = conectar()
try:
    fase_valor = sh.worksheet("Fase_Actual").acell('A1').value
    fase_actual = int(fase_valor) if fase_valor and fase_valor.isdigit() else 1
except: fase_actual = 1

st.markdown('<p class="big-title">🏆 QUINIELA MUNDIALISTA 2026</p>', unsafe_allow_html=True)

pestana_reg, pestana_leader = st.tabs(["📝 Registrar", "📊 Posiciones"])

with pestana_reg:
    if fase_actual == 1:
        nombre = st.text_input("👤 Tu nombre completo")
        
        # Botones de ayuda
        col1, col2 = st.columns(2)
        if col1.button("🎲 Aleatorio"):
            for eq in todos: st.session_state[f"cb_{eq}"] = False
            for eq in random.sample(todos, 32): st.session_state[f"cb_{eq}"] = True
            st.rerun()
        if col2.button("🧹 Limpiar"):
            for eq in todos: st.session_state[f"cb_{eq}"] = False
            st.rerun()

        # DIBUJAR LOS GRUPOS CON CHECKBOXES
        for grupo, equipos in mundial_grupos.items():
            with st.expander(grupo, expanded=False):
                for eq in equipos:
                    if f"cb_{eq}" not in st.session_state: st.session_state[f"cb_{eq}"] = False
                    st.checkbox(eq, key=f"cb_{eq}")

        # ENVÍO
        if st.button("🚀 Enviar Registro"):
            sel = [eq for eq in todos if st.session_state.get(f"cb_{eq}")]
            if len(sel) == 32:
                sh.worksheet("Participantes").append_row([nombre, ", ".join(sel)])
                st.success("¡Registrado!")
            else: st.error(f"Selecciona exactamente 32. Llevas {len(sel)}.")
    else:
        st.info("La Fase de Grupos ha cerrado. Espera la configuración de los Brackets.")

with pestana_leader:
    # (Aquí va tu lógica de la tabla de posiciones que ya tenías)
    st.write("Cargando posiciones...")