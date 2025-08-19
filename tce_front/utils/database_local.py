from sqlalchemy import create_engine
import pandas as pd

# Configuração de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'tce',
    'user': 'postgres',
    'password': 'postgres'
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
    
def get_municipios():
    """
    Retorna uma lista de municípios disponíveis no banco de dados.
    """
    query = "SELECT DISTINCT codigo_municipio, nome FROM municipio ORDER BY nome;"
    return query_db(query)