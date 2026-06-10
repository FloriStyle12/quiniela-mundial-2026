import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread
import unicodedata

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="La Quiniela Pro 2026", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .big-title { font-size:32px !important; font-weight: bold; color: #1E3A8A; text-align: center; }
    .subtitle { font-size:16px !important; text-align: center; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🏆 LA QUINIELA MUNDIALISTA 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma oficial de predicciones y resultados.</p>', unsafe_allow_html=True)

def normalizar_texto(texto):
    if not texto: return ""
    texto_limpio = "".join(c for c in texto if c.isalnum() or c.isspace())
    texto_limpio = "".join(c for c in unicodedata.normalize('NFD', texto_limpio) if unicodedata.category(c) != 'Mn')
    return texto_limpio.strip().lower()

@st.cache_resource
def iniciar_cliente_google():
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
    return gspread.service_account_from_dict(credenciales), gsheets_conf["spreadsheet"]

@st.cache_data(ttl=60)
def cargar_datos_quiniela():
    gc, url_hoja = iniciar_cliente_google()
    sh = gc.open_by_url(url_hoja)
    datos_p = sh.get_worksheet(0).get_all_values()
    try: res_oficiales = sh.worksheet("Resultados_Oficiales").col_values(1)[1:]
    except: res_oficiales = []
    try: lista_partidos = sh.worksheet("Partidos_Eliminatoria").get_all_records()
    except: lista_partidos = []
    try: datos_elim = sh.worksheet("Respuestas_Eliminatoria").get_all_values()[1:]
    except: datos_elim = []
    return datos_p, res_oficiales, lista_partidos, datos_elim

p_registro, p_eliminatoria, p_leaderboard = st.tabs(["📝 Fase de Grupos", "⚔️ Rondas Eliminatorias", "📊 Tabla de Posiciones"])

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

with p_registro:
    nombre_u = st.text_input("👤 Tu nombre completo:", key="n_grupos")
    
    # Inicializar estado
    for eq in todos:
        if f"cb_{eq}" not in st.session_state: st.session_state[f"cb_{eq}"] = False
    
    # Panel lateral botones
    st.sidebar.header("⚙️ Panel de Control")
    if st.sidebar.button("🎲 Llenar 32 Equipos (Aleatorio)"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        for eq in random.sample(todos, 32): st.session_state[f"cb_{eq}"] = True
        st.rerun()
    if st.sidebar.button("🧹 Limpiar Selección"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        st.rerun()

    # Selección
    sel = [eq for eq in todos if st.session_state[f"cb_{eq}"]]
    sub = st.tabs(["📌 A-D", "📌 E-H", "📌 I-L"])
    
    grupos_list = list(mundial_grupos.keys())
    for i, g in enumerate(grupos_list):
        with sub[i // 4]:
            st.markdown(f"**{g}**")
            for eq in mundial_grupos[g]:
                st.checkbox(eq, key=f"cb_{eq}", disabled=(len(sel) >= 32 and not st.session_state[f"cb_{eq}"]))

    if len(sel) == 32 and st.button("🚀 Enviar Predicción"):
        gc, url = iniciar_cliente_google()
        gc.open_by_url(url).get_worksheet(0).append_row([nombre_u, ", ".join(sel)])
        st.cache_data.clear()
        st.success("¡Enviado!")

# Lógica de eliminatoria y tabla omitida en este bloque por espacio, usa la que tenías previamente.