import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import poisson
import json

# ==========================================
# CONFIGURACIÓN INICIAL Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Pronosticador de Fútbol Profesional",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .metric-card {
        background-color: #1E2640;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363D;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DICCIONARIOS OFICIALES DE EQUIPOS (LISTAS ESTRICTAS POR TORNEO)
# ==========================================
EQUIPOS_CHAMPIONS = {
    "Real Madrid": "Top 1", "Barcelona": "Top 1", "Atlético de Madrid": "Top 1", "Villarreal": "Top 1", "Real Betis": "Top 1",
    "Manchester City": "Top 1", "Arsenal": "Top 1", "Liverpool": "Top 1", "Aston Villa": "Top 1", "Manchester United": "Top 1",
    "Bayern Múnich": "Top 1", "Borussia Dortmund": "Top 1", "VfB Stuttgart": "Top 1", "RB Leipzig": "Top 1",
    "Inter de Milán": "Top 1", "Napoli": "Top 1", "Roma": "Top 1", "Como 1907": "Top 1",
    "PSG": "Top 2", "Lille": "Top 2", "Lens": "Top 2",
    "Feyenoord": "Top 2", "PSV Eindhoven": "Top 2", "Porto": "Top 2", "Sporting CP": "Top 2",
    "Galatasaray": "Media / Alta", "Fenerbahçe": "Media / Alta", "Shakhtar Donetsk": "Media / Alta",
    "Club Brujas": "Media / Alta", "Bodø/Glimt": "Media", "Slavia Praga": "Media",
    "Slovan Bratislava": "Menor", "LASK Linz": "Media",
    "AEK Atenas": "Media", "Viking Stavanger": "Menor", "Sabah": "Menor"
}

EQUIPOS_EUROPA = {
    "AC Milan": "Top 1", "Juventus": "Top 1",
    "Bayer Leverkusen": "Top 1", "Hoffenheim": "Top 1",
    "Olympique de Marsella": "Top 2", "Olympique de Lyon": "Top 2", "Stade Rennais": "Top 2",
    "Real Sociedad": "Top 2", "Celta de Vigo": "Top 2",
    "Crystal Palace": "Top 2", "Bournemouth": "Top 2", "Sunderland": "Media / Alta",
    "AZ Alkmaar": "Media / Alta", "NEC Nijmegen": "Media",
    "Benfica": "Top 2", "União Torreense": "Menor",
    "Red Bull Salzburg": "Media / Alta", "Sturm Graz": "Media",
    "Beşiktaş": "Media / Alta", "Ferencváros": "Media", "Lech Poznań": "Media",
    "Anderlecht": "Media", "Viktoria Plzeň": "Media", "Sparta Praga": "Media",
    "Celtic": "Media / Alta", "Dinamo Zagreb": "Media / Alta", "Olympiacos": "Media / Alta",
    "Levski Sofia": "Menor", "OFI Creta": "Menor", "Jagiellonia Białystok": "Menor",
    "AC Omonia Nicosia": "Menor", "Lillestrøm SK": "Menor", "FC Ararat-Armenia": "Menor",
    "Hapoel Be'er Sheva": "Menor", "NK Celje": "Menor"
}

EQUIPOS_CONFERENCE = {
    "Brighton & Hove Albion": "Top 2",
    "Atalanta": "Top 1",
    "Getafe": "Media / Alta",
    "SC Freiburg": "Media / Alta",
    "AS Monaco": "Top 2",
    "Ajax": "Top 2", "FC Twente": "Media / Alta",
    "SC Braga": "Top 2",
    "KAA Gent": "Media",
    "Panathinaikos": "Media", "FC Lugano": "Media", "FC Copenhagen": "Media",
    "Midtjylland": "Media", "SK Brann": "Media", "Hajduk Split": "Media",
    "Pafos FC": "Menor", "KuPS Kuopio": "Menor", "Riga FC": "Menor",
    "Inter Club d'Escaldes": "Menor", "Hearts": "Media", "Jablonec": "Menor"
}

# ==========================================
# GESTIÓN DE ESTADO Y PURGA ESTRICTA DE NOMBRES
# ==========================================
if 'torneo_actual' not in st.session_state:
    st.session_state.torneo_actual = "Champions League"

def obtener_equipos_torneo(torneo):
    if torneo == "Champions League":
        return EQUIPOS_CHAMPIONS
    elif torneo == "Europa League":
        return EQUIPOS_EUROPA
    else:
        return EQUIPOS_CONFERENCE

def purgar_equipos_fuera_de_lugar(nombre_torneo):
    """Filtra y remueve de session_state cualquier equipo que no pertenezca al torneo."""
    prefix = nombre_torneo.lower().replace(" ", "_")
    equipos_permitidos = set(obtener_equipos_torneo(nombre_torneo).keys())
    
    key_tabla = f'{prefix}_tabla'
    if key_tabla in st.session_state:
        st.session_state[key_tabla] = {
            eq: stats for eq, stats in st.session_state[key_tabla].items()
            if eq in equipos_permitidos
        }

def inicializar_torneo(nombre_torneo):
    prefix = nombre_torneo.lower().replace(" ", "_")
    equipos_dict = obtener_equipos_torneo(nombre_torneo)
    
    if f'{prefix}_partidos' not in st.session_state:
        st.session_state[f'{prefix}_partidos'] = []
    
    if f'{prefix}_tabla' not in st.session_state:
        st.session_state[f'{prefix}_tabla'] = {}

    for eq in equipos_dict.keys():
        if eq not in st.session_state[f'{prefix}_tabla']:
            st.session_state[f'{prefix}_tabla'][eq] = {
                "PJ": 0, "PG": 0, "PE": 0, "PP": 0,
                "GF": 0, "GC": 0, "DG": 0, "Pts": 0
            }

    purgar_equipos_fuera_de_lugar(nombre_torneo)

for torneo in ["Champions League", "Europa League", "Conference League"]:
    inicializar_torneo(torneo)

# ==========================================
# MOTOR MATEMÁTICO (DIXON-COLES Y POISSON - SIN CAMBIOS)
# ==========================================
def dixon_coles_adjustment(x, y, lambda_x, mu_y, rho=-0.13):
    if x == 0 and y == 0:
        return 1 - lambda_x * mu_y * rho
    elif x == 0 and y == 1:
        return 1 + lambda_x * rho
    elif x == 1 and y == 0:
        return 1 + mu_y * rho
    elif x == 1 and y == 1:
        return 1 - rho
    else:
        return 1.0

def calcular_probabilidades_partido(l_local, l_visitante, max_goles=7):
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
    
    return prob_local, prob_empate, prob_visitante, prob_matriz

def obtener_lambdas(eq_local, eq_vis, torneo):
    equipos = obtener_equipos_torneo(torneo)
    prefix = torneo.lower().replace(" ", "_")
    tabla = st.session_state[f'{prefix}_tabla']
    
    cat_l = equipos.get(eq_local, "Media")
    cat_v = equipos.get(eq_vis, "Media")
    
    base_l = 1.6 if "Top 1" in cat_l else (1.4 if "Top 2" in cat_l else 1.1)
    base_v = 1.4 if "Top 1" in cat_v else (1.2 if "Top 2" in cat_v else 0.9)
    
    stats_l = tabla.get(eq_local, {"PJ": 0, "GF": 0, "GC": 0})
    stats_v = tabla.get(eq_vis, {"PJ": 0, "GF": 0, "GC": 0})
    
    if stats_l["PJ"] > 0:
        factor_l = (stats_l["GF"] / stats_l["PJ"]) / max(1.0, (stats_v["GC"] / max(1, stats_v["PJ"])))
        base_l = (base_l + factor_l) / 2
        
    if stats_v["PJ"] > 0:
        factor_v = (stats_v["GF"] / stats_v["PJ"]) / max(1.0, (stats_l["GC"] / max(1, stats_l["PJ"])))
        base_v = (base_v + factor_v) / 2

    return max(0.4, base_l), max(0.3, base_v)

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

# Forzar purga al navegar entre pestañas o selecciones
purgar_equipos_fuera_de_lugar(torneo_sel)

st.title(f"🏆 Pronosticador: {torneo_sel}")

pestanas = st.tabs(["📊 Tabla de Posiciones", "⚽ Registrar Partido", "🔮 Pronóstico Dixon-Coles", "📈 Diagnósticos Avanzados", "💾 Respaldos (Móvil/PC)"])

# ------------------------------------------
# PESTAÑA 1: TABLA DE POSICIONES
# ------------------------------------------
with pestanas[0]:
    st.subheader(f"Tabla En Vivo - {torneo_sel}")
    
    equipos_validos = set(obtener_equipos_torneo(torneo_sel).keys())
    tabla_raw = st.session_state[f'{prefix_act}_tabla']
    
    # Filtrar estrictamente antes de renderizar la tabla
    tabla_filtrada = {k: v for k, v in tabla_raw.items() if k in equipos_validos}
    
    df_tabla = pd.DataFrame.from_dict(tabla_filtrada, orient='index')
    df_tabla = df_tabla.sort_values(by=["Pts", "DG", "GF"], ascending=False)
    
    st.dataframe(df_tabla.style.highlight_max(axis=0, subset=["Pts", "DG", "GF"], color="#1E3A8A"), use_container_width=True)

# ------------------------------------------
# PESTAÑA 2: REGISTRAR PARTIDO
# ------------------------------------------
with pestanas[1]:
    st.subheader("Ingresar Resultado Oficial")
    equipos_lista = sorted(list(obtener_equipos_torneo(torneo_sel).keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        eq_loc = st.selectbox("Equipo Local:", equipos_lista, key="reg_loc")
        goles_loc = st.number_input("Goles Local:", min_value=0, max_value=15, value=0, key="g_loc")
    with col2:
        eq_vis = st.selectbox("Equipo Visitante:", [e for e in equipos_lista if e != eq_loc], key="reg_vis")
        goles_vis = st.number_input("Goles Visitante:", min_value=0, max_value=15, value=0, key="g_vis")
        
    if st.button("Guardar Partido", type="primary"):
        st.session_state[f'{prefix_act}_partidos'].append({
            "local": eq_loc, "goles_local": goles_loc,
            "visitante": eq_vis, "goles_visitante": goles_vis
        })
        
        t = st.session_state[f'{prefix_act}_tabla']
        t[eq_loc]["PJ"] += 1; t[eq_vis]["PJ"] += 1
        t[eq_loc]["GF"] += goles_loc; t[eq_loc]["GC"] += goles_vis
        t[eq_vis]["GF"] += goles_vis; t[eq_vis]["GC"] += goles_loc
        t[eq_loc]["DG"] = t[eq_loc]["GF"] - t[eq_loc]["GC"]
        t[eq_vis]["DG"] = t[eq_vis]["GF"] - t[eq_vis]["GC"]
        
        if goles_loc > goles_vis:
            t[eq_loc]["PG"] += 1; t[eq_loc]["Pts"] += 3
            t[eq_vis]["PP"] += 1
        elif goles_loc < goles_vis:
            t[eq_vis]["PG"] += 1; t[eq_vis]["Pts"] += 3
            t[eq_loc]["PP"] += 1
        else:
            t[eq_loc]["PE"] += 1; t[eq_loc]["Pts"] += 1
            t[eq_vis]["PE"] += 1; t[eq_vis]["Pts"] += 1
            
        st.success(f"¡Partido {eq_loc} {goles_loc} - {goles_vis} {eq_vis} registrado con éxito!")
        st.rerun()

# ------------------------------------------
# PESTAÑA 3: PRONÓSTICO DIXON-COLES
# ------------------------------------------
with pestanas[2]:
    st.subheader("Calculadora de Probabilidades Poisson / Dixon-Coles")
    equipos_lista = sorted(list(obtener_equipos_torneo(torneo_sel).keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        p_loc = st.selectbox("Equipo Local (Pronóstico):", equipos_lista, key="p_loc")
    with c2:
        p_vis = st.selectbox("Equipo Visitante (Pronóstico):", [e for e in equipos_lista if e != p_loc], key="p_vis")
        
    l_l, l_v = obtener_lambdas(p_loc, p_vis, torneo_sel)
    p_local, p_empate, p_visitante, matriz = calcular_probabilidades_partido(l_l, l_v)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(f"Victoria {p_loc}", f"{p_local*100:.1f}%", f"Cuota: {1/max(0.01, p_local):.2f}")
    col_m2.metric("Empate", f"{p_empate*100:.1f}%", f"Cuota: {1/max(0.01, p_empate):.2f}")
    col_m3.metric(f"Victoria {p_vis}", f"{p_visitante*100:.1f}%", f"Cuota: {1/max(0.01, p_visitante):.2f}")
    
    st.markdown("---")
    st.subheader("Matriz de Marcadores Exactos Probables")
    df_matriz = pd.DataFrame(matriz[:5, :5], 
                             index=[f"{p_loc} {i}" for i in range(5)],
                             columns=[f"{p_vis} {j}" for j in range(5)])
    st.dataframe((df_matriz * 100).style.format("{:.2f}%").background_gradient(cmap="Blues"), use_container_width=True)

# ------------------------------------------
# PESTAÑA 4: DIAGNÓSTICOS AVANZADOS
# ------------------------------------------
with pestanas[3]:
    st.subheader("Análisis Técnico y Estadístico")
    st.write(f"Parámetros actuales del motor para **{torneo_sel}**:")
    st.json({
        "Ajuste Dixon-Coles (rho)": -0.13,
        "Total Equipos en Torneo": len(obtener_equipos_torneo(torneo_sel)),
        "Partidos Registrados": len(st.session_state[f'{prefix_act}_partidos'])
    })

# ------------------------------------------
# PESTAÑA 5: RESPALDOS (MÓVIL / PC)
# ------------------------------------------
with pestanas[4]:
    st.subheader("Sistema de Respaldos Multiformato (.txt / .json)")
    st.info("Descarga o restaura la información de tus partidos sin bloqueos en navegadores móviles.")
    
    datos_exportar = {}
    for t_nom in ["Champions League", "Europa League", "Conference League"]:
        p_name = t_nom.lower().replace(" ", "_")
        eq_permitidos = set(obtener_equipos_torneo(t_nom).keys())
        
        datos_exportar[f"{p_name}_partidos"] = st.session_state.get(f"{p_name}_partidos", [])
        tabla_orig = st.session_state.get(f"{p_name}_tabla", {})
        datos_exportar[f"{p_name}_tabla"] = {k: v for k, v in tabla_orig.items() if k in eq_permitidos}
    
    json_str = json.dumps(datos_exportar, indent=4, ensure_ascii=False)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="💾 Descargar Respaldo Móvil (.txt)",
            data=json_str,
            file_name="respaldo_pronosticador.txt",
            mime="text/plain",
            type="primary"
        )
    with col_d2:
        st.download_button(
            label="💾 Descargar Respaldo Estándar (.json)",
            data=json_str,
            file_name="respaldo_pronosticador.json",
            mime="application/json"
        )
        
    st.markdown("---")
    st.subheader("Restaurar Respaldo")
    
    archivo_subido = st.file_uploader("Selecciona tu archivo de respaldo (.txt o .json):", type=["txt", "json"], key="uploader_respaldo")
    
    if archivo_subido is not None:
        try:
            contenido = json.load(archivo_subido)
            for key, val in contenido.items():
                st.session_state[key] = val
            
            for t_nom in ["Champions League", "Europa League", "Conference League"]:
                purgar_equipos_fuera_de_lugar(t_nom)
                
            st.success("¡Respaldo restaurado y purgado con éxito!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al leer el archivo de respaldo: {e}")

