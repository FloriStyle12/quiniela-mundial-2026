import streamlit as st
import pandas as pd
import random
import toml
import os
import gspread

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="La Quiniela Pro 2026", page_icon="⚽", layout="centered")

# Parche visual para banderas en Windows
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Twemoji+Mozilla&display=swap');
    html, body, [data-testid="stWidgetLabel"], .stCheckbox label, .stRadioButton label {
        font-family: 'Twemoji Mozilla', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .big-title { font-size:32px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .subtitle { font-size:16px !important; text-align: center; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🏆 LA QUINIELA MUNDIALISTA 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma oficial de predicciones y resultados en tiempo real.</p>', unsafe_allow_html=True)

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

# 3. MENÚ PRINCIPAL (Pestañas de la App)
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
todos_los_equipos = [eq for grupo in mundial_grupos.values() for eq in grupo]

# ==========================================
# SECCIÓN 1: FASE DE GRUPOS (REGISTRO)
# ==========================================
with p_registro:
    nombre_usuario = st.text_input("👤 Escribe tu nombre completo:", placeholder="Ej. Víctor Rodríguez", key="user_name_grupos")
    st.write("---")
    
    for eq in todos_los_equipos:
        clave_eq = f"cb_{eq}"
        if clave_eq not in st.session_state: st.session_state[clave_eq] = False

    equipos_seleccionados = [eq for eq in todos_los_equipos if st.session_state[f"cb_{eq}"]]
    total_seleccionados = len(equipos_seleccionados)

    sub_tabs = st.tabs(["📌 Grupos A - D", "📌 Grupos E - H", "📌 Grupos I - L"])
    def dibujar_grupo(nombre_grupo):
        st.markdown(f"#### 📅 {nombre_grupo}")
        cols = st.columns(2)
        for idx, equipo in enumerate(mundial_grupos[nombre_grupo]):
            col_actual = cols[idx % 2]
            clave_cb = f"cb_{equipo}"
            debe_bloquearse = total_seleccionados >= 32 and not st.session_state[clave_cb]
            col_actual.checkbox(equipo, key=clave_cb, disabled=debe_bloquearse)

    with sub_tabs[0]: dibujar_grupo("Grupo A"); dibujar_grupo("Grupo B"); dibujar_grupo("Grupo C"); dibujar_grupo("Grupo D")
    with sub_tabs[1]: dibujar_grupo("Grupo E"); dibujar_grupo("Grupo F"); dibujar_grupo("Grupo G"); dibujar_grupo("Grupo H")
    with sub_tabs[2]: dibujar_grupo("Grupo I"); dibujar_grupo("Grupo J"); dibujar_grupo("Grupo K"); dibujar_grupo("Grupo L")

    st.write("---")
    st.metric(label="Seleccionados", value=f"{total_seleccionados} / 32")

    if not nombre_usuario.strip():
        st.info("💡 Ingresa tu nombre arriba para habilitar el envío.")
    elif total_seleccionados == 32:
        if st.button("🚀 Enviar Predicción Grupos"):
            try:
                sh = conectar_google_sheets()
                ws = sh.get_worksheet(0)
                ws.append_row([nombre_usuario.strip(), ", ".join(sorted(equipos_seleccionados))])
                st.balloons()
                st.success("¡Fase de grupos registrada! 🏆")
            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# SECCIÓN 2: RONDAS ELIMINATORIAS (DINÁMICAS)
# ==========================================
with p_eliminatoria:
    st.markdown("### ⚔️ Pronósticos de Eliminación Directa")
    st.write("Selecciona quién ganará cada duelo conforme se vayan definiendo los partidos reales.")
    
    nombre_elim = st.text_input("👤 Confirma tu nombre completo:", placeholder="Debe ser idéntico al que registraste", key="user_name_elim")
    st.write("---")
    
    try:
        sh = conectar_google_sheets()
        # Intentamos leer la pestaña de los duelos directos
        try:
            ws_partidos = sh.worksheet("Partidos_Eliminatoria")
            lista_partidos = ws_partidos.get_all_records()
        except Exception:
            lista_partidos = []
            st.warning("⚠️ El administrador aún no ha dado de alta partidos en 'Partidos_Eliminatoria'.")

        if len(lista_partidos) == 0:
            st.info("No hay partidos disponibles para pronosticar en este momento.")
        else:
            pronosticos_usuario = {}
            # Pintamos de forma dinámica cada partido que el admin puso en Sheets
            for partido in lista_partidos:
                id_p = str(partido["ID_Partido"])
                eq1 = partido["Equipo_1"]
                eq2 = partido["Equipo_2"]
                
                st.markdown(f"##### 📑 Partido #{id_p}")
                # Radio button para elegir al ganador en el cel
                seleccion = st.radio(
                    f"¿Quién avanza a la siguiente ronda?",
                    options=[eq1, eq2],
                    index=None,
                    key=f"partido_{id_p}"
                )
                pronosticos_usuario[id_p] = seleccion
                st.write("")

            if st.button("💾 Guardar mis Pronósticos de Eliminatoria"):
                if not nombre_elim.strip():
                    st.error("Por favor ingresa tu nombre para guardar.")
                elif None in pronosticos_usuario.values():
                    st.warning("Asegúrate de responder todos los partidos que están en pantalla.")
                else:
                    # Guardamos las respuestas en una nueva pestaña oculta para el procesamiento
                    try:
                        try: ws_resp = sh.worksheet("Respuestas_Eliminatoria")
                        except Exception: ws_resp = sh.add_worksheet(title="Respuestas_Eliminatoria", rows="100", cols="20")
                        
                        if len(ws_resp.get_all_values()) == 0:
                            ws_resp.append_row(["Participante", "Partido_ID", "Prediccion"])
                        
                        # Borramos registros viejos de este usuario si ya existían para que pueda actualizar
                        celdas = ws_resp.findall(nombre_elim.strip())
                        for celda in reversed(celdas):
                            if celda.col == 1: ws_resp.delete_rows(celda.row)
                        
                        # Guardamos los nuevos pronósticos uno por uno
                        for id_p, pred in pronosticos_usuario.items():
                            ws_resp.append_row([nombre_elim.strip(), id_p, pred])
                        
                        st.balloons()
                        st.success("¡Tus duelos directos se guardaron correctamente!")
                    except Exception as e: st.error(f"Error al guardar: {e}")
    except Exception as e: st.error(f"Error de conexión: {e}")

# ==========================================
# SECCIÓN 3: LEADERBOARD (TABLA DE POSICIONES)
# ==========================================
with p_leaderboard:
    st.markdown("### 📊 Clasificación General (1 Punto por Acierto)")
    if st.button("🔄 Actualizar Tabla"): st.rerun()

    try:
        sh = conectar_google_sheets()
        
        # 1. Puntos de Fase de Grupos
        ws_p = sh.get_worksheet(0)
        datos_p = ws_p.get_all_values()
        try:
            ws_oficial = sh.worksheet("Resultados_Oficiales")
            res_oficiales_grupos = ws_oficial.col_values(1)[1:]
        except Exception: res_oficiales_grupos = []

        # 2. Puntos de Eliminatoria Directa
        try:
            ws_partidos = sh.worksheet("Partidos_Eliminatoria")
            dict_partidos = {str(p["ID_Partido"]): p["Ganador_Real"] for p in ws_partidos.get_all_records() if p["Ganador_Real"]}
            
            ws_resp_elim = sh.worksheet("Respuestas_Eliminatoria")
            datos_elim = ws_resp_elim.get_all_values()[1:]
        except Exception:
            dict_partidos = {}
            datos_elim = []

        if len(datos_p) <= 1:
            st.info("Aún no hay participantes registrados.")
        else:
            filas_usuarios = datos_p[1:] if "nombre" in datos_p[0][0].lower() else datos_p
            puntuaciones = {}

            # Calculamos puntos de grupos
            for fila in filas_usuarios:
                if len(fila) < 2: continue
                nombre = fila[0].strip()
                equipos = [e.strip() for e in fila[1].split(",")]
                aciertos_g = sum(1 for eq in equipos if eq in res_oficiales_grupos)
                puntuaciones[nombre] = {"Grupos": aciertos_g, "Eliminatoria": 0}

            # Calculamos puntos de eliminatorias
            for row in datos_elim:
                if len(row) < 3: continue
                user = row[0].strip()
                id_partido = str(row[1])
                prediccion = row[2].strip()
                
                if id_partido in dict_partidos and dict_partidos[id_partido] == prediccion:
                    if user in puntuaciones:
                        puntuaciones[user]["Eliminatoria"] += 1

            # Armamos el ranking sumando todo
            lista_ranking = []
            for user, pts in puntuaciones.items():
                total = pts["Grupos"] + pts["Eliminatoria"]
                lista_ranking.append({
                    "Participante": user, 
                    "Pts Grupos ⚽": pts["Grupos"], 
                    "Pts Eliminatoria ⚔️": pts["Eliminatoria"], 
                    "TOTAL ⭐": total
                })

            df = pd.DataFrame(lista_ranking).sort_values(by="TOTAL ⭐", ascending=False).reset_index(drop=True)
            df.index = df.index + 1
            st.dataframe(df, use_container_width=True)
            
            if len(df) > 0:
                st.success(f"🔥 ¡**{df.iloc[0]['Participante']}** va a la cabeza de la competencia!")
    except Exception as e: st.code(e)