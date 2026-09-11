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
st.markdown("<p style='text-align: center; color: #8b949e;'>Simulación avanzada con Monte Carlo (3,000 reps), Memoria Inteligente H2H y Analista Táctico.</p>", unsafe_allow_html=True)
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
    st.session_state.torneo_actual = "Champions"

for torneo_key, dict_eq in [("Champions", EQUIPOS_CHAMPIONS), ("Europa", EQUIPOS_EUROPA), ("Conference", EQUIPOS_CONFERENCE)]:
    key_name = f"standings_{torneo_key}"
    if key_name not in st.session_state:
        st.session_state[key_name] = {
            eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GA": 0, "Pts": 0, "Liga": liga,
                 "Casa_PJ": 0, "Casa_GF": 0, "Casa_GA": 0,
                 "Visita_PJ": 0, "Visita_GF": 0, "Visita_GA": 0}
            for eq, liga in dict_eq.items()
        }

if 'historial_partidos' not in st.session_state:
    st.session_state.historial_partidos = []

# --- 3. BOTONES DE NAVEGACIÓN HORIZONTALES (ESTILO MÓVIL) ---
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("🌟 Champions", use_container_width=True):
        st.session_state.torneo_actual = "Champions"
with col_b2:
    if st.button("🥈 Europa", use_container_width=True):
        st.session_state.torneo_actual = "Europa"
with col_b3:
    if st.button("🥉 Conference", use_container_width=True):
        st.session_state.torneo_actual = "Conference"

if st.session_state.torneo_actual == "Champions":
    nombre_torneo_completo = "UEFA Champions League"
    dic_equipos = EQUIPOS_CHAMPIONS
    standings_key = "standings_Champions"
elif st.session_state.torneo_actual == "Europa":
    nombre_torneo_completo = "UEFA Europa League"
    dic_equipos = EQUIPOS_EUROPA
    standings_key = "standings_Europa"
else:
    nombre_torneo_completo = "UEFA Conference League"
    dic_equipos = EQUIPOS_CONFERENCE
    standings_key = "standings_Conference"

current_standings = st.session_state[standings_key]

st.markdown(f"<p style='text-align: center; color: #58a6ff; font-weight: bold;'>Competición Activa: {nombre_torneo_completo}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. REGISTRO DE PARTIDOS ---
st.markdown("### 📝 Registrar Partido de la Jornada")
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([2, 1, 1, 2, 1])

lista_nombres_eq = sorted(list(dic_equipos.keys()))

with col_p1:
    eq_local_reg = st.selectbox("Local", lista_nombres_eq, key="reg_local")
with col_p2:
    goles_local_reg = st.number_input("GL", 0, 20, 0, key="reg_gl")
with col_p3:
    goles_vis_reg = st.number_input("GV", 0, 20, 0, key="reg_gv")
with col_p4:
    eq_vis_reg = st.selectbox("Visita", lista_nombres_eq, index=1 if len(lista_nombres_eq) > 1 else 0, key="reg_vis")
with col_p5:
    st.markdown("<br>", unsafe_allow_html=True)
    registrar_btn = st.button("💾 Guardar", use_container_width=True)

if registrar_btn:
    if eq_local_reg == eq_vis_reg:
        st.error("⚠️ El local y visita deben ser distintos.")
    else:
        current_standings[eq_local_reg]["PJ"] += 1
        current_standings[eq_local_reg]["Casa_PJ"] += 1
        current_standings[eq_local_reg]["GF"] += goles_local_reg
        current_standings[eq_local_reg]["Casa_GF"] += goles_local_reg
        current_standings[eq_local_reg]["GA"] += goles_vis_reg
        current_standings[eq_local_reg]["Casa_GA"] += goles_vis_reg

        current_standings[eq_vis_reg]["PJ"] += 1
        current_standings[eq_vis_reg]["Visita_PJ"] += 1
        current_standings[eq_vis_reg]["GF"] += goles_vis_reg
        current_standings[eq_vis_reg]["Visita_GF"] += goles_vis_reg
        current_standings[eq_vis_reg]["GA"] += goles_local_reg
        current_standings[eq_vis_reg]["Visita_GA"] += goles_local_reg

        if goles_local_reg > goles_vis_reg:
            current_standings[eq_local_reg]["G"] += 1
            current_standings[eq_local_reg]["Pts"] += 3
            current_standings[eq_vis_reg]["P"] += 1
        elif goles_local_reg < goles_vis_reg:
            current_standings[eq_vis_reg]["G"] += 1
            current_standings[eq_vis_reg]["Pts"] += 3
            current_standings[eq_local_reg]["P"] += 1
        else:
            current_standings[eq_local_reg]["E"] += 1
            current_standings[eq_local_reg]["Pts"] += 1
            current_standings[eq_vis_reg]["E"] += 1
            current_standings[eq_vis_reg]["Pts"] += 1

        st.session_state.historial_partidos.append({
            "Torneo": nombre_torneo_completo,
            "Local": eq_local_reg,
            "Goles_L": goles_local_reg,
            "Goles_V": goles_vis_reg,
            "Visita": eq_vis_reg
        })
        st.success(f"✅ Registrado: {eq_local_reg} {goles_local_reg} - {goles_vis_reg} {eq_vis_reg}")

st.markdown("---")

# --- 5. TABLA DE POSICIONES ---
st.markdown(f"### 📊 Tabla de Posiciones - {nombre_torneo_completo}")

tabla_data = []
for eq, stats in current_standings.items():
    dg = stats["GF"] - stats["GA"]
    tabla_data.append({
        "Equipo": eq,
        "PJ": stats["PJ"],
        "G": stats["G"],
        "E": stats["E"],
        "P": stats["P"],
        "GF": stats["GF"],
        "GA": stats["GA"],
        "DG": dg,
        "Pts": stats["Pts"],
        "Perfil": stats["Liga"]
    })

df_tabla = pd.DataFrame(tabla_data)
df_tabla = df_tabla.sort_values(by=["Pts", "DG", "GF"], ascending=[False, False, False]).reset_index(drop=True)
df_tabla.index += 1

st.dataframe(df_tabla, use_container_width=True)

st.markdown("---")

# --- 6. MEMORIA H2H ---
def obtener_memoria_historica(eq_local, eq_visita, historial_partidos):
    if not historial_partidos:
        return "🧠 **Memoria Inteligente:** Sin duelos previos en esta sesión."
    
    duelos = [
        p for p in historial_partidos 
        if p['Torneo'] == nombre_torneo_completo and 
           ((p['Local'] == eq_local and p['Visita'] == eq_visita) or 
            (p['Local'] == eq_visita and p['Visita'] == eq_local))
    ]
    
    if duelos:
        u = duelos[-1]
        ganador = u['Local'] if u['Goles_L'] > u['Goles_V'] else (u['Visita'] if u['Goles_V'] > u['Goles_L'] else "Empate")
        return f"🧠 **Memoria H2H:** Último antecedente directo: **{u['Local']} {u['Goles_L']} - {u['Goles_V']} {u['Visita']}** (Ganador: {ganador})."
    
    return "🧠 **Memoria Inteligente:** Equipos con inercia competitiva activa en la jornada."

# --- 7. SIMULACIÓN MONTE CARLO ---
st.markdown("### 🔬 Simulación y Pronóstico (Monte Carlo x 3,000)")

col_s1, col_s2 = st.columns(2)
with col_s1:
    eq_sim_local = st.selectbox("Local a Simular", lista_nombres_eq, key="sim_l")
with col_s2:
    eq_sim_vis = st.selectbox("Visita a Simular", lista_nombres_eq, index=1 if len(lista_nombres_eq) > 1 else 0, key="sim_v")

if st.button("🚀 EJECUTAR MONTE CARLO", type="primary", use_container_width=True):
    if eq_sim_local == eq_sim_vis:
        st.error("⚠️ Elige equipos distintos.")
    else:
        stats_l = current_standings[eq_sim_local]
        stats_v = current_standings[eq_sim_vis]

        pj_l_casa = max(1, stats_l["Casa_PJ"])
        pj_v_vis = max(1, stats_v["Visita_PJ"])
        pj_l_tot = max(1, stats_l["PJ"])
        pj_v_tot = max(1, stats_v["PJ"])

        gf_casa_l = stats_l["Casa_GF"] / pj_l_casa
        ga_vis_v = stats_v["Visita_GA"] / pj_v_vis if stats_v["Visita_GA"] > 0 else (stats_v["GA"] / pj_l_tot)

        gf_vis_v = stats_v["Visita_GF"] / pj_v_vis
        ga_casa_l = stats_l["Casa_GA"] / pj_l_casa if stats_l["Casa_GA"] > 0 else (stats_l["GA"] / pj_v_tot)

        if stats_l["PJ"] == 0 and stats_v["PJ"] == 0:
            lambda_l = 1.8 if stats_l["Liga"] in ["Top 1", "Top 2"] else 1.2
            lambda_v = 1.4 if stats_v["Liga"] in ["Top 1", "Top 2"] else 0.9
        else:
            lambda_l = max(0.5, (gf_casa_l + ga_vis_v) / 2.0)
            lambda_v = max(0.5, (gf_vis_v + ga_casa_l) / 2.0)

        simulaciones = 3000
        goles_sim_l = np.random.poisson(lambda_l, simulaciones)
        goles_sim_v = np.random.poisson(lambda_v, simulaciones)

        wins_l = np.sum(goles_sim_l > goles_sim_v)
        wins_v = np.sum(goles_sim_v > goles_sim_l)
        empates = np.sum(goles_sim_l == goles_sim_v)
        overs = np.sum((goles_sim_l + goles_sim_v) > 2.5)
        btts = np.sum((goles_sim_l > 0) & (goles_sim_v > 0))

        p_local = (wins_l / simulaciones) * 100
        p_empate = (empates / simulaciones) * 100
        p_vis = (wins_v / simulaciones) * 100
        p_over = (overs / simulaciones) * 100
        p_btts = (btts / simulaciones) * 100

        nota_memoria = obtener_memoria_historica(eq_sim_local, eq_sim_vis, st.session_state.historial_partidos)
        xg_total = lambda_l + lambda_v

        if abs(lambda_l - lambda_v) > 1.2:
            fav = eq_sim_local if lambda_l > lambda_v else eq_sim_vis
            texto_analisis = f"⚡ **Alerta de rodillo:** El **{fav}** llega con todo el poder ofensivo."
        elif xg_total < 2.1:
            texto_analisis = "🛡️ **¡Cerrojo táctico!** Choque defensivo de margen mínimo (Under)."
        elif lambda_l > 1.4 and lambda_v > 1.4:
            texto_analisis = "⚽ **¡Lluvia de goles!** Alto porcentaje de ambos marcan."
        else:
            texto_analisis = "⚖️ **¡Pronóstico reservado!** Paridad estadística total."

        conteo_marcadores = {}
        for gl, gv in zip(goles_sim_l, goles_sim_v):
            k = (int(gl), int(gv))
            conteo_marcadores[k] = conteo_marcadores.get(k, 0) + 1

        top_5 = sorted(conteo_marcadores.items(), key=lambda x: x[1], reverse=True)[:5]

        st.markdown(f"""
            <div class='card'>
                <h4>🔬 Resultados Monte Carlo</h4>
                <p><b>xG {eq_sim_local}:</b> <code>{lambda_l:.2f}</code> | <b>xG {eq_sim_vis}:</b> <code>{lambda_v:.2f}</code></p>
                <hr style='border-color: #30363d;'>
                <p>🏠 <b>Victoria {eq_sim_local}:</b> <b>{p_local:.1f}%</b></p>
                <p>⚖️ <b>Empate:</b> <b>{p_empate:.1f}%</b></p>
                <p>✈️ <b>Victoria {eq_sim_vis}:</b> <b>{p_vis:.1f}%</b></p>
                <hr style='border-color: #30363d;'>
                <p>⚽ <b>Más 2.5 Goles:</b> <b>{p_over:.1f}%</b> | 🎯 <b>BTTS:</b> <b>{p_btts:.1f}%</b></p>
                <div class='analisis-box'>
                    {texto_analisis}<br><br>{nota_memoria}
                </div>
                <p><b>🎯 Top 5 Marcadores Exactos:</b></p>
                <ul>
        """, unsafe_allow_html=True)

        for item in top_5:
            m = item[0]
            c = item[1]
            prob = (c / simulaciones) * 100
            st.markdown(f"<li><b>{m[0]} - {m[1]}</b> ➔ <b>{prob:.1f}%</b></li>", unsafe_allow_html=True)

        st.markdown("</ul></div>", unsafe_allow_html=True)
        st.success("¡Simulación completada con éxito!")

# --- 8. HISTORIAL Y LIMPIEZA ---
if len(st.session_state.historial_partidos) > 0:
    st.markdown("---")
    st.markdown("### 📜 Historial de Partidos")
    df_historial = pd.DataFrame(st.session_state.historial_partidos)
    st.dataframe(df_historial, use_container_width=True)

    if st.button("🗑️ Consolidar Jornada y Limpiar Historial", type="secondary", use_container_width=True):
        st.session_state.historial_partidos = []
        st.success("¡Historial limpiado! Las tablas de posiciones se mantienen intactas.")
        st.rerun()
