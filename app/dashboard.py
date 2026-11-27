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
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    span[data-baseweb="tag"] {
        background-color: #E0F2FE !important;
        border: 1px solid #BAE6FD !important;
        color: #0369A1 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    span[data-baseweb="tag"] svg { fill: #0369A1 !important; }
    .header-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0F4C81;
        border-radius: 10px;
        padding: 20px 26px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .header-top { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
    .header-title { font-size: 1.55rem; font-weight: 700; color: #0F172A; margin: 0; letter-spacing: -0.02em; }
    .status-badge {
        background-color: #CCFBF1; color: #0F766E; border: 1px solid #99F6E4;
        padding: 4px 12px; border-radius: 999px; font-size: 0.76rem; font-weight: 600;
    }
    .header-subtitle { color: #475569; font-size: 0.92rem; margin: 8px 0 14px 0; line-height: 1.5; }
    .stack-badge {
        display: inline-block; background-color: #F1F5F9; color: #334155;
        border: 1px solid #CBD5E1; border-radius: 6px; padding: 3px 10px;
        font-size: 0.75rem; font-weight: 600; margin-right: 6px; margin-bottom: 4px;
    }
    .kpi-box {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 18px 20px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .kpi-title { color: #64748B; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px; }
    .kpi-num { color: #0F172A; font-size: 1.7rem; font-weight: 700; line-height: 1.2; }
    .kpi-foot { color: #0D9488; font-size: 0.8rem; font-weight: 600; margin-top: 6px; }
    .author-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
    .author-brand { color: #0F4C81; font-weight: 800; font-size: 0.95rem; letter-spacing: -0.01em; }
    .author-name { color: #0F172A; font-size: 1.02rem; font-weight: 700; margin-top: 10px; }
    .author-role { color: #0284C7; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px; }
    .author-desc { color: #475569; font-size: 0.79rem; line-height: 1.45; margin-bottom: 10px; }
    .author-link { display: inline-block; color: #0F4C81 !important; text-decoration: none; font-size: 0.8rem; font-weight: 600; margin-right: 12px; }
</style>
""", unsafe_allow_html=True)

DW_PATH = Path("data/warehouse/hospital_dw.duckdb")


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


with st.sidebar:
    st.markdown(
        """
        <div class="author-box">
            <div style="display:flex; align-items:center; gap:10px;">
                <svg width="32" height="32" viewBox="0 0 36 36" fill="none">
                    <rect width="36" height="36" rx="8" fill="#0F4C81"/>
                    <path d="M18 9V27M9 18H27" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round"/>
                    <circle cx="27" cy="9" r="3.5" fill="#14B8A6"/>
                </svg>
                <div>
                    <div class="author-brand">LSDataScience</div>
                    <div style="color:#64748B; font-size:0.7rem; font-weight:600;">HEALTHCARE DATA ENGINEERING</div>
                </div>
            </div>
            <div class="author-name">Luccas Silva</div>
            <div class="author-role">Analista de Sistemas & Dados</div>
            <div class="author-desc">
                +10 anos de atuação em TI Hospitalar (MV Soul / PEP), Oracle SQL/PL/SQL, Python ETL e Business Intelligence.
            </div>
            <a class="author-link" href="https://github.com/LSDataScience" target="_blank">GitHub ↗</a>
            <a class="author-link" href="https://www.linkedin.com/in/luccas-silva/" target="_blank">LinkedIn ↗</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not DW_PATH.exists():
    st.warning("Data Warehouse ainda não gerado. Execute `python -m src.pipeline` no terminal primeiro.")
    st.stop()

df = load_warehouse()
df["dt_atendimento"] = pd.to_datetime(df["dt_atendimento"])

with st.sidebar:
    st.markdown("#### Filtros Assistenciais")
    periodo_label = st.selectbox(
        "Janela Temporal",
        ["Últimos 12 meses", "Últimos 6 meses", "Últimos 3 meses"],
        index=0,
    )
    meses_map = {"Últimos 12 meses": 12, "Últimos 6 meses": 6, "Últimos 3 meses": 3}
    data_corte = df["dt_atendimento"].max() - pd.DateOffset(months=meses_map[periodo_label])

    unidades_disp = sorted(df["nm_unidade"].unique())
    unidades = st.multiselect("Unidade Hospitalar", unidades_disp, default=unidades_disp)

    fontes_disp = sorted(df["fonte_pagadora"].unique())
    fontes = st.multiselect("Fonte Pagadora", fontes_disp, default=fontes_disp)

    tipos_disp = sorted(df["ds_tipo_atendimento"].unique())
    tipos = st.multiselect("Caráter do Atendimento", tipos_disp, default=tipos_disp)

    if st.button("🔄 Recarregar Dados do DW", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

df_filt = df[
    (df["dt_atendimento"] >= data_corte)
    & (df["nm_unidade"].isin(unidades))
    & (df["fonte_pagadora"].isin(fontes))
    & (df["ds_tipo_atendimento"].isin(tipos))
]

st.markdown(
    """
    <div class="header-card">
        <div class="header-top">
            <h1 class="header-title">Inteligência Operacional & Indicadores Hospitalares</h1>
            <span class="status-badge">● ETL Sincronizado · Oracle 23ai → Python → DuckDB</span>
        </div>
        <p class="header-subtitle">
            Painel analítico desenvolvido sobre arquitetura dimensional (Star Schema) com dados hospitalares sintéticos
            anonimizados (LGPD), demonstrando extração transacional Oracle PL/SQL, regras de Data Quality e BI clínico.
        </p>
        <div>
            <span class="stack-badge">Oracle Database 23ai</span>
            <span class="stack-badge">PL/SQL & Query Tuning</span>
            <span class="stack-badge">Python Thin ETL</span>
            <span class="stack-badge">Star Schema (DW)</span>
            <span class="stack-badge">DuckDB & Apache Parquet</span>
            <span class="stack-badge">LGPD SHA-256</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Atendimentos ({periodo_label})</div>
        <div class="kpi-num">{total_atend:,}</div>
        <div class="kpi-foot">✓ Registros validados (Data Quality)</div>
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Taxa de Ocupação Operacional</div>
        <div class="kpi-num">{taxa_ocupacao:.1f}%</div>
        <div class="kpi-foot">Capacidade ativa: {int(leitos_unicos)} leitos</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Tempo Médio Permanência (ALOS)</div>
        <div class="kpi-num">{alos:.2f} dias</div>
        <div class="kpi-foot">Referência institucional: ≤ 6,5 dias</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    fat_fmt = f"R$ {fat_total/1e6:,.2f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
    tk_fmt = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Produção & Receita Bruta</div>
        <div class="kpi-num">{fat_fmt}</div>
        <div class="kpi-foot">Ticket médio: {tk_fmt}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

tab1, tab2, tab3 = st.tabs([
    "Evolução Assistencial & Ocupação",
    "Produção por Unidade & Convênios",
    "Arquitetura & Tuning Oracle",
])

with tab1:
    col_esq, col_dir = st.columns([1.65, 1])

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
            labels={"ano_mes": "Competência", "qtd": "Atendimentos", "ds_tipo_atendimento": "Caráter"},
            color_discrete_map={
                "Ambulatório": "#0F4C81",
                "Internação": "#0D9488",
                "Urgência / Emergência": "#3B82F6",
            },
        )
        fig_line.update_traces(line=dict(width=2.5), marker=dict(size=7))
        fig_line.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=55, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_dir:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(taxa_ocupacao, 1),
            number={"suffix": "%", "font": {"color": "#0F172A", "size": 40}},
            title={
                "text": "Ocupação Global de Leitos<br><span style='font-size:12px;color:#64748B'>Meta Assistencial: 75% a 85%</span>",
                "font": {"color": "#0F172A", "size": 15},
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
            height=380,
            margin=dict(l=25, r=25, t=65, b=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab2:
    c_a, c_b = st.columns([1.35, 1])

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
            title="Volume Assistencial: Unidade Hospitalar × Especialidade",
            labels=dict(x="Especialidade", y="Unidade", color="Atendimentos"),
        )
        fig_heat.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A"),
            margin=dict(l=20, r=20, t=55, b=20),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with c_b:
        mix_fonte = (
            df_filt.groupby("fonte_pagadora", as_index=False)["vl_total_conta"]
            .sum()
        )
        fig_donut = px.pie(
            mix_fonte,
            names="fonte_pagadora",
            values="vl_total_conta",
            hole=0.62,
            title="Participação na Receita: SUS vs. Saúde Suplementar",
            color_discrete_sequence=["#0F4C81", "#0D9488"],
        )
        fig_donut.update_traces(textposition="outside", textinfo="percent+label")
        fig_donut.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            font=dict(color="#0F172A"),
            showlegend=False,
            margin=dict(l=20, r=20, t=55, b=20),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

with tab3:
    st.markdown("#### Decisões de Arquitetura & Otimização (Portfólio LSDataScience)")
    col_t1, col_t2 = st.columns(2)
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