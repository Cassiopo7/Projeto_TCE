import streamlit as st
import subprocess
from etl_interface import get_progresso_por_tipo, get_municipios_pendentes, get_funcoes_etl_disponiveis

st.set_page_config(page_title="Painel ETL - Dossiê", layout="wide")

st.title("📊 Painel de Monitoramento - ETL Dossiê")

st.header("1️⃣ Progresso por Tipo de Dado")
progresso = get_progresso_por_tipo()
for item in progresso:
    st.metric(label=item["tipo_dado"], value=item["total"])

st.header("2️⃣ Verificar Municípios Pendentes")
col1, col2, col3 = st.columns(3)
with col1:
    tipo = st.selectbox("Tipo de dado", get_funcoes_etl_disponiveis())
with col2:
    ano = st.number_input("Ano", value=2025, step=1)
with col3:
    mes = st.number_input("Mês", min_value=1, max_value=12, value=5)

if st.button("🔍 Mostrar Municípios Pendentes"):
    pendentes = get_municipios_pendentes(tipo, ano, mes)
    if pendentes:
        st.warning(f"{len(pendentes)} municípios pendentes")
        st.code(", ".join(pendentes))
    else:
        st.success("✅ Nenhum município pendente")

st.header("3️⃣ Executar Função ETL Manualmente")

funcao = st.selectbox("Escolher função", get_funcoes_etl_disponiveis())
if st.button("▶️ Executar Função"):
    try:
        comando = ["python3", "main.py", funcao]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        st.text_area("Saída:", resultado.stdout + "\n" + resultado.stderr, height=300)
    except Exception as e:
        st.error(f"Erro ao executar função: {e}")