from dash import html, dcc
import plotly.express as px
from utils.database import query_db

def render_content(municipio_id):
    # Consulta simplificada para resumo de agentes públicos
    agentes_publicos = query_db(f"""
        SELECT 
            exercicio_orcamento AS ano,
            orgao AS órgão,
            vinculo AS vínculo,
            COUNT(*) AS quantidade
        FROM vw_detalhes_agentes_publicos
        WHERE codigo_municipio = '{municipio_id}'
        GROUP BY exercicio_orcamento, orgao, vinculo
        ORDER BY exercicio_orcamento, orgao;
    """)

    # Verificar se há dados
    if agentes_publicos.empty:
        return html.Div([
            html.H3("Sem dados disponíveis para este município.", style={'textAlign': 'center'})
        ])

    # Gráfico: Distribuição de agentes públicos por vínculo e órgão
    fig = px.bar(
        agentes_publicos,
        x='órgão',
        y='quantidade',
        color='vínculo',
        barmode='stack',
        labels={'órgão': 'Órgão', 'quantidade': 'Quantidade', 'vínculo': 'Vínculo'},
        title='Distribuição de Agentes Públicos por Órgão e Vínculo'
    )

    # Tabela: Detalhes de Agentes Públicos
    table_header = [
        html.Thead(html.Tr([
            html.Th("Ano"),
            html.Th("Órgão"),
            html.Th("Vínculo"),
            html.Th("Quantidade")
        ]))
    ]
    table_body = [
        html.Tbody([
            html.Tr([
                html.Td(row['ano']),
                html.Td(row['órgão']),
                html.Td(row['vínculo']),
                html.Td(row['quantidade'])
            ]) for _, row in agentes_publicos.iterrows()
        ])
    ]

    return html.Div([
        html.H3("Resumo de Agentes Públicos", className="tab-title"),
        dcc.Graph(figure=fig, className="graph"),
        html.Div([
            html.H4("Tabela de Agentes Públicos"),
            html.Table(table_header + table_body, className="table")
        ], className="table-container")
    ])