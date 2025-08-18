from sqlalchemy import create_engine, text
from config import DB_CONFIG

def get_engine():
    url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(url)

def get_progresso_por_tipo():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tipo_dado, COUNT(*) AS total_registros
            FROM controle_carga
            GROUP BY tipo_dado
            ORDER BY tipo_dado
        """)).fetchall()
        return [{"tipo_dado": row[0], "total": row[1]} for row in result]

def get_municipios_pendentes(tipo, ano, mes):
    engine = get_engine()
    with engine.connect() as conn:
        carregados = conn.execute(text("""
            SELECT codigo_municipio FROM controle_carga
            WHERE tipo_dado = :tipo AND ano = :ano AND mes = :mes
        """), {"tipo": tipo, "ano": ano, "mes": mes}).fetchall()
        codigos_carregados = {row[0] for row in carregados}

        todos = conn.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
        return [row[0] for row in todos if row[0] not in codigos_carregados]

def get_funcoes_etl_disponiveis():
    return [
        "load_municipios",
        "load_orgaos",
        "load_receitas",
        "load_despesas",
        "load_licitacao",
        "load_prestacao_contas",
        "load_liquidacoes",
        "load_notas_empenho"
    ]