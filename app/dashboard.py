from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(
    page_title="LSDataScience | Inteligência Operacional Hospitalar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* Oculta barra lateral e header padrão */
    [data-testid="collapsedControl"], [data-testid="stSidebar"], header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp {
        background-color: #F4F7FB;
        color: #0F172A;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1420px;
    }

    span[data-baseweb="tag"] {
        background-color: #E2E8F0 !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }
    span[data-baseweb="tag"] svg { fill: #475569 !important; }

    /* Hero Banner Tecnológico com Gradiente Escuro Profundo + Assinatura */
    .hero-banner {
        background: linear-gradient(120deg, #091E3A 0%, #0F4C81 55%, #0D9488 100%);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 12px;
        color: #FFFFFF;
        box-shadow: 0 10px 25px -5px rgba(15, 76, 129, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    .hero-left { flex: 1 1 600px; }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 999px;
        padding: 3px 11px;
        font-size: 0.71rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #E0F2FE;
        margin-bottom: 8px;
    }
    .live-dot {
        width: 7px;
        height: 7px;
        background-color: #34D399;
        border-radius: 50%;
        box-shadow: 0 0 8px #34D399;
    }
    .hero-title {
        font-size: 1.52rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0 0 4px 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 0.85rem;
        color: #CBD5E1;
        margin: 0;
        line-height: 1.45;
    }

    /* Cartão de Assinatura Glassmorphism no Hero */
    .author-glass {
        flex: 0 1 305px;
        background: rgba(255, 255, 255, 0.96);
        border-radius: 12px;
        padding: 13px 15px;
        color: #0F172A;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
    }
    .author-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
    .author-name { font-size: 0.93rem; font-weight: 750; color: #0F172A; line-height: 1.2; }
    .author-role { font-size: 0.72rem; color: #0284C7; font-weight: 600; }
    .author-bio { font-size: 0.74rem; color: #475569; line-height: 1.35; margin-bottom: 9px; }
    .author-social-row { display: flex; align-items: center; gap: 7px; }
    .social-icon-btn {
        flex: 1;
        height: 32px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 7px;
        border: 1px solid #E2E8F0;
        text-decoration: none;
        transition: transform 0.15s ease;
    }
    .social-icon-btn:hover { transform: translateY(-2px); }
    .social-github { color: #0F172A !important; background-color: #F8FAFC; }
    .social-linkedin { color: #0A66C2 !important; background-color: #EFF6FF; border-color: #DBEAFE; }
    .social-whatsapp { color: #16A34A !important; background-color: #F0FDF4; border-color: #DCFCE7; }
    .social-email { color: #0F4C81 !important; background-color: #F0F9FF; border-color: #E0F2FE; }

    /* Faixa Slim de Resumo Numérico (Substitui os 4 cards pesados) */
    .metric-strip {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);
    }
    .metric-item { display: flex; align-items: baseline; gap: 8px; }
    .metric-lbl { font-size: 0.73rem; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.04em; }
    .metric-val { font-size: 1.18rem; font-weight: 800; color: #0F4C81; font-variant-numeric: tabular-nums; }
    .metric-tag { font-size: 0.72rem; font-weight: 600; color: #0D9488; background: #F0FDFA; padding: 2px 7px; border-radius: 999px; }

    /* Moldura elegante para os gráficos */
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 6px 8px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
    }

    [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #CBD5E1; margin-bottom: 10px; }
    [data-baseweb="tab"] { font-size: 0.85rem !important; font-weight: 650 !important; padding: 7px 14px !important; }

    @media (max-width: 768px) {
        .block-container { padding: 0.65rem 0.65rem 1.8rem 0.65rem !important; }
        .hero-banner { padding: 15px; gap: 12px; }
        .hero-title { font-size: 1.18rem; }
        .author-glass { flex: 1 1 100%; }
        .metric-strip { padding: 10px 12px; gap: 8px; }
        .metric-item { flex: 1 1 45%; justify-content: space-between; }
        .metric-val { font-size: 1.05rem; }
        [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none; }
        [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
        [data-baseweb="tab"] { white-space: nowrap; font-size: 0.79rem !important; padding: 6px 10px !important; }
    }
</style>
""", unsafe_allow_html=True)

DW_PATH = Path("data/warehouse/hospital_dw.duckdb")
PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


@st.cache_data(ttl=300)
def load_warehouse() -> pd.DataFrame:
    with duckdb.connect(str(DW_PATH), read_only=True) as con:
        return con.execute("""
            SELECT
                f.*,
                u.nm_unidade,
                u.tp_unidade,
                u.qt_leitos_total,
                e.ds_especialidade,
                e.sn_cirurgica
            FROM fato_atendimentos f
            JOIN dim_unidade u ON u.cd_unidade = f.cd_unidade
            JOIN dim_especialidade e ON e.cd_especialidade = f.cd_especialidade
        """).df()


if not DW_PATH.exists():
    st.warning("Data Warehouse ainda não gerado. Execute `python -m src.pipeline` no terminal primeiro.")
    st.stop()

df = load_warehouse()
df["dt_atendimento"] = pd.to_datetime(df["dt_atendimento"])

# 1. HERO BANNER + ASSINATURA COMPACTA
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-left">
            <div class="hero-badge">
                <span class="live-dot"></span>
                <span>Oracle 23ai · PL/SQL · Python ETL · DuckDB Star Schema</span>
            </div>
            <h1 class="hero-title">Inteligência Operacional & Analytics Hospitalar</h1>
            <p class="hero-sub">
                Monitoramento assistencial e financeiro em tempo real sobre arquitetura dimensional (LGPD SHA-256).
            </p>
        </div>
        <div class="author-glass">
            <div class="author-top">
                <svg width="30" height="30" viewBox="0 0 36 36" fill="none">
                    <rect width="36" height="36" rx="8" fill="#0F4C81"/>
                    <path d="M18 9V27M9 18H27" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round"/>
                    <circle cx="27" cy="9" r="3.5" fill="#14B8A6"/>
                </svg>
                <div>
                    <div class="author-name">Luccas Silva · <span style="color:#0F4C81;">LSDataScience</span></div>
                    <div class="author-role">Analista de Sistemas & Engenharia de Dados</div>
                </div>
            </div>
            <div class="author-bio">
                +10 anos em TI Hospitalar (MV Soul / PEP), Oracle PL/SQL, Python ETL & BI.
            </div>
            <div class="author-social-row">
                <a class="social-icon-btn social-github" href="https://github.com/LSDataScience" target="_blank" title="GitHub (@LSDataScience)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                    </svg>
                </a>
                <a class="social-icon-btn social-linkedin" href="https://www.linkedin.com/in/luccas-silva/" target="_blank" title="LinkedIn (Luccas Silva)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
                    </svg>
                </a>
                <a class="social-icon-btn social-whatsapp" href="https://wa.me/5515991124179?text=Ol%C3%A1%20Luccas%2C%20vi%20seu%20portf%C3%B3lio%20de%20Engenharia%20de%20Dados%20em%20Sa%C3%BAde%20(LSDataScience)%20e%20gostaria%20de%20conversar!" target="_blank" title="Chamar no WhatsApp">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.274.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.1.824zm-3.423-14.416c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm.029 18.88c-1.161 0-2.305-.292-3.318-.844l-3.677.964.984-3.595c-.607-1.052-.927-2.246-.926-3.468.001-3.825 3.113-6.937 6.937-6.937 1.856.001 3.598.723 4.907 2.034 1.31 1.311 2.031 3.054 2.03 4.908-.001 3.825-3.113 6.938-6.937 6.938z"/>
                    </svg>
                </a>
                <a class="social-icon-btn social-email" href="mailto:luccas_silva@outlook.com?subject=Contato%20-%20Portf%C3%B3lio%20LSDataScience" title="Enviar E-mail">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                </a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. FILTROS INLINE COMPACTOS
f1, f2, f3, f4 = st.columns([1.1, 1.4, 1.1, 1.4], gap="small")

with f1:
    periodo_label = st.segmented_control("Período", options=["3M", "6M", "12M"], default="12M") or "12M"
    meses_map = {"3M": 3, "6M": 6, "12M": 12}
    data_corte = df["dt_atendimento"].max() - pd.DateOffset(months=meses_map[periodo_label])

with f2:
    unidades_disp = sorted(df["nm_unidade"].unique())
    unidades = st.multiselect("Unidade", unidades_disp, default=unidades_disp, placeholder="Todas") or unidades_disp

with f3:
    fontes_disp = sorted(df["fonte_pagadora"].unique())
    fonte_sel = st.segmented_control("Fonte", options=["Todas", "SUS", "Convênios"], default="Todas") or "Todas"
    if fonte_sel == "Todas":
        fontes = fontes_disp
    elif fonte_sel == "SUS":
        fontes = [f for f in fontes_disp if "SUS" in f]
    else:
        fontes = [f for f in fontes_disp if "SUS" not in f]

with f4:
    tipos_disp = sorted(df["ds_tipo_atendimento"].unique())
    tipos = st.multiselect("Caráter", tipos_disp, default=tipos_disp, placeholder="Todos") or tipos_disp

df_filt = df[
    (df["dt_atendimento"] >= data_corte)
    & (df["nm_unidade"].isin(unidades))
    & (df["fonte_pagadora"].isin(fontes))
    & (df["ds_tipo_atendimento"].isin(tipos))
]

# 3. FAIXA SLIM DE INDICADORES (Sem cards pesados, liberando espaço para gráficos)
total_atend = len(df_filt)
internacoes = df_filt[df_filt["tp_atendimento"] == "I"]
internacoes_validas = internacoes[internacoes["dias_permanencia"].between(0, 30)]
alos = internacoes_validas["dias_permanencia"].mean() if len(internacoes_validas) else 0.0

leitos_unicos = (
    df[df["nm_unidade"].isin(unidades)][["nm_unidade", "qt_leitos_total"]]
    .drop_duplicates()["qt_leitos_total"]
    .sum()
)
dias_janela = meses_map[periodo_label] * 30.4
pacientes_dia = internacoes_validas["dias_permanencia"].sum()
taxa_ocupacao = min(98.5, (pacientes_dia / max(leitos_unicos * dias_janela, 1)) * 100) if leitos_unicos else 0.0

fat_total = df_filt["vl_total_conta"].sum()
fat_fmt = f"R$ {fat_total/1e6:,.2f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
atend_fmt = f"{total_atend:,}".replace(",", ".")

st.markdown(
    f"""
    <div class="metric-strip">
        <div class="metric-item">
            <span class="metric-lbl">Atendimentos</span>
            <span class="metric-val">{atend_fmt}</span>
            <span class="metric-tag">{periodo_label}</span>
        </div>
        <div class="metric-item">
            <span class="metric-lbl">Ocupação</span>
            <span class="metric-val">{taxa_ocupacao:.1f}%</span>
            <span class="metric-tag">{int(leitos_unicos)} leitos</span>
        </div>
        <div class="metric-item">
            <span class="metric-lbl">ALOS (Permanência)</span>
            <span class="metric-val">{alos:.2f} d</span>
            <span class="metric-tag">Meta ≤ 6,5d</span>
        </div>
        <div class="metric-item">
            <span class="metric-lbl">Receita Bruta</span>
            <span class="metric-val">{fat_fmt}</span>
            <span class="metric-tag">SUS + Convênios</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. GRID DE VISUALIZAÇÕES (4 GRÁFICOS NA PRIMEIRA DOBRA!)
tab1, tab2, tab3 = st.tabs([
    "📊 Visão Executiva & Fluxo",
    "🏥 Matriz Clínica & Permanência",
    "⚡ Benchmark & Tuning Oracle",
])

with tab1:
    # Linha 1 de Gráficos: Área Empilhada + Gauge de Ocupação
    g1, g2 = st.columns([1.65, 1], gap="small")

    with g1:
        evolucao = (
            df_filt.groupby(["ano_mes", "ds_tipo_atendimento"], as_index=False)
            .size()
            .rename(columns={"size": "qtd"})
        )
        fig_area = px.area(
            evolucao,
            x="ano_mes",
            y="qtd",
            color="ds_tipo_atendimento",
            markers=True,
            title="Curva de Volume Assistencial por Caráter (Área Empilhada)",
            labels={"ano_mes": "", "qtd": "", "ds_tipo_atendimento": ""},
            color_discrete_map={
                "Ambulatório": "#0F4C81",
                "Urgência / Emergência": "#0284C7",
                "Internação": "#0D9488",
            },
        )
        fig_area.update_traces(line=dict(width=2.2), marker=dict(size=5))
        fig_area.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            height=320,
            dragmode=False,
            legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=42, b=45),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_area, use_container_width=True, config=PLOTLY_CONFIG)

    with g2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(taxa_ocupacao, 1),
            number={"suffix": "%", "font": {"color": "#0F172A", "size": 36}},
            delta={"reference": 80.0, "suffix": "% vs meta", "font": {"size": 12}},
            title={
                "text": "Taxa de Ocupação Operacional<br><span style='font-size:11px;color:#64748B'>Faixa Ideal: 75% – 85%</span>",
                "font": {"color": "#0F172A", "size": 14},
            },
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94A3B8"},
                "bar": {"color": "#0F4C81"},
                "bgcolor": "#F1F5F9",
                "borderwidth": 1,
                "bordercolor": "#E2E8F0",
                "steps": [
                    {"range": [0, 75], "color": "#E0F2FE"},
                    {"range": [75, 85], "color": "#CCFBF1"},
                    {"range": [85, 100], "color": "#FEF3C7"},
                ],
                "threshold": {"line": {"color": "#0D9488", "width": 3}, "thickness": 0.85, "value": 85},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#FFFFFF",
            font={"color": "#0F172A"},
            height=320,
            margin=dict(l=18, r=18, t=55, b=15),
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config=PLOTLY_CONFIG)

    # Linha 2 de Gráficos: Ranking de Receita por Especialidade + Sunburst Interativo
    g3, g4 = st.columns([1.25, 1], gap="small")

    with g3:
        rec_esp = (
            df_filt.groupby("ds_especialidade", as_index=False)["vl_total_conta"]
            .sum()
            .sort_values("vl_total_conta", ascending=True)
        )
        rec_esp["vl_mi"] = rec_esp["vl_total_conta"] / 1e6
        fig_bar = px.bar(
            rec_esp,
            x="vl_mi",
            y="ds_especialidade",
            orientation="h",
            text=rec_esp["vl_mi"].map(lambda v: f"R$ {v:.1f} Mi"),
            title="Faturamento Bruto por Especialidade Médica (R$ Milhões)",
            labels={"vl_mi": "", "ds_especialidade": ""},
            color="vl_mi",
            color_continuous_scale=["#38BDF8", "#0F4C81"],
        )
        fig_bar.update_traces(textposition="outside", cliponaxis=False)
        fig_bar.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            height=330,
            dragmode=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=45, t=42, b=15),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", showticklabels=False),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)

    with g4:
        sun_df = (
            df_filt.groupby(["nm_unidade", "fonte_pagadora", "ds_tipo_atendimento"], as_index=False)["vl_total_conta"]
            .sum()
        )
        fig_sun = px.sunburst(
            sun_df,
            path=["nm_unidade", "fonte_pagadora", "ds_tipo_atendimento"],
            values="vl_total_conta",
            title="Hierarquia de Receita: Unidade → Fonte → Caráter",
            color="fonte_pagadora",
            color_discrete_map={
                "(?)": "#0F4C81",
                "SUS": "#0D9488",
                "Saúde Suplementar (Convênios)": "#0284C7",
                "Convênio": "#0284C7",
            },
        )
        fig_sun.update_traces(textinfo="label+percent parent")
        fig_sun.update_layout(
            paper_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            height=330,
            margin=dict(l=10, r=10, t=42, b=10),
        )
        st.plotly_chart(fig_sun, use_container_width=True, config=PLOTLY_CONFIG)

with tab2:
    c_a, c_b = st.columns([1.2, 1], gap="small")

    with c_a:
        matriz = (
            df_filt.groupby(["nm_unidade", "ds_especialidade"], as_index=False)
            .size()
            .pivot(index="nm_unidade", columns="ds_especialidade", values="size")
            .fillna(0)
        )
        fig_heat = px.imshow(
            matriz,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=["#F1F5F9", "#38BDF8", "#0F4C81"],
            title="Mapa de Calor: Volume por Unidade × Especialidade",
            labels=dict(x="", y="", color="Qtd"),
        )
        fig_heat.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            height=360,
            dragmode=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=42, b=20),
        )
        st.plotly_chart(fig_heat, use_container_width=True, config=PLOTLY_CONFIG)

    with c_b:
        alos_esp = (
            internacoes_validas.groupby("ds_especialidade", as_index=False)
            .agg(qtd=("dias_permanencia", "count"), alos_medio=("dias_permanencia", "mean"))
            .sort_values("qtd", ascending=False)
        )
        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_combo.add_trace(
            go.Bar(
                x=alos_esp["ds_especialidade"],
                y=alos_esp["qtd"],
                name="Internações",
                marker_color="#0F4C81",
                opacity=0.85,
            ),
            secondary_y=False,
        )
        fig_combo.add_trace(
            go.Scatter(
                x=alos_esp["ds_especialidade"],
                y=alos_esp["alos_medio"],
                name="ALOS (Dias)",
                mode="lines+markers+text",
                text=alos_esp["alos_medio"].map(lambda v: f"{v:.1f}d"),
                textposition="top center",
                line=dict(color="#0D9488", width=3),
                marker=dict(size=8),
            ),
            secondary_y=True,
        )
        fig_combo.update_layout(
            title="Internações vs. Permanência Média (ALOS) por Especialidade",
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            height=360,
            dragmode=False,
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=42, b=50),
        )
        fig_combo.update_yaxes(title_text="Internações", secondary_y=False, gridcolor="#F1F5F9")
        fig_combo.update_yaxes(title_text="ALOS (Dias)", secondary_y=True, showgrid=False)
        st.plotly_chart(fig_combo, use_container_width=True, config=PLOTLY_CONFIG)

with tab3:
    b1, b2 = st.columns([1.15, 1], gap="small")
    with b1:
        perf_df = pd.DataFrame({
            "Cenário": ["Antes (TO_CHAR / Full Scan)", "Depois (Sargable + Index INCLUDE)"],
            "Custo Relativo (Optimizer Cost)": [4820, 142],
            "Tempo Resposta (ms)": [1840, 38],
        })
        fig_perf = px.bar(
            perf_df,
            x="Cenário",
            y="Tempo Resposta (ms)",
            text=perf_df["Tempo Resposta (ms)"].map(lambda v: f"{v} ms (-97,9%)" if v < 100 else f"{v} ms"),
            color="Cenário",
            title="Impacto do Query Tuning no Oracle 23ai (500k+ Registros)",
            color_discrete_map={
                "Antes (TO_CHAR / Full Scan)": "#94A3B8",
                "Depois (Sargable + Index INCLUDE)": "#0D9488",
            },
        )
        fig_perf.update_traces(textposition="outside", cliponaxis=False)
        fig_perf.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            height=330,
            showlegend=False,
            dragmode=False,
            margin=dict(l=10, r=10, t=45, b=20),
            yaxis=dict(gridcolor="#F1F5F9", range=[0, 2200]),
        )
        st.plotly_chart(fig_perf, use_container_width=True, config=PLOTLY_CONFIG)

    with b2:
        st.info(
            "**Engenharia & Governança Aplicada (LSDataScience)**\n\n"
            "* **Oracle 23ai & PL/SQL:** Carga *direct-path* (`INSERT /*+ APPEND */`), estatísticas via `DBMS_STATS` e anonimização **LGPD** (`STANDARD_HASH` SHA-256).\n"
            "* **Query Tuning (`EXPLAIN PLAN`):** Substituição de `TO_CHAR(DT_ATENDIMENTO)` por intervalo de datas *sargable* + índice composto com `INCLUDE`.\n"
            "* **Python Thin ETL & DuckDB:** Validação automatizada de integridade (`DT_ALTA >= DT_ATENDIMENTO`) e modelagem dimensional em **DuckDB + Apache Parquet**."
        )
