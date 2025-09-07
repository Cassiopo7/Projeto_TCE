# db_setup.py

from sqlalchemy import create_engine, text
from config import DB_CONFIG

def setup_database():
    # Conectando ao banco de dados usando SQLAlchemy
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    
    with engine.connect() as conn:
        # Inicia uma transação
        with conn.begin():
            # Abre o arquivo SQL e lê cada instrução separadamente
            with open("tce_back/database/db_schema.sql", "r") as schema_file:
                sql_commands = schema_file.read().split(";")  # Divide em comandos individuais
                
                # Executa cada comando individualmente, ignorando linhas vazias
                for command in sql_commands:
                    if command.strip():  # Ignora linhas vazias
                        conn.execute(text(command))
        # A transação é confirmada automaticamente ao sair do bloco 'with conn.begin()'