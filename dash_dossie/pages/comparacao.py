from dash import html, dcc
import plotly.graph_objects as go
from utils.database import query_db


def render_content():
    # Buscar todos os municípios disponíveis
    municipios = query_db("SELECT codigo_municipio, nome FROM municipio ORDER BY nome")

    municipio_options = [
        {'label': row['nome'], 'value': row['codigo_municipio']}
        for _, row in municipios.iterrows()
    ]

    return html.Div([
        html.H3("Comparação de Municípios", className="tab-title"),
        html.Div([
            dcc.Dropdown(
                id='comparacao-municipios-dropdown',
                options=municipio_options,
                multi=True,
                placeholder="Selecione até 20 municípios",
                className="dropdown"
            ),
            html.Button(
                "Atualizar Comparação",
                id='comparacao-button',
                className="button",
                style={'margin-top': '20px'}
            )
        ], className="dropdown-container"),
        html.Div(id='comparacao-visualizacao', className="grid-container"),
        html.Button("Gerar PDF", id='generate-pdf-button', className="button", style={'display': 'none'}),
        dcc.Download(id="download-pdf")
    ])


def render_visualizacao(municipios_selecionados):
    if not municipios_selecionados or len(municipios_selecionados) > 20:
        return html.Div("Selecione até 20 municípios para comparação.", className="error-message")

    # Buscar nomes dos municípios selecionados
    municipio_nomes = query_db(f"""
        SELECT codigo_municipio, nome
        FROM municipio
        WHERE codigo_municipio IN ({','.join(f"'{m}'" for m in municipios_selecionados)})
    """)
    nome_mapping = {row['codigo_municipio']: row['nome'] for _, row in municipio_nomes.iterrows()}

    visualizacao = []
    for municipio_id in municipios_selecionados:
        receitas = query_db(f"""
            SELECT MAX(valor_arrecadado_ate_mes) AS total_receitas 
            FROM receita_detalhada 
            WHERE municipio_id = '{municipio_id}' AND ano = 2024
        """)
        despesas = query_db(f"""
            SELECT MAX(valor_empenhado_ate_mes) AS total_despesas 
            FROM despesa_detalhada 
            WHERE municipio_id = '{municipio_id}' AND ano = 2024
        """)
        orcamento = query_db(f"""
            SELECT valor_total_supl_orcamento AS total_orcamento 
            FROM orcamentos 
            WHERE municipio_id = (SELECT id FROM municipio WHERE codigo_municipio = '{municipio_id}')
            AND exercicio_orcamento = 202400
        """)

        # Processar valores
        receita_valor = receitas.iloc[0]['total_receitas'] if not receitas.empty else 0
        despesa_valor = despesas.iloc[0]['total_despesas'] if not despesas.empty else 0
        orcamento_valor = orcamento.iloc[0]['total_orcamento'] if not orcamento.empty else 0

        # Criar gráfico
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Receitas', 'Despesas', 'Orçamento'],
            y=[receita_valor, despesa_valor, orcamento_valor],
            marker_color=['#2E8B57', '#FF6347', '#4682B4']  # Cores
        ))
        fig.update_layout(
            title=f"{nome_mapping.get(municipio_id, 'Município Não Encontrado')} (2024)",
            yaxis_title="Valor (R$)",
            xaxis_title="Categorias",
            height=400
        )

        # Adicionar o gráfico ao layout
        visualizacao.append(
            html.Div([
                dcc.Graph(figure=fig, className="grid-item")
            ], className="municipio-container")
        )

    return html.Div(visualizacao, className="grid-container")


def render_html(municipios_selecionados):
    if not municipios_selecionados or len(municipios_selecionados) > 20:
        return "<h3>Selecione até 20 municípios para comparação.</h3>"

    # Buscar nomes dos municípios selecionados
    municipio_nomes = query_db(f"""
        SELECT codigo_municipio, nome
        FROM municipio
        WHERE codigo_municipio IN ({','.join(f"'{m}'" for m in municipios_selecionados)})
    """)
    nome_mapping = {row['codigo_municipio']: row['nome'] for _, row in municipio_nomes.iterrows()}

    html_content = "<h3 style='text-align: center;'>Comparação de Municípios</h3>"

    for municipio_id in municipios_selecionados:
        receitas = query_db(f"""
            SELECT MAX(valor_arrecadado_ate_mes) AS total_receitas 
            FROM receita_detalhada 
            WHERE municipio_id = '{municipio_id}' AND ano = 2024
        """)
        despesas = query_db(f"""
            SELECT MAX(valor_empenhado_ate_mes) AS total_despesas 
            FROM despesa_detalhada 
            WHERE municipio_id = '{municipio_id}' AND ano = 2024
        """)
        orcamento = query_db(f"""
            SELECT valor_total_supl_orcamento AS total_orcamento 
            FROM orcamentos 
            WHERE municipio_id = (SELECT id FROM municipio WHERE codigo_municipio = '{municipio_id}')
            AND exercicio_orcamento = 202400
        """)

        receita_valor = receitas.iloc[0]['total_receitas'] if not receitas.empty else 0
        despesa_valor = despesas.iloc[0]['total_despesas'] if not despesas.empty else 0
        orcamento_valor = orcamento.iloc[0]['total_orcamento'] if not orcamento.empty else 0

        html_content += f"""
        <h4>{nome_mapping.get(municipio_id, 'Município Não Encontrado')} (2024)</h4>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; text-align: left;">
            <thead>
                <tr style="background-color: #4682B4; color: white;">
                    <th style="padding: 8px; border: 1px solid #ddd;">Categoria</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Valor (R$)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">Receitas</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{receita_valor:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">Despesas</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{despesa_valor:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">Orçamento</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{orcamento_valor:.2f}</td>
                </tr>
            </tbody>
        </table>
        """

    return html_content