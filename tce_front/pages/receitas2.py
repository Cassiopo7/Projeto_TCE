from dash import html, dcc
import plotly.express as px
from utils.database import query_db

# Função genérica para criar gráficos
def criar_grafico(dados, x, y, orientacao="v", titulo="", text=None, color=None, labels=None, cores=None, barmode=None):
    fig = px.bar(
        dados,
        x=x,
        y=y,
        orientation=orientacao,
        text=text,
        color=color,
        barmode=barmode,
        color_discrete_sequence=cores or ['#4682B4', '#2E8B57'],
        labels=labels,
        title=titulo,
    )
    fig.update_traces(
        texttemplate='R$ %{text:,.2f}' if text else None,
        textposition='outside',
    )
    fig.update_layout(
        xaxis=dict(title=labels.get(x, ""), tickformat=',.2f') if x else None,
        yaxis=dict(title=labels.get(y, "")) if y else None,
    )
    return fig

# Função genérica para consultas e transformação
def consultar_dados(municipio_id, ano, consulta, id_vars, value_vars, var_name, value_name):
    dados = query_db(consulta.format(municipio_id=municipio_id, ano=ano))
    if dados.empty:
        return None
    return dados.melt(
        id_vars=id_vars,
        value_vars=value_vars,
        var_name=var_name,
        value_name=value_name,
    )

# Função principal de renderização
def render_content(municipio_id, ano):
    consultas = {
        "previsao_arrecadacao": {
            "query": """
                SELECT 
                    ano::text AS ano, 
                    SUM(distinct valor_previsto_orcamento) AS valor_previsto,
                    SUM(distinct valor_arrecadado_no_mes) AS valor_arrecadado
                FROM receita
                WHERE municipio_id = '{municipio_id}'
                GROUP BY ano
                ORDER BY ano;
            """,
            "id_vars": ["ano"],
            "value_vars": ["valor_previsto", "valor_arrecadado"],
            "var_name": "Categoria",
            "value_name": "Valor (R$)",
            "grafico": {
                "x": "Valor (R$)",
                "y": "ano",
                "orientacao": "h",
                "barmode": "group",
                "titulo": "Previsão x Arrecadação",
                "color": "Categoria",
                "labels": {"ano": "Ano", "Valor (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
        "receita_mes": {
            "query": """
                SELECT 
                    TO_CHAR(TO_DATE(mes || '-' || '01' || '-' || ano, 'MM-DD-YYYY'), 'Month YYYY') AS mes_ano, 
                    SUM(distinct valor_arrecadado_no_mes) as valor_arrecadado_no_mes
                FROM receita
                WHERE municipio_id = '{municipio_id}'
                GROUP BY ano, mes
                ORDER BY ano, mes;
            """,
            "id_vars": ["mes_ano"],
            "value_vars": ["valor_arrecadado_no_mes"],
            "var_name": "Categoria",
            "value_name": "Valor mensal (R$)",
            "grafico": {
                "x": "mes_ano",
                "y": "Valor mensal (R$)",
                "titulo": "Receitas por Mês",
                "labels": {"mes_ano": "Mês", "Valor mensal (R$)": "Valor mensal (R$)", "Categoria": "Categoria"},
            },
        },
        "receita_por_origem": {
            "query": """
                SELECT 
                    CASE 
                        WHEN codigo_rubrica LIKE '1.1%' THEN 'Receitas Tributárias'
                        WHEN codigo_rubrica LIKE '1.2%' THEN 'Receitas de Contribuições'
                        WHEN codigo_rubrica LIKE '1.3%' THEN 'Receita Patrimonial'
                        WHEN codigo_rubrica LIKE '1.7%' THEN 'Transferências Correntes'
                        ELSE 'Outras Receitas'
                    END AS tipo_receita,
                    SUM(distinct valor_arrecadado_no_mes) AS valor_arrecadado_por_origem
                FROM receita
                WHERE municipio_id = '{municipio_id}' AND codigo_rubrica IS NOT NULL
                GROUP BY CASE 
                        WHEN codigo_rubrica LIKE '1.1%' THEN 'Receitas Tributárias'
                        WHEN codigo_rubrica LIKE '1.2%' THEN 'Receitas de Contribuições'
                        WHEN codigo_rubrica LIKE '1.3%' THEN 'Receita Patrimonial'
                        WHEN codigo_rubrica LIKE '1.7%' THEN 'Transferências Correntes'
                        ELSE 'Outras Receitas'
                    END
                ORDER BY valor_arrecadado_por_origem ASC;
            """,
            "id_vars": ["tipo_receita"],
            "value_vars": ["valor_arrecadado_por_origem"],
            "var_name": "Categoria",
            "value_name": "Valor arrecadado por origem (R$)",
            "grafico": {
                "x": "Valor arrecadado por origem (R$)",
                "y": "tipo_receita",
                "orientacao": "h",
                "titulo": "Receita Orçamentária",
                "color": "Categoria",
                "labels": {"tipo_receita": "Origem", "Valor arrecadado por origem (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
        "receita_transferencia": {
            "query": """
                SELECT 
                    CASE 
                        WHEN codigo_rubrica LIKE '1.7.1%' THEN 'Transferências da União'
                        WHEN codigo_rubrica LIKE '1.7.2%' THEN 'Transferências dos Estados'
                        WHEN codigo_rubrica LIKE '1.7.3%' THEN 'Transferências dos Municípios'
                        WHEN codigo_rubrica LIKE '1.7.4%' THEN 'Transferências Multigovernamentais'
                        WHEN codigo_rubrica LIKE '1.7.5%' THEN 'Transferências de Consórcios Públicos'
                        WHEN codigo_rubrica LIKE '1.7.6%' THEN 'Transferências do Exterior'
                        WHEN codigo_rubrica LIKE '1.7.7%' THEN 'Transferências de Pessoas'
                        WHEN codigo_rubrica LIKE '1.7.8%' THEN 'Transferências de Convênios'
                        ELSE 'Outras Transferências'
                    END AS tipo_receita,
                    SUM(distinct valor_arrecadado_no_mes) AS valor_arrecadado_por_origem
                FROM receita
                WHERE municipio_id = '{municipio_id}' AND codigo_rubrica LIKE '1.7%'
                GROUP BY CASE 
                        WHEN codigo_rubrica LIKE '1.7.1%' THEN 'Transferências da União'
                        WHEN codigo_rubrica LIKE '1.7.2%' THEN 'Transferências dos Estados'
                        WHEN codigo_rubrica LIKE '1.7.3%' THEN 'Transferências dos Municípios'
                        WHEN codigo_rubrica LIKE '1.7.4%' THEN 'Transferências Multigovernamentais'
                        WHEN codigo_rubrica LIKE '1.7.5%' THEN 'Transferências de Consórcios Públicos'
                        WHEN codigo_rubrica LIKE '1.7.6%' THEN 'Transferências do Exterior'
                        WHEN codigo_rubrica LIKE '1.7.7%' THEN 'Transferências de Pessoas'
                        WHEN codigo_rubrica LIKE '1.7.8%' THEN 'Transferências de Convênios'
                        ELSE 'Outras Transferências'
                    END
                ORDER BY valor_arrecadado_por_origem ASC;
            """,
            "id_vars": ["tipo_receita"],
            "value_vars": ["valor_arrecadado_por_origem"],
            "var_name": "Categoria",
            "value_name": "Receita de transferencia (R$)",
            "grafico": {
                "x": "Receita de transferencia (R$)",
                "y": "tipo_receita",
                "orientacao": "h",
                "titulo": "Receita de transferência",
                "color": "Categoria",
                "labels": {"tipo_receita": "Origem transferência", "Receita de transferencia (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
        "receita_tributaria": {
            "query": """
                SELECT 
                    CASE 
                        WHEN codigo_rubrica LIKE '1.1.1%' THEN 'Impostos'
                        WHEN codigo_rubrica LIKE '1.1.2%' THEN 'Taxas'
                        WHEN codigo_rubrica LIKE '1.1.3%' THEN 'Contribuição de Melhoria'
                        ELSE 'Outras Receitas Tributárias'
                    END AS tipo_receita,
                    SUM(distinct valor_arrecadado_no_mes) AS valor_arrecadado_por_origem
                FROM receita
                WHERE municipio_id = '{municipio_id}' AND codigo_rubrica LIKE '1.1%'
                GROUP BY CASE 
                        WHEN codigo_rubrica LIKE '1.1.1%' THEN 'Impostos'
                        WHEN codigo_rubrica LIKE '1.1.2%' THEN 'Taxas'
                        WHEN codigo_rubrica LIKE '1.1.3%' THEN 'Contribuição de Melhoria'
                        ELSE 'Outras Receitas Tributárias'
                    END
                ORDER BY valor_arrecadado_por_origem ASC;
            """,
            "id_vars": ["tipo_receita"],
            "value_vars": ["valor_arrecadado_por_origem"],
            "var_name": "Categoria",
            "value_name": "Arrecadação tributária (R$)",
            "grafico": {
                "x": "Arrecadação tributária (R$)",
                "y": "tipo_receita",
                "orientacao": "h",
                "titulo": "Receita Tributária",
                "color": "Categoria",
                "labels": {"tipo_receita": "Fonte tributária", "Arrecadação tributária (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
    }

    graficos = []
    for chave, config in consultas.items():
        dados_long = consultar_dados(municipio_id, ano, config["query"], config["id_vars"], config["value_vars"], config["var_name"], config["value_name"])
        if dados_long is None:
            return html.Div(f"Sem dados disponíveis para {chave.replace('_', ' ')}.", className="error-message")
        grafico = criar_grafico(dados_long, **config["grafico"])
        graficos.append(dcc.Graph(figure=grafico, className="graph"))

    return html.Div([
        html.H3("RECEITAS", className="tab-title"),
        *graficos,
        html.Div([
            html.Button("Gerar PDF", id='generate-pdf-button', className="button"),
            dcc.Download(id="download-pdf"),
        ], className="table-container"),
    ])
