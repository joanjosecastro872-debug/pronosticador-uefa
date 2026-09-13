import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import poisson, skellam
import json

# ==========================================
# CONFIGURACIÓN INICIAL Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Pronosticador Pro: Base en Tabla & Montecarlo",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .card-mensaje {
        background-color: #161B22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DICCIONARIOS OFICIALES CON ELO INICIAL
# ==========================================
EQUIPOS_CHAMPIONS = {
    "Real Madrid": ("Top 1", 1750), "Barcelona": ("Top 1", 1730), "Atlético de Madrid": ("Top 1", 1700), "Villarreal": ("Top 1", 1620), "Real Betis": ("Top 1", 1610),
    "Manchester City": ("Top 1", 1800), "Arsenal": ("Top 1", 1760), "Liverpool": ("Top 1", 1770), "Aston Villa": ("Top 1", 1650), "Manchester United": ("Top 1", 1660),
    "Bayern Múnich": ("Top 1", 1780), "Borussia Dortmund": ("Top 1", 1690), "VfB Stuttgart": ("Top 1", 1600), "RB Leipzig": ("Top 1", 1670),
    "Inter de Milán": ("Top 1", 1740), "Napoli": ("Top 1", 1680), "Roma": ("Top 1", 1630), "Como 1907": ("Top 1", 1550),
    "PSG": ("Top 2", 1720), "Lille": ("Top 2", 1600), "Lens": ("Top 2", 1580),
    "Feyenoord": ("Top 2", 1590), "PSV Eindhoven": ("Top 2", 1610), "Porto": ("Top 2", 1640), "Sporting CP": ("Top 2", 1630),
    "Galatasaray": ("Media / Alta", 1540), "Fenerbahçe": ("Media / Alta", 1530), "Shakhtar Donetsk": ("Media / Alta", 1520),
    "Club Brujas": ("Media / Alta", 1510), "Bodø/Glimt": ("Media", 1480), "Slavia Praga": ("Media", 1490),
    "Slovan Bratislava": ("Menor", 1350), "LASK Linz": ("Media", 1470),
    "AEK Atenas": ("Media", 1460), "Viking Stavanger": ("Menor", 1330), "Sabah": ("Menor", 1300)
}

EQUIPOS_EUROPA = {
    "AC Milan": ("Top 1", 1710), "Juventus": ("Top 1", 1700), "Bayer Leverkusen": ("Top 1", 1740), "Hoffenheim": ("Top 1", 1590),
    "Olympique de Marsella": ("Top 2", 1630), "Olympique de Lyon": ("Top 2", 1620), "Stade Rennais": ("Top 2", 1580),
    "Real Sociedad": ("Top 2", 1640), "Celta de Vigo": ("Top 2", 1570), "Crystal Palace": ("Top 2", 1600),
    "Bournemouth": ("Top 2", 1580), "Sunderland": ("Media / Alta", 1500), "AZ Alkmaar": ("Media / Alta", 1520),
    "NEC Nijmegen": ("Media", 1450), "Benfica": ("Top 2", 1660), "União Torreense": ("Menor", 1320),
    "Red Bull Salzburg": ("Media / Alta", 1550), "Sturm Graz": ("Media", 1460), "Beşiktaş": ("Media / Alta", 1530),
    "Ferencváros": ("Media", 1440), "Lech Poznań": ("Media", 1430), "Anderlecht": ("Media", 1450),
    "Viktoria Plzeň": ("Media", 1440), "Sparta Praga": ("Media", 1470), "Celtic": ("Media / Alta", 1510),
    "Dinamo Zagreb": ("Media / Alta", 1500), "Olympiacos": ("Media / Alta", 1520), "Levski Sofia": ("Menor", 1340),
    "OFI Creta": ("Menor", 1300), "Jagiellonia Białystok": ("Menor", 1310), "AC Omonia Nicosia": ("Menor", 1290),
    "Lillestrøm SK": ("Menor", 1330), "FC Ararat-Armenia": ("Menor", 1280), "Hapoel Be'er Sheva": ("Menor", 1320), "NK Celje": ("Menor", 1300)
}

EQUIPOS_CONFERENCE = {
    "Brighton & Hove Albion": ("Top 2", 1650), "Atalanta": ("Top 1", 1720), "Getafe": ("Media / Alta", 1540),
    "SC Freiburg": ("Media / Alta", 1560), "AS Monaco": ("Top 2", 1630), "Ajax": ("Top 2", 1640),
    "FC Twente": ("Media / Alta", 1520), "SC Braga": ("Top 2", 1610), "KAA Gent": ("Media", 1480),
    "Panathinaikos": ("Media", 1470), "FC Lugano": ("Media", 1430), "FC Copenhagen": ("Media", 1500),
    "Midtjylland": ("Media", 1490), "SK Brann": ("Media", 1420), "Hajduk Split": ("Media", 1440),
    "Pafos FC": ("Menor", 1310), "KuPS Kuopio": ("Menor", 1290), "Riga FC": ("Menor", 1300),
    "Inter Club d'Escaldes": ("Menor", 1200), "Hearts": ("Media", 1450), "Jablonec": ("Menor", 1320)
}

# ==========================================
# GESTIÓN DE ESTADO Y PURGA ESTRICTA
# ==========================================
if 'torneo_actual' not in st.session_state:
    st.session_state.torneo_actual = "Champions League"

def obtener_equipos_torneo(torneo):
    if torneo == "Champions League": return EQUIPOS_CHAMPIONS
    elif torneo == "Europa League": return EQUIPOS_EUROPA
    else: return EQUIPOS_CONFERENCE

def purgar_equipos_fuera_de_lugar(nombre_torneo):
    prefix = nombre_torneo.lower().replace(" ", "_")
    equipos_permitidos = set(obtener_equipos_torneo(nombre_torneo).keys())
    key_tabla = f'{prefix}_tabla'
    if key_tabla in st.session_state:
        st.session_state[key_tabla] = {eq: stats for eq, stats in st.session_state[key_tabla].items() if eq in equipos_permitidos}

def inicializar_torneo(nombre_torneo):
    prefix = nombre_torneo.lower().replace(" ", "_")
    equipos_dict = obtener_equipos_torneo(nombre_torneo)
    if f'{prefix}_partidos' not in st.session_state: st.session_state[f'{prefix}_partidos'] = []
    if f'{prefix}_tabla' not in st.session_state: st.session_state[f'{prefix}_tabla'] = {}
    
    for eq, (cat, elo_base) in equipos_dict.items():
        if eq not in st.session_state[f'{prefix}_tabla']:
            st.session_state[f'{prefix}_tabla'][eq] = {
                "PJ": 0, "PG": 0, "PE": 0, "PP": 0,
                "GF": 0, "GC": 0, "DG": 0, "Pts": 0,
                "Elo": elo_base, "Categoria": cat
            }
        else:
            if "Elo" not in st.session_state[f'{prefix}_tabla'][eq]:
                st.session_state[f'{prefix}_tabla'][eq]["Elo"] = elo_base
            if "Categoria" not in st.session_state[f'{prefix}_tabla'][eq]:
                st.session_state[f'{prefix}_tabla'][eq]["Categoria"] = cat
                
    purgar_equipos_fuera_de_lugar(nombre_torneo)

for torneo in ["Champions League", "Europa League", "Conference League"]:
    inicializar_torneo(torneo)

# ==========================================
# MOTOR MATEMÁTICO BASADO ESTRICTAMENTE EN LA TABLA
# ==========================================
def actualizar_elo(elo_local, elo_vis, goles_l, goles_v, k=32):
    diff = (elo_vis - (elo_local + 100)) / 400
    e_local = 1 / (1 + 10 ** diff)
    e_vis = 1 / (1 + 10 ** (-diff))
    
    if goles_l > goles_v: s_local, s_vis = 1.0, 0.0
    elif goles_l < goles_v: s_local, s_vis = 0.0, 1.0
    else: s_local, s_vis = 0.5, 0.5
        
    return round(elo_local + k * (s_local - e_local)), round(elo_vis + k * (s_vis - e_vis))

def dixon_coles_adjustment(x, y, lambda_x, mu_y, rho=-0.13):
    if x == 0 and y == 0: return 1 - lambda_x * mu_y * rho
    elif x == 0 and y == 1: return 1 + lambda_x * rho
    elif x == 1 and y == 0: return 1 + mu_y * rho
    elif x == 1 and y == 1: return 1 - rho
    else: return 1.0

def calcular_lambdas_desde_tabla(eq_local, eq_vis, torneo):
    """Calcula los goles esperados basándose PURAMENTE en los datos de la tabla de posiciones."""
    prefix = torneo.lower().replace(" ", "_")
    tabla = st.session_state[f'{prefix}_tabla']
    
    data_l = tabla.get(eq_local, {"PJ": 0, "GF": 0, "GC": 0, "Elo": 1500})
    data_v = tabla.get(eq_vis, {"PJ": 0, "GF": 0, "GC": 0, "Elo": 1500})
    
    # Promedios base iniciales si aún no hay partidos jugados
    l_ataque_l = (data_l["GF"] / data_l["PJ"]) if data_l["PJ"] > 0 else (1.8 if "Top 1" in data_l.get("Categoria", "") else 1.3)
    l_defensa_v = (data_v["GC"] / data_v["PJ"]) if data_v["PJ"] > 0 else 1.2
    
    l_ataque_v = (data_v["GF"] / data_v["PJ"]) if data_v["PJ"] > 0 else (1.5 if "Top 1" in data_v.get("Categoria", "") else 1.0)
    l_defensa_l = (data_l["GC"] / data_l["PJ"]) if data_l["PJ"] > 0 else 1.0

    # Cruzar ataque real del local con la defensa real del visitante (y viceversa)
    lambda_local = max(0.4, (l_ataque_l + l_defensa_v) / 2)
    lambda_visitante = max(0.3, (l_ataque_v + l_defensa_l) / 2)

    return lambda_local, lambda_visitante, data_l["Elo"], data_v["Elo"]

def calcular_probabilidades_partido(l_local, l_visitante, elo_l, elo_v, max_goles=7):
    # Ajuste dinámico basado en la tabla y Elo
    diff_elo = (elo_l - elo_v) / 400
    factor_elo = 1 + (diff_elo * 0.20)
    l_local = max(0.4, l_local * factor_elo)
    l_visitante = max(0.3, l_visitante / factor_elo)

    prob_matriz = np.zeros((max_goles, max_goles))
    for x in range(max_goles):
        for y in range(max_goles):
            p_x = poisson.pmf(x, l_local)
            p_y = poisson.pmf(y, l_visitante)
            adj = dixon_coles_adjustment(x, y, l_local, l_visitante)
            prob_matriz[x, y] = p_x * p_y * adj
            
    prob_matriz = prob_matriz / np.sum(prob_matriz)
    prob_local = np.sum(np.tril(prob_matriz, -1))
    prob_empate = np.sum(np.diag(prob_matriz))
    prob_visitante = np.sum(np.triu(prob_matriz, 1))
    
    skellam_empate = skellam.pmf(0, l_local, l_visitante) * 100
    skellam_l1 = skellam.pmf(1, l_local, l_visitante) * 100
    skellam_v1 = skellam.pmf(-1, l_local, l_visitante) * 100

    # Montecarlo (10,000 iteraciones)
    sim_goles_l = np.random.poisson(l_local, 10000)
    sim_goles_v = np.random.poisson(l_visitante, 10000)
    mc_wins_l = np.sum(sim_goles_l > sim_goles_v) / 100.0
    mc_empates = np.sum(sim_goles_l == sim_goles_v) / 100.0
    mc_wins_v = np.sum(sim_goles_l < sim_goles_v) / 100.0

    return prob_local, prob_empate, prob_visitante, prob_matriz, {
        "skellam_empate": skellam_empate,
        "skellam_l1": skellam_l1,
        "skellam_v1": skellam_v1,
        "mc_local": mc_wins_l,
        "mc_empate": mc_empates,
        "mc_visita": mc_wins_v
    }

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.sidebar.title("⚽ Navegación")
torneo_sel = st.sidebar.selectbox(
    "Selecciona la Competición:",
    ["Champions League", "Europa League", "Conference League"],
    index=["Champions League", "Europa League", "Conference League"].index(st.session_state.torneo_actual)
)
st.session_state.torneo_actual = torneo_sel
prefix_act = torneo_sel.lower().replace(" ", "_")
purgar_equipos_fuera_de_lugar(torneo_sel)

st.title(f"🏆 Pronosticador Pro (Basado en Tabla): {torneo_sel}")

pestanas = st.tabs(["📊 Tabla & Elo", "⚽ Registrar Partido", "🔮 Pronóstico Inteligente", "📈 Diagnósticos Avanzados", "💾 Respaldos"])

# ------------------------------------------
# PESTAÑA 1: TABLA Y ELO
# ------------------------------------------
with pestanas[0]:
    st.subheader(f"Tabla En Vivo y Rating Elo - {torneo_sel}")
    equipos_validos = set(obtener_equipos_torneo(torneo_sel).keys())
    tabla_raw = st.session_state[f'{prefix_act}_tabla']
    tabla_filtrada = {k: v for k, v in tabla_raw.items() if k in equipos_validos}
    
    df_tabla = pd.DataFrame.from_dict(tabla_filtrada, orient='index')
    df_tabla = df_tabla.sort_values(by=["Pts", "Elo", "DG"], ascending=False)
    st.dataframe(df_tabla, use_container_width=True)

# ------------------------------------------
# PESTAÑA 2: REGISTRAR PARTIDO
# ------------------------------------------
with pestanas[1]:
    st.subheader("Ingresar Resultado Oficial")
    equipos_lista = sorted(list(obtener_equipos_torneo(torneo_sel).keys()))
    
    with st.form(key=f"form_registrar_{prefix_act}"):
        c1, c2 = st.columns(2)
        with c1:
            eq_loc = st.selectbox("Equipo Local:", equipos_lista)
            goles_loc = st.number_input("Goles Local:", min_value=0, max_value=15, value=0)
        with c2:
            eq_vis = st.selectbox("Equipo Visitante:", equipos_lista)
            goles_vis = st.number_input("Goles Visitante:", min_value=0, max_value=15, value=0)
            
        enviado = st.form_submit_button("Guardar Partido", type="primary")
        
        if enviado:
            if eq_loc == eq_vis:
                st.error("⚠️ El equipo local y el visitante no pueden ser el mismo.")
            else:
                st.session_state[f'{prefix_act}_partidos'].append({
                    "local": eq_loc, "goles_local": goles_loc,
                    "visitante": eq_vis, "goles_visitante": goles_vis
                })
                
                t = st.session_state[f'{prefix_act}_tabla']
                elo_viejo_l = t[eq_loc]["Elo"]
                elo_viejo_v = t[eq_vis]["Elo"]
                nuevo_elo_l, nuevo_elo_v = actualizar_elo(elo_viejo_l, elo_viejo_v, goles_loc, goles_vis)
                t[eq_loc]["Elo"] = nuevo_elo_l
                t[eq_vis]["Elo"] = nuevo_elo_v
                
                t[eq_loc]["PJ"] += 1; t[eq_vis]["PJ"] += 1
                t[eq_loc]["GF"] += goles_loc; t[eq_loc]["GC"] += goles_vis
                t[eq_vis]["GF"] += goles_vis; t[eq_vis]["GC"] += goles_loc
                t[eq_loc]["DG"] = t[eq_loc]["GF"] - t[eq_loc]["GC"]
                t[eq_vis]["DG"] = t[eq_vis]["GF"] - t[eq_vis]["GC"]
                
                if goles_loc > goles_vis:
                    t[eq_loc]["PG"] += 1; t[eq_loc]["Pts"] += 3; t[eq_vis]["PP"] += 1
                elif goles_loc < goles_vis:
                    t[eq_vis]["PG"] += 1; t[eq_vis]["Pts"] += 3; t[eq_loc]["PP"] += 1
                else:
                    t[eq_loc]["PE"] += 1; t[eq_loc]["Pts"] += 1; t[eq_vis]["PE"] += 1; t[eq_vis]["Pts"] += 1
                    
                st.success(f"¡Partido guardado! Tabla y Elo actualizados.")

# ------------------------------------------
# PESTAÑA 3: PRONÓSTICO INTELIGENTE (BASADO EN TABLA)
# ------------------------------------------
with pestanas[2]:
    st.subheader("🔮 Centro de Análisis: Motor Conectado a la Tabla en Vivo")
    equipos_dict = obtener_equipos_torneo(torneo_sel)
    equipos_lista = sorted(list(equipos_dict.keys()))
    
    c1, c2 = st.columns(2)
    with c1: p_loc = st.selectbox("Equipo Local:", equipos_lista, key="p_loc")
    with c2: p_vis = st.selectbox("Equipo Visitante:", [e for e in equipos_lista if e != p_loc], key="p_vis")
        
    l_l, l_v, elo_l, elo_v = calcular_lambdas_desde_tabla(p_loc, p_vis, torneo_sel)
    p_local, p_empate, p_visitante, matriz, metrics = calcular_probabilidades_partido(l_l, l_v, elo_l, elo_v)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(f"Victoria {p_loc}", f"{p_local*100:.1f}%", f"Montecarlo: {metrics['mc_local']:.1f}%")
    col_m2.metric("Empate", f"{p_empate*100:.1f}%", f"Montecarlo: {metrics['mc_empate']:.1f}%")
    col_m3.metric(f"Victoria {p_vis}", f"{p_visitante*100:.1f}%", f"Montecarlo: {metrics['mc_visita']:.1f}%")
    
    st.markdown("---")
    st.markdown("### 💬 Diagnóstico Basado en Rendimiento de Tabla")
    
    max_idx = np.unravel_index(np.argmax(matriz), matriz.shape)
    g_l_pred, g_v_pred = max_idx
    prob_exacta = matriz[g_l_pred, g_v_pred] * 100
    
    btts_prob = np.sum(matriz[1:, 1:]) * 100
    over_25_prob = sum(matriz[x, y] for x in range(matriz.shape[0]) for y in range(matriz.shape[1]) if x + y >= 3) * 100
    
    st.markdown(f"""
    <div class="card-mensaje">
        <h4>🎯 Marcador Exacto Reflejado por la Tabla</h4>
        <p style="font-size: 20px; color: #58A6FF; font-weight: bold;">{p_loc} {g_l_pred} - {g_v_pred} {p_vis}</p>
        <p>Probabilidad matemática exacta: <b>{prob_exacta:.1f}%</b> (Calculado con los promedios reales de goles de la tabla)</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card-mensaje">
        <h4>⚽ Proyecciones y Tendencia de Goles</h4>
        <ul>
            <li><b>¿Ambos equipos marcan (BTTS)?</b> Probabilidad: <b>{btts_prob:.1f}%</b></li>
            <li><b>Línea de Goles (Más de 2.5):</b> Probabilidad: <b>{over_25_prob:.1f}%</b></li>
            <li><b>Simulación Montecarlo (10k iteraciones):</b> Local gana {metrics['mc_local']:.1f}% | Empate {metrics['mc_empate']:.1f}% | Visita gana {metrics['mc_visita']:.1f}%</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📈 Matriz Completa de Marcadores Exactos (%)")
    df_matriz = pd.DataFrame((matriz[:5, :5] * 100).round(2), 
                             index=[f"{p_loc} {i}" for i in range(5)],
                             columns=[f"{p_vis} {j}" for j in range(5)])
    st.dataframe(df_matriz.astype(str) + "%", use_container_width=True)

# ------------------------------------------
# PESTAÑA 4: DIAGNÓSTICOS
# ------------------------------------------
with pestanas[3]:
    st.subheader("Análisis Técnico del Motor")
    st.json({
        "Fuente de Datos": "Tabla de Posiciones en Vivo (Goles a favor y en contra reales)",
        "Modelos Activos": ["Poisson basado en Tabla", "Elo Dinámico", "Skellam", "Montecarlo"],
        "Total Equipos en Torneo": len(obtener_equipos_torneo(torneo_sel)),
        "Partidos Registrados": len(st.session_state[f'{prefix_act}_partidos'])
    })

# ------------------------------------------
# PESTAÑA 5: RESPALDOS
# ------------------------------------------
with pestanas[4]:
    st.subheader("Sistema de Respaldos Multiformato (.txt / .json)")
    datos_exportar = {}
    for t_nom in ["Champions League", "Europa League", "Conference League"]:
        p_name = t_nom.lower().replace(" ", "_")
        eq_permitidos = set(obtener_equipos_torneo(t_nom).keys())
        datos_exportar[f"{p_name}_partidos"] = st.session_state.get(f"{p_name}_partidos", [])
        datos_exportar[f"{p_name}_tabla"] = {k: v for k, v in st.session_state.get(f"{p_name}_tabla", {}).items() if k in eq_permitidos}
    
    json_str = json.dumps(datos_exportar, indent=4, ensure_ascii=False)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.download_button("💾 Descargar Respaldo Móvil (.txt)", json_str, "respaldo.txt", "text/plain", type="primary")
    with col_d2: st.download_button("💾 Descargar Respaldo Estándar (.json)", json_str, "respaldo.json", "application/json")
        
    st.markdown("---")
    archivo_subido = st.file_uploader("Restaurar Respaldo (.txt o .json):", type=["txt", "json"])
    if archivo_subido is not None and st.button("🔄 Aplicar Respaldo", type="primary"):
        try:
            contenido = json.load(archivo_subido)
            for key, val in contenido.items(): st.session_state[key] = val
            for t_nom in ["Champions League", "Europa League", "Conference League"]: purgar_equipos_fuera_de_lugar(t_nom)
            st.success("¡Respaldo restaurado con éxito!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

