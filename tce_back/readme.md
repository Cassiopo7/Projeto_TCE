# Projeto Dossiê TCE-CE

Este projeto é um sistema de ETL (Extração, Transformação e Carga) que coleta dados da API pública do Tribunal de Contas do Estado do Ceará (TCE-CE), os armazena em um banco de dados PostgreSQL e fornece um dashboard para monitoramento e interação.

## Funcionalidades

- **Extração de Dados**: Coleta de diversas fontes de dados da API do TCE-CE, como municípios, órgãos, receitas, despesas, licitações, prestações de contas, liquidações e notas de empenho.
- **Carga de Dados**: Armazenamento dos dados em um banco de dados PostgreSQL.
- **Controle de Carga**: Sistema de controle para evitar o reprocessamento de dados já carregados.
- **Dashboard Interativo**: Uma interface web construída com Streamlit para:
  - Monitorar o progresso da carga de cada tipo de dado.
  - Verificar municípios com dados pendentes para um determinado período.
  - Executar manualmente as funções de carga para cada tipo de dado.

## Como Executar

### Pré-requisitos

- Python 3.10+
- PostgreSQL
- Git

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd Dossie
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados:**
   - Certifique-se de que seu servidor PostgreSQL esteja em execução.
   - Renomeie o arquivo `.env.example` para `.env` e preencha com as suas credenciais do PostgreSQL.

### Execução

1. **Para alimentar a base de dados (processo ETL completo):**
   ```bash
   python3 main.py
   ```

2. **Para rodar o Dashboard de monitoramento:**
   ```bash
   streamlit run dashboard.py
   ```

## Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação, orquestra o processo de ETL.
- `dashboard.py`: Aplicação web do dashboard com Streamlit.
- `config.py`: Configurações da aplicação (API, banco de dados).
- `requirements.txt`: Lista de dependências do projeto.
- `etl_interface.py`: Funções que servem de interface entre o dashboard e o banco de dados.
- `data_extraction/`
  - `api_client.py`: Cliente para realizar as chamadas à API do TCE-CE.
  - `data_loader.py`: Funções para carregar os dados no banco de dados.
- `database/`
  - `db_config.py`: Configuração da conexão com o banco de dados.
  - `db_schema.sql`: Esquema do banco de dados.
  - `db_setup.py`: Script para inicializar e configurar o banco de dados.
