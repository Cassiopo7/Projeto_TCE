from dash import html, dcc
import plotly.express as px
from utils.database import query_db, query_db_params

# Função genérica para criar gráficos

import plotly.express as px

def criar_grafico(
    dados,
    x=None,
    y=None,
    tipo="bar",  # Define o tipo de gráfico: "bar", "line", etc.
    orientacao="v",
    titulo="",
    text=None,
    color=None,
    labels=None,
    cores=None,
    barmode=None,
    linha_estilo=None,  # Argumento adicional para customizar gráficos de linha
):
    # Escolha da função de plot com base no tipo de gráfico
    if tipo == "bar":
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
        # Posição de texto específica para gráficos de barra
        textposition = 'outside'
    elif tipo == "line":
        fig = px.line(
            dados,
            x=x,
            y=y,
            text=text,
            color=color,
            line_shape=linha_estilo or "linear",
            color_discrete_sequence=cores or ['#4682B4', '#2E8B57'],
            labels=labels,
            title=titulo,
        )
        # Posição de texto específica para gráficos de linha
        textposition = 'top center'  # Escolha uma posição válida
    else:
        raise ValueError(f"Tipo de gráfico '{tipo}' não suportado.")

    # Atualizações comuns para ambos os tipos de gráfico
    fig.update_traces(
        texttemplate='R$ %{text:,.2f}' if text else None,
        textposition=textposition if text else None,
    )
    fig.update_layout(
        xaxis=dict(title=labels.get(x, ""), tickformat=',.2f') if x and labels else None,
        yaxis=dict(title=labels.get(y, "")) if y and labels else None,
    )
    
    return fig


# Função genérica para consultas e transformação
def consultar_dados(municipio_id, consulta, id_vars, value_vars, var_name, value_name):
    dados = query_db(consulta.format(municipio_id=municipio_id))
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
        "fixacao_execucao": {
            "query": """
                SELECT 
                    ano::text AS ano, 
                    SUM(distinct valor_fixado_orcamento_bal_despesa) AS valor_fixado,
                    SUM(distinct valor_liquidado_no_mes) AS valor_executado
                FROM despesa_detalhada
                WHERE municipio_id = '{municipio_id}'
                GROUP BY ano
                ORDER BY ano;
            """,
            "id_vars": ["ano"],
            "value_vars": ["valor_fixado", "valor_executado"],
            "var_name": "Categoria",
            "value_name": "Valor (R$)",
            "grafico": {
                "tipo": "bar",
                "x": "Valor (R$)",
                "y": "ano",
                "barmode": "group",
                "orientacao": "h",
                "titulo": "Fixação x Execução",
                "color": "Categoria",
                "labels": {"ano": "Ano", "Valor (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
        "despesa_mensal": {
            "query": """
                SELECT 
                    TO_CHAR(TO_DATE(ano || '-' || mes || '-01', 'YYYY-MM-DD'), 'Month YYYY') AS mes_ano, 
                    SUM(distinct valor_empenhado_no_mes) as valor_empenhado,
                    SUM(distinct valor_liquidado_no_mes) as valor_liquidado,
                    SUM(distinct valor_pago_no_mes) as valor_pago
                FROM despesa_detalhada
                WHERE municipio_id = '{municipio_id}' AND ano = '{'" + str(ano) + "'}'
                GROUP BY ano,mes
                ORDER BY ano,mes;
            """,
            "id_vars": ["mes_ano"],
            "value_vars": ["valor_empenhado", "valor_liquidado", "valor_pago"],
            "var_name": "Categoria",
            "value_name": "Valor mensal (R$)",
            "grafico": {
                "tipo": "bar",
                "x": "mes_ano",
                "y": "Valor mensal (R$)",
                "barmode": "group",
                "titulo": "Despesa Mensal",
                "color": "Categoria",
                "cores": ['#0047AB', '#FF8C00', '#3CB371'],
                "labels": {"mes_ano": "Mês", "Valor mensal (R$)": "Valor mensal (R$)", "Categoria": "Categoria"},
            },
        },
        "despesa_mensal_por_exercicio": {
            "query": """
                SELECT 
                    ano,
                    mes, 
                    SUM(distinct valor_liquidado_no_mes) AS valor_liquidado
                FROM despesa_detalhada
                WHERE ano = '{'" + str(ano) + "'}'
                GROUP BY ano, mes
                ORDER BY ano, mes;
            """,
            "id_vars": ["ano"],
            "value_vars": ["mes","valor_liquidado"],
            "var_name": "mes",
            "value_name": "Valor R$",
            "grafico": {
                "tipo": "line",
                "x": "mes",
                "y": "Valor R$",
                "orientacao": "h",
                "titulo": "Despesa mensal por exercício",
                "color": "ano",
                "labels": {"mes": "Mês", "valor_liquidado": "Valor R$", "ano": "Ano"},
            },
        },
        "proc_adm_licitacoes": {
            "query": """
                SELECT 
                    descricao_status, 
                    SUM(valor_estimado) as valorestimado
                FROM licitacao
                WHERE municipio_id = '{municipio_id}'
                GROUP BY descricao_status;
            """,
            "id_vars": ["descricao_status"],
            "value_vars": ["valorestimado"],
            "var_name": "Categoria",
            "value_name": "Valor (R$)",
            "grafico": {
                "tipo": "bar",
                "x": "Valor (R$)",
                "y": "descricao_status",
                "barmode": "group",
                "orientacao": "h",
                "titulo": "Procedimentos administrativos para aquisições de bens e serviços",
                "color": "Categoria",
                "labels": {"descricao_status": "Proc administrativo", "Valor (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
        "modalidade_licitacao": {
            "query": """
                SELECT 
                    descricao_modalidade, 
                    SUM(valor_estimado) as valorestimado
                FROM licitacao
                WHERE municipio_id = '{municipio_id}'
                GROUP BY descricao_modalidade;
            """,
            "id_vars": ["descricao_modalidade"],
            "value_vars": ["valorestimado"],
            "var_name": "Categoria",
            "value_name": "Valor (R$)",
            "grafico": {
                "tipo": "bar",
                "x": "Valor (R$)",
                "y": "descricao_modalidade",
                "barmode": "group",
                "orientacao": "h",
                "titulo": "Processos licitatórios: pagamentos por modalidade de licitação",
                "color": "Categoria",
                "labels": {"descricao_moddalidade": "Modalidade", "Valor (R$)": "Valor (R$)", "Categoria": "Categoria"},
            },
        },
    }

    graficos = []
    for chave, config in consultas.items():
        dados_long = consultar_dados(municipio_id, config["query"], config["id_vars"], config["value_vars"], config["var_name"], config["value_name"])
        if dados_long is None:
            return html.Div(f"Sem dados disponíveis para {chave.replace('_', ' ')}.", className="error-message")
        grafico = criar_grafico(dados_long, **config["grafico"])
        graficos.append(dcc.Graph(figure=grafico, className="graph"))

    return html.Div([
        html.H3("DESPESAS", className="tab-title"),
        *graficos,
        html.Div([
            html.Button("Gerar PDF", id='generate-pdf-button', className="button"),
            dcc.Download(id="download-pdf"),
        ], className="table-container"),
    ])
