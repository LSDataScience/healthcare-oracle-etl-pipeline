from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="LSDataScience | Inteligência Operacional Hospitalar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="collapsedControl"], [data-testid="stSidebar"], header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1380px;
    }

    span[data-baseweb="tag"] {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #1E293B !important;
        border-radius: 6px !important;
        font-size: 0.76rem !important;
        font-weight: 500 !important;
    }
    span[data-baseweb="tag"] svg { fill: #64748B !important; }

    .hero-wrapper {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        flex-wrap: wrap;
    }
    .hero-left { flex: 1 1 620px; }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.73rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #0F4C81;
        margin-bottom: 6px;
    }
    .live-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18);
    }
    .hero-title {
        font-size: 1.55rem;
        font-weight: 750;
        color: #0F172A;
        margin: 0 0 6px 0;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    .hero-desc {
        color: #475569;
        font-size: 0.88rem;
        line-height: 1.5;
        margin: 0 0 12px 0;
        max-width: 780px;
    }
    .tech-pills { display: flex; flex-wrap: wrap; gap: 6px; }
    .tech-pill {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        color: #334155;
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .author-pill-card {
        flex: 0 1 310px;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    .author-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .author-name { font-size: 0.94rem; font-weight: 700; color: #0F172A; line-height: 1.2; }
    .author-sub { font-size: 0.74rem; color: #0284C7; font-weight: 600; }
    .author-bio { font-size: 0.76rem; color: #64748B; line-height: 1.4; margin-bottom: 10px; }
    .author-social-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .social-icon-btn {
        flex: 1;
        height: 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        color: #334155 !important;
        text-decoration: none;
        transition: all 0.15s ease;
    }
    .social-icon-btn:hover {
        background-color: #F1F5F9;
        border-color: #CBD5E1;
        transform: translateY(-1px);
    }
    .social-github { color: #0F172A !important; }
    .social-linkedin { color: #0A66C2 !important; background-color: #EFF6FF; border-color: #DBEAFE; }
    .social-whatsapp { color: #16A34A !important; background-color: #F0FDF4; border-color: #DCFCE7; }
    .social-email { color: #0F4C81 !important; background-color: #F0F9FF; border-color: #E0F2FE; }

    .filter-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 6px;
    }

    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        margin-bottom: 8px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0F4C81, #0D9488);
        opacity: 0.85;
    }
    .kpi-label {
        color: #64748B;
        font-size: 0.73rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.62rem;
        font-weight: 750;
        letter-spacing: -0.02em;
        font-variant-numeric: tabular-nums;
        line-height: 1.15;
    }
    .kpi-meta {
        color: #0D9488;
        font-size: 0.76rem;
        font-weight: 600;
        margin-top: 6px;
    }

    [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 12px;
    }
    [data-baseweb="tab"] {
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        padding: 8px 14px !important;
    }

    /* Ajustes responsivos para Mobile */
    @media (max-width: 768px) {
        .block-container { padding: 0.75rem 0.75rem 2rem 0.75rem !important; }
        .hero-wrapper { padding: 15px 16px; gap: 14px; border-radius: 12px; }
        .hero-title { font-size: 1.2rem; }
        .hero-desc { font-size: 0.82rem; margin-bottom: 10px; }
        .tech-pill { font-size: 0.66rem; padding: 2px 8px; }
        .author-pill-card { flex: 1 1 100%; padding: 12px 14px; }
        .kpi-card { padding: 13px 15px; }
        .kpi-value { font-size: 1.38rem; }
        [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none; }
        [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
        [data-baseweb="tab"] { white-space: nowrap; font-size: 0.8rem !important; padding: 7px 10px !important; }
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

# 1. HERO + ASSINATURA DO AUTOR COM ÍCONES VETORIAIS COMPACTOS
st.markdown(
    """
    <div class="hero-wrapper">
        <div class="hero-left">
            <div class="hero-eyebrow">
                <span class="live-dot"></span>
                <span>ETL Sincronizado · Oracle 23ai → Python → DuckDB</span>
            </div>
            <h1 class="hero-title">Inteligência Operacional & Indicadores Hospitalares</h1>
            <p class="hero-desc">
                Arquitetura dimensional (Star Schema) com dados hospitalares sintéticos anonimizados (LGPD),
                integrando extração transacional Oracle PL/SQL, regras de Data Quality e BI clínico.
            </p>
            <div class="tech-pills">
                <span class="tech-pill">Oracle 23ai</span>
                <span class="tech-pill">PL/SQL & Query Tuning</span>
                <span class="tech-pill">Python Thin ETL</span>
                <span class="tech-pill">Star Schema</span>
                <span class="tech-pill">DuckDB & Parquet</span>
                <span class="tech-pill">LGPD SHA-256</span>
            </div>
        </div>
        <div class="author-pill-card">
            <div class="author-header">
                <svg width="32" height="32" viewBox="0 0 36 36" fill="none">
                    <rect width="36" height="36" rx="8" fill="#0F4C81"/>
                    <path d="M18 9V27M9 18H27" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round"/>
                    <circle cx="27" cy="9" r="3.5" fill="#14B8A6"/>
                </svg>
                <div>
                    <div class="author-name">Luccas Silva · <span style="color:#0F4C81;">LSDataScience</span></div>
                    <div class="author-sub">Analista de Sistemas & Engenharia de Dados</div>
                </div>
            </div>
            <div class="author-bio">
                +10 anos em TI Hospitalar (MV Soul / PEP), Oracle SQL/PL/SQL, Python ETL e BI Clínico.
            </div>
            <div class="author-social-row">
                <a class="social-icon-btn social-github" href="https://github.com/LSDataScience" target="_blank" title="GitHub (@LSDataScience)" aria-label="GitHub">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                    </svg>
                </a>
                <a class="social-icon-btn social-linkedin" href="https://www.linkedin.com/in/luccas-silva/" target="_blank" title="LinkedIn (Luccas Silva)" aria-label="LinkedIn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
                    </svg>
                </a>
                <a class="social-icon-btn social-whatsapp" href="https://wa.me/5515991124179?text=Ol%C3%A1%20Luccas%2C%20vi%20seu%20portf%C3%B3lio%20de%20Engenharia%20de%20Dados%20em%20Sa%C3%BAde%20(LSDataScience)%20e%20gostaria%20de%20conversar!" target="_blank" title="Chamar no WhatsApp" aria-label="WhatsApp">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.274.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.1.824zm-3.423-14.416c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm.029 18.88c-1.161 0-2.305-.292-3.318-.844l-3.677.964.984-3.595c-.607-1.052-.927-2.246-.926-3.468.001-3.825 3.113-6.937 6.937-6.937 1.856.001 3.598.723 4.907 2.034 1.31 1.311 2.031 3.054 2.03 4.908-.001 3.825-3.113 6.938-6.937 6.938z"/>
                    </svg>
                </a>
                <a class="social-icon-btn social-email" href="mailto:luccas_silva@outlook.com?subject=Contato%20-%20Portf%C3%B3lio%20LSDataScience" title="Enviar E-mail (luccas_silva@outlook.com)" aria-label="E-mail">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                </a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. BARRA DE FILTROS ABERTA E COLADA AOS DADOS
st.markdown('<div class="filter-label">🎛️ Filtros Assistenciais em Tempo Real</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([1.15, 1.35, 1.15, 1.35], gap="small")

with f1:
    periodo_label = st.segmented_control(
        "Janela Temporal",
        options=["3M", "6M", "12M"],
        default="12M",
    )
    if not periodo_label:
        periodo_label = "12M"
    meses_map = {"3M": 3, "6M": 6, "12M": 12}
    periodo_nome = {"3M": "Últimos 3 meses", "6M": "Últimos 6 meses", "12M": "Últimos 12 meses"}[periodo_label]
    data_corte = df["dt_atendimento"].max() - pd.DateOffset(months=meses_map[periodo_label])

with f2:
    unidades_disp = sorted(df["nm_unidade"].unique())
    unidades = st.multiselect(
        "Unidade Hospitalar",
        unidades_disp,
        default=unidades_disp,
        placeholder="Todas as unidades",
    )
    if not unidades:
        unidades = unidades_disp

with f3:
    fontes_disp = sorted(df["fonte_pagadora"].unique())
    fonte_sel = st.segmented_control(
        "Fonte Pagadora",
        options=["Todas", "SUS", "Convênios"],
        default="Todas",
    )
    if not fonte_sel or fonte_sel == "Todas":
        fontes = fontes_disp
    elif fonte_sel == "SUS":
        fontes = [f for f in fontes_disp if "SUS" in f]
    else:
        fontes = [f for f in fontes_disp if "SUS" not in f]

with f4:
    tipos_disp = sorted(df["ds_tipo_atendimento"].unique())
    tipos = st.multiselect(
        "Caráter do Atendimento",
        tipos_disp,
        default=tipos_disp,
        placeholder="Todos os caracteres",
    )
    if not tipos:
        tipos = tipos_disp

df_filt = df[
    (df["dt_atendimento"] >= data_corte)
    & (df["nm_unidade"].isin(unidades))
    & (df["fonte_pagadora"].isin(fontes))
    & (df["ds_tipo_atendimento"].isin(tipos))
]

st.write("")

# 3. KPIs EXECUTIVOS IMEDIATAMENTE ABAIXO DOS FILTROS
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
ticket_medio = df_filt["vl_total_conta"].mean() if total_atend else 0.0

k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Atendimentos ({periodo_nome})</div>
        <div class="kpi-value">{total_atend:,}</div>
        <div class="kpi-meta">✓ Registros validados (Data Quality)</div>
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Taxa de Ocupação Operacional</div>
        <div class="kpi-value">{taxa_ocupacao:.1f}%</div>
        <div class="kpi-meta">Capacidade ativa: {int(leitos_unicos)} leitos</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Tempo Médio Permanência (ALOS)</div>
        <div class="kpi-value">{alos:.2f} dias</div>
        <div class="kpi-meta">Referência institucional: ≤ 6,5 dias</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    fat_fmt = f"R$ {fat_total/1e6:,.2f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
    tk_fmt = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Produção & Receita Bruta</div>
        <div class="kpi-value">{fat_fmt}</div>
        <div class="kpi-meta">Ticket médio: {tk_fmt}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 4. VISUALIZAÇÕES ANALÍTICAS
tab1, tab2, tab3 = st.tabs([
    "Evolução Assistencial & Ocupação",
    "Produção por Unidade & Convênios",
    "Arquitetura & Tuning Oracle",
])

with tab1:
    col_esq, col_dir = st.columns([1.65, 1], gap="medium")

    with col_esq:
        evolucao = (
            df_filt.groupby(["ano_mes", "ds_tipo_atendimento"], as_index=False)
            .size()
            .rename(columns={"size": "qtd"})
        )
        fig_line = px.line(
            evolucao,
            x="ano_mes",
            y="qtd",
            color="ds_tipo_atendimento",
            markers=True,
            title="Série Histórica de Atendimentos por Caráter",
            labels={"ano_mes": "Competência", "qtd": "Atendimentos", "ds_tipo_atendimento": ""},
            color_discrete_map={
                "Ambulatório": "#0F4C81",
                "Internação": "#0D9488",
                "Urgência / Emergência": "#3B82F6",
            },
        )
        fig_line.update_traces(line=dict(width=2.5), marker=dict(size=6))
        fig_line.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=12),
            dragmode=False,
            legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5),
            margin=dict(l=12, r=12, t=48, b=55),
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(gridcolor="#F1F5F9", title=""),
        )
        st.plotly_chart(fig_line, use_container_width=True, config=PLOTLY_CONFIG)

    with col_dir:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(taxa_ocupacao, 1),
            number={"suffix": "%", "font": {"color": "#0F172A", "size": 36}},
            title={
                "text": "Ocupação Global de Leitos<br><span style='font-size:12px;color:#64748B'>Meta Assistencial: 75% a 85%</span>",
                "font": {"color": "#0F172A", "size": 14},
            },
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94A3B8"},
                "bar": {"color": "#0F4C81"},
                "bgcolor": "#F1F5F9",
                "borderwidth": 1,
                "bordercolor": "#E2E8F0",
                "steps": [
                    {"range": [0, 70], "color": "#E0F2FE"},
                    {"range": [70, 85], "color": "#CCFBF1"},
                    {"range": [85, 100], "color": "#FEF3C7"},
                ],
                "threshold": {"line": {"color": "#0D9488", "width": 3}, "thickness": 0.8, "value": 85},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#FFFFFF",
            font={"color": "#0F172A"},
            height=340,
            margin=dict(l=20, r=20, t=60, b=15),
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config=PLOTLY_CONFIG)

with tab2:
    c_a, c_b = st.columns([1.35, 1], gap="medium")

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
            color_continuous_scale=["#F1F5F9", "#7DD3FC", "#0F4C81"],
            title="Volume Assistencial: Unidade × Especialidade",
            labels=dict(x="", y="", color="Qtd"),
        )
        fig_heat.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=11),
            dragmode=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=48, b=20),
        )
        st.plotly_chart(fig_heat, use_container_width=True, config=PLOTLY_CONFIG)

    with c_b:
        mix_fonte = (
            df_filt.groupby("fonte_pagadora", as_index=False)["vl_total_conta"]
            .sum()
        )
        fig_donut = px.pie(
            mix_fonte,
            names="fonte_pagadora",
            values="vl_total_conta",
            hole=0.58,
            title="Participação na Receita: SUS vs. Convênios",
            color_discrete_sequence=["#0F4C81", "#0D9488"],
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label", textfont_size=12)
        fig_donut.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            font=dict(color="#0F172A"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
            margin=dict(l=12, r=12, t=48, b=35),
        )
        st.plotly_chart(fig_donut, use_container_width=True, config=PLOTLY_CONFIG)

with tab3:
    st.markdown("#### Decisões de Arquitetura & Otimização (Portfólio LSDataScience)")
    col_t1, col_t2 = st.columns(2, gap="medium")
    with col_t1:
        st.info(
            "**1. Banco de Dados & Tuning (Oracle 23ai Free)**\n\n"
            "* **Carga em Lote:** Package PL/SQL (`PKG_GERA_MASSA_DADOS`) com `INSERT /*+ APPEND */` e `CONNECT BY LEVEL` gerando 500.000+ registros sintéticos.\n"
            "* **Conformidade LGPD:** Anonimização nativa via `STANDARD_HASH(..., 'SHA256')`.\n"
            "* **Query Tuning (`EXPLAIN PLAN`):** Eliminação de `TABLE ACCESS FULL` causada por `TO_CHAR(DT_ATENDIMENTO)` usando filtros *sargables* e índice composto com `INCLUDE`."
        )
    with col_t2:
        st.success(
            "**2. Engenharia de Dados & Camada Analítica (Python + DuckDB)**\n\n"
            "* **Extração Thin Mode:** Conector `python-oracledb` sem dependência de Instant Client.\n"
            "* **Data Quality:** Validação automática descartando inconsistências temporais (`DT_ALTA < DT_ATENDIMENTO`).\n"
            "* **Star Schema & Parquet:** Persistência analítica em **DuckDB** (`FATO_ATENDIMENTOS`, `DIM_UNIDADE`, `DIM_ESPECIALIDADE`) e exportação colunar em **Apache Parquet**."
        )