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

# Parche visual para banderas y estilos estéticos
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Twemoji+Mozilla&display=swap');
    html, body, [data-testid="stWidgetLabel"], .stCheckbox label {
        font-family: 'Twemoji Mozilla', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .big-title { font-size:32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .subtitle { font-size:16px !important; text-align: center; color: #4B5563; margin-bottom: 20px; }
    .match-box { 
        background-color: #F3F4F6; 
        padding: 12px; 
        border-radius: 8px; 
        border-left: 5px solid #1E3A8A; 
        margin-bottom: 10px;
    }
    .match-title { font-weight: bold; color: #1F2937; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🏆 LA QUINIELA MUNDIALISTA 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma oficial de predictions y resultados en tiempo real.</p>', unsafe_allow_html=True)

# DICCIONARIO MAESTRO DE BANDERAS (Para transformar texto plano de Sheets a visual estético)
DICCIONARIO_BANDERAS = {
    "mexico": "🇲🇽", "sudafrica": "🇿🇦", "corea del sur": "🇰🇷", "republica checa": "🇨🇿",
    "canada": "🇨🇦", "bosnia y herzegovina": "🇧🇦", "catar": "🇶🇦", "suiza": "🇨🇭",
    "brasil": "🇧🇷", "marruecos": "🇲🇦", "haiti": "🇭🇹", "escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "estados unidos": "🇺🇸", "usa": "🇺🇸", "paraguay": "🇵🇾", "australia": "🇦🇺", "trinidad y tobago": "🇹🇹",
    "alemania": "🇩🇪", "curazao": "🇨🇼", "costa de marfil": "🇨🇮", "ecuador": "🇪🇨",
    "paises bajos": "🇳🇱", "holanda": "🇳🇱", "japon": "🇯🇵", "suecia": "🇸🇪", "tunez": "🇹🇳",
    "belgica": "🇧🇪", "egipto": "🇪🇬", "iran": "🇮🇷", "nueva zelanda": "🇳🇿",
    "espana": "🇪🇸", "cabo verde": "🇨🇻", "arabia saudita": "🇸🇦", "uruguay": "🇺🇾",
    "francia": "🇫🇷", "senegal": "🇸🇳", "iraq": "🇮🇶", "irak": "🇮🇶", "noruega": "🇳🇴",
    "argentina": "🇦🇷", "argelia": "🇩🇿", "austria": "🇦🇹", "jordania": "🇯🇴",
    "portugal": "🇵🇹", "rd congo": "🇨🇩", "uzbekistan": "🇺🇿", "colombia": "🇨🇴",
    "inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "croacia": "🇭🇷", "ghana": "🇬🇭", "panama": "🇵🇦"
}

# MAPEO DE FASES SOLICITADO
MAPEO_FASES = {
    32: "⚽ Fase de Grupos",
    16: "🏁 16vos de Final",
    8: "🔥 8vos de Final",
    4: "🏅 4tos de Final",
    2: "🥵 Semifinal",
    1: "👑 Gran Final"
}

# FUNCIÓN AUXILIAR: Limpia texto para comparaciones
def limpiar_texto_equipo(texto):
    if not texto:
        return ""
    t = str(texto).lower()
    t = re.sub(r'[áàäâ]', 'a', t)
    t = re.sub(r'[éèëê]', 'e', t)
    t = re.sub(r'[íìïî]', 'i', t)
    t = re.sub(r'[óòöô]', 'o', t)
    t = re.sub(r'[úùüû]', 'u', t)
    t = re.sub(r'[^a-zñ ]', '', t)
    return " ".join(t.split())

# FUNCIÓN AUXILIAR: Devuelve el nombre del equipo con su bandera si existe
def obtener_nombre_con_bandera(nombre_plano):
    nombre_limpio = limpiar_texto_equipo(nombre_plano)
    bandera = DICCIONARIO_BANDERAS.get(nombre_limpio, "🏳️") # Bandera blanca si no se encuentra
    # Formatea Capitalizado (Ej: "mexico" -> "México")
    nombre_formateado = str(nombre_plano).strip().title()
    return f"{bandera} {nombre_formateado}"

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

# --- FUNCIONES CON CACHÉ ---
@st.cache_data(ttl=600)
def cargar_datos_sheets():
    sh = conectar_google_sheets()
    
    # Leer Fase Actual
    try:
        ws_fase = sh.worksheet("Fase_Actual")
        fase = int(ws_fase.acell('A1').value)
    except:
        fase = 32 # Default a fase de grupos si falla
        
    ws_participantes = sh.get_worksheet(0)
    datos_p = ws_participantes.get_all_values()
    
    try:
        ws_oficial = sh.worksheet("Resultados_Oficiales")
        oficiales_f1 = [row for row in ws_oficial.col_values(1)[1:] if row]
    except:
        oficiales_f1 = []
        
    try:
        ws_partidos = sh.worksheet("Eliminatorias_Partidos")
        partidos_totales = ws_partidos.get_all_records()
    except:
        partidos_totales = []
        
    try:
        ws_votos = sh.worksheet("Eliminatorias_Votos")
        votos_totales = ws_votos.get_all_records()
    except:
        votos_totales = []
        
    return fase, datos_p, oficiales_f1, partidos_totales, votos_totales

try:
    fase_actual, datos_p, oficiales_f1, partidos_totales, votos_totales = cargar_datos_sheets()
except Exception as e:
    st.error("Error al obtener los datos de Google Sheets.")
    st.stop()

# 3. MENÚ PRINCIPAL
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

    # MODO: FASE DE GRUPOS (Código 32)
    if fase_actual == 32:
        st.subheader(f"{MAPEO_FASES.get(fase_actual, 'Fase de Grupos')}: Tus 32 Clasificados")
        
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
                    st.cache_data.clear()
                    st.balloons()
                    st.success("¡Tu quiniela de grupos ha sido registrada con éxito! 🏆")
                except Exception as e:
                    st.error("Error de escritura en el servidor.")
        else:
            st.warning(f"Asegúrate de completar tu selección. Llevas {total_seleccionados} de 32 equipos.")

    # MODO: BRACKETS ELIMINATORIOS (Códigos 16, 8, 4, 2, 1)
    else:
        nombre_fase_bonito = MAPEO_FASES.get(fase_actual, f"Fase {fase_actual}")
        st.subheader(f"{nombre_fase_bonito}")
        st.write("Selecciona al equipo que ganará en cada partido directo para avanzar de ronda.")
        
        df_partidos = pd.DataFrame(partidos_totales)
        if df_partidos.empty:
            st.info("El Comisionado aún no ha estructurado los partidos en Sheets.")
        else:
            partidos_fase = df_partidos[df_partidos['Fase'] == fase_actual]
            if partidos_fase.empty:
                st.info(f"No hay partidos cargados en la hoja de cálculo para la {nombre_fase_bonito}.")
            else:
                if not nombre_usuario.strip():
                    st.info("💡 Coloca tu nombre arriba para poder registrar tus votos.")
                
                votos_formulario = {}
                
                # Desplegar Brackets con el nuevo diseño estético solicitado
                for idx, fila_p in partidos_fase.iterrows():
                    p_id = fila_p['Partido_ID']
                    
                    # Transformamos texto plano de Sheets a nombres con banderas reales
                    eq1_con_bandera = obtener_nombre_con_bandera(fila_p['Equipo1'])
                    eq2_con_bandera = obtener_nombre_con_bandera(fila_p['Equipo2'])
                    
                    # Contenedor estético visual por partido
                    st.markdown(f"""
                        <div class="match-box">
                            <div class="match-title">Partido {p_id} ─── {nombre_fase_bonito}</div>
                            <div style="color: #4B5563; font-size: 14px;">Mano a mano directo:</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    seleccion_voto = st.radio(
                        f"Selecciona al ganador del Partido {p_id}:",
                        options=[eq1_con_bandera, eq2_con_bandera],
                        key=f"vote_{p_id}",
                        label_visibility="collapsed" # Oculta la etiqueta repetitiva para máxima limpieza visual
                    )
                    
                    # Guardamos el nombre limpio original para enviarlo de vuelta a Sheets sin emojis
                    votos_formulario[p_id] = fila_p['Equipo1'] if seleccion_voto == eq1_con_bandera else fila_p['Equipo2']
                    st.write("") # Espaciador sutil entre llaves
                
                if nombre_usuario.strip() and st.button("💾 Enviar Mis Pronósticos Oficiales"):
                    try:
                        sh = conectar_google_sheets()
                        ws_votos = sh.worksheet("Eliminatorias_Votos")
                        filas_batch = []
                        for part_id, equipo_votado in votos_formulario.items():
                            filas_batch.append([nombre_usuario.strip(), fase_actual, part_id, equipo_votado])
                        
                        ws_votos.append_rows(filas_batch)
                        st.cache_data.clear()
                        st.balloons()
                        st.success(f"¡Tus pronósticos para la fase '{nombre_fase_bonito}' fueron registrados!")
                    except Exception as e:
                        st.error("Error al guardar los votos.")

# ==========================================
# SECCIÓN 2: LEADERBOARD (TABLA DE POSICIONES)
# ==========================================
with pestana_leaderboard:
    st.markdown("### 📊 Clasificación General Acumulativa")
    
    if st.button("🔄 Forzar Actualización desde Google Sheets"):
        st.cache_data.clear()
        st.rerun()

    try:
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