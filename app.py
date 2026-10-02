import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

st.set_page_config(
    page_title="EOT Guatavita · Aprestamiento",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Theme / CSS
# -----------------------------
def load_css():
    css_path = BASE_DIR / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()


@st.cache_data
def load_data():
    actors = pd.read_csv(DATA_DIR / "actores_aprestamiento.csv")
    strategies = pd.read_csv(DATA_DIR / "estrategias_aprestamiento.csv")
    annual = pd.read_csv(DATA_DIR / "resumen_anual.csv")
    scale = pd.read_csv(DATA_DIR / "presupuesto_escala.csv")
    return actors, strategies, annual, scale


actors, strategies, annual, scale = load_data()

# -----------------------------
# Helpers
# -----------------------------
QUADRANT_COLORS = {
    "A - Poco interés / Poca influencia": "#94a3b8",
    "B - Mucho interés / Poca influencia": "#f59e0b",
    "C - Poco interés / Mucha influencia": "#3b82f6",
    "D - Mucho interés / Mucha influencia": "#16a34a",
}


def money(v):
    if pd.isna(v):
        return "N/D"
    return f"${float(v):,.0f}".replace(",", ".")


def card(title, value, note="", icon=""):
    return f"""
    <div class='metric-card'>
      <div class='metric-icon'>{icon}</div>
      <div class='metric-title'>{title}</div>
      <div class='metric-value'>{value}</div>
      <div class='metric-note'>{note}</div>
    </div>
    """


def actor_card(row):
    return f"""
    <div class='actor-card'>
      <div class='actor-top'>
        <span class='actor-badge'>{row['Categoria']}</span>
        <span class='quadrant-badge'>{row['Cuadrante'].split(' - ')[0]}</span>
      </div>
      <h3>{row['Actor']}</h3>
      <p><b>Interés:</b> {row['Interes_Nivel']}/5 &nbsp; · &nbsp; <b>Influencia:</b> {row['Influencia_Nivel']}/5</p>
      <p><b>Aprestamiento:</b> {row['Involucramiento']}</p>
      <p><b>Estrategia:</b> {row['Estrategia']}</p>
    </div>
    """


# -----------------------------
# Sidebar navigation and filters
# -----------------------------
st.sidebar.markdown("# 🗺️ EOT Guatavita")
st.sidebar.caption("Dashboard interactivo · Fase de Aprestamiento")

page = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Actores de Aprestamiento", "Presupuesto", "Estrategias", "Asistente IA"],
)

st.sidebar.markdown("---")
q_filter = st.sidebar.multiselect(
    "Cuadrante de matriz",
    options=sorted(actors["Cuadrante"].unique()),
    default=sorted(actors["Cuadrante"].unique()),
)
cat_filter = st.sidebar.multiselect(
    "Categoría",
    options=sorted(actors["Categoria"].unique()),
    default=[],
)
search = st.sidebar.text_input("Buscar actor", placeholder="Ej. IGAC, CAR, JAC...")

actors_filtered = actors[actors["Cuadrante"].isin(q_filter)].copy()
if cat_filter:
    actors_filtered = actors_filtered[actors_filtered["Categoria"].isin(cat_filter)]
if search.strip():
    actors_filtered = actors_filtered[
        actors_filtered["Actor"].str.contains(search.strip(), case=False, na=False)
    ]

# -----------------------------
# HOME
# -----------------------------
if page == "Inicio":
    st.markdown("<div class='hero'><span class='eyebrow'>EOT GUATAVITA · APRESTAMIENTO</span><h1>Mapa de actores, estrategias y presupuesto</h1><p>Una superficie interactiva para explorar los actores de la fase de aprestamiento y conectar su participación con las estrategias y el presupuesto del proceso.</p></div>", unsafe_allow_html=True)

    total_budget = annual.loc[annual["FASE"].str.contains("TOTAL", na=False), "Presupuesto_Num"]
    total_budget = total_budget.iloc[0] if len(total_budget) else float(annual["Presupuesto_Num"].sum())
    ap_budget = strategies["Presupuesto_Num"].sum()

    cols = st.columns(4)
    vals = [
        ("Actores", f"{len(actors):,}", "incluidos en Aprestamiento", "👥"),
        ("Cuadrantes", f"{actors['Cuadrante'].nunique()}", "según la matriz suministrada", "🧩"),
        ("Sesiones", f"{len(strategies)}", "estrategias detalladas de Aprestamiento", "📅"),
        ("Presupuesto anual", money(total_budget), "plan anual de participación", "💰"),
    ]
    for c, (t, v, n, i) in zip(cols, vals):
        with c:
            st.markdown(card(t, v, n, i), unsafe_allow_html=True)

    st.markdown("### 🔎 Vista rápida del mapa de actores")
    st.caption("Pasa el cursor sobre cada punto para ver el actor y su información. Haz clic en un punto para abrir su ficha.")
    fig = px.scatter(
        actors,
        x="Influencia_Nivel",
        y="Interes_Nivel",
        color="Cuadrante",
        color_discrete_map=QUADRANT_COLORS,
        hover_name="Actor",
        hover_data={"Categoria": True, "Cuadrante": True, "Interes_Nivel": True, "Influencia_Nivel": True, "Actor": False},
        size=[13] * len(actors),
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white")), selector=dict(mode="markers"))
    fig.update_layout(
        height=480,
        xaxis=dict(dtick=1, range=[0.5, 5.5], title="Influencia (1–5)"),
        yaxis=dict(dtick=1, range=[0.5, 5.5], title="Interés (1–5)"),
        legend_title_text="Cuadrante",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    ev = st.plotly_chart(fig, use_container_width=True, key="home_actor_map", on_select="rerun", selection_mode="points")
    if getattr(ev, "selection", None) and ev.selection.get("points"):
        p = ev.selection["points"][0]
        idx = p.get("point_index", p.get("point_number", 0))
        selected = actors.iloc[idx]
        st.markdown(actor_card(selected), unsafe_allow_html=True)

    st.markdown("### 💰 Presupuesto del Aprestamiento")
    b1, b2 = st.columns([2, 1])
    with b1:
        budget_plot = strategies[["CARÁCTER", "Presupuesto_Num"]].groupby("CARÁCTER", as_index=False).sum()
        fig_b = px.bar(
            budget_plot,
            x="CARÁCTER",
            y="Presupuesto_Num",
            text_auto=".2s",
            labels={"Presupuesto_Num": "Presupuesto (COP)", "CARÁCTER": "Escala"},
            title="Presupuesto de Aprestamiento por escala",
        )
        fig_b.update_layout(height=340, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_b, use_container_width=True)
    with b2:
        st.markdown("<div class='info-card'><b>Aprestamiento</b><br><span class='big-money'>" + money(ap_budget) + "</span><br><small>Suma de las 10 sesiones de la sección APRESTAMIENTO de ESTRATEGIAS.</small></div>", unsafe_allow_html=True)
        st.markdown("<div class='info-card'><b>Fuente</b><br>PRIORIZACION + ESTRATEGIAS<br><small>Se conservan las etiquetas y textos originales de la información suministrada.</small></div>", unsafe_allow_html=True)

# -----------------------------
# ACTORS
# -----------------------------
elif page == "Actores de Aprestamiento":
    st.title("👥 Actores de Aprestamiento")
    st.caption("La información se toma exclusivamente de la sección APRESTAMIENTO de PRIORIZACION.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Actores visibles", len(actors_filtered))
    c2.metric("Mucho interés", int((actors_filtered["Interes_Nivel"] >= 4).sum()))
    c3.metric("Mucha influencia", int((actors_filtered["Influencia_Nivel"] >= 4).sum()))
    c4.metric("Categorías", actors_filtered["Categoria"].nunique())

    fig = px.scatter(
        actors_filtered,
        x="Influencia_Nivel",
        y="Interes_Nivel",
        color="Cuadrante",
        color_discrete_map=QUADRANT_COLORS,
        hover_name="Actor",
        hover_data={
            "Categoria": True,
            "Cuadrante": True,
            "Interes_Nivel": True,
            "Influencia_Nivel": True,
            "Estrategia": True,
            "Actor": False,
        },
        size=[15] * len(actors_filtered),
    )
    fig.update_traces(marker=dict(line=dict(width=1.2, color="white")))
    fig.update_layout(
        height=570,
        xaxis=dict(dtick=1, range=[0.5, 5.5], title="Influencia (1–5)"),
        yaxis=dict(dtick=1, range=[0.5, 5.5], title="Interés (1–5)"),
        margin=dict(l=20, r=20, t=30, b=20),
    )
    ev = st.plotly_chart(fig, use_container_width=True, key="actor_matrix", on_select="rerun", selection_mode="points")

    if getattr(ev, "selection", None) and ev.selection.get("points"):
        p = ev.selection["points"][0]
        idx = p.get("point_index", p.get("point_number", 0))
        selected = actors_filtered.iloc[idx]
        st.markdown("---")
        st.markdown("### 📌 Ficha del actor seleccionado")
        st.markdown(actor_card(selected), unsafe_allow_html=True)
    else:
        st.info("Haz clic en un actor del gráfico para abrir su ficha de involucramiento y estrategia.")

    st.markdown("### Tabla de actores")
    show_cols = ["Actor", "Categoria", "Interes_Nivel", "Influencia_Nivel", "Cuadrante", "Involucramiento", "Estrategia"]
    st.dataframe(
        actors_filtered[show_cols].rename(columns={
            "Categoria":"Categoría", "Interes_Nivel":"Interés", "Influencia_Nivel":"Influencia",
            "Involucramiento":"Rol / acciones", "Estrategia":"Estrategia"
        }),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Interés": st.column_config.NumberColumn("Interés", min_value=1, max_value=5, format="%d/5"),
            "Influencia": st.column_config.NumberColumn("Influencia", min_value=1, max_value=5, format="%d/5"),
        },
    )

    st.markdown("### ✨ Tarjetas interactivas")
    st.caption("Estas tarjetas reproducen el comportamiento visual del sitio original: al pasar el cursor elevan la tarjeta y cambian la sombra.")
    for start in range(0, min(len(actors_filtered), 12), 3):
        row = actors_filtered.iloc[start:start+3]
        cs = st.columns(3)
        for c, (_, r) in zip(cs, row.iterrows()):
            with c:
                st.markdown(actor_card(r), unsafe_allow_html=True)

# -----------------------------
# BUDGET
# -----------------------------
elif page == "Presupuesto":
    st.title("💰 Presupuesto")
    st.caption("Valores tomados de ESTRATEGIAS; se muestran el plan anual y el detalle del Aprestamiento.")

    total_row = annual[annual["FASE"].str.contains("TOTAL", na=False)]
    total_year = total_row.iloc[0]["Presupuesto_Num"] if not total_row.empty else annual["Presupuesto_Num"].sum()
    ap_budget = strategies["Presupuesto_Num"].sum()
    avg = strategies["Presupuesto_Num"].mean()

    c = st.columns(4)
    c[0].metric("Total anual", money(total_year))
    c[1].metric("Aprestamiento", money(ap_budget))
    c[2].metric("Sesiones Aprestamiento", len(strategies))
    c[3].metric("Promedio por sesión", money(avg))

    left, right = st.columns(2)
    with left:
        phase = annual[annual["Presupuesto_Num"].notna() & ~annual["FASE"].str.contains("TOTAL", na=False)].copy()
        fig_phase = px.pie(phase, names="FASE", values="Presupuesto_Num", hole=.55, title="Distribución del presupuesto anual por fase")
        fig_phase.update_layout(height=420)
        st.plotly_chart(fig_phase, use_container_width=True)
    with right:
        bp = strategies.groupby("CARÁCTER", as_index=False)["Presupuesto_Num"].sum()
        fig_scale = px.bar(bp, x="CARÁCTER", y="Presupuesto_Num", text_auto=True, title="Aprestamiento por escala", labels={"Presupuesto_Num":"COP"})
        fig_scale.update_layout(height=420)
        st.plotly_chart(fig_scale, use_container_width=True)

    st.markdown("### 📋 Plan anual")
    st.dataframe(
        annual[["FASE","PERIODO","SESIONES","PRESUPUESTO","% DEL TOTAL","OBJETIVO DE LA FASE"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 📅 Detalle presupuestal del Aprestamiento")
    detail = strategies[["CARÁCTER","SESIÓN","CRONOGRAMA","DURACIÓN","CONVOCADOS","META ASISTENCIA","Presupuesto_Num","ESTRATEGIA"]].copy()
    detail["Presupuesto"] = detail["Presupuesto_Num"].apply(money)
    detail["Meta asistencia"] = (detail["META ASISTENCIA"] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(detail.drop(columns=["Presupuesto_Num","META ASISTENCIA"]), use_container_width=True, hide_index=True)

    csv = detail.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar detalle visible (CSV)", csv, file_name="presupuesto_aprestamiento.csv", mime="text/csv")

# -----------------------------
# STRATEGIES
# -----------------------------
elif page == "Estrategias":
    st.title("📅 Estrategias de participación · Aprestamiento")
    char = st.multiselect("Filtrar por carácter", sorted(strategies["CARÁCTER"].unique()), default=[])
    q = st.text_input("Buscar sesión", placeholder="Escribe una palabra del nombre de la sesión")
    s = strategies.copy()
    if char:
        s = s[s["CARÁCTER"].isin(char)]
    if q.strip():
        s = s[s["SESIÓN"].str.contains(q.strip(), case=False, na=False)]

    st.caption(f"Mostrando {len(s)} de {len(strategies)} sesiones.")
    for _, r in s.iterrows():
        st.markdown(f"""
        <div class='strategy-card'>
          <div class='strategy-head'><span class='actor-badge'>{r['CARÁCTER']}</span><span class='budget-badge'>{money(r['Presupuesto_Num'])}</span></div>
          <h3>{r['SESIÓN']}</h3>
          <p><b>Cronograma:</b> {r['CRONOGRAMA']} &nbsp; · &nbsp; <b>Duración:</b> {r['DURACIÓN']}</p>
          <p><b>Objetivo:</b> {r['OBJETIVO']}</p>
          <p><b>Estrategia:</b> {r['ESTRATEGIA']}</p>
          <p><b>Actores:</b> {r['ACTORES QUE HACEN PARTE']}</p>
          <details><summary>Ver componentes y productos</summary>
            <p><b>Qué la compone:</b> {r['QUÉ LA COMPONE']}</p>
            <p><b>Aspectos:</b> {r['ASPECTOS A TRATAR']}</p>
            <p><b>Responsable:</b> {r['RESPONSABLE']}</p>
            <p><b>Apoyo:</b> {r['APOYO']}</p>
            <p><b>Resultado:</b> {r['RESULTADO ESPERADO']}</p>
            <p><b>Producto:</b> {r['PRODUCTO']}</p>
          </details>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# AI ASSISTANT
# -----------------------------
elif page == "Asistente IA":
    st.title("🤖 Asistente IA para Aprestamiento")
    st.caption("Diseñado para redactar fichas o resúmenes usando exclusivamente la información disponible en el dashboard.")

    try:
        from google import genai
    except Exception:
        genai = None

    key = None
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        key = os.getenv("GEMINI_API_KEY")

    selected_actor_name = st.selectbox(
        "Actor para contextualizar",
        actors_filtered["Actor"].tolist() if len(actors_filtered) else actors["Actor"].tolist(),
        key="ai_actor_selectbox"
    )
    actor = actors[actors["Actor"] == selected_actor_name].iloc[0]
    prompt = st.text_area(
        "Solicitud",
        value="Genera una ficha ejecutiva del actor, indicando su posición en la matriz, rol en Aprestamiento y estrategia de involucramiento. No inventes información."
    )

    if st.button("Generar", type="primary"):
        context = actor.to_dict()
        if genai is None:
            st.error("Instala google-genai para activar el asistente.")
        elif not key:
            st.warning("Configura GEMINI_API_KEY en Streamlit Secrets para activar la IA.")
        else:
            try:
                client = genai.Client(api_key=key)
                full = f"Usa exclusivamente estos datos JSON del actor: {context}. Solicitud: {prompt}. Responde en español, de forma clara, sin inventar competencias, fechas, cifras o relaciones no presentes en los datos."
                
                response = client.models.generate_content(
                    model="gemini-3.8-flash", 
                    contents=full
                )
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error al procesar la solicitud: {e}")

    with st.expander("¿Para qué usaría la IA aquí?"):
        st.write("Preparar fichas de reunión, resúmenes de actores, borradores de agenda, síntesis de estrategias y preguntas para mesas de participación. La IA debe transformar el contenido existente, no decidir por sí sola la matriz de actores ni inventar datos.")
