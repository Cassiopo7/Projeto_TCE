import requests
from markupsafe import escape
from dash import Input, Output, State, html, ctx, dcc
from pages.comparacao import render_visualizacao
from pages import home, despesas, receitas2, pessoal, comparacao, receitas2


def register_callbacks(app):
    # Callback único para troca de abas e atualização do município
    @app.callback(
        Output('tabs-content', 'children'),
        [Input('tabs', 'value'), Input('municipio-dropdown', 'value'), Input('ano-dropdown', 'value')],
        prevent_initial_call=True
    )
    def render_tab_and_update_municipio(tab_name, municipio_id, ano):
        print(f"Tab selecionada: {tab_name}, Município: {municipio_id}")

        if not municipio_id and tab_name != 'comparacao':
            return html.Div("Nenhum município selecionado.", className="error-message")

        if tab_name == 'receitas2':
            return receitas2.render_content(municipio_id, ano)
        if tab_name == 'home':
            return home.render_content(municipio_id, ano)
        elif tab_name == 'despesas':
            return despesas.render_content(municipio_id, ano)
        elif tab_name == 'pessoal':
            return pessoal.render_content(municipio_id)
        elif tab_name == 'comparacao':
            return comparacao.render_content()
        return html.Div("Aba não encontrada.", className="error-message")

    # Callback para atualização da comparação de municípios
    @app.callback(
        Output('comparacao-visualizacao', 'children'),
        [Input('comparacao-button', 'n_clicks')],
        [State('comparacao-municipios-dropdown', 'value'), State('ano-dropdown', 'value')]
    )
    def update_comparacao(n_clicks, municipios_selecionados, ano):
        print(f"Botão clicado {n_clicks}, Municípios selecionados: {municipios_selecionados}")

        if not n_clicks:
            return html.Div("Selecione municípios e clique em 'Atualizar Comparação'.", className="info-message")

        if not municipios_selecionados:
            return html.Div("Nenhum município selecionado. Escolha até 20 municípios.", className="error-message")

        if len(municipios_selecionados) > 20:
            return html.Div("Selecione no máximo 20 municípios para a comparação.", className="error-message")

        return render_visualizacao(municipios_selecionados, ano)

    # Callback para geração de PDF
    @app.callback(
        Output('download-pdf', 'data'),
        [Input('generate-pdf-button', 'n_clicks')],
        [State('tabs', 'value'), State('municipio-dropdown', 'value')],
        prevent_initial_call=True
    )
    def generate_pdf(n_clicks, current_tab, municipio_id):
        if ctx.triggered_id == 'generate-pdf-button':
            print(f"Gerando PDF para a aba: {current_tab}, Município: {municipio_id}")

            # Cabeçalho e logo
            logo_url = "https://nagelconsultoria.com.br/wp-content/uploads/2014/10/logo-nagel.png"
            header = f"""
            <div style="text-align: center;">
                <img src="{logo_url}" alt="Logo Nagel Consultoria" style="max-height: 100px; margin-bottom: 20px;">
                <h1 style="color: #2E8B57; font-size: 28px;">Relatório - {current_tab.capitalize()}</h1>
            </div>
            """

            # Corpo da aba atual
            try:
                if current_tab == 'receitas2':
                    body = receitas2.render_html(municipio_id)
                elif current_tab == 'home':
                    body = home.render_html(municipio_id)
                elif current_tab == 'despesas':
                    body = despesas.render_html(municipio_id)
                elif current_tab == 'pessoal':
                    body = pessoal.render_html(municipio_id)
                elif current_tab == 'comparacao':
                    body = comparacao.render_html()
                else:
                    body = "<p>Conteúdo não encontrado.</p>"
            except Exception as e:
                print(f"Erro ao renderizar HTML: {str(e)}")
                return dcc.send_string("Erro ao gerar o PDF: problema ao renderizar o conteúdo.", filename="erro.txt")

            # HTML completo
            full_html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Relatório - {current_tab.capitalize()}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #2E8B57; color: white; }}
                </style>
            </head>
            <body>
                {header}
                {body}
            </body>
            </html>
            """

            # Backend URL para geração de PDF
            backend_url = "http://localhost:8040/generate-pdf"

            try:
                response = requests.post(backend_url, json={"html": full_html})
                response.raise_for_status()  # Levantar erro se o status não for 200

                # Retorna o PDF como download
                return dcc.send_bytes(
                    response.content,
                    filename=f"relatorio-{current_tab}.pdf"
                )
            except Exception as e:
                print(f"Erro ao gerar o PDF: {str(e)}")
                return dcc.send_string("Erro ao gerar o PDF: não foi possível conectar ao backend.", filename="erro.txt")