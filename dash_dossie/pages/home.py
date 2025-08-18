from dash import html, dcc
import plotly.express as px
from utils.database import query_db

def render_content(municipio_id):
    # Buscar nome do município
    municipio_info = query_db(f"SELECT nome FROM municipio WHERE codigo_municipio = '{municipio_id}'")
    municipio_nome = municipio_info.iloc[0]['nome'] if not municipio_info.empty else "Município Não Encontrado"

    # Queries para 2023
    receitas_2023 = query_db(f"""
        SELECT MAX(valor_arrecadado_ate_mes) AS total_receitas 
        FROM receita_detalhada 
        WHERE municipio_id = '{municipio_id}' AND ano = 2023
    """)
    despesas_2023 = query_db(f"""
        SELECT MAX(valor_empenhado_ate_mes) AS total_despesas 
        FROM despesa_detalhada 
        WHERE municipio_id = '{municipio_id}' AND ano = 2023
    """)
    orcamento_2023 = query_db(f"""
        SELECT valor_total_supl_orcamento AS total_orcamento 
        FROM orcamentos 
        WHERE municipio_id = '{municipio_id}' AND exercicio_orcamento = 202300
    """)

    # Queries para 2024
    receitas_2024 = query_db(f"""
        SELECT MAX(valor_arrecadado_ate_mes) AS total_receitas 
        FROM receita_detalhada 
        WHERE municipio_id = '{municipio_id}' AND ano = 2024
    """)
    despesas_2024 = query_db(f"""
        SELECT MAX(valor_empenhado_ate_mes) AS total_despesas 
        FROM despesa_detalhada 
        WHERE municipio_id = '{municipio_id}' AND ano = 2024
    """)
    orcamento_2024 = query_db(f"""
        SELECT valor_total_supl_orcamento AS total_orcamento 
        FROM orcamentos 
        WHERE municipio_id = '{municipio_id}' AND exercicio_orcamento = 202400
    """)

    # Valores para 2023
    receita_2023_valor = receitas_2023.iloc[0]['total_receitas'] if not receitas_2023.empty else 0
    despesa_2023_valor = despesas_2023.iloc[0]['total_despesas'] if not despesas_2023.empty else 0
    orcamento_2023_valor = orcamento_2023.iloc[0]['total_orcamento'] if not orcamento_2023.empty else 0

    # Valores para 2024
    receita_2024_valor = receitas_2024.iloc[0]['total_receitas'] if not receitas_2024.empty else 0
    despesa_2024_valor = despesas_2024.iloc[0]['total_despesas'] if not despesas_2024.empty else 0
    orcamento_2024_valor = orcamento_2024.iloc[0]['total_orcamento'] if not orcamento_2024.empty else 0

    # Gráfico para 2023
    fig_2023 = px.bar(
        x=['Receitas', 'Despesas', 'Orçamento'],  # Inclui orçamento
        y=[receita_2023_valor, despesa_2023_valor, orcamento_2023_valor],
        labels={'x': 'Categoria', 'y': 'Valor (R$)'},
        title=f"Resumo de 2023 - {municipio_nome}",
        color_discrete_sequence=['#2E8B57', '#FF6347', '#4682B4']  # Verde, Vermelho, Azul
    )

    # Gráfico para 2024
    fig_2024 = px.bar(
        x=['Receitas', 'Despesas', 'Orçamento'],  # Inclui orçamento
        y=[receita_2024_valor, despesa_2024_valor, orcamento_2024_valor],
        labels={'x': 'Categoria', 'y': 'Valor (R$)'},
        title=f"Resumo de 2024 - {municipio_nome}",
        color_discrete_sequence=['#2E8B57', '#FF6347', '#4682B4']  # Verde, Vermelho, Azul
    )

    return html.Div([
        html.H3(f"Resumo do {municipio_nome}", className="tab-title"),
        dcc.Graph(figure=fig_2023, className="graph"),
        dcc.Graph(figure=fig_2024, className="graph")
    ])