from dash import html, dcc
import plotly.express as px
from utils.database import query_db, query_db_params

def render_content(municipio_id, ano):
    # Buscar nome do município
    municipio_info = query_db(f"SELECT nome FROM municipio WHERE codigo_municipio = '{municipio_id}'")
    municipio_nome = municipio_info.iloc[0]['nome'] if not municipio_info.empty else "Município Não Encontrado"

    # Queries para 2023
    receitas_ref = query_db_params(
        """
        SELECT MAX(valor_arrecadado_ate_mes) AS total_receitas 
        FROM receita_detalhada 
        WHERE municipio_id = :municipio AND ano = :ano
        """,
        {"municipio": municipio_id, "ano": int(ano)}
    )
    despesas_ref = query_db_params(
        """
        SELECT MAX(valor_empenhado_ate_mes) AS total_despesas 
        FROM despesa_detalhada 
        WHERE municipio_id = :municipio AND ano = :ano
        """,
        {"municipio": municipio_id, "ano": int(ano)}
    )
    orcamento_ref = query_db_params(
        """
        SELECT valor_total_supl_orcamento AS total_orcamento 
        FROM orcamentos 
        WHERE municipio_id = :municipio AND exercicio_orcamento = :exercicio
        """,
        {"municipio": municipio_id, "exercicio": int(f"{ano}00")}
    )

    # Queries para 2024
    ano_comp = int(ano) - 1
    receitas_prev = query_db_params(
        """
        SELECT MAX(valor_arrecadado_ate_mes) AS total_receitas 
        FROM receita_detalhada 
        WHERE municipio_id = :municipio AND ano = :ano
        """,
        {"municipio": municipio_id, "ano": ano_comp}
    )
    despesas_prev = query_db_params(
        """
        SELECT MAX(valor_empenhado_ate_mes) AS total_despesas 
        FROM despesa_detalhada 
        WHERE municipio_id = :municipio AND ano = :ano
        """,
        {"municipio": municipio_id, "ano": ano_comp}
    )
    orcamento_prev = query_db_params(
        """
        SELECT valor_total_supl_orcamento AS total_orcamento 
        FROM orcamentos 
        WHERE municipio_id = :municipio AND exercicio_orcamento = :exercicio
        """,
        {"municipio": municipio_id, "exercicio": int(f"{ano_comp}00")}
    )

    # Valores para 2023
    receita_prev_valor = receitas_prev.iloc[0]['total_receitas'] if not receitas_prev.empty else 0
    despesa_prev_valor = despesas_prev.iloc[0]['total_despesas'] if not despesas_prev.empty else 0
    orcamento_prev_valor = orcamento_prev.iloc[0]['total_orcamento'] if not orcamento_prev.empty else 0

    # Valores para 2024
    receita_ref_valor = receitas_ref.iloc[0]['total_receitas'] if not receitas_ref.empty else 0
    despesa_ref_valor = despesas_ref.iloc[0]['total_despesas'] if not despesas_ref.empty else 0
    orcamento_ref_valor = orcamento_ref.iloc[0]['total_orcamento'] if not orcamento_ref.empty else 0

    # Gráfico para 2023
    fig_prev = px.bar(
        x=['Receitas', 'Despesas', 'Orçamento'],
        y=[receita_prev_valor, despesa_prev_valor, orcamento_prev_valor],
        labels={'x': 'Categoria', 'y': 'Valor (R$)'},
        title=f"Resumo de {ano_comp} - {municipio_nome}",
        color_discrete_sequence=['#2E8B57', '#FF6347', '#4682B4']
    )

    # Gráfico para 2024
    fig_ref = px.bar(
        x=['Receitas', 'Despesas', 'Orçamento'],
        y=[receita_ref_valor, despesa_ref_valor, orcamento_ref_valor],
        labels={'x': 'Categoria', 'y': 'Valor (R$)'},
        title=f"Resumo de {ano} - {municipio_nome}",
        color_discrete_sequence=['#2E8B57', '#FF6347', '#4682B4']
    )

    return html.Div([
        html.H3(f"Resumo do {municipio_nome}", className="tab-title"),
        html.Div([
            html.Div([
                html.H4("KPIs"),
                html.Ul([
                    html.Li(f"Receita {ano}: R$ {receita_ref_valor:,.2f}"),
                    html.Li(f"Despesa {ano}: R$ {despesa_ref_valor:,.2f}"),
                    html.Li(f"Orçamento {ano}: R$ {orcamento_ref_valor:,.2f}"),
                    html.Li(f"Resultado {ano}: R$ {(receita_ref_valor - despesa_ref_valor):,.2f}"),
                    html.Li(f"Variação Receita vs {ano_comp}: {((receita_ref_valor - receita_prev_valor) / receita_prev_valor * 100 if receita_prev_valor else 0):.2f}%"),
                ])
            ], className="kpi-container")
        ]),
        dcc.Graph(figure=fig_prev, className="graph"),
        dcc.Graph(figure=fig_ref, className="graph")
    ])