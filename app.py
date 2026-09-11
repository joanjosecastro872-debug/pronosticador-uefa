import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import json

# Configuración de la página
st.set_page_config(
    page_title="Zohan Pronostic - Mobile Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #f0f6fc; }
    .card { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 20px; }
    .metric-card { background-color: #21262d; padding: 15px; border-radius: 8px; border: 1px solid #30363d; text-align: center; }
    .mensaje-box { background-color: #1f242d; padding: 15px; border-radius: 10px; border-left: 5px solid #58a6ff; margin-top: 10px; margin-bottom: 10px; font-size: 16px; }
    .btts-box { background-color: #1b2820; padding: 15px; border-radius: 10px; border-left: 5px solid #3fb950; margin-top: 10px; margin-bottom: 10px; font-size: 16px; }
    .fuerza-box { background-color: #2b1f1d; padding: 15px; border-radius: 10px; border-left: 5px solid #f85149; margin-top: 10px; margin-bottom: 10px; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h2 style='text-align: center; color: #58a6ff;'>🇪🇺 ZOHAN PRONOSTIC - MOTOR CON LECTURA Y MENSAJES</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- DICCIONARIOS DE EQUIPOS ---
EQUIPOS_CHAMPIONS = {
    "Real Madrid": "Top 1", "Barcelona": "Top 1", "Atlético de Madrid": "Top 1", "Villarreal": "Top 1", "Real Betis": "Top 1",
    "Manchester City": "Top 1", "Arsenal": "Top 1", "Liverpool": "Top 1", "Aston Villa": "Top 1", "Manchester United": "Top 1",
    "Bayern Múnich": "Top 1", "Borussia Dortmund": "Top 1", "VfB Stuttgart": "Top 1", "RB Leipzig": "Top 1",
    "Inter de Milán": "Top 1", "Napoli": "Top 1", "Roma": "Top 1", "Como 1907": "Top 1",
    "PSG": "Top 2", "Lille": "Top 2", "Lens": "Top 2",
    "Feyenoord": "Top 2", "PSV Eindhoven": "Top 2", "Porto": "Top 2", "Sporting CP": "Top 2", "Benfica": "Top 2",
    "Fenerbahçe": "Media / Alta", "Galatasaray": "Media / Alta", "Shakhtar Donetsk": "Media / Alta",
    "Club Brujas": "Media / Alta", "Bodø/Glimt": "Media", "Slavia Praga": "Media",
    "Slovan Bratislava": "Menor", "Sturm Graz": "Media", "LASK Linz": "Media",
    "AEK Atenas": "Media", "Viking Stavanger": "Menor", "Sabah": "Menor"
}

EQUIPOS_EUROPA = {
    "Crystal Palace": "Top 1", "Bournemouth": "Top 1", "Sunderland": "Top 1",
    "AC Milan": "Top 1", "Juventus": "Top 1", "Real Sociedad": "Top 1",
    "Celta de Vigo": "Top 1", "Bayer Leverkusen": "Top 1", "Hoffenheim": "Top 1",
    "Olympique de Marsella": "Top 2", "Stade Rennais": "Top 2", "Olympique de Lyon": "Top 2",
    "AZ Alkmaar": "Top 2", "NEC Negen": "Top 2", "Benfica (EL)": "Top 2", "Torreense": "Top 2",
    "Anderlecht": "Media / Alta", "Union Saint-Gilloise": "Media / Alta", "Beşiktaş": "Media / Alta",
    "Olympiacos": "Media / Alta", "OFI Creta": "Media", "Sparta Praga": "Media",
    "Viktoria Plzeň": "Media", "Ferencváros": "Media", "Dinamo Zagreb": "Media / Alta",
    "Red Bull Salzburg": "Media / Alta", "Sturm Graz (EL)": "Media", "Celtic": "Media / Alta",
    "Estrella Roja": "Media / Alta", "Lech Poznań": "Media", "Jagiellonia": "Menor",
    "Lillestrøm": "Media", "Omonia Nicosia": "Menor", "Hapoel Be'er Sheva": "Menor",
    "Celje": "Menor", "Ararat-Armenia": "Menor"
}

EQUIPOS_CONFERENCE = {
    "Atalanta": "Top 1", "Getafe": "Top 1", "SC Friburgo": "Top 1", "AS Monaco": "Top 1",
    "Brighton": "Top 1", "Ajax": "Top 2", "FC Twente": "Top 2", "SC Braga": "Top 2",
    "FC Copenhague": "Media / Alta", "FC Midtjylland": "Media", "FC Nordsjælland": "Media",
    "AGF Aarhus": "Media", "SK Brann": "Media", "Mjällby AIF": "Menor", "KuPS Kuopio": "Menor",
    "Rangers": "Media / Alta", "Heart of Midlothian": "Media", "KAA Gent": "Media / Alta",
    "Sint-Truidense": "Media", "FC Lugano": "Media", "FC St. Gallen": "Media", "FC Thun": "Media",
    "Panathinaikos": "Media / Alta", "Trabzonspor": "Media / Alta", "Crvena Zvezda (Conf)": "Media / Alta",
    "Hajduk Split": "Media", "FK Jablonec": "Menor", "Borac Banja Luka": "Menor",
    "Raków": "Media", "Pafos FC": "Menor", "Riga FC": "Menor", "KF Egnatia": "Menor",
    "Iberia Tbilisi": "Menor", "Kairat Almaty": "Menor", "Kauno Žalgiris": "Menor",
    "CSKA Sofía": "Media", "Universitatea Craiova": "Media"
}

PESO_NIVEL = {"Top 1": 5, "Top 2": 4, "Media / Alta": 3, "Media": 2, "Menor": 1}

# --- INICIALIZAR ESTADO DE SESIÓN ---
def inicializar_estado():
    for torneo_key, dict_eq in [("Champions", EQUIPOS_CHAMPIONS), ("Europa", EQUIPOS_EUROPA), ("Conference", EQUIPOS_CONFERENCE)]:
        key_standings = f"standings_{torneo_key}"
        if key_standings not in st.session_state:
            st.session_state[key_standings] = {
                eq: {
                    "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
                    "Racha": [], "Partidos_Sufridos": []
                }
                for eq, liga in dict_eq.items()
            }
    if 'historial_partidos' not in st.session_state:
        st.session_state.historial_partidos = []

inicializar_estado()

# --- SELECTOR DE TORNEO ---
torneo_uefa = st.selectbox(
    "🏆 Selecciona la Competición Europea",
    ["UEFA Champions League", "UEFA Europa League", "UEFA Conference League"],
    key="select_torneo"
)

if torneo_uefa == "UEFA Champions League":
    standings_key = "standings_Champions"
elif torneo_uefa == "UEFA Europa League":
    standings_key = "standings_Europa"
else:
    standings_key = "standings_Conference"

current_standings = st.session_state[standings_key]
lista_equipos = sorted(list(current_standings.keys()))

st.markdown("---")

# --- PESTAÑAS ---
tab_juego, tab_tabla, tab_analisis, tab_historial, tab_respaldo = st.tabs([
    "⚽ Registrar Partido", 
    "📊 Tabla Viva", 
    "🤖 Pronóstico y Lectura",
    "📜 Historial",
    "💾 Guardar / Cargar"
])

# --- PESTAÑA 1: REGISTRAR PARTIDO ---
with tab_juego:
    st.markdown("### 🏟️ Carga de Resultados")
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🏠 Local")
        equipo_local = st.selectbox("Selecciona Local", lista_equipos, key="loc_sel")
        goles_local = st.number_input("Goles Local", 0, 20, 0, key="g_loc")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_eq2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("✈️ Visitante")
        equipos_vis = [e for e in lista_equipos if e != equipo_local]
        equipo_visita = st.selectbox("Selecciona Visitante", equipos_vis, key="vis_sel")
        goles_visita = st.number_input("Goles Visitante", 0, 20, 0, key="g_vis")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 Registrar Partido", type="primary", use_container_width=True):
        lvl_loc = PESO_NIVEL.get(current_standings[equipo_local]["Liga"], 3)
        lvl_vis = PESO_NIVEL.get(current_standings[equipo_visita]["Liga"], 3)

        current_standings[equipo_local]["PJ"] += 1
        current_standings[equipo_local]["GF"] += goles_local
        current_standings[equipo_local]["GA"] += goles_visita

        current_standings[equipo_visita]["PJ"] += 1
        current_standings[equipo_visita]["GF"] += goles_visita
        current_standings[equipo_visita]["GA"] += goles_local

        if goles_local > goles_visita:
            current_standings[equipo_local]["G"] += 1
            current_standings[equipo_local]["Pts"] += 3
            current_standings[equipo_local]["Racha"].append("G")
            current_standings[equipo_visita]["P"] += 1
            current_standings[equipo_visita]["Racha"].append("P")

            if (lvl_loc - lvl_vis >= 2) and (goles_local - goles_visita == 1):
                msg = f"Ganó ajustado ({goles_local}-{goles_visita}) ante {equipo_visita}"
                current_standings[equipo_local]["Partidos_Sufridos"].append(msg)

        elif goles_visita > goles_local:
            current_standings[equipo_visita]["G"] += 1
            current_standings[equipo_visita]["Pts"] += 3
            current_standings[equipo_visita]["Racha"].append("G")
            current_standings[equipo_local]["P"] += 1
            current_standings[equipo_local]["Racha"].append("P")

            if (lvl_vis - lvl_loc >= 2) and (goles_visita - goles_local == 1):
                msg = f"Ganó ajustado ({goles_visita}-{goles_local}) de visita ante {equipo_local}"
                current_standings[equipo_visita]["Partidos_Sufridos"].append(msg)

        else:
            current_standings[equipo_local]["E"] += 1
            current_standings[equipo_local]["Pts"] += 1
            current_standings[equipo_local]["Racha"].append("E")
            current_standings[equipo_visita]["E"] += 1
            current_standings[equipo_visita]["Pts"] += 1
            current_standings[equipo_visita]["Racha"].append("E")

            if (lvl_loc - lvl_vis >= 2):
                msg = f"Empató en casa contra {equipo_visita}"
                current_standings[equipo_local]["Partidos_Sufridos"].append(msg)

        st.session_state.historial_partidos.append({
            "Torneo": torneo_uefa, "Local": equipo_local, "GL": goles_local, "GV": goles_visita, "Visitante": equipo_visita
        })
        st.success(f"✅ ¡Partido sumado a la tabla!")

# --- PESTAÑA 2: TABLA VIVA ---
with tab_tabla:
    st.markdown(f"### 📊 Tabla Viva - {torneo_uefa}")
    data_list = []
    for eq, stats in current_standings.items():
        dg = stats["GF"] - stats["GA"]
        racha_str = " ".join([f"[{r}]" for r in stats["Racha"][-5:]]) if stats["Racha"] else "Sin partidos"
        prom_gf = round(stats["GF"] / stats["PJ"], 2) if stats["PJ"] > 0 else 0.0
        prom_ga = round(stats["GA"] / stats["PJ"], 2) if stats["PJ"] > 0 else 0.0
        
        data_list.append({
            "Equipo": eq, "Perfil": stats["Liga"], "PJ": stats["PJ"],
            "G": stats["G"], "E": stats["E"], "P": stats["P"],
            "GF": stats["GF"], "GA": stats["GA"], "Prom GF": prom_gf,
            "Prom GA": prom_ga, "DG": dg, "Pts": stats["Pts"], "Forma": racha_str
        })
    
    df_standings = pd.DataFrame(data_list).sort_values(by=["Pts", "DG", "GF"], ascending=False).reset_index(drop=True)
    df_standings.index += 1
    st.dataframe(df_standings, use_container_width=True)

# --- PESTAÑA 3: PRONÓSTICO CON MENSAJES DIRECTOS ---
with tab_analisis:
    st.markdown("### 🔬 Pronóstico, Lectura en Vivo y Marcadores")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pred_local = st.selectbox("Selecciona Local", lista_equipos, key="p_loc")
    with col_p2:
        pred_visita = st.selectbox("Selecciona Visitante", [e for e in lista_equipos if e != pred_local], key="p_vis")
        
    if st.button("🚀 Calcular Estadísticas y Generar Lectura", type="primary", use_container_width=True):
        st_l = current_standings[pred_local]
        st_v = current_standings[pred_visita]
        
        # Promedios de goles directos sin modificar nada
        prom_gf_l = (st_l["GF"] / st_l["PJ"]) if st_l["PJ"] > 0 else {"Top 1": 2.2, "Top 2": 1.7, "Media / Alta": 1.4, "Media": 1.1, "Menor": 0.8}.get(st_l["Liga"], 1.2)
        prom_ga_l = (st_l["GA"] / st_l["PJ"]) if st_l["PJ"] > 0 else 1.0
        prom_gf_v = (st_v["GF"] / st_v["PJ"]) if st_v["PJ"] > 0 else {"Top 1": 2.0, "Top 2": 1.5, "Media / Alta": 1.2, "Media": 1.0, "Menor": 0.7}.get(st_v["Liga"], 1.0)
        prom_ga_v = (st_v["GA"] / st_v["PJ"]) if st_v["PJ"] > 0 else 1.2

        lambda_local = max(0.4, (prom_gf_l + prom_ga_v) / 2.0)
        lambda_visita = max(0.3, (prom_gf_v + prom_ga_l) / 2.0)

        max_goles = 8
        matriz_prob = np.zeros((max_goles, max_goles))
        rho = -0.13

        for i in range(max_goles):
            for j in range(max_goles):
                p_i = poisson.pmf(i, lambda_local)
                p_j = poisson.pmf(j, lambda_visita)
                prob_base = p_i * p_j
                
                if i == 0 and j == 0: tau = 1.0 - (lambda_local * lambda_visita * rho)
                elif i == 1 and j == 0: tau = 1.0 + (lambda_local * rho)
                elif i == 0 and j == 1: tau = 1.0 + (lambda_visita * rho)
                elif i == 1 and j == 1: tau = 1.0 - rho
                else: tau = 1.0
                    
                matriz_prob[i, j] = max(0.0, prob_base * tau)

        matriz_prob /= np.sum(matriz_prob)

        p_local = np.sum(np.tril(matriz_prob, -1)) * 100
        p_empate = np.sum(np.diag(matriz_prob)) * 100
        p_visita = np.sum(np.triu(matriz_prob, 1)) * 100

        p_btts = sum(matriz_prob[i, j] for i in range(1, max_goles) for j in range(1, max_goles)) * 100
        p_over25 = sum(matriz_prob[i, j] for i in range(max_goles) for j in range(max_goles) if (i + j) > 2.5) * 100

        st.markdown("---")
        
        # --- GENERADOR DE MENSAJES Y LECTURA CON VIDA ---
        st.markdown("### 🗣️ Mensaje y Lectura Claro del Partido")
        
        # Mensajes de Fuerza
        if p_local >= 58.0:
            st.markdown(f"<div class='fuerza-box'>💪 **VIENE CON FUERZA DE LOCAL:** **{pred_local}** marca una clara ventaja estadística. Sus números de ataque y los goles encajados por {pred_visita} sugieren que va a dominar el partido de principio a fin.</div>", unsafe_allow_html=True)
        elif p_visita >= 55.0:
            st.markdown(f"<div class='fuerza-box'>🚀 **VIENE CON FUERZA DE VISITANTE:** **{pred_visita}** sobrepasa el nivel del local en los modelos. Tienen toda la tendencia a imponer su jerarquía fuera de casa.</div>", unsafe_allow_html=True)
        elif abs(p_local - p_visita) <= 8.0:
            st.markdown(f"<div class='mensaje-box'>⚖️ **CHOQUE TRABADO Y PAREJO:** Ninguno logra sacarse una ventaja clara. Las probabilidades están muy apretadas y el margen de error será mínimo. Ideal para cubrir empates o hándicaps.</div>", unsafe_allow_html=True)

        # Mensajes de Ambos Marcan (BTTS)
        if p_btts >= 62.0:
            st.markdown(f"<div class='btts-box'>🔥 **AMBOS MARCAN CALIENTE ({p_btts:.1f}%):** Hay una tendencia altísima a que los dos equipos anoten gol. Tanto **{pred_local}** como **{pred_visita}** vienen generando peligro constante pero concediendo en defensa.</div>", unsafe_allow_html=True)
        elif p_btts <= 42.0:
            st.markdown(f"<div class='mensaje-box'>🛡️ **AMBOS MARCAN FRÍO ({p_btts:.1f}%):** Poca probabilidad de goles por ambos lados. Las estadísticas sugieren que al menos uno mantendrá el arco en cero o se impondrá un marcador corto.</div>", unsafe_allow_html=True)

        # Mensajes de Goles (Over / Under)
        if p_over25 >= 60.0:
            st.markdown(f"<div class='btts-box'>⚽ **TENDENCIA A GOLEADA / MARCADOR ABIERTO:** Con un Over 2.5 en **{p_over25:.1f}%**, las tablas vivas marcan un partido de ritmo abierto con alta expectativa de varios goles.</div>", unsafe_allow_html=True)
        elif p_over25 <= 38.0:
            st.markdown(f"<div class='mensaje-box'>🔒 **PARTIDO DE POCOS ESPACIOS:** La expectativa de goles combinada es baja. Marcador cerrado proyectado (tipo 1-0, 0-0, 0-1).</div>", unsafe_allow_html=True)

        # Sufrimiento previo si aplica
        if len(st_l["Partidos_Sufridos"]) > 0:
            for msj in st_l["Partidos_Sufridos"][-2:]:
                st.markdown(f"<div class='mensaje-box'>⚠️ **OJO CON {pred_local.upper()}:** En partidos recientes {msj}. Ha estado apretado.</div>", unsafe_allow_html=True)
        if len(st_v["Partidos_Sufridos"]) > 0:
            for msj in st_v["Partidos_Sufridos"][-2:]:
                st.markdown(f"<div class='mensaje-box'>⚠️ **OJO CON {pred_visita.upper()}:** En partidos recientes {msj}. Ha estado apretado.</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📌 Promedios Actuales de Tabla")
        st.info(f"🏠 **{pred_local}:** Anotado: **{prom_gf_l:.2f}** | Encajado: **{prom_ga_l:.2f}**")
        st.info(f"✈️ **{pred_visita}:** Anotado: **{prom_gf_v:.2f}** | Encajado: **{prom_ga_v:.2f}**")

        st.markdown("### 📊 Porcentajes del Partido")
        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1: st.markdown(f"<div class='metric-card'><h4>Gana {pred_local}</h4><h2>{p_local:.1f}%</h2></div>", unsafe_allow_html=True)
        with res_c2: st.markdown(f"<div class='metric-card'><h4>Empate</h4><h2>{p_empate:.1f}%</h2></div>", unsafe_allow_html=True)
        with res_c3: st.markdown(f"<div class='metric-card'><h4>Gana {pred_visita}</h4><h2>{p_visita:.1f}%</h2></div>", unsafe_allow_html=True)

        res_k1, res_k2 = st.columns(2)
        with res_k1: st.markdown(f"<div class='metric-card' style='margin-top:10px;'><h4>Ambos Anotan</h4><h3>{p_btts:.1f}%</h3></div>", unsafe_allow_html=True)
        with res_k2: st.markdown(f"<div class='metric-card' style='margin-top:10px;'><h4>Más de 2.5 Goles</h4><h3>{p_over25:.1f}%</h3></div>", unsafe_allow_html=True)

        # --- TABLA DE MARCADORES EXACTOS ---
        st.markdown("---")
        st.markdown("### 🎯 Top Marcadores Exactos Más Probables")
        
        marcadores_lista = []
        for i in range(6):
            for j in range(6):
                prob = matriz_prob[i, j] * 100
                marcadores_lista.append({
                    "Marcador": f"{pred_local} {i} - {j} {pred_visita}",
                    "Probabilidad": prob
                })
        
        df_marcadores = pd.DataFrame(marcadores_lista).sort_values(by="Probabilidad", ascending=False).head(8).reset_index(drop=True)
        df_marcadores.index += 1
        df_marcadores["Probabilidad"] = df_marcadores["Probabilidad"].map(lambda x: f"{x:.2f}%")
        
        st.dataframe(df_marcadores, use_container_width=True)

# --- PESTAÑA 4: HISTORIAL ---
with tab_historial:
    st.markdown(f"### 📜 Partidos Registrados - {torneo_uefa}")
    partidos_torneo = [p for p in st.session_state.historial_partidos if p["Torneo"] == torneo_uefa]
    if partidos_torneo:
        st.dataframe(pd.DataFrame(partidos_torneo), use_container_width=True)
    else:
        st.info("No hay partidos registrados en este torneo.")

# --- PESTAÑA 5: GUARDAR Y CARGAR EN EL TELÉFONO ---
with tab_respaldo:
    st.markdown("### 📲 Respaldos para tu Teléfono")
    
    datos_actuales = {
        "standings_Champions": st.session_state["standings_Champions"],
        "standings_Europa": st.session_state["standings_Europa"],
        "standings_Conference": st.session_state["standings_Conference"],
        "historial_partidos": st.session_state["historial_partidos"]
    }
    json_bytes = json.dumps(datos_actuales, ensure_ascii=False, indent=2).encode('utf-8')
    
    st.download_button(
        label="📥 Descargar Respaldo de la Tabla al Teléfono",
        data=json_bytes,
        file_name="respaldo_futbol_zohan.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown("#### 📤 Restaurar la Tabla desde tu Teléfono")
    archivo_subido = st.file_uploader("Selecciona tu archivo de respaldo (.json)", type=["json"])
    
    if archivo_subido is not None:
        try:
            datos_cargados = json.load(archivo_subido)
            st.session_state["standings_Champions"] = datos_cargados["standings_Champions"]
            st.session_state["standings_Europa"] = datos_cargados["standings_Europa"]
            st.session_state["standings_Conference"] = datos_cargados["standings_Conference"]
            st.session_state["historial_partidos"] = datos_cargados["historial_partidos"]
            st.success("✅ ¡Tabla restaurada con éxito!")
        except Exception as e:
            st.error("❌ El archivo no es válido.")

