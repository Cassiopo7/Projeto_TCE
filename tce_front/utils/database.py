from sqlalchemy import create_engine, text
import pandas as pd
from functools import lru_cache

# Configuração de conexão - usando variáveis de ambiente como no backend
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'tce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Criação do engine SQLAlchemy
DB_URI = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DB_URI)

def query_db(sql_query):
    """
    Executa uma query SQL no banco de dados PostgreSQL usando SQLAlchemy e retorna um DataFrame do Pandas.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(sql_query, connection)
        return df
    except Exception as e:
        print(f"Erro ao executar a query: {e}")
        return pd.DataFrame()

def query_db_params(sql_query: str, params: dict):
    """
    Executa uma query SQL parametrizada usando SQLAlchemy text() para evitar injeção.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    except Exception as e:
        print(f"Erro ao executar a query parametrizada: {e}")
        return pd.DataFrame()
    
def get_municipios():
    """
    Retorna uma lista de municípios disponíveis no banco de dados.
    """
    query = "SELECT DISTINCT codigo_municipio, nome FROM municipio ORDER BY nome;"
    return query_db(query)

@lru_cache(maxsize=1)
def get_anos_disponiveis():
    """
    Retorna anos distintos presentes nas tabelas de receita/despesa/orçamentos.
    """
    try:
        anos_receita = query_db("SELECT DISTINCT ano FROM receita WHERE ano IS NOT NULL ORDER BY ano")
        anos_despesa = query_db("SELECT DISTINCT ano FROM despesa WHERE ano IS NOT NULL ORDER BY ano")
        anos_orc = query_db("SELECT DISTINCT CAST(exercicio_orcamento AS INTEGER) AS ano FROM orcamentos WHERE exercicio_orcamento IS NOT NULL ORDER BY ano")
        todos = pd.concat([
            anos_receita.rename(columns={"ano": "ano"}),
            anos_despesa.rename(columns={"ano": "ano"}),
            anos_orc.rename(columns={"ano": "ano"}),
        ], ignore_index=True)
        if todos.empty:
            return []
        anos_unicos = sorted(set(int(a) for a in todos["ano"].dropna().astype(int)))
        return anos_unicos
    except Exception as e:
        print(f"Erro ao buscar anos disponíveis: {e}")
        return []