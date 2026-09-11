import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuración inicial de la página
st.set_page_config(
    page_title="Zohan Pronostic - UEFA Engine Pro",
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
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h2 style='text-align: center; color: #58a6ff;'>🇪🇺 ZOHAN PRONOSTIC - MOTOR UEFA & TABLA VIVA</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Sistema automatizado con memoria de sesión, desglose Casa/Visita, coeficientes de liga y Poisson.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 1. DICCIONARIOS DE EQUIPOS OFICIALES (36 POR TORNEO) ---
EQUIPOS_CHAMPIONS = {
    # España
    "Real Madrid": "Top 1", "Barcelona": "Top 1", "Atlético de Madrid": "Top 1", "Villarreal": "Top 1", "Real Betis": "Top 1",
    # Inglaterra
    "Manchester City": "Top 1", "Arsenal": "Top 1", "Liverpool": "Top 1", "Aston Villa": "Top 1", "Manchester United": "Top 1",
    # Alemania
    "Bayern Múnich": "Top 1", "Borussia Dortmund": "Top 1", "VfB Stuttgart": "Top 1", "RB Leipzig": "Top 1",
    # Italia
    "Inter de Milán": "Top 1", "Napoli": "Top 1", "Roma": "Top 1", "Como 1907": "Top 1",
    # Francia
    "PSG": "Top 2", "Lille": "Top 2", "Lens": "Top 2",
    # Países Bajos y Portugal
    "Feyenoord": "Top 2", "PSV Eindhoven": "Top 2", "Porto": "Top 2", "Sporting CP": "Top 2", "Benfica": "Top 2",
    # Previas y Otros
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

# --- 2. INICIALIZAR MEMORIA DE SESIÓN (SESSION STATE) ---
if 'torneo_actual' not in st.session_state:
    st.session_state.torneo_actual = "UEFA Champions League"

if 'standings' not in st.session_state:
    # Inicializamos con Champions por defecto
    st.session_state.standings = {
        eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
             "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
             "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
        for eq, liga in EQUIPOS_CHAMPIONS.items()
    }

# --- SELECTOR DE TORNEO ---
torneo_uefa = st.selectbox(
    "🏆 Selecciona la Competición Europea",
    ["UEFA Champions League", "UEFA Europa League", "UEFA Conference League"],
    key="select_torneo"
)

# Si cambia el torneo, reiniciamos la estructura de la memoria con sus equipos correctos
if torneo_uefa != st.session_state.torneo_actual:
    st.session_state.torneo_actual = torneo_uefa
    dic_sel = EQUIPOS_CHAMPIONS if torneo_uefa == "UEFA Champions League" else (EQUIPOS_EUROPA if torneo_uefa == "UEFA Europa League" else EQUIPOS_CONFERENCE)
    st.session_state.standings = {
        eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
             "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
             "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
        for eq, liga in dic_sel.items()
    }
    st.rerun()

st.markdown("---")

# --- PESTAÑAS DE LA APLICACIÓN ---
tab_juego, tab_tabla, tab_analisis = st.tabs([
    "⚽ Registrar Partido (Casa vs Visita)", 
    "📊 Tabla Viva de Posiciones", 
    "🤖 Motor de Pronóstico (Poisson)"
])

lista_equipos = list(st.session_state.standings.keys())

with tab_juego:
    st.markdown("### 🏟️ Carga de Resultados de la Jornada")
    st.markdown("El sistema procesa de forma automática los datos para la tabla general y separa las estadísticas de **Local (Casa)** y **Visitante** para los futuros pronósticos.")
    
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
        # 1. Actualizar General Local
        st.session_state.standings[equipo_local]["PJ"] += 1
        st.session_state.standings[equipo_local]["GF"] += goles_local
        st.session_state.standings[equipo_local]["GA"] += goles_visita
        
        # Actualizar Específico Casa
        st.session_state.standings[equipo_local]["Casa_PJ"] += 1
        st.session_state.standings[equipo_local]["Casa_GF"] += goles_local
        st.session_state.standings[equipo_local]["Casa_GA"] += goles_visita

        # 2. Actualizar General Visitante
        st.session_state.standings[equipo_visita]["PJ"] += 1
        st.session_state.standings[equipo_visita]["GF"] += goles_visita
        st.session_state.standings[equipo_visita]["GA"] += goles_local
        
        # Actualizar Específico Visita
        st.session_state.standings[equipo_visita]["Visita_PJ"] += 1
        st.session_state.standings[equipo_visita]["Visita_GF"] += goles_visita
        st.session_state.standings[equipo_visita]["Visita_GA"] += goles_local

        # 3. Lógica de Puntos
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
            
        st.success(f"¡Marcador guardado! {equipo_local} {goles_local} - {goles_visita} {equipo_visita} procesado correctamente.")

with tab_tabla:
    st.markdown(f"### 📊 Tabla General de Posiciones - {torneo_uefa}")
    st.markdown("Ordenada automáticamente por Criterios Oficiales UEFA (Puntos ➔ Diferencia de Goles ➔ Goles a Favor).")
    
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
    df_standings.index += 1 # Posición en tabla del 1 al 36
    
    st.dataframe(df_standings, use_container_width=True)
    
    if st.button("🔄 Reiniciar Todo el Torneo (Borrar Datos)"):
        dic_sel = EQUIPOS_CHAMPIONS if torneo_uefa == "UEFA Champions League" else (EQUIPOS_EUROPA if torneo_uefa == "UEFA Europa League" else EQUIPOS_CONFERENCE)
        st.session_state.standings = {
            eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
                 "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
                 "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
            for eq, liga in dic_sel.items()
        }
        st.rerun()

with tab_analisis:
    st.markdown("### 🤖 Motor Matemático de Pronóstico (Poisson + Casa/Visita)")
    st.markdown("Cruza el rendimiento específico del local en su estadio frente al rendimiento del visitante en carretera.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pred_local = st.selectbox("Selecciona Local para Pronóstico", lista_equipos, key="p_loc")
    with col_p2:
        pred_visita = st.selectbox("Selecciona Visitante para Pronóstico", [e for e in lista_equipos if e != pred_local], key="p_vis")
        
    if st.button("⚡ Calcular Probabilidades del Partido", type="primary"):
        # Obtener métricas internas de Casa y Visita registradas en la memoria
        stats_l = st.session_state.standings[pred_local]
        stats_v = st.session_state.standings[pred_visita]
        
        # Promedios de goles Casa vs Visita (con base defensiva/ofensiva por defecto si van 0 partidos)
        lam_l = (stats_l["Casa_GF"] / max(stats_l["Casa_PJ"], 1)) if stats_l["Casa_PJ"] > 0 else 1.5
        lam_v = (stats_v["Visita_GF"] / max(stats_v["Visita_PJ"], 1)) if stats_v["Visita_PJ"] > 0 else 1.1
        
        # Ajuste de coeficiente de liga simple
        coef_map = {"Top 1": 1.2, "Top 2": 1.1, "Media / Alta": 1.0, "Media": 0.9, "Menor": 0.8}
        f_l = coef_map.get(stats_l["Liga"], 1.0)
        f_v = coef_map.get(stats_v["Liga"], 1.0)
        
        lambda_local_final = lam_l * f_l
        lambda_visita_final = lam_v * f_v
        
        # Simulación Poisson matriz 6x6
        prob_matrix = np.outer(
            [poisson.pmf(i, lambda_local_final) for i in range(6)],
            [poisson.pmf(j, lambda_visita_final) for j in range(6)]
        )
        
        win_local = np.sum(np.tril(prob_matrix, -1))
        empate = np.sum(np.diag(prob_matrix))
        win_visita = np.sum(np.triu(prob_matrix, 1))
        
        st.markdown("---")
        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1:
            st.markdown(f"<div class='metric-card'><h4>Gana {pred_local}</h4><h2>{win_local*100:.1f}%</h2></div>", unsafe_allow_html=True)
        with res_c2:
            st.markdown(f"<div class='metric-card'><h4>Empate</h4><h2>{empate*100:.1f}%</h2></div>", unsafe_allow_html=True)
        with res_c3:
            st.markdown(f"<div class='metric-card'><h4>Gana {pred_visita}</h4><h2>{win_visita*100:.1f}%</h2></div>", unsafe_allow_html=True)
            
        st.info(f"💡 **Expectativa de Goles (xG ajustado):** {pred_local} **{lambda_local_final:.2f}** - **{lambda_visita_final:.2f}** {pred_visita}")
