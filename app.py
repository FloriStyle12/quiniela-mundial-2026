import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread  # 🚀 Conector oficial de Google

# Configuración de la página web
st.set_page_config(page_title="La Quiniela Pro 2026", page_icon="⚽", layout="centered")

st.title("🏆 La Quiniela Mundialista 2026")
st.write("Registra tu nombre y selecciona exactamente los 32 equipos que crees que clasificarán a la siguiente ronda.")

st.write("---")

nombre_usuario = st.text_input("👤 Escribe tu nombre completo:", placeholder="Ej. Juan Pérez")

st.write("---")

# Los 12 grupos oficiales del Mundial 2026
mundial_grupos = {
    "Grupo A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 República Checa"],
    "Grupo B": ["🇨🇦 Canadá", "🇧🇦 Bosnia y Herzegovina", "🇶🇦 Catar", "🇨🇭 Suiza"],
    "Grupo C": ["🇧🇷 Brasil", "🇲🇦 Mararruecos", "🇭🇹 Haití", "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"],
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

todos_los_equipos = [equipo for grupo in mundial_grupos.values() for equipo in grupo]

for grupo_lista in mundial_grupos.values():
    for eq in grupo_lista:
        clave_eq = f"cb_{eq}"
        if clave_eq not in st.session_state:
            st.session_state[clave_eq] = False

st.sidebar.header("⚙️ Herramientas de Desarrollo")

if st.sidebar.button("🎲 Llenar 32 Equipos Aleatorios"):
    for eq in todos_los_equipos:
        st.session_state[f"cb_{eq}"] = False
    equipos_azar = random.sample(todos_los_equipos, 32)
    for eq in equipos_azar:
        st.session_state[f"cb_{eq}"] = True
    st.rerun()

if st.sidebar.button("🧹 Limpiar Todo"):
    for eq in todos_los_equipos:
        st.session_state[f"cb_{eq}"] = False
    st.rerun()

equipos_seleccionados = [eq for eq in todos_los_equipos if st.session_state[f"cb_{eq}"]]
total_seleccionados = len(equipos_seleccionados)

for grupo, equipos in mundial_grupos.items():
    st.subheader(f"📅 {grupo}")
    cols = st.columns(2)
    for idx, equipo in enumerate(equipos):
        col_actual = cols[idx % 2]
        clave_checkbox = f"cb_{equipo}"
        esta_encendido = st.session_state[clave_checkbox]
        debe_bloquearse = total_seleccionados >= 32 and not esta_encendido
        col_actual.checkbox(equipo, key=clave_checkbox, disabled=debe_bloquearse)

st.write("---")
st.metric(label="Equipos seleccionados", value=f"{total_seleccionados} / 32")

if not nombre_usuario.strip():
    st.warning("⚠️ Por favor, escribe tu nombre arriba para poder activar el botón de enviar.")

elif total_seleccionados == 32:
    st.success(f"¡Perfecto, {nombre_usuario}! Has alcanzado el límite de 32 equipos. Las demás opciones se han bloqueado.")
    
    if st.button("Enviar Mi Quiniela 🚀"):
        try:
            # 1. Cargar datos del secrets.toml manualmente usando la librería toml
            ruta_secretos = os.path.join(".streamlit", "secrets.toml")
            secretos_dict = toml.load(ruta_secretos)
            gsheets_conf = secretos_dict["connections"]["gsheets"]
            
            # 2. Reconstruir el diccionario de credenciales oficiales de Google
            credenciales = {
                "type": gsheets_conf["type"],
                "project_id": gsheets_conf["project_id"],
                "private_key_id": gsheets_conf["private_key_id"],
                "private_key": gsheets_conf["private_key"].replace("\\n", "\n"), # Limpiamos saltos de línea de la clave
                "client_email": gsheets_conf["client_email"],
                "client_id": gsheets_conf["client_id"],
                "auth_uri": gsheets_conf["auth_uri"],
                "token_uri": gsheets_conf["token_uri"],
                "auth_provider_x509_cert_url": gsheets_conf["auth_provider_x509_cert_url"],
                "client_x509_cert_url": gsheets_conf["client_x509_cert_url"]
            }
            
            # 3. Autenticación directa con la API oficial de Google
            gc = gspread.service_account_from_dict(credenciales)
            
            # 4. Abrir la hoja usando su URL directa
            url_hoja = gsheets_conf["spreadsheet"]
            sh = gc.open_by_url(url_hoja)
            worksheet = sh.get_worksheet(0) # Abre la primera pestaña
            
            # 5. Preparar la nueva fila con los datos
            equipos_texto = ", ".join(sorted(equipos_seleccionados))
            nueva_fila = [nombre_usuario.strip(), equipos_texto]
            
            # 6. Insertar la fila al final de la hoja de cálculo
            worksheet.append_row(nueva_fila)
            
            st.balloons()
            st.success("¡Tu quiniela ha sido registrada exitosamente en Google Sheets con el conector nativo! 🏆")
            
        except Exception as e:
            st.error("Error crítico en la conexión nativa de Google.")
            st.code(e)
else:
    st.warning(f"Aún te faltan equipos. Tienes {total_seleccionados} de 32.")