from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from callbacks import register_callbacks
from layout import app_layout
from flask_caching import Cache
from flask import request, send_file
import pdfkit
from flask_cors import CORS

# Inicialização do app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Análise de Municípios"

CORS(app.server)  # Permitir todas as origens

# Layout do app
app.layout = app_layout

# Configuração do cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # Tempo em segundos
})

# Registrar callbacks
register_callbacks(app)

# Rota para geração de PDF
@app.server.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json  # Receber os dados do frontend
    html_content = data.get('html', '')  # HTML do conteúdo gerado na aba
    logo_url = data.get('logo_url', '')  # URL do logo enviado

    # Adicionar logo e marca no HTML
    header_html = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{logo_url}" alt="Logo" style="max-height: 100px;">
        <h3>Relatório Gerado</h3>
    </div>
    """
    full_html = f"""
    <html>
    <body>
        {header_html}
        {html_content}
    </body>
    </html>
    """

    # Caminho para salvar o PDF gerado
    pdf_path = 'relatorio.pdf'

    # Gerar o PDF usando pdfkit
    try:
        pdfkit.from_string(full_html, pdf_path)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8040)