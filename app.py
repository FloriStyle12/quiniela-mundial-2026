import streamlit as st
import random
import os
import gspread
import toml

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

# 3. LÓGICA PRINCIPAL
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
    
    # Inicializar estado para los 48 checkboxes
    for eq in todos:
        if f"cb_{eq}" not in st.session_state: st.session_state[f"cb_{eq}"] = False
        
    col1, col2 = st.columns(2)
    if col1.button("🎲 Aleatorio"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        # Selecciona 32 al azar de los que existan en la lista
        for eq in random.sample(todos, min(len(todos), 32)): st.session_state[f"cb_{eq}"] = True
        st.rerun()
    if col2.button("🧹 Limpiar"):
        for eq in todos: st.session_state[f"cb_{eq}"] = False
        st.rerun()

    for grupo, equipos in mundial_grupos.items():
        with st.expander(grupo):
            for eq in equipos: st.checkbox(eq, key=f"cb_{eq}")
    
    if st.button("Enviar Registro"):
        sel = [eq for eq in todos if st.session_state[f"cb_{eq}"]]
        if len(sel) != 32:
            st.error(f"Debes seleccionar exactamente 32 equipos. Llevas: {len(sel)}")
        else:
            sh.worksheet("Participantes").append_row([nombre, ", ".join(sel)])
            st.success("¡Registrado en 'Participantes'!")

elif fase_actual > 1:
    st.write(f"### Fase Eliminatoria (Fase {fase_actual})")
    st.info("La plataforma está esperando tus datos de esta fase.")

st.write("---")
if st.button("🔄 Actualizar"): st.rerun()