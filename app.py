import streamlit as st
import pandas as pd
import gspread
import random
from google.oauth2.service_account import Credentials

# 1. Configuración de la Página
st.set_page_config(page_title="Quiniela Mundial 2026", layout="centered")

# 2. Conexión Segura a Google Sheets
@st.cache_resource
def conectar_sheets():
    # Reemplaza esto con la configuración de tus secrets de Streamlit
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(st.secrets["gspread"], scopes=scope)
    client = gspread.authorize(creds)
    # Reemplaza con el nombre exacto de tu archivo de Google Sheets
    return client.open("Quiniela_Mundial_2026")

try:
    spreadsheet = conectar_sheets()
except Exception as e:
    st.error("Error al conectar con Google Sheets. Verifica tus credenciales.")
    st.stop()

# 3. Base de Datos de Equipos (12 Grupos - 48 Selecciones)
MUNDIAL_GRUPOS = {
    "Grupo A": ["Canadá 🇨🇦", "Argelia 🇩🇿", "Corea del Sur 🇰🇷", "Francia 🇫🇷"],
    "Grupo B": ["México 🇲🇽", "Australia 🇦🇺", "Túnez 🇹🇳", "Alemania 🇩🇪"],
    "Grupo C": ["Estados Unidos 🇺🇸", "Marruecos 🇲🇦", "Uzbekistán 🇺🇿", "Italia 🇮🇹"],
    "Grupo D": ["Nueva Zelanda 🇳🇿", "Egipto 🇪🇬", "Irak 🇮🇶", "España 🇪🇸"],
    "Grupo E": ["Brasil 🇧🇷", "Catar 🇶🇦", "Camerún 🇨🇲", "Portugal 🇵🇹"],
    "Grupo F": ["Argentina 🇦🇷", "Irán 🇮🇷", "Ghana 🇬🇭", "Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿"],
    "Grupo G": ["Uruguay 🇺🇾", "Japón 🇯🇵", "Senegal 🇸🇳", "Bélgica 🇧🇪"],
    "Grupo H": ["Colombia 🇨🇴", "Arabia Saudita 🇸🇦", "Marruecos 🇲🇦", "Países Bajos 🇳🇱"],
    "Grupo I": ["Ecuador 🇪🇨", "Emiratos Árabes 🇦🇪", "Nigeria 🇳🇬", "Croacia 🇭🇷"],
    "Grupo J": ["Perú 🇵🇪", "Omán 🇴🇲", "Costa de Marfil 🇨🇮", "Dinamarca 🇩🇰"],
    "Grupo L": ["Chile 🇨🇱", "China 🇨🇳", "Sudáfrica 🇿🇦", "Suiza 🇨🇭"],
    "Grupo M": ["Paraguay 🇵🇾", "Australia 🇦🇺", "Zambia 🇿🇲", "Suencia 🇸🇪"]
}

# Lista plana de todos los equipos
TODOS_LOS_EQUIPOS = [equipo for grupo in MUNDIAL_GRUPOS.values() for equipo in grupo]

# 4. Leer Estado Actual del Torneo
sheet_fase = spreadsheet.worksheet("Fase_Actual")
fase_actual = int(sheet_fase.acell('A1').value)

# Inicializar Session States para Fase 1
if "picks_fase1" not in st.session_state:
    st.session_state.picks_fase1 = []

# 5. Menú de Navegación de la App
opcion = st.sidebar.radio("Navegación", ["📝 Registrar Pronósticos", "📊 Tabla de Posiciones"])

# --- VISTA: REGISTRAR PRONÓSTICOS ---
if opcion == "📝 Registrar Pronósticos":
    
    if fase_actual == 1:
        st.title("⚽ Fase de Grupos: Elige tus 32 Clasificados")
        st.write("Selecciona exactamente 32 países de los 12 grupos para avanzar a la ronda eliminatoria.")
        
        # Botón Aleatorio (Random)
        if st.button("🎲 Llenado Aleatorio (Random)"):
            st.session_state.picks_fase1 = random.sample(TODOS_LOS_EQUIPOS, 32)
            st.rerun()

        # Contador Visual
        total_seleccionados = len(st.session_state.picks_fase1)
        st.metric(label="Equipos Seleccionados", value=f"{total_seleccionados} / 32")

        if total_seleccionados > 32:
            st.error("Has seleccionado más de 32 equipos. Remueve algunos antes de guardar.")

        # Renderizar los 12 grupos
        for grupo, equipos in MUNDIAL_GRUPOS.items():
            with st.expander(f"📂 {grupo}"):
                for equipo in equipos:
                    esta_marcado = equipo in st.session_state.picks_fase1
                    
                    # Regla de bloqueo si ya hay 32 seleccionados y este no está marcado
                    debe_bloquearse = total_seleccionados >= 32 and not esta_marcado
                    
                    cb = st.checkbox(
                        equipo, 
                        value=esta_marcado, 
                        disabled=debe_bloquearse,
                        key=f"f1_{equipo}"
                    )
                    
                    # Manejo de clics manuales
                    if cb and equipo not in st.session_state.picks_fase1:
                        st.session_state.picks_fase1.append(equipo)
                        st.rerun()
                    elif not cb and equipo in st.session_state.picks_fase1:
                        st.session_state.picks_fase1.remove(equipo)
                        st.rerun()

        # Formulario de Envío Seguro
        st.write("---")
        if total_seleccionados == 32:
            nombre_usuario = st.text_input("Escribe tu nombre completo para validar tu participación:")
            if st.button("💾 Enviar Quiniela Oficial"):
                if nombre_usuario.strip() == "":
                    st.warning("Por favor, introduce tu nombre antes de guardar.")
                else:
                    try:
                        sheet_usuarios = spreadsheet.worksheet("Fase1_Usuarios")
                        cadena_picks = ", ".join(st.session_state.picks_fase1)
                        sheet_usuarios.append_row([nombre_usuario.strip(), cadena_picks])
                        st.success(f"¡Excelente {nombre_usuario}! Tus 32 selecciones han sido registradas de forma segura.")
                        st.session_state.picks_fase1 = []
                    except Exception as e:
                        st.error(f"Error al conectar con la base de datos: {e}")
        else:
            st.info("El botón para guardar aparecerá automáticamente cuando selecciones exactamente 32 equipos.")

    # --- LÓGICA DE FASES ELIMINATORIAS (16vos, 8vos, etc.) ---
    else:
        st.title(f"🏆 Ronda de {fase_actual}vos de Final")
        st.write("Selecciona al equipo que consideras que ganará cada enfrentamiento directo.")
        
        try:
            sheet_partidos = spreadsheet.worksheet("Eliminatorias_Partidos")
            df_partidos = pd.DataFrame(sheet_partidos.get_all_records())
            
            # Filtrar solo los partidos cargados manualmente para la fase activa
            partidos_activos = df_partidos[df_partidos['Fase'] == fase_actual]
            
            if partidos_activos.empty:
                st.info("El Administrador aún no ha cargado los cruces oficiales para esta fase en Google Sheets.")
            else:
                nombre_usuario = st.text_input("Introduce tu nombre registrado:")
                
                votos_fase = {}
                for idx, row in partidos_activos.iterrows():
                    st.write(f"**Partido {row['Partido_ID']}**")
                    voto = st.radio(
                        "¿Quién avanza?",
                        options=[row['Equipo1'], row['Equipo2']],
                        key=f"el_{row['Partido_ID']}"
                    )
                    votos_fase[row['Partido_ID']] = voto
                    st.write("---")
                
                if st.button("💾 Enviar Votos de Eliminatoria"):
                    if nombre_usuario.strip() == "":
                        st.warning("Debes introducir tu nombre para guardar tus votos.")
                    else:
                        sheet_votos = spreadsheet.worksheet("Eliminatorias_Votos")
                        filas_a_guardar = []
                        for part_id, eleccion in votos_fase.items():
                            filas_a_guardar.append([nombre_usuario.strip(), fase_actual, part_id, eleccion])
                        
                        sheet_votos.append_rows(filas_a_guardar)
                        st.success("Tus pronósticos de eliminación directa han sido guardados exitosamente.")
        except Exception as e:
            st.error(f"Error al procesar las fases eliminatorias: {e}")

# --- VISTA: TABLA DE POSICIONES (STANDINGS) ---
elif opcion == "📊 Tabla de Posiciones":
    st.title("🏆 Tabla de Posiciones General (Standings)")
    st.write("Puntaje acumulado en tiempo real a lo largo de todas las fases del mundial.")
    
    try:
        # 1. Procesar puntos de la Fase de Grupos
        sheet_f1_usuarios = spreadsheet.worksheet("Fase1_Usuarios")
        usuarios_f1 = sheet_f1_usuarios.get_all_records()
        
        sheet_f1_oficiales = spreadsheet.worksheet("Fase1_Oficiales")
        oficiales_f1 = set([row['Equipos_Clasificados'] for row in sheet_f1_oficiales.get_all_records() if row['Equipos_Clasificados']])
        
        tabla_puntos = {}
        
        for u in usuarios_f1:
            nombre = u['Nombre']
            picks_usuario = set([p.strip() for p in u['Equipos_32'].split(",") if p.strip()])
            # Intersección matemática de conjuntos: 1 acierto = 1 punto
            aciertos_f1 = len(picks_usuario & oficiales_f1)
            tabla_puntos[nombre] = {"Fase de Grupos": aciertos_f1, "Eliminatorias": 0, "Total": aciertos_f1}
            
        # 2. Procesar puntos acumulados de Eliminatorias si existen
        sheet_partidos = spreadsheet.worksheet("Eliminatorias_Partidos")
        partidos_oficiales = sheet_partidos.get_all_records()
        
        # Mapeo directo de soluciones oficiales: {Partido_ID: Ganador_Oficial}
        resultados_reales = {p['Partido_ID']: p['Ganador_Oficial'] for p in partidos_oficiales if p['Ganador_Oficial']}
        
        sheet_votos = spreadsheet.worksheet("Eliminatorias_Votos")
        votos_usuarios = sheet_votos.get_all_records()
        
        for v in votos_usuarios:
            nombre = v['Nombre']
            partido = v['Partido_ID']
            voto = v['Voto_Usuario']
            
            # Si el usuario existe en el registro y el partido ya tiene un ganador oficial resuelto
            if nombre in tabla_puntos and partido in resultados_reales:
                if voto == resultados_reales[partido]:
                    # Sumamos 1 punto por acierto en eliminatoria directo al acumulado
                    tabla_puntos[nombre]["Eliminatorias"] += 1
                    tabla_puntos[nombre]["Total"] += 1
                    
        # Convertir datos procesados en DataFrame para visualización profesional
        if tabla_puntos:
            data_ranking = []
            for nombre, datos in tabla_puntos.items():
                data_ranking.append({
                    "Participante": nombre,
                    "Pts Grupos ⚽": datos["Fase de Grupos"],
                    "Pts Eliminatorias 🏆": datos["Eliminatorias"],
                    "Puntaje Total ⭐": datos["Total"]
                })
                
            df_ranking = pd.DataFrame(data_ranking).sort_values(by="Puntaje Total ⭐", ascending=False)
            
            # Estilizar tabla limpia
            st.dataframe(
                df_ranking, 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Aún no se registran participantes en la base de datos.")
            
    except Exception as e:
        st.error(f"Error al compilar la tabla de standings: {e}")