from dash import html, dcc
import plotly.express as px
from utils.database import query_db

def render_content(municipio_id):
    # Consulta simplificada para resumo de agentes públicos
    agentes_publicos = query_db(f"""
        SELECT 
            ap.exercicio_orcamento AS ano,
            o.nome_orgao AS órgão,
            ap.codigo_vinculo AS vínculo,
            COUNT(*) AS quantidade
        FROM agentes_publicos ap
        LEFT JOIN orgao o ON ap.codigo_orgao = o.codigo_orgao AND ap.municipio_id = o.municipio_id
        WHERE ap.municipio_id = '{municipio_id}'
        GROUP BY ap.exercicio_orcamento, o.nome_orgao, ap.codigo_vinculo
        ORDER BY ap.exercicio_orcamento, o.nome_orgao;
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