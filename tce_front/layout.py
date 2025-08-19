from dash import dcc, html
from utils.database import get_municipios, get_anos_disponiveis

# Carregar municípios
municipios = get_municipios()
anos_disponiveis = get_anos_disponiveis()

# Criar opções do dropdown com os nomes reais dos municípios
municipio_options = [
    {'label': row['nome'], 'value': row['codigo_municipio']}
    for _, row in municipios.iterrows()
]

# Define o valor padrão como o primeiro município da lista
default_municipio = municipio_options[0]['value'] if municipio_options else None
default_ano = anos_disponiveis[-1] if anos_disponiveis else None

# Layout principal
app_layout = html.Div([
    html.H1("Análise de Municípios", className="main-title"),
    html.Div([
        html.Label("Selecione o Município:", className="dropdown-label"),
        dcc.Dropdown(
            id='municipio-dropdown',
            options=municipio_options,
            value=default_municipio,  # Valor padrão
            className="dropdown"
        )
    ], className="dropdown-container"),
    html.Div([
        html.Label("Selecione o Ano:", className="dropdown-label"),
        dcc.Dropdown(
            id='ano-dropdown',
            options=[{"label": str(a), "value": int(a)} for a in anos_disponiveis],
            value=default_ano,
            clearable=False,
            className="dropdown",
            persistence=True,
            persistence_type='local'
        )
    ], className="dropdown-container"),

    dcc.Tabs(id='tabs', value='receitas2', children=[
        dcc.Tab(label='Receitas Detalhadas', value='receitas2', className="tab"),
        dcc.Tab(label='Despesas Detalhadas', value='despesas', className="tab"),
        dcc.Tab(label='Receitas x Despesas', value='home', className="tab"),
        dcc.Tab(label='Pessoal', value='pessoal', className="tab"),
        dcc.Tab(label='Comparação de Municípios', value='comparacao', className="tab"),
    ], className="tabs-container"),

    

    dcc.Loading(
        id='tabs-loading',
        type='circle',
        children=html.Div(id='tabs-content', className="tabs-content")
    )
])