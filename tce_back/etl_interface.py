from sqlalchemy import create_engine, text
from config import DB_CONFIG, API_BASE_URL
import requests

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


def get_total_municipios():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM municipio")).fetchone()
        return int(result[0]) if result and result[0] is not None else 0


def get_contagem_carregada_por_periodo(tipo: str, ano: int, mes: int) -> int:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT COUNT(DISTINCT codigo_municipio)
                FROM controle_carga
                WHERE tipo_dado = :tipo AND ano = :ano AND mes = :mes
                """
            ),
            {"tipo": tipo, "ano": ano, "mes": mes},
        ).fetchone()
        return int(result[0]) if result and result[0] is not None else 0


def get_progresso_por_periodo(tipo: str, ano: int, mes: int):
    total = get_total_municipios()
    carregados = get_contagem_carregada_por_periodo(tipo, ano, mes)
    restante = max(total - carregados, 0)
    pct = (carregados / total * 100.0) if total else 0.0
    return {
        "total_municipios": total,
        "carregados": carregados,
        "restante": restante,
        "percentual": pct,
    }


def ping_db() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def ping_api(timeout: float = 3.0) -> bool:
    try:
        resp = requests.get(API_BASE_URL, timeout=timeout)
        return resp.status_code < 500
    except Exception:
        return False


def get_progresso_tipos_no_periodo(ano: int, mes: int):
    """
    Retorna contagem por tipo para o período informado (distinct municipios por tipo).
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT tipo_dado, COUNT(DISTINCT codigo_municipio) AS municipios_carregados
                FROM controle_carga
                WHERE ano = :ano AND mes = :mes
                GROUP BY tipo_dado
                ORDER BY tipo_dado
                """
            ),
            {"ano": ano, "mes": mes},
        ).fetchall()
        return [{"tipo_dado": r[0], "municipios": int(r[1])} for r in result]


def get_ultima_execucao_por_tipo():
    """
    Retorna a última execução por tipo com base em uma coluna de timestamp em controle_carga.
    Detecta dinamicamente a coluna entre nomes comuns ou qualquer coluna timestamp.
    """
    engine = get_engine()
    with engine.connect() as conn:
        # Tentar nomes conhecidos primeiro
        candidatos = [
            "updated_at",
            "created_at",
            "processado_em",
            "executado_em",
            "data_execucao",
        ]
        col_encontrada = None
        for nome in candidatos:
            r = conn.execute(
                text(
                    """
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'controle_carga' AND column_name = :c
                    """
                ),
                {"c": nome},
            ).fetchone()
            if r:
                col_encontrada = nome
                break

        # Se não encontrou, pegar qualquer coluna timestamp
        if not col_encontrada:
            r = conn.execute(
                text(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'controle_carga' 
                      AND data_type LIKE 'timestamp%'
                    LIMIT 1
                    """
                )
            ).fetchone()
            if r:
                col_encontrada = r[0]

        if not col_encontrada:
            return []

        result = conn.execute(
            text(
                f"""
                SELECT tipo_dado, MAX({col_encontrada}) AS ultima
                FROM controle_carga
                GROUP BY tipo_dado
                ORDER BY tipo_dado
                """
            )
        ).fetchall()
        return [
            {"tipo_dado": row[0], "ultima_execucao": row[1].isoformat() if row[1] else None}
            for row in result
        ]