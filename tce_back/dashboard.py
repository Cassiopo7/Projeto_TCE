import streamlit as st
import subprocess
import time
from datetime import datetime
import pandas as pd
from etl_interface import (
    get_progresso_por_tipo,
    get_municipios_pendentes,
    get_funcoes_etl_disponiveis,
    get_total_municipios,
    get_progresso_por_periodo,
    get_progresso_tipos_no_periodo,
    ping_db,
    ping_api,
)

st.set_page_config(page_title="Painel ETL - Dossiê", layout="wide")


@st.cache_data(ttl=60)
def load_progresso_df() -> pd.DataFrame:
    try:
        dados = get_progresso_por_tipo()
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar progresso: {e}")
        return pd.DataFrame(columns=["tipo_dado", "total"])


@st.cache_data(ttl=300)
def load_funcoes() -> list:
    try:
        return list(get_funcoes_etl_disponiveis())
    except Exception as e:
        st.error(f"Erro ao carregar funções ETL: {e}")
        return []

st.title("📊 Painel de Monitoramento - ETL Dossiê")

# Sidebar: atualização e informações
st.sidebar.subheader("Atualização")
if st.sidebar.button("🔄 Atualizar agora"):
    load_progresso_df.clear()
    load_funcoes.clear()
    st.experimental_rerun()

st.sidebar.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Sidebar: Saúde da pipeline
st.sidebar.subheader("Saúde da Pipeline")
col_ok1, col_ok2 = st.sidebar.columns(2)
with col_ok1:
    st.metric("DB", "OK" if ping_db() else "ERRO")
with col_ok2:
    st.metric("API", "OK" if ping_api() else "ERRO")

st.header("1️⃣ Progresso por Tipo de Dado")
df_prog = load_progresso_df()
if df_prog.empty:
    st.info("Sem dados de progresso disponíveis.")
else:
    # KPIs gerais
    total_registros = int(df_prog["total"].sum()) if "total" in df_prog else 0
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total de registros", f"{total_registros:,}")
    col_b.metric("Tipos monitorados", f"{df_prog['tipo_dado'].nunique()}")
    maior = df_prog.sort_values("total", ascending=False).head(1)
    col_c.metric(
        "Maior tipo (registros)",
        f"{maior.iloc[0]['tipo_dado']} ({int(maior.iloc[0]['total']):,})" if not maior.empty else "-",
    )

    # Gráfico e tabela
    st.bar_chart(df_prog.set_index("tipo_dado")["total"], use_container_width=True)
    with st.expander("Detalhamento do progresso (tabela)"):
        st.dataframe(df_prog.sort_values("total", ascending=False), use_container_width=True)

st.header("2️⃣ Completude por Período e Pendências")
col1, col2, col3 = st.columns(3)
with col1:
    tipo = st.selectbox("Tipo de dado", load_funcoes(), index=0 if load_funcoes() else None)
with col2:
    ano = st.number_input("Ano", value=datetime.now().year, step=1)
with col3:
    mes = st.number_input("Mês", min_value=1, max_value=12, value=max(1, datetime.now().month - 1))

filtro_texto = st.text_input("Filtrar municípios (contém)", "")

prog = get_progresso_por_periodo(tipo, int(ano), int(mes))
total_muns = get_total_municipios()
colp1, colp2, colp3, colp4 = st.columns(4)
colp1.metric("Municípios (total)", f"{prog['total_municipios']}")
colp2.metric("Carregados", f"{prog['carregados']}")
colp3.metric("Restantes", f"{prog['restante']}")
colp4.metric("Completude", f"{prog['percentual']:.1f}%")

# Barra de progresso visual
st.progress(min(int(prog['percentual']), 100))

# Tabela por tipo no período
with st.expander("Progresso por tipo no período"):
    df_tipo_periodo = pd.DataFrame(get_progresso_tipos_no_periodo(int(ano), int(mes)))
    if not df_tipo_periodo.empty:
        df_tipo_periodo["percentual"] = (df_tipo_periodo["municipios"] / total_muns * 100).round(1)
        st.dataframe(df_tipo_periodo, use_container_width=True)
    else:
        st.caption("Sem registros no período.")

if st.button("🔍 Mostrar Municípios Pendentes"):
    with st.spinner("Consultando pendências..."):
        pendentes = get_municipios_pendentes(tipo, int(ano), int(mes))
    if pendentes:
        df_pend = pd.DataFrame({"municipio": pendentes})
        if filtro_texto:
            df_pend = df_pend[df_pend["municipio"].str.contains(filtro_texto, case=False, na=False)]

        st.warning(f"{len(df_pend)} municípios pendentes exibidos")
        st.dataframe(df_pend, use_container_width=True)

        csv_bytes = df_pend.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv_bytes,
            file_name=f"municipios_pendentes_{tipo}_{int(ano)}_{int(mes)}.csv",
            mime="text/csv",
        )
    else:
        st.success("✅ Nenhum município pendente")

st.header("3️⃣ Executar Função ETL Manualmente")

funcao = st.selectbox("Escolher função", load_funcoes(), index=0 if load_funcoes() else None)
if st.button("▶️ Executar Função"):
    try:
        comando = ["python3", "main.py", funcao]
        with st.spinner(f"Executando {funcao}..."):
            inicio = time.time()
            resultado = subprocess.run(comando, capture_output=True, text=True)
            duracao = time.time() - inicio
        if resultado.returncode == 0:
            st.success(f"✅ Execução concluída em {duracao:.1f}s")
        else:
            st.error(f"❌ Execução terminou com código {resultado.returncode} em {duracao:.1f}s")
        with st.expander("Ver logs"):
            st.text_area("Saída:", resultado.stdout + "\n" + resultado.stderr, height=300)
    except Exception as e:
        st.error(f"Erro ao executar função: {e}")