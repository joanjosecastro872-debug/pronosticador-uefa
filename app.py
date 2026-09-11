import streamlit as st
import pandas as pd
import numpy as np

# Configuración inicial de la página
st.set_page_config(
    page_title="Zohan Pronostic - UEFA Engine Pro Max",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS en Modo Oscuro Profesional
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f0f6fc;
    }
    .card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #21262d;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .analisis-box {
        background-color: #1f242d;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #58a6ff;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h2 style='text-align: center; color: #58a6ff;'>🇪🇺 ZOHAN PRONOSTIC - MOTOR UEFA PRO MAX</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Simulación avanzada con Monte Carlo (3,000 reps), Historial de Partidos, Resultados Exactos y Análisis Táctico.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 1. DICCIONARIOS DE EQUIPOS OFICIALES (36 POR TORNEO) ---
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

# --- 2. INICIALIZAR MEMORIA DE SESIÓN ---
if 'torneo_actual' not in st.session_state:
    st.session_state.torneo_actual = "UEFA Champions League"

if 'standings' not in st.session_state:
    st.session_state.standings = {
        eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
             "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
             "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
        for eq, liga in EQUIPOS_CHAMPIONS.items()
    }

if 'historial_partidos' not in st.session_state:
    st.session_state.historial_partidos = []

# --- SELECTOR DE TORNEO ---
torneo_uefa = st.selectbox(
    "🏆 Selecciona la Competición Europea",
    ["UEFA Champions League", "UEFA Europa League", "UEFA Conference League"],
    key="select_torneo"
)

if torneo_uefa != st.session_state.torneo_actual:
    st.session_state.torneo_actual = torneo_uefa
    dic_sel = EQUIPOS_CHAMPIONS if torneo_uefa == "UEFA Champions League" else (EQUIPOS_EUROPA if torneo_uefa == "UEFA Europa League" else EQUIPOS_CONFERENCE)
    st.session_state.standings = {
        eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
             "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
             "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
        for eq, liga in dic_sel.items()
    }
    st.session_state.historial_partidos = []
    st.rerun()

st.markdown("---")

# --- PESTAÑAS DE LA APLICACIÓN ---
tab_juego, tab_tabla, tab_analisis = st.tabs([
    "⚽ Registrar Partido & Historial", 
    "📊 Tabla Viva de Posiciones", 
    "🤖 Motor de Pronóstico (Monte Carlo + Poisson)"
])

lista_equipos = list(st.session_state.standings.keys())

with tab_juego:
    st.markdown("### 🏟️ Carga de Resultados de la Jornada")
    st.markdown("Registra los marcadores. El sistema actualiza la tabla y guarda un historial detallado por si necesitas borrar alguno.")
    
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🏠 Equipo Local (Casa)")
        equipo_local = st.selectbox("Selecciona Local", lista_equipos, key="loc_sel")
        goles_local = st.number_input("Goles Local", 0, 20, 0, key="g_loc")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_eq2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("✈️ Equipo Visitante")
        equipos_visitantes = [e for e in lista_equipos if e != equipo_local]
        equipo_visita = st.selectbox("Selecciona Visitante", equipos_visitantes, key="vis_sel")
        goles_visita = st.number_input("Goles Visitante", 0, 20, 0, key="g_vis")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 Registrar Partido en el Torneo", type="primary", use_container_width=True):
        # Actualizar estadísticas de equipos
        st.session_state.standings[equipo_local]["PJ"] += 1
        st.session_state.standings[equipo_local]["GF"] += goles_local
        st.session_state.standings[equipo_local]["GA"] += goles_visita
        st.session_state.standings[equipo_local]["Casa_PJ"] += 1
        st.session_state.standings[equipo_local]["Casa_GF"] += goles_local
        st.session_state.standings[equipo_local]["Casa_GA"] += goles_visita

        st.session_state.standings[equipo_visita]["PJ"] += 1
        st.session_state.standings[equipo_visita]["GF"] += goles_visita
        st.session_state.standings[equipo_visita]["GA"] += goles_local
        st.session_state.standings[equipo_visita]["Visita_PJ"] += 1
        st.session_state.standings[equipo_visita]["Visita_GF"] += goles_visita
        st.session_state.standings[equipo_visita]["Visita_GA"] += goles_local

        if goles_local > goles_visita:
            st.session_state.standings[equipo_local]["G"] += 1
            st.session_state.standings[equipo_local]["Pts"] += 3
            st.session_state.standings[equipo_visita]["P"] += 1
        elif goles_visita > goles_local:
            st.session_state.standings[equipo_visita]["G"] += 1
            st.session_state.standings[equipo_visita]["Pts"] += 3
            st.session_state.standings[equipo_local]["P"] += 1
        else:
            st.session_state.standings[equipo_local]["E"] += 1
            st.session_state.standings[equipo_local]["Pts"] += 1
            st.session_state.standings[equipo_visita]["E"] += 1
            st.session_state.standings[equipo_visita]["Pts"] += 1
            
        # Guardar en el historial de partidos
        partido_id = len(st.session_state.historial_partidos) + 1
        st.session_state.historial_partidos.append({
            "id": partido_id,
            "local": equipo_local,
            "g_loc": goles_local,
            "g_vis": goles_visita,
            "visita": equipo_visita
        })
            
        st.success(f"¡Marcador guardado con éxito! {equipo_local} {goles_local} - {goles_visita} {equipo_visita}")

    # --- HISTORIAL DE PARTIDOS CON BOTÓN DE BORRAR ---
    st.markdown("---")
    st.markdown("### 📋 Historial de Partidos Registrados")
    if len(st.session_state.historial_partidos) == 0:
        st.info("No hay partidos registrados todavía.")
    else:
        st.markdown("Si cometiste un error en algún partido, puedes eliminarlo aquí y la tabla se recalculará automáticamente.")
        for p in reversed(st.session_state.historial_partidos):
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.markdown(f"**Partido #{p['id']}**: {p['local']} **{p['g_loc']} - {p['g_vis']}** {p['visita']}")
            with col_h2:
                if st.button("🗑️ Borrar", key=f"del_{p['id']}"):
                    # Revertir estadísticas del partido borrado
                    loc = p['local']
                    vis = p['visita']
                    gl = p['g_loc']
                    gv = p['g_vis']

                    st.session_state.standings[loc]["PJ"] -= 1
                    st.session_state.standings[loc]["GF"] -= gl
                    st.session_state.standings[loc]["GA"] -= gv
                    st.session_state.standings[loc]["Casa_PJ"] -= 1
                    st.session_state.standings[loc]["Casa_GF"] -= gl
                    st.session_state.standings[loc]["Casa_GA"] -= gv

                    st.session_state.standings[vis]["PJ"] -= 1
                    st.session_state.standings[vis]["GF"] -= gv
                    st.session_state.standings[vis]["GA"] -= gl
                    st.session_state.standings[vis]["Visita_PJ"] -= 1
                    st.session_state.standings[vis]["Visita_GF"] -= gv
                    st.session_state.standings[vis]["Visita_GA"] -= gl

                    if gl > gv:
                        st.session_state.standings[loc]["G"] -= 1
                        st.session_state.standings[loc]["Pts"] -= 3
                        st.session_state.standings[vis]["P"] -= 1
                    elif gv > gl:
                        st.session_state.standings[vis]["G"] -= 1
                        st.session_state.standings[vis]["Pts"] -= 3
                        st.session_state.standings[loc]["P"] -= 1
                    else:
                        st.session_state.standings[loc]["E"] -= 1
                        st.session_state.standings[loc]["Pts"] -= 1
                        st.session_state.standings[vis]["E"] -= 1
                        st.session_state.standings[vis]["Pts"] -= 1

                    # Eliminar del historial
                    st.session_state.historial_partidos = [x for x in st.session_state.historial_partidos if x["id"] != p["id"]]
                    st.success(f"Partido #{p['id']} eliminado correctamente.")
                    st.rerun()

with tab_tabla:
    st.markdown(f"### 📊 Tabla General de Posiciones - {torneo_uefa}")
    st.markdown("Ordenada automáticamente por Criterios UEFA (Puntos ➔ Diferencia de Goles ➔ Goles a Favor).")
    
    data_list = []
    for eq, stats in st.session_state.standings.items():
        dg = stats["GF"] - stats["GA"]
        data_list.append({
            "Equipo": eq,
            "Liga": stats["Liga"],
            "PJ": stats["PJ"],
            "G": stats["G"],
            "E": stats["E"],
            "P": stats["P"],
            "GF": stats["GF"],
            "GA": stats["GA"],
            "DG": dg,
            "Pts": stats["Pts"]
        })
    
    df_standings = pd.DataFrame(data_list)
    df_standings = df_standings.sort_values(by=["Pts", "DG", "GF"], ascending=False).reset_index(drop=True)
    df_standings.index += 1
    
    st.dataframe(df_standings, use_container_width=True)
    
    if st.button("🔄 Reiniciar Todo el Torneo (Borrar Datos y Historial)"):
        dic_sel = EQUIPOS_CHAMPIONS if torneo_uefa == "UEFA Champions League" else (EQUIPOS_EUROPA if torneo_uefa == "UEFA Europa League" else EQUIPOS_CONFERENCE)
        st.session_state.standings = {
            eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
                 "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
                 "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
            for eq, liga in dic_sel.items()
        }
        st.session_state.historial_partidos = []
        st.rerun()

with tab_analisis:
    st.markdown("### 🤖 Motor de Pronóstico Avanzado (Monte Carlo + Poisson)")
    st.markdown("Simula el encuentro **3,000 veces** con desglose exacto de victorias, empates y marcadores más repetidos.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pred_local = st.selectbox("Selecciona Local para Pronóstico", lista_equipos, key="p_loc")
    with col_p2:
        pred_visita = st.selectbox("Selecciona Visitante para Pronóstico", [e for e in lista_equipos if e != pred_local], key="p_vis")
        
    if st.button("⚡ Ejecutar Simulación (3,000 Repeticiones)", type="primary"):
        stats_l = st.session_state.standings[pred_local]
        stats_v = st.session_state.standings[pred_visita]
        
        # Expectativas base de goles
        lam_l = (stats_l["Casa_GF"] / max(stats_l["Casa_PJ"], 1)) if stats_l["Casa_PJ"] > 0 else 1.5
        lam_v = (stats_v["Visita_GF"] / max(stats_v["Visita_PJ"], 1)) if stats_v["Visita_PJ"] > 0 else 1.1
        
        # Coeficientes de nivel de liga
        coef_map = {"Top 1": 1.2, "Top 2": 1.1, "Media / Alta": 1.0, "Media": 0.9, "Menor": 0.8}
        f_l = coef_map.get(stats_l["Liga"], 1.0)
        f_v = coef_map.get(stats_v["Liga"], 1.0)
        
        lambda_local_final = lam_l * f_l
        lambda_visita_final = lam_v * f_v
        
        # --- SIMULACIÓN MONTE CARLO (3,000 repeticiones) ---
        np.random.seed(42)
        sim_goles_local = np.random.poisson(lambda_local_final, 3000)
        sim_goles_visita = np.random.poisson(lambda_visita_final, 3000)
        
        vueltas_local = int(np.sum(sim_goles_local > sim_goles_visita))
        vueltas_empate = int(np.sum(sim_goles_local == sim_goles_visita))
        vueltas_visita = int(np.sum(sim_goles_local < sim_goles_visita))
        
        prob_l = (vueltas_local / 3000) * 100
        prob_e = (vueltas_empate / 3000) * 100
        prob_v = (vueltas_visita / 3000) * 100
        
        btts_prob = (np.sum((sim_goles_local > 0) & (sim_goles_visita > 0)) / 3000) * 100
        over_25 = (np.sum((sim_goles_local + sim_goles_visita) > 2.5) / 3000) * 100
        
        cuota_l = 100 / prob_l if prob_l > 0 else 99.0
        cuota_e = 100 / prob_e if prob_e > 0 else 99.0
        cuota_v = 100 / prob_v if prob_v > 0 else 99.0

        # Calcular resultados exactos más frecuentes en las simulaciones
        df_sim = pd.DataFrame({"L": sim_goles_local, "V": sim_goles_visita})
        df_sim["Marcador"] = df_sim["L"].astype(str) + " - " + df_sim["V"].astype(str)
        top_marcadores = df_sim["Marcador"].value_counts().head(3)

        st.markdown("---")
        st.markdown("#### 📊 Probabilidades y Desglose de las 3,000 Simulaciones")
        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1:
            st.markdown(f"<div class='metric-card'><h4>Gana {pred_local}</h4><h2>{prob_l:.1f}%</h2><p style='color: #8b949e; font-size: 14px;'>Victorias: <b>{vueltas_local} / 3000</b><br>Cuota Justa: <b>{cuota_l:.2f}</b></p></div>", unsafe_allow_html=True)
        with res_c2:
            st.markdown(f"<div class='metric-card'><h4>Empate</h4><h2>{prob_e:.1f}%</h2><p style='color: #8b949e; font-size: 14px;'>Empates: <b>{vueltas_empate} / 3000</b><br>Cuota Justa: <b>{cuota_e:.2f}</b></p></div>", unsafe_allow_html=True)
        with res_c3:
            st.markdown(f"<div class='metric-card'><h4>Gana {pred_visita}</h4><h2>{prob_v:.1f}%</h2><p style='color: #8b949e; font-size: 14px;'>Victorias: <b>{vueltas_visita} / 3000</b><br>Cuota Justa: <b>{cuota_v:.2f}</b></p></div>", unsafe_allow_html=True)
            
        st.markdown("---")
        extra_c1, extra_c2, extra_c3 = st.columns(3)
        with extra_c1:
            st.metric(label="⚽ Expectativa de Goles (xG)", value=f"{lambda_local_final:.2f} - {lambda_visita_final:.2f}")
        with extra_c2:
            st.metric(label="🔥 Ambos Anotan (BTTS)", value=f"{btts_prob:.1f}%")
        with extra_c3:
            st.metric(label="📈 Más de 2.5 Goles (Over)", value=f"{over_25:.1f}%")

        # Mostrar los marcadores exactos más repetidos
        st.markdown("#### 🎯 Top 3 Resultados Exactos más Frecuentes en las Simulaciones")
        m_col1, m_col2, m_col3 = st.columns(3)
        cols_m = [m_col1, m_col2, m_col3]
        for i, (marcador, veces) in enumerate(top_marcadores.items()):
            porcentaje_m = (veces / 3000) * 100
            with cols_m[i]:
                st.markdown(f"<div class='metric-card' style='padding: 10px;'><h3 style='margin: 0; color: #58a6ff;'>{marcador}</h3><p style='margin: 5px 0 0 0; color: #8b949e; font-size: 13px;'>Repetido {veces} veces ({porcentaje_m:.1f}%)</p></div>", unsafe_allow_html=True)

        # --- LÓGICA DE MENSAJES Y ANÁLISIS INTELIGENTE ---
        total_xg = lambda_local_final + lambda_visita_final
        diff_prob = abs(prob_l - prob_v)

        if btts_prob > 65 and total_xg > 2.8:
            comentario = f"🔥 **Análisis Zohan:** ¡Duelo de poder a poder! Tanto **{pred_local}** como **{pred_visita}** llegan con una pegada tremenda. El modelo huele sangre: alta probabilidad de goles en ambos arcos y un ritmo frenético desde el minuto uno."
        elif total_xg < 2.0 and prob_e > 30:
            comentario = f"♟️ **Análisis Zohan:** Ajá, aquí hay respeto mutuo. Es un ajedrez táctico entre dos planteles donde nadie quiere regalar nada. El margen de error es mínimo y se va a definir por detalles."
        elif diff_prob > 35:
            favorito = pred_local if prob_l > prob_v else pred_visita
            comentario = f"⚡ **Análisis Zohan:** Desequilibrio notable en el papel. **{favorito}** muestra una superioridad clara en su coeficiente de rendimiento y producción ofensiva."
        else:
            comentario = f"⚖️ **Análisis Zohan:** Empate técnico absoluto o cruce súper cerrado. Las simulaciones de Monte Carlo no ven un claro dominador. Cualquier genialidad individual va a inclinar la balanza."

        st.markdown(f"""
            <div class='analisis-box'>
                <h4>🧠 Diagnóstico Táctico Automático</h4>
                <p style='font-size: 16px; line-height: 1.5; color: #f0f6fc; margin-bottom: 0;'>{comentario}</p>
            </div>
        """, unsafe_allow_html=True)
