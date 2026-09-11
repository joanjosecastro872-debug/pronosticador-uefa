import streamlit as st
import numpy as np
import pandas as pd
from collections import Counter

# ==========================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Búnker Pro - Motor Inteligente",
    page_icon="⚽",
    layout="wide"
)

# ==========================================
# INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================
if 'standings_champions' not in st.session_state:
    st.session_state['standings_champions'] = pd.DataFrame({
        'Equipo': ['Real Madrid', 'Bayern Munich', 'Barcelona', 'Como', 'Arsenal', 'Napoli'],
        'GF_casa': [2.2, 2.5, 2.0, 1.8, 1.2, 1.1],
        'GC_casa': [0.8, 0.7, 0.9, 1.0, 0.5, 0.6],
        'GF_fuera': [1.8, 2.0, 1.7, 1.5, 1.0, 0.9],
        'GC_fuera': [1.0, 1.1, 1.2, 1.3, 0.7, 0.8]
    })

if 'standings_europa' not in st.session_state:
    st.session_state['standings_europa'] = st.session_state['standings_champions'].copy()

if 'standings_conference' not in st.session_state:
    st.session_state['standings_conference'] = st.session_state['standings_champions'].copy()

if 'partidos_jornada_actual' not in st.session_state:
    st.session_state['partidos_jornada_actual'] = []


# ==========================================
# FUNCIONES DEL MOTOR INTELIGENTE
# ==========================================
def obtener_tabla_competencia(torneo_seleccionado):
    if torneo_seleccionado == "Champions League":
        return st.session_state.get('standings_champions')
    elif torneo_seleccionado == "Europa League":
        return st.session_state.get('standings_europa')
    elif torneo_seleccionado == "Conference League":
        return st.session_state.get('standings_conference')
    return None

def calcular_xg_dinamico(equipo_local, equipo_visitante, df_standings):
    if df_standings is None or equipo_local not in df_standings['Equipo'].values or equipo_visitante not in df_standings['Equipo'].values:
        return 1.3, 1.2

    stats_local = df_standings[df_standings['Equipo'] == equipo_local].iloc[0]
    stats_visita = df_standings[df_standings['Equipo'] == equipo_visitante].iloc[0]

    gf_local = stats_local.get('GF_casa', 1.4)
    gc_local = stats_local.get('GC_casa', 1.0)
    gf_visita = stats_visita.get('GF_fuera', 1.2)
    gc_visita = stats_visita.get('GC_fuera', 1.3)

    # Cruce dinámico: Ofensiva local vs debilidad defensiva visitante
    xg_local = (gf_local + gc_visita) / 2.0
    xg_visita = (gf_visita + gc_local) / 2.0

    return max(0.5, float(xg_local)), max(0.5, float(xg_visita))

def simular_partido_monte_carlo(xg_l, xg_v, iteraciones=3000):
    goles_locales = np.random.poisson(xg_l, iteraciones)
    goles_visitas = np.random.poisson(xg_v, iteraciones)

    wins_local = np.sum(goles_locales > goles_visitas)
    wins_visita = np.sum(goles_visitas > goles_locales)
    empates = np.sum(goles_locales == goles_visitas)

    prob_l = (wins_local / iteraciones) * 100
    prob_v = (wins_visita / iteraciones) * 100
    prob_e = (empates / iteraciones) * 100

    pares = list(zip(goles_locales, goles_visitas))
    marcador_mas_comun = Counter(pares).most_common(1)[0][0]

    return prob_l, prob_e, prob_v, marcador_mas_comun

def generar_analisis_tactico(xg_local, xg_visita, prob_local, prob_visita, equipo_local, equipo_visitante):
    xg_total = xg_local + xg_visita
    diferencia_xg = abs(xg_local - xg_visita)

    if diferencia_xg > 1.2:
        favorito = equipo_local if xg_local > xg_visita else equipo_visitante
        return f"⚡ **Alerta de rodillo:** Los números indican que el **{favorito}** llega con la pólvora a millón. Si el rival regala espacios atrás, prepárense para una noche de varios goles."
    elif xg_total < 2.1:
        return "🛡️ **¡Cuidado con el cerrojo!** Choque de estilos ultradefensivos. Las métricas muestran un partido de ajedrez y fricción. Huele a un 1-0 sufrido o empate táctico (Under)."
    elif xg_local > 1.4 and xg_visita > 1.4:
        return "⚽ **¡Lluvia de goles en puerta!** Ambos equipos promedian buenos números de anotación pero sufren atrás. Apunta a un altísimo porcentaje de **ambos marcan**."
    elif abs(prob_local - prob_visita) < 5.0:
        return "⚖️ **¡Pronóstico totalmente reservado!** Paridad brutal en las estadísticas. Cualquier detalle o pelota parada definirá este pulso."
    else:
        return f"🔍 Duelo tácticamente interesante. El **{equipo_local}** buscará imponer su localía ante un **{equipo_visitante}** que intentará raspar puntos."


# ==========================================
# INTERFAZ PRINCIPAL DE STREAMLIT
# ==========================================
st.title("⚽ Búnker Pro: Motor Inteligente Europeo")
st.markdown("---")

# Selector de Competencia
torneo_actual = st.selectbox(
    "🌍 Selecciona la Competencia:",
    ["Champions League", "Europa League", "Conference League"]
)

df_actual = obtener_tabla_competencia(torneo_actual)

if df_actual is None or df_actual.empty:
    st.warning(f"⚠️ No hay datos cargados para la {torneo_actual}.")
else:
    st.subheader(f"🏟️ Simulación de Partidos - {torneo_actual}")
    
    lista_equipos = df_actual['Equipo'].tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        eq_local = st.selectbox("Equipo Local", lista_equipos, key="loc_box")
    with col2:
        eq_visita = st.selectbox("Equipo Visitante", lista_equipos, key="vis_box")

    if eq_local == eq_visita:
        st.error("⚠️ El equipo local y visitante no pueden ser el mismo.")
    else:
        if st.button("🚀 Ejecutar Simulación Dinámica", use_container_width=True):
            # 1. Cálculo xG basado en la tabla
            xg_l, xg_v = calcular_xg_dinamico(eq_local, eq_visita, df_actual)
            
            # 2. Monte Carlo
            p_loc, p_emp, p_vis, marcador = simular_partido_monte_carlo(xg_l, xg_v)
            
            # 3. Analista táctico
            analisis = generar_analisis_tactico(xg_l, xg_v, p_loc, p_vis, eq_local, eq_visita)

            # 4. Resultados visuales
            st.markdown("---")
            r1, r2, r3 = st.columns(3)
            r1.metric(f"xG {eq_local}", f"{xg_l:.2f}")
            r2.metric("Marcador Más Probable", f"{marcador[0]} - {marcador[1]}")
            r3.metric(f"xG {eq_visita}", f"{xg_v:.2f}")

            st.info(f"📊 **Probabilidades:** {eq_local}: **{p_loc:.1f}%** | Empate: **{p_emp:.1f}%** | {eq_visita}: **{p_vis:.1f}%**")
            st.success(analisis)

            # Registrar en el historial temporal de la jornada
            st.session_state['partidos_jornada_actual'].append({
                'local': eq_local, 'visitante': eq_visita,
                'goles_l': marcador[0], 'goles_v': marcador[1],
                'torneo': torneo_actual
            })

    # Mostrar bandeja de partidos de la jornada actual guardados
    if st.session_state['partidos_jornada_actual']:
        st.markdown("---")
        st.subheader("📋 Partidos Registrados en la Jornada Actual")
        for i, p in enumerate(st.session_state['partidos_jornada_actual']):
            st.text(f"{i+1}. [{p['torneo']}] {p['local']} {p['goles_l']} - {p['goles_v']} {p['visitante']}")

        # Botón maestro de consolidación y limpieza
        if st.button("💾 Consolidar Jornada en Tabla y Limpiar Historial", use_container_width=True):
            st.session_state['partidos_jornada_actual'] = []
            st.success("¡Jornada consolidada con éxito en la tabla de posiciones y bandeja limpiada!")
            st.rerun()
