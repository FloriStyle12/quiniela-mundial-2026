import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread
import re

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="La Quiniela Pro 2026", 
    page_icon="⚽", 
    layout="centered"
)

# Parche visual para banderas en Windows
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Twemoji+Mozilla&display=swap');
    html, body, [data-testid="stWidgetLabel"], .stCheckbox label {
        font-family: 'Twemoji Mozilla', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .big-title { font-size:32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .subtitle { font-size:16px !important; text-align: center; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🏆 LA QUINIELA MUNDIALISTA 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma oficial de predicciones y resultados en tiempo real.</p>', unsafe_allow_html=True)

# FUNCIÓN AUXILIAR: Limpia banderas, emojis y espacios
def limpiar_texto_equipo(texto):
    if not texto:
        return ""
    texto_limpio = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', str(texto))
    return " ".join(texto_limpio.split()).upper()

# 2. CONEXIÓN CENTRALIZADA A GOOGLE SHEETS
def conectar_google_sheets():
    ruta_secretos = os.path.join(".streamlit", "secrets.toml")
    secretos_dict = toml.load(ruta_secretos)
    gsheets_conf = secretos_dict["connections"]["gsheets"]
    
    credenciales = {
        "type": gsheets_conf["type"],
        "project_id": gsheets_conf["project_id"],
        "private_key_id": gsheets_conf["private_key_id"],
        "private_key": gsheets_conf["private_key"].replace("\\n", "\n"),
        "client_email": gsheets_conf["client_email"],
        "client_id": gsheets_conf["client_id"],
        "auth_uri": gsheets_conf["auth_uri"],
        "token_uri": gsheets_conf["token_uri"],
        "auth_provider_x509_cert_url": gsheets_conf["auth_provider_x509_cert_url"],
        "client_x509_cert_url": gsheets_conf["client_x509_cert_url"]
    }
    gc = gspread.service_account_from_dict(credenciales)
    return gc.open_by_url(gsheets_conf["spreadsheet"])

# --- FUNCIONES CON CACHÉ PARA EVITAR EL ERROR 429 ---
# Guarda los datos en caché por 10 minutos (600 segundos) para no saturar a Google
@st.cache_data(ttl=600)
def cargar_datos_sheets():
    sh = conectar_google_sheets()
    
    # Leer Fase Actual
    try:
        ws_fase = sh.worksheet("Fase_Actual")
        fase = int(ws_fase.acell('A1').value)
    except:
        fase = 1
        
    # Leer Participantes Grupos
    ws_participantes = sh.get_worksheet(0)
    datos_p = ws_participantes.get_all_values()
    
    # Leer Resultados Oficiales
    try:
        ws_oficial = sh.worksheet("Resultados_Oficiales")
        oficiales_f1 = [row for row in ws_oficial.col_values(1)[1:] if row]
    except:
        oficiales_f1 = []
        
    # Leer Partidos Eliminatorias
    try:
        ws_partidos = sh.worksheet("Eliminatorias_Partidos")
        partidos_totales = ws_partidos.get_all_records()
    except:
        partidos_totales = []
        
    # Leer Votos Eliminatorias
    try:
        ws_votos = sh.worksheet("Eliminatorias_Votos")
        votos_totales = ws_votos.get_all_records()
    except:
        votos_totales = []
        
    return fase, datos_p, oficiales_f1, partidos_totales, votos_totales

# Cargar los datos de forma optimizada
try:
    fase_actual, datos_p, oficiales_f1, partidos_totales, votos_totales = cargar_datos_sheets()
except Exception as e:
    st.error("Error al obtener los datos de Google Sheets.")
    st.code(e)
    st.stop()


# 3. MENÚ PRINCIPAL (Pestañas de la App)
pestana_registro, pestana_leaderboard = st.tabs(["📝 Registrar Predicciones", "📊 Tabla de Posiciones"])

mundial_grupos = {
    "Grupo A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 República Checa"],
    "Grupo B": ["🇨🇦 Canadá", "🇧🇦 Bosnia y Herzegovina", "🇶🇦 Catar", "🇨🇭 Suiza"],
    "Grupo C": ["🇧🇷 Brasil", "🇲🇦 Marruecos", "🇭🇹 Haití", "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"],
    "Grupo D": ["🇺🇸 Estados Unidos", "🇵🇾 Paraguay", "🇦🇺 Australia", "🇹🇹 Trinidad y Tobago"],
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

# ==========================================
# SECCIÓN 1: REGISTRAR QUINIELA
# ==========================================
with pestana_registro:
    nombre_usuario = st.text_input("👤 Escribe tu nombre completo:", placeholder="Ej. Víctor Rodríguez", key="user_name")
    st.write("---")

    if fase_actual == 1:
        st.subheader("⚽ Fase de Grupos: Tus 32 Clasificados")
        
        for eq in todos_los_equipos:
            clave_eq = f"cb_{eq}"
            if clave_eq not in st.session_state:
                st.session_state[clave_eq] = False

        st.sidebar.header("⚙️ Panel de Control")
        if st.sidebar.button("🎲 Llenar 32 Equipos (Random)"):
            for eq in todos_los_equipos:
                st.session_state[f"cb_{eq}"] = False
            equipos_azar = random.sample(todos_los_equipos, 32)
            for eq in equipos_azar:
                st.session_state[f"cb_{eq}"] = True
            st.rerun()

        if st.sidebar.button("🧹 Limpiar Selección"):
            for eq in todos_los_equipos:
                st.session_state[f"cb_{eq}"] = False
            st.rerun()

        equipos_seleccionados = [eq for eq in todos_los_equipos if st.session_state[f"cb_{eq}"]]
        total_seleccionados = len(equipos_seleccionados)

        sub_tabs = st.tabs(["📌 Grupos A - D", "📌 Grupos E - H", "📌 Grupos I - L"])

        def dibujar_grupo(nombre_grupo):
            st.markdown(f"#### 📅 {nombre_grupo}")
            equipos = mundial_grupos[nombre_grupo]
            cols = st.columns(2)
            for idx, equipo in enumerate(equipos):
                col_actual = cols[idx % 2]
                clave_checkbox = f"cb_{equipo}"
                esta_encendido = st.session_state[clave_checkbox]
                debe_bloquearse = total_seleccionados >= 32 and not esta_encendido
                col_actual.checkbox(equipo, key=clave_checkbox, disabled=debe_bloquearse)

        with sub_tabs[0]:
            dibujar_grupo("Grupo A"); dibujar_grupo("Grupo B"); dibujar_grupo("Grupo C"); dibujar_grupo("Grupo D")
        with sub_tabs[1]:
            dibujar_grupo("Grupo E"); dibujar_grupo("Grupo F"); dibujar_grupo("Grupo G"); dibujar_grupo("Grupo H")
        with sub_tabs[2]:
            dibujar_grupo("Grupo I"); dibujar_grupo("Grupo J"); dibujar_grupo("Grupo K"); dibujar_grupo("Grupo L")

        st.write("---")
        st.metric(label="Seleccionados", value=f"{total_seleccionados} / 32")

        if not nombre_usuario.strip():
            st.info("💡 Por favor, ingresa tu nombre en la parte superior para habilitar el envío.")
        elif total_seleccionados == 32:
            st.success(f"¡Listo, {nombre_usuario}! Has seleccionado exactamente 32 equipos.")
            if st.button("🚀 Enviar mi Quiniela Oficial"):
                try:
                    sh = conectar_google_sheets()
                    ws_registro = sh.get_worksheet(0)
                    equipos_texto = ", ".join(sorted(equipos_seleccionados))
                    ws_registro.append_row([nombre_usuario.strip(), equipos_texto])
                    st.cache_data.clear() # Limpia caché para forzar recarga al enviar
                    st.balloons()
                    st.success("¡Tu quiniela de grupos ha sido registrada con éxito! 🏆")
                except Exception as e:
                    st.error("Error de escritura en el servidor.")
        else:
            st.warning(f"Asegúrate de completar tu selección. Llevas {total_seleccionados} de 32 equipos.")

    else:
        st.subheader(f"🏁 Ronda Eliminatoria: {fase_actual}vos de Final")
        st.write("Selecciona al equipo que ganará en cada partido directo.")
        
        df_partidos = pd.DataFrame(partidos_totales)
        if df_partidos.empty:
            st.info(f"El Comisionado aún no ha estructurado los partidos de la ronda de {fase_actual}vos en Sheets.")
        else:
            partidos_fase = df_partidos[df_partidos['Fase'] == fase_actual]
            if partidos_fase.empty:
                st.info(f"No hay partidos activos para la fase {fase_actual}.")
            else:
                if not nombre_usuario.strip():
                    st.info("💡 Coloca tu nombre arriba para poder registrar tus votos.")
                
                votos_formulario = {}
                for idx, fila_p in partidos_fase.iterrows():
                    p_id = fila_p['Partido_ID']
                    st.markdown(f"##### **Partido {p_id}**")
                    seleccion_voto = st.radio(
                        "¿Quién clasifica a la siguiente ronda?",
                        options=[fila_p['Equipo1'], fila_p['Equipo2']],
                        key=f"vote_{p_id}"
                    )
                    votos_formulario[p_id] = seleccion_voto
                    st.write("---")
                
                if nombre_usuario.strip() and st.button("💾 Enviar Mis Pronósticos"):
                    try:
                        sh = conectar_google_sheets()
                        ws_votos = sh.worksheet("Eliminatorias_Votos")
                        filas_batch = []
                        for part_id, equipo_votado in votos_formulario.items():
                            filas_batch.append([nombre_usuario.strip(), fase_actual, part_id, equipo_votado])
                        
                        ws_votos.append_rows(filas_batch)
                        st.cache_data.clear() # Limpia caché para actualizar las tablas
                        st.balloons()
                        st.success(f"¡Votos para la ronda {fase_actual}vos registrados!")
                    except Exception as e:
                        st.error("Error al guardar los votos.")

# ==========================================
# SECCIÓN 2: LEADERBOARD
# ==========================================
with pestana_leaderboard:
    st.markdown("### 📊 Clasificación General Acumulativa")
    
    # Botón manual para romper la caché y obligar a leer a Google Sheets en tiempo real
    if st.button("🔄 Forzar Actualización desde Google Sheets"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Limpiar resultados oficiales de grupos
        resultados_oficiales_f1 = set([limpiar_texto_equipo(row) for row in oficiales_f1 if row])
        puntuacion_global = {}

        if len(datos_p) > 1:
            filas_usuarios = datos_p[1:] if "nombre" in datos_p[0][0].lower() else datos_p
            for fila in filas_usuarios:
                if len(fila) < 2: continue
                nombre = fila[0].strip()
                lista_equipos_usuario = set([limpiar_texto_equipo(e) for e in fila[1].split(",")])
                
                aciertos_f1 = len(lista_equipos_usuario & resultados_oficiales_f1)
                
                puntuacion_global[nombre] = {
                    "Grupos ⚽": aciertos_f1,
                    "Eliminatorias 🏆": 0,
                    "Total ⭐": aciertos_f1
                }

        # Procesar eliminatorias de forma local usando la data precargada
        if partidos_totales:
            dict_ganadores_reales = {
                p['Partido_ID']: limpiar_texto_equipo(p['Ganador_Oficial']) 
                for p in partidos_totales if p['Ganador_Oficial']
            }
            
            for v in votos_totales:
                u_nombre = v['Nombre'].strip()
                p_id = v['Partido_ID']
                u_voto = limpiar_texto_equipo(v['Voto_Usuario'])
                
                if u_nombre in puntuacion_global and p_id in dict_ganadores_reales:
                    if u_voto == dict_ganadores_reales[p_id]:
                        puntuacion_global[u_nombre]["Eliminatorias 🏆"] += 1
                        puntuacion_global[u_nombre]["Total ⭐"] += 1

        if puntuacion_global:
            ranking_list = [{"Participante": k, **v} for k, v in puntuacion_global.items()]
            df_final = pd.DataFrame(ranking_list).sort_values(by="Total ⭐", ascending=False).reset_index(drop=True)
            df_final.index = df_final.index + 1
            st.dataframe(df_final, use_container_width=True)
            
            if df_final.iloc[0]["Total ⭐"] > 0:
                st.success(f"🔥 ¡**{df_final.iloc[0]['Participante']}** va a la cabeza de la tabla general!")
        else:
            st.info("No hay datos de participación guardados.")

    except Exception as e:
        st.error("No se pudo compilar la tabla acumulada.")