
# Projeto Dash de Análise de Municípios

Este projeto é uma aplicação web desenvolvida com Dash e Flask para análise de receitas, despesas e comparações financeiras entre municípios. A aplicação permite a visualização de gráficos, tabelas detalhadas e a exportação de relatórios em formato PDF. O objetivo principal é fornecer uma ferramenta interativa e prática para análise de dados financeiros municipais.

## Estrutura do Projeto

O projeto está estruturado nos seguintes diretórios e arquivos principais:

- **`app.py`**: Arquivo principal que inicia a aplicação Dash e configura o layout, callbacks e servidor.
- **`callbacks.py`**: Contém os callbacks responsáveis por manipular interações do usuário e atualizações de layout.
- **`layout.py`**: Define o layout principal da aplicação, incluindo as abas e componentes visuais.
- **`pages/`**: Diretório contendo scripts específicos para renderizar cada aba.
  - **`home.py`**: Página inicial com resumo geral do município selecionado.
  - **`despesas.py`**: Página que detalha despesas por órgão e ano.
  - **`receitas.py`**: Página que detalha receitas por órgão e ano.
  - **`pessoal.py`**: Página com informações sobre agentes públicos e seus vínculos.
  - **`comparacao.py`**: Página para comparação de até 20 municípios.
- **`utils/database.py`**: Funções para conexão com o banco de dados PostgreSQL e execução de queries.
- **`assets/`**: Diretório contendo o arquivo CSS para estilização.

---

## Funcionalidades

### 1. Seleção de Municípios
- Um dropdown na página inicial permite selecionar um município. 
- Atualiza as abas automaticamente para refletir o município escolhido.

### 2. Visualização de Receitas e Despesas
- **Gráficos de Barras**:
  - Mostram os valores empenhados, pagos, previstos e arrecadados.
  - Organizados por órgão e ano.
- **Tabelas**:
  - Resumo detalhado por órgão.

### 3. Comparação de Municípios
- Comparação simultânea de até 20 municípios.
- Exibição em formato de grade com gráficos individuais.
- Possibilidade de exportar os gráficos como PDF.

### 4. Geração de Relatórios PDF
- Exportação de cada aba como PDF com cabeçalho personalizado e logo.

---

## Métodos Detalhados

### 1. `app.py`
- **Função Principal**:
  - Inicia o Dash e Flask.
  - Configura o layout e registra os callbacks.
  - Configura o cache para otimizar desempenho.
- **Execução**:
  ```bash
  python app.py
  ```

### 2. `callbacks.py`
- **`render_tab`**:
  - Atualiza o conteúdo da aba com base no município selecionado.
- **`update_comparacao`**:
  - Atualiza a comparação de municípios ao clicar no botão "Atualizar Comparação".
- **`generate_pdf`**:
  - Gera um PDF do conteúdo atual da aba.
  - Envia a requisição ao backend Flask para renderizar o HTML como PDF.

### 3. `layout.py`
- Define o layout principal da aplicação com:
  - Dropdown de seleção de municípios.
  - Abas para navegação.
  - Contêiner para conteúdo dinâmico.

### 4. `pages/home.py`
- Renderiza a página inicial com um resumo de receitas, despesas e orçamento do município selecionado.

### 5. `pages/despesas.py`
- Consulta o banco de dados para exibir:
  - Gráficos de barras de despesas empenhadas e pagas.
  - Tabela detalhada por órgão.

### 6. `pages/receitas.py`
- Similar a `despesas.py`, mas foca em receitas previstas e arrecadadas.

### 7. `pages/pessoal.py`
- Exibe informações sobre agentes públicos:
  - Nome, CPF, vínculo e órgão.

### 8. `pages/comparacao.py`
- Permite comparar municípios.
- Renderiza gráficos de barras com valores agregados para receitas, despesas e orçamento.

### 9. `utils/database.py`
- **Funções**:
  - `query_db`: Executa uma query SQL no banco e retorna os resultados como DataFrame.
  - `get_municipios`: Retorna a lista de municípios disponíveis.

---

## Configuração do Banco de Dados

O projeto utiliza PostgreSQL como banco de dados. A estrutura básica inclui tabelas como `municipio`, `receita_detalhada`, `despesa_detalhada`, `orcamentos` e `prestacao_contas`.

### Exemplo de Configuração (`utils/database.py`)
```python
DB_CONFIG = {
    'host': '206.42.25.89',
    'port': '5432',
    'database': 'nagel',
    'user': 'cassio',
    'password': '92291248'
}
```

---

## Configuração do Ambiente

### Requisitos
- Python 3.8+
- PostgreSQL
- Bibliotecas Python:
  - `dash`
  - `flask`
  - `pandas`
  - `sqlalchemy`
  - `plotly`

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-repositorio.git
   cd projeto
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python3 -m venv myvenv
   source myvenv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o banco de dados em `utils/database.py`.

---

## Como Rodar

1. Inicie o backend Flask para geração de PDFs:
   ```bash
   python backend_pdf.py
   ```

2. Inicie o Dash:
   ```bash
   python app.py
   ```

3. Acesse a aplicação em:
   ```
   http://localhost:8060
   ```

---

## Exportação de Relatórios

Os relatórios PDF são gerados para as seguintes abas:
- Receitas Detalhadas
- Despesas Detalhadas
- Comparação de Municípios

---

## Estilo e Layout

O estilo da aplicação é definido no arquivo `assets/style.css`. Ajustes podem ser feitos para modificar cores, margens e tamanhos.

---

## Problemas Conhecidos

- **PDF não gerado no servidor**:
  - Verifique a URL do backend.
  - Certifique-se de que as permissões estão configuradas.

- **Demora na troca de abas**:
  - Habilite caching para otimizar desempenho.

---

## Contato

Se encontrar problemas ou tiver sugestões, entre em contato com:
- **Email**: suporte@nagelconsultoria.com.br
- **Telefone**: (85) 9999-9999
