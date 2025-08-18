
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database.db_config import get_db_engine
import requests
from data_extraction.api_client import fetch_data, get_all_municipios, get_orgaos, get_agentes_publicos, get_licitacao, get_receitas, get_prestacao_contas, get_unidade_orcamentaria, get_orcamentos, get_orcamentos_receita, get_despesa_elemento_projeto, get_despesa_projeto_atividade, get_despesa_categoria_economica

# Função genérica de controle incremental
def ja_processado(session, tipo, codigo, ano, mes):
    return session.execute(text("""
        SELECT 1 FROM controle_carga
        WHERE tipo_dado = :tipo AND codigo_municipio = :codigo AND ano = :ano AND mes = :mes
    """), {"tipo": tipo, "codigo": codigo, "ano": ano, "mes": mes}).fetchone()

def registrar_processamento(session, tipo, codigo, ano, mes):
    session.execute(text("""
        INSERT INTO controle_carga (tipo_dado, codigo_municipio, ano, mes)
        VALUES (:tipo, :codigo, :ano, :mes)
        ON CONFLICT DO NOTHING
    """), {"tipo": tipo, "codigo": codigo, "ano": ano, "mes": mes})

def load_municipios():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = get_all_municipios()

    if isinstance(municipios, list) and municipios:
        print(f"[INFO] Carregando {len(municipios)} municípios.")
        for municipio in municipios:
            if isinstance(municipio, dict):
                session.execute(
                    text("INSERT INTO municipio (codigo_municipio, nome) VALUES (:codigo, :nome) ON CONFLICT (codigo_municipio) DO NOTHING"),
                    {
                        "codigo": municipio["codigo_municipio"],
                        "nome": municipio["nome_municipio"]
                    }
                )
        session.commit()

        result = session.execute(text("SELECT COUNT(*) FROM municipio")).scalar()
        print(f"[INFO] Total de municípios no banco: {result}")
    else:
        print("[ERRO] Nenhum município encontrado.")

    session.close()

# Função incremental: órgãos

def load_orgaos():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    for municipio_id in range(2, 186):
        codigo_municipio = str(municipio_id).zfill(3)
        start_year = 2023
        end_year = datetime.now().year

        for year in range(start_year, end_year + 1):
            if ja_processado(session, "orgao", codigo_municipio, year, 0):
                print(f"[SKIP] Órgãos {codigo_municipio}/{year} já processados.")
                continue

            exercicio_orcamento = f"{year}00"
            orgaos = get_orgaos(codigo_municipio, exercicio_orcamento)

            if not orgaos:
                print(f"[INFO] Nenhum órgão encontrado para município {codigo_municipio}, exercício {exercicio_orcamento}.")
                continue

            for orgao in orgaos:
                try:
                    session.execute(
                        text("""
                            INSERT INTO orgao (
                                municipio_id, exercicio_orcamento, codigo_orgao, nome_orgao,
                                codigo_tipo_unidade, cgc_orgao
                            ) VALUES (
                                (SELECT id FROM municipio WHERE codigo_municipio = :codigo_municipio),
                                :exercicio_orcamento, :codigo_orgao, :nome_orgao,
                                :codigo_tipo_unidade, :cgc_orgao
                            ) ON CONFLICT DO NOTHING
                        """),
                        {
                            "codigo_municipio": codigo_municipio,
                            "exercicio_orcamento": exercicio_orcamento,
                            "codigo_orgao": orgao["codigo_orgao"],
                            "nome_orgao": orgao["nome_orgao"],
                            "codigo_tipo_unidade": orgao["codigo_tipo_unidade"],
                            "cgc_orgao": orgao["cgc_orgao"]
                        }
                    )
                except Exception as e:
                    print(f"[ERRO] Falha ao inserir órgão {orgao['codigo_orgao']} para município {codigo_municipio}: {e}")
                    session.rollback()

            registrar_processamento(session, "orgao", codigo_municipio, year, 0)
            session.commit()
            print(f"[INFO] Dados de órgãos carregados para município {codigo_municipio}, exercício {exercicio_orcamento}.")

    session.close()
    print("[INFO] Processamento de órgãos concluído.")

def load_receitas():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    for municipio_id in range(2, 186):
        codigo_municipio = str(municipio_id).zfill(3)
        start_year = 2023
        end_year = datetime.now().year
        end_month = datetime.now().month

        for year in range(start_year, end_year + 1):
            last_month = 12 if year < end_year else end_month
            for month in range(1, last_month + 1):
                if ja_processado(session, "receita", codigo_municipio, year, month):
                    print(f"[SKIP] Receita {codigo_municipio}/{year}/{month} já processada.")
                    continue

                exercicio_orcamento = f"{year}00"
                data_referencia = f"{year}{str(month).zfill(2)}"

                try:
                    receitas = get_receitas(codigo_municipio, exercicio_orcamento, data_referencia)
                    for receita in receitas:
                        session.execute(text("""
                            INSERT INTO receita (
                                municipio_id, ano, mes, codigo_orgao, codigo_unidade, codigo_rubrica,
                                tipo_balancete, valor_previsto_orcamento, valor_arrecadado_no_mes,
                                valor_arrecadado_ate_mes, valor_anulacoes_no_mes, valor_anulacoes_ate_mes,
                                tipo_fonte, codigo_fonte
                            ) VALUES (
                                (SELECT id FROM municipio WHERE codigo_municipio = :codigo_municipio),
                                :ano, :mes, :codigo_orgao, :codigo_unidade, :codigo_rubrica,
                                :tipo_balancete, :valor_previsto_orcamento, :valor_arrecadado_no_mes,
                                :valor_arrecadado_ate_mes, :valor_anulacoes_no_mes, :valor_anulacoes_ate_mes,
                                :tipo_fonte, :codigo_fonte
                            )
                        """), {
                            "codigo_municipio": codigo_municipio,
                            "ano": year,
                            "mes": month,
                            "codigo_orgao": receita["codigo_orgao"],
                            "codigo_unidade": receita["codigo_unidade"].strip(),
                            "codigo_rubrica": receita["codigo_rubrica"],
                            "tipo_balancete": receita["tipo_balancete"],
                            "valor_previsto_orcamento": receita["valor_previsto_orcamento"],
                            "valor_arrecadado_no_mes": receita["valor_arrecadacao_no_mes"],
                            "valor_arrecadado_ate_mes": receita["valor_arrecadacao_ate_mes"],
                            "valor_anulacoes_no_mes": receita["valor_anulacoes_no_mes"],
                            "valor_anulacoes_ate_mes": receita["valor_anulacoes_ate_mes"],
                            "tipo_fonte": receita["tipo_fonte"],
                            "codigo_fonte": receita["codigo_fonte"]
                        })

                    registrar_processamento(session, "receita", codigo_municipio, year, month)
                    session.commit()
                    print(f"[INFO] Receita {codigo_municipio}/{year}/{month} carregada com sucesso.")

                except requests.RequestException as e:
                    print(f"[ERRO] Requisição falhou para {codigo_municipio}/{year}/{month}: {e}")
                except Exception as e:
                    print(f"[ERRO] Falha ao processar {codigo_municipio}/{year}/{month}: {e}")
                    session.rollback()

    session.close()

def load_despesas():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    for municipio_id in range(2, 186):
        codigo_municipio = str(municipio_id).zfill(3)
        start_year = 2023
        end_year = datetime.now().year
        end_month = datetime.now().month

        for year in range(start_year, end_year + 1):
            last_month = 12 if year < end_year else end_month
            for month in range(1, last_month + 1):
                if ja_processado(session, "despesa", codigo_municipio, year, month):
                    print(f"[SKIP] Despesa {codigo_municipio}/{year}/{month} já processada.")
                    continue

                data_referencia = f"{year}{str(month).zfill(2)}"
                exercicio_orcamento = f"{year}00"
                deslocamento = 0

                try:
                    while True:
                        response = fetch_data(
                            f"https://api-dados-abertos.tce.ce.gov.br/balancete_despesa_orcamentaria?"
                            f"codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
                            f"&data_referencia={data_referencia}&quantidade=100&deslocamento={deslocamento}"
                        )

                        if not response or "data" not in response or not response["data"].get("data"):
                            break

                        dados = response["data"]["data"]

                        for item in dados:
                            session.execute(text("""
                                INSERT INTO despesa (
                                    municipio_id, ano, mes, codigo_orgao, codigo_unidade, codigo_funcao,
                                    codigo_subfuncao, codigo_programa, codigo_projeto_atividade,
                                    numero_projeto_atividade, numero_subprojeto_atividade, codigo_elemento_despesa,
                                    tipo_balancete, valor_fixado_orcamento_bal_despesa, valor_supl_no_mes,
                                    valor_supl_ate_mes, valor_anulacoes_dotacao_no_mes, valor_empenhado_no_mes,
                                    valor_empenhado_ate_mes, valor_saldo_dotacao, valor_pago_no_mes,
                                    valor_pago_ate_mes, valor_empenhado_pagar, valor_anulacoes_dotacao_ate_mes,
                                    valor_anulacoes_empenhos_no_mes, valor_anulacoes_empenhos_ate_mes,
                                    valor_liquidado_no_mes, valor_liquidado_ate_mes,
                                    valor_estornos_liquidacao_no_mes, valor_estornos_liquidacao_ate_mes,
                                    valor_estornos_pagos_no_mes, valor_estornos_pagos_ate_mes,
                                    tipo_fonte, codigo_fonte
                                ) VALUES (
                                    (SELECT id FROM municipio WHERE codigo_municipio = :codigo_municipio),
                                    :ano, :mes, :codigo_orgao, :codigo_unidade, :codigo_funcao,
                                    :codigo_subfuncao, :codigo_programa, :codigo_projeto_atividade,
                                    :numero_projeto_atividade, :numero_subprojeto_atividade, :codigo_elemento_despesa,
                                    :tipo_balancete, :valor_fixado_orcamento_bal_despesa, :valor_supl_no_mes,
                                    :valor_supl_ate_mes, :valor_anulacoes_dotacao_no_mes, :valor_empenhado_no_mes,
                                    :valor_empenhado_ate_mes, :valor_saldo_dotacao, :valor_pago_no_mes,
                                    :valor_pago_ate_mes, :valor_empenhado_pagar, :valor_anulacoes_dotacao_ate_mes,
                                    :valor_anulacoes_empenhos_no_mes, :valor_anulacoes_empenhos_ate_mes,
                                    :valor_liquidado_no_mes, :valor_liquidado_ate_mes,
                                    :valor_estornos_liquidacao_no_mes, :valor_estornos_liquidacao_ate_mes,
                                    :valor_estornos_pagos_no_mes, :valor_estornos_pagos_ate_mes,
                                    :tipo_fonte, :codigo_fonte
                                )
                            """), {
                                "codigo_municipio": codigo_municipio,
                                "ano": year,
                                "mes": month,
                                "codigo_orgao": item.get("codigo_orgao"),
                                "codigo_unidade": item.get("codigo_unidade", "").strip(),
                                "codigo_funcao": item.get("codigo_funcao"),
                                "codigo_subfuncao": item.get("codigo_subfuncao"),
                                "codigo_programa": item.get("codigo_programa"),
                                "codigo_projeto_atividade": item.get("codigo_projeto_atividade"),
                                "numero_projeto_atividade": item.get("numero_projeto_atividade"),
                                "numero_subprojeto_atividade": item.get("numero_subprojeto_atividade"),
                                "codigo_elemento_despesa": item.get("codigo_elemento_despesa"),
                                "tipo_balancete": item.get("tipo_balancete"),
                                "valor_fixado_orcamento_bal_despesa": item.get("valor_fixado_orcamento_bal_despesa", 0),
                                "valor_supl_no_mes": item.get("valor_supl_no_mes", 0),
                                "valor_supl_ate_mes": item.get("valor_supl_ate_mes", 0),
                                "valor_anulacoes_dotacao_no_mes": item.get("valor_anulacoes_dotacao_no_mes", 0),
                                "valor_empenhado_no_mes": item.get("valor_empenhado_no_mes", 0),
                                "valor_empenhado_ate_mes": item.get("valor_empenhado_ate_mes", 0),
                                "valor_saldo_dotacao": item.get("valor_saldo_dotacao", 0),
                                "valor_pago_no_mes": item.get("valor_pago_no_mes", 0),
                                "valor_pago_ate_mes": item.get("valor_pago_ate_mes", 0),
                                "valor_empenhado_pagar": item.get("valor_empenhado_pagar", 0),
                                "valor_anulacoes_dotacao_ate_mes": item.get("valor_anulacoes_dotacao_ate_mes", 0),
                                "valor_anulacoes_empenhos_no_mes": item.get("valor_anulacoes_empenhos_no_mes", 0),
                                "valor_anulacoes_empenhos_ate_mes": item.get("valor_anulacoes_empenhos_ate_mes", 0),
                                "valor_liquidado_no_mes": item.get("valor_liquidado_no_mes", 0),
                                "valor_liquidado_ate_mes": item.get("valor_liquidado_ate_mes", 0),
                                "valor_estornos_liquidacao_no_mes": item.get("valor_estornos_liquidacao_no_mes", 0),
                                "valor_estornos_liquidacao_ate_mes": item.get("valor_estornos_liquidacao_ate_mes", 0),
                                "valor_estornos_pagos_no_mes": item.get("valor_estornos_pagos_no_mes", 0),
                                "valor_estornos_pagos_ate_mes": item.get("valor_estornos_pagos_ate_mes", 0),
                                "tipo_fonte": item.get("tipo_fonte"),
                                "codigo_fonte": item.get("codigo_fonte")
                            })

                        deslocamento += 100

                    registrar_processamento(session, "despesa", codigo_municipio, year, month)
                    session.commit()
                    print(f"[INFO] Despesa {codigo_municipio}/{year}/{month} carregada com sucesso.")

                except Exception as e:
                    print(f"[ERRO] Falha ao processar despesa {codigo_municipio}/{year}/{month}: {e}")
                    session.rollback()

    session.close()


def load_agentes_publicos():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    for municipio_id in range(2, 186):
        codigo_municipio = str(municipio_id).zfill(3)
        start_year = 2023
        end_year = datetime.now().year

        for year in range(start_year, end_year + 1):
            if ja_processado(session, "agente_publico", codigo_municipio, year, 0):
                print(f"[SKIP] Agentes públicos {codigo_municipio}/{year} já processados.")
                continue

            deslocamento = 0

            try:
                while True:
                    response = get_agentes_publicos(
                        codigo_municipio=codigo_municipio,
                        exercicio_orcamento=f"{year}00",
                        deslocamento=deslocamento,
                        quantidade=100
                    )

                    agentes = response.get("agentes", [])
                    if not agentes:
                        break

                    for agente in agentes:
                        session.execute(text("""
                            INSERT INTO agentes_publicos (
                                municipio_id, exercicio_orcamento, codigo_orgao, codigo_unidade,
                                cpf_servidor, codigo_ingresso, codigo_vinculo, codigo_expediente,
                                situacao_funcional, codigo_regime_juridico, codigo_ocupacao_cbo,
                                tipo_cargo, data_referencia_agente_publico, nome_servidor, nm_tipo_cargo
                            ) VALUES (
                                (SELECT id FROM municipio WHERE codigo_municipio = :codigo_municipio),
                                :exercicio_orcamento, :codigo_orgao, :codigo_unidade, :cpf_servidor,
                                :codigo_ingresso, :codigo_vinculo, :codigo_expediente, :situacao_funcional,
                                :codigo_regime_juridico, :codigo_ocupacao_cbo, :tipo_cargo,
                                :data_referencia_agente_publico, :nome_servidor, :nm_tipo_cargo
                            ) ON CONFLICT DO NOTHING
                        """), {
                            "codigo_municipio": codigo_municipio,
                            "exercicio_orcamento": f"{year}00",
                            "codigo_orgao": agente.get("codigo_orgao"),
                            "codigo_unidade": agente.get("codigo_unidade", "").strip(),
                            "cpf_servidor": agente.get("cpf_servidor"),
                            "codigo_ingresso": agente.get("codigo_ingresso"),
                            "codigo_vinculo": agente.get("codigo_vinculo"),
                            "codigo_expediente": agente.get("codigo_expediente"),
                            "situacao_funcional": agente.get("situacao_funcional"),
                            "codigo_regime_juridico": agente.get("codigo_regime_juridico"),
                            "codigo_ocupacao_cbo": agente.get("codigo_ocupacao_cbo"),
                            "tipo_cargo": agente.get("tipo_cargo"),
                            "data_referencia_agente_publico": agente.get("data_referencia_agente_publico"),
                            "nome_servidor": agente.get("nome_servidor", "").strip(),
                            "nm_tipo_cargo": agente.get("nm_tipo_cargo", "").strip()
                        })

                    deslocamento += 100

                registrar_processamento(session, "agente_publico", codigo_municipio, year, 0)
                session.commit()
                print(f"[INFO] Agentes públicos {codigo_municipio}/{year} carregados com sucesso.")

            except Exception as e:
                print(f"[ERRO] Falha ao processar agentes públicos {codigo_municipio}/{year}: {e}")
                session.rollback()

    session.close()

# Função incremental: licitação

def load_licitacao():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT id, codigo_municipio FROM municipio")).fetchall()

    for municipio in municipios:
        municipio_id = municipio[0]
        codigo_municipio = municipio[1]
        ano = 2023  # a API exige uma faixa, mas o controle local será por ano

        if ja_processado(session, "licitacao", codigo_municipio, ano, 0):
            print(f"[SKIP] Licitações {codigo_municipio}/{ano} já processadas.")
            continue

        try:
            licitacoes = get_licitacao(codigo_municipio)
            if not licitacoes:
                print(f"[INFO] Sem dados de licitação para município {codigo_municipio}.")
                continue

            for lic in licitacoes:
                data_realizacao = lic.get("data_realizacao_licitacao")
                ano_licitacao = int(data_realizacao.split("-")[0]) if data_realizacao else None

                session.execute(text("""
                    INSERT INTO licitacao (
                        municipio_id, ano, tipo_licitacao, modalidade, numero_licitacao,
                        descricao_objeto, valor_estimado, valor_limite_superior,
                        cpf_gestor, data_realizacao, status
                    ) VALUES (
                        :municipio_id, :ano, :tipo_licitacao, :modalidade, :numero_licitacao,
                        :descricao_objeto, :valor_estimado, :valor_limite_superior,
                        :cpf_gestor, :data_realizacao, :status
                    ) ON CONFLICT DO NOTHING
                """), {
                    "municipio_id": municipio_id,
                    "ano": ano_licitacao,
                    "tipo_licitacao": lic.get("tipo_licitacao"),
                    "modalidade": lic.get("modalidade_licitacao"),
                    "numero_licitacao": lic.get("numero_licitacao"),
                    "descricao_objeto": f"{lic.get('descricao1_objeto_licitacao', '')} {lic.get('descricao2_objeto_licitacao', '')}",
                    "valor_estimado": lic.get("valor_orcado_estimado"),
                    "valor_limite_superior": lic.get("valor_limite_superior"),
                    "cpf_gestor": lic.get("cpf_gestor"),
                    "data_realizacao": data_realizacao,
                    "status": lic.get("modalidade_processo_administrativo")
                })

            registrar_processamento(session, "licitacao", codigo_municipio, ano, 0)
            session.commit()
            print(f"[INFO] Licitações carregadas para município {codigo_municipio}.")

        except Exception as e:
            print(f"[ERRO] Falha ao carregar licitações para município {codigo_municipio}: {e}")
            session.rollback()

    session.close()


def load_prestacao_contas():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT id, codigo_municipio FROM municipio")).fetchall()

    for municipio in municipios:
        municipio_id = municipio[0]
        codigo_municipio = municipio[1]

        try:
            prestacoes = get_prestacao_contas(codigo_municipio)
            if not prestacoes:
                print(f"[INFO] Sem dados de prestação de contas para município {codigo_municipio}.")
                continue

            for prestacao in prestacoes:
                data_referencia = prestacao.get("data_referencia")
                ano = int(data_referencia[:4]) if data_referencia else None
                mes = int(data_referencia[4:6]) if data_referencia else None

                if not ano or not mes:
                    continue

                if ja_processado(session, "prestacao_contas", codigo_municipio, ano, mes):
                    print(f"[SKIP] Prestação de contas {codigo_municipio}/{ano}/{mes} já processada.")
                    continue

                session.execute(text("""
                    INSERT INTO prestacao_contas (
                        municipio_id, ano, mes, unidade_gestora, data_entrega, data_limite,
                        status_entrega, descricao_situacao
                    ) VALUES (
                        :municipio_id, :ano, :mes, :unidade_gestora, :data_entrega, :data_limite,
                        :status_entrega, :descricao_situacao
                    ) ON CONFLICT DO NOTHING
                """), {
                    "municipio_id": municipio_id,
                    "ano": ano,
                    "mes": mes,
                    "unidade_gestora": prestacao.get("nome_unidade", "Não Informado"),
                    "data_entrega": prestacao.get("data_entrega"),
                    "data_limite": prestacao.get("data_limite"),
                    "status_entrega": prestacao.get("status_situacao_entrega", "Não Informado"),
                    "descricao_situacao": prestacao.get("descricao_situacao_entrega", "Não Informado")
                })

                registrar_processamento(session, "prestacao_contas", codigo_municipio, ano, mes)

            session.commit()
            print(f"[INFO] Prestação de contas carregadas para município {codigo_municipio}.")

        except Exception as e:
            print(f"[ERRO] Falha ao carregar prestação de contas para município {codigo_municipio}: {e}")
            session.rollback()

    session.close()


def load_unidade_orcamentaria():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    anos = [2023, 2024, 2025]

    for municipio_id in range(2, 186):
        codigo_municipio = str(municipio_id).zfill(3)

        for ano in anos:
            exercicio_orcamento = f"{ano}00"
            if ja_processado(session, "unidade_orcamentaria", codigo_municipio, ano, 0):
                print(f"[SKIP] Unidade orçamentária {codigo_municipio}/{ano} já processada.")
                continue

            deslocamento = 0

            try:
                while True:
                    unidades = get_unidade_orcamentaria(codigo_municipio, exercicio_orcamento, quantidade=100, deslocamento=deslocamento)

                    if not unidades:
                        break

                    for unidade in unidades:
                        session.execute(text("""
                            INSERT INTO unidade_orcamentaria (
                                municipio_id, exercicio_orcamento, codigo_orgao, codigo_unidade,
                                codigo_tipo_unidade, nome_unidade, tipo_administracao_unidade
                            ) VALUES (
                                (SELECT id FROM municipio WHERE codigo_municipio = :codigo_municipio),
                                :exercicio_orcamento, :codigo_orgao, :codigo_unidade,
                                :codigo_tipo_unidade, :nome_unidade, :tipo_administracao_unidade
                            ) ON CONFLICT DO NOTHING
                        """), {
                            "codigo_municipio": codigo_municipio,
                            "exercicio_orcamento": unidade.get("exercicio_orcamento"),
                            "codigo_orgao": unidade.get("codigo_orgao", "").strip(),
                            "codigo_unidade": unidade.get("codigo_unidade", "").strip(),
                            "codigo_tipo_unidade": unidade.get("codigo_tipo_unidade"),
                            "nome_unidade": unidade.get("nome_unidade"),
                            "tipo_administracao_unidade": unidade.get("tipo_administracao_unidade")
                        })

                    deslocamento += 100

                registrar_processamento(session, "unidade_orcamentaria", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Unidade orçamentária {codigo_municipio}/{ano} carregada com sucesso.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar unidade orçamentária {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()

def load_orcamentos():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT id, codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        municipio_id = municipio[0]
        codigo_municipio = municipio[1]

        for ano in anos:
            if ja_processado(session, "orcamento", codigo_municipio, ano, 0):
                print(f"[SKIP] Orçamento {codigo_municipio}/{ano} já processado.")
                continue

            exercicio_orcamento = f"{ano}00"

            try:
                orcamentos = get_orcamentos(codigo_municipio, exercicio_orcamento)
                if not orcamentos:
                    print(f"[INFO] Sem orçamentos para município {codigo_municipio}, ano {ano}.")
                    continue

                for orc in orcamentos:
                    session.execute(text("""
                        INSERT INTO orcamentos (
                            municipio_id, exercicio_orcamento, numero_lei_orcamento,
                            valor_total_fixado_orcamento, numero_perc_supl_orcamento,
                            valor_total_supl_orcamento, data_envio_loa, data_aprov_loa, data_public_loa
                        ) VALUES (
                            :municipio_id, :exercicio_orcamento, :numero_lei_orcamento,
                            :valor_total_fixado_orcamento, :numero_perc_supl_orcamento,
                            :valor_total_supl_orcamento, :data_envio_loa, :data_aprov_loa, :data_public_loa
                        ) ON CONFLICT DO NOTHING
                    """), {
                        "municipio_id": municipio_id,
                        "exercicio_orcamento": orc.get("exercicio_orcamento"),
                        "numero_lei_orcamento": orc.get("nu_lei_orcamento"),
                        "valor_total_fixado_orcamento": orc.get("valor_total_fixado_orcamento"),
                        "numero_perc_supl_orcamento": orc.get("numero_perc_sup_orcamento"),
                        "valor_total_supl_orcamento": orc.get("valor_total_supl_orcamento"),
                        "data_envio_loa": orc.get("data_envio_loa"),
                        "data_aprov_loa": orc.get("data_aprov_loa"),
                        "data_public_loa": orc.get("data_public_loa")
                    })

                registrar_processamento(session, "orcamento", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Orçamentos carregados para município {codigo_municipio}/{ano}.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar orçamento para município {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()

def load_balancete_despesa_extra_orcamentaria():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT id, codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        municipio_id, codigo_municipio = municipio

        for ano in anos:
            for mes in range(1, 13):
                if ja_processado(session, "balancete_despesa_extra", codigo_municipio, ano, mes):
                    print(f"[SKIP] Balancete extra {codigo_municipio}/{ano}/{mes} já processado.")
                    continue

                exercicio_orcamento = f"{ano}00"
                data_referencia = f"{ano}{mes:02}"
                print(f"[INFO] Buscando balancete extra para {codigo_municipio} - {data_referencia}")

                try:
                    balancetes = fetch_data(
                        f"https://api-dados-abertos.tce.ce.gov.br/balancete_despesa_extra_orcamentaria?"
                        f"codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}&data_referencia={data_referencia}"
                    )

                    if not balancetes or "data" not in balancetes or not balancetes["data"]:
                        print(f"[INFO] Sem dados de balancete extra para {codigo_municipio}/{ano}/{mes}.")
                        continue

                    for b in balancetes["data"]:
                        session.execute(text("""
                            INSERT INTO balancete_despesa_extra_orcamentaria (
                                codigo_municipio, exercicio_orcamento, codigo_orgao, codigo_unidade,
                                codigo_conta_extraorcamentaria, data_referencia, tipo_balancete,
                                valor_anulacao_no_mes, valor_anulacao_ate_mes, valor_pago_no_mes, valor_pago_ate_mes
                            ) VALUES (
                                :codigo_municipio, :exercicio_orcamento, :codigo_orgao, :codigo_unidade,
                                :codigo_conta_extraorcamentaria, :data_referencia, :tipo_balancete,
                                :valor_anulacao_no_mes, :valor_anulacao_ate_mes, :valor_pago_no_mes, :valor_pago_ate_mes
                            ) ON CONFLICT DO NOTHING
                        """), b)

                    registrar_processamento(session, "balancete_despesa_extra", codigo_municipio, ano, mes)
                    session.commit()
                    print(f"[INFO] Balancete extra carregado para {codigo_municipio}/{ano}/{mes}.")

                except Exception as e:
                    print(f"[ERRO] Erro ao carregar balancete extra {codigo_municipio}/{ano}/{mes}: {e}")
                    session.rollback()

    session.close()

def load_receita_extra_orcamentaria():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT id, codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        municipio_id, codigo_municipio = municipio

        for ano in anos:
            for mes in range(1, 13):
                if ja_processado(session, "receita_extra", codigo_municipio, ano, mes):
                    print(f"[SKIP] Receita extra {codigo_municipio}/{ano}/{mes} já processada.")
                    continue

                exercicio_orcamento = f"{ano}00"
                data_referencia = f"{ano}{mes:02}"

                print(f"[INFO] Buscando receita extra para {codigo_municipio} - {data_referencia}")

                try:
                    deslocamento = 0
                    while True:
                        response = fetch_data(
                            f"https://api-dados-abertos.tce.ce.gov.br/balancete_receita_extra_orcamentaria?"
                            f"codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}&data_referencia={data_referencia}"
                            f"&quantidade=100&deslocamento={deslocamento}"
                        )

                        if not response or "data" not in response or not response["data"]:
                            break

                        for receita in response["data"]:
                            session.execute(text("""
                                INSERT INTO receita_extra_orcamentaria (
                                    codigo_municipio, exercicio_orcamento, codigo_orgao, codigo_unidade,
                                    codigo_conta_extraorcamentaria, data_referencia, tipo_balancete,
                                    valor_anulacoes_empenhos_no_mes, valor_nulacoes_dotacao_ate_mes,
                                    valor_arrecadacao_empenhos_no_mes, valor_arrecadacao_dotacao_ate_mes
                                ) VALUES (
                                    :codigo_municipio, :exercicio_orcamento, :codigo_orgao, :codigo_unidade,
                                    :codigo_conta_extraorcamentaria, :data_referencia, :tipo_balancete,
                                    :valor_anulacoes_empenhos_no_mes, :valor_nulacoes_dotacao_ate_mes,
                                    :valor_arrecadacao_empenhos_no_mes, :valor_arrecadacao_dotacao_ate_mes
                                ) ON CONFLICT DO NOTHING
                            """), receita)

                        deslocamento += 100

                    registrar_processamento(session, "receita_extra", codigo_municipio, ano, mes)
                    session.commit()
                    print(f"[INFO] Receita extra carregada para {codigo_municipio}/{ano}/{mes}.")

                except Exception as e:
                    print(f"[ERRO] Falha ao carregar receita extra {codigo_municipio}/{ano}/{mes}: {e}")
                    session.rollback()

    session.close()

def load_orcamentos_receita():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        codigo_municipio = municipio[0]

        for ano in anos:
            if ja_processado(session, "orcamento_receita", codigo_municipio, ano, 0):
                print(f"[SKIP] Orçamento Receita {codigo_municipio}/{ano} já processado.")
                continue

            exercicio_orcamento = f"{ano}00"
            print(f"[INFO] Buscando orçamento receita para {codigo_municipio}/{ano}...")

            try:
                receitas = get_orcamentos_receita(codigo_municipio, exercicio_orcamento)
                if not receitas:
                    print(f"[INFO] Nenhum dado retornado para {codigo_municipio}/{ano}.")
                    continue

                for receita in receitas:
                    session.execute(text("""
                        INSERT INTO orcamento_receita (
                            codigo_municipio, exercicio_orcamento, codigo_orgao,
                            codigo_unidade, codigo_rubrica, tipo_fonte,
                            codigo_fonte, descricao_rubrica, valor_previsto
                        ) VALUES (
                            :codigo_municipio, :exercicio_orcamento, :codigo_orgao,
                            :codigo_unidade, :codigo_rubrica, :tipo_fonte,
                            :codigo_fonte, :descricao_rubrica, :valor_previsto
                        ) ON CONFLICT DO NOTHING
                    """), receita)

                registrar_processamento(session, "orcamento_receita", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Orçamento Receita carregado para {codigo_municipio}/{ano}.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar orçamento receita {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()

def load_despesa_elemento_projeto():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        codigo_municipio = municipio[0]

        for ano in anos:
            if ja_processado(session, "despesa_elemento_projeto", codigo_municipio, ano, 0):
                print(f"[SKIP] Despesa Elemento Projeto {codigo_municipio}/{ano} já processado.")
                continue

            exercicio_orcamento = f"{ano}00"
            print(f"[INFO] Buscando despesa elemento projeto para {codigo_municipio}/{ano}...")

            try:
                dados = get_despesa_elemento_projeto(codigo_municipio, exercicio_orcamento)
                if not dados:
                    print(f"[INFO] Nenhum dado retornado para {codigo_municipio}/{ano}.")
                    continue

                for item in dados:
                    session.execute(text("""
                        INSERT INTO despesa_elemento_projeto (
                            codigo_municipio, exercicio_orcamento, codigo_orgao,
                            codigo_unidade, codigo_funcao, codigo_subfuncao,
                            codigo_programa, codigo_projeto_atividade, numero_projeto_atividade,
                            numero_subprojeto_atividade, codigo_elemento_despesa, tipo_fonte,
                            codigo_fonte, valor_atual_categoria_economica, valor_orcado_categoria_economica
                        ) VALUES (
                            :codigo_municipio, :exercicio_orcamento, :codigo_orgao,
                            :codigo_unidade, :codigo_funcao, :codigo_subfuncao,
                            :codigo_programa, :codigo_projeto_atividade, :numero_projeto_atividade,
                            :numero_subprojeto_atividade, :codigo_elemento_despesa, :tipo_fonte,
                            :codigo_fonte, :valor_atual_categoria_economica, :valor_orcado_categoria_economica
                        ) ON CONFLICT DO NOTHING
                    """), item)

                registrar_processamento(session, "despesa_elemento_projeto", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Despesa Elemento Projeto carregado para {codigo_municipio}/{ano}.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar despesa elemento projeto {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()


def load_despesa_projeto_atividade():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        codigo_municipio = municipio[0]

        for ano in anos:
            if ja_processado(session, "despesa_projeto_atividade", codigo_municipio, ano, 0):
                print(f"[SKIP] Despesa Projeto Atividade {codigo_municipio}/{ano} já processada.")
                continue

            exercicio_orcamento = f"{ano}00"
            print(f"[INFO] Buscando despesa projeto atividade para {codigo_municipio}/{ano}...")

            try:
                dados = get_despesa_projeto_atividade(codigo_municipio, exercicio_orcamento)
                if not dados:
                    print(f"[INFO] Nenhum dado retornado para {codigo_municipio}/{ano}.")
                    continue

                for item in dados:
                    session.execute(text("""
                        INSERT INTO despesa_projeto_atividade (
                            codigo_municipio, exercicio_orcamento, codigo_orgao, codigo_unidade,
                            codigo_funcao, codigo_subfuncao, codigo_programa, codigo_projeto_atividade,
                            numero_projeto_atividade, numero_subprojeto_atividade, codigo_tipo_orcamento,
                            nome_projeto_atividade, descricao_projeto_atividade, valor_total_fixado_projeto_atividade
                        ) VALUES (
                            :codigo_municipio, :exercicio_orcamento, :codigo_orgao, :codigo_unidade,
                            :codigo_funcao, :codigo_subfuncao, :codigo_programa, :codigo_projeto_atividade,
                            :numero_projeto_atividade, :numero_subprojeto_atividade, :codigo_tipo_orcamento,
                            :nome_projeto_atividade, :descricao_projeto_atividade, :valor_total_fixado_projeto_atividade
                        ) ON CONFLICT DO NOTHING
                    """), item)

                registrar_processamento(session, "despesa_projeto_atividade", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Despesa Projeto Atividade carregada para {codigo_municipio}/{ano}.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar despesa projeto atividade {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()


def load_despesa_categoria_economica():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        codigo_municipio = municipio[0]

        for ano in anos:
            if ja_processado(session, "despesa_categoria_economica", codigo_municipio, ano, 0):
                print(f"[SKIP] Despesa Categoria Econômica {codigo_municipio}/{ano} já processada.")
                continue

            exercicio_orcamento = f"{ano}00"
            print(f"[INFO] Buscando despesa categoria econômica para {codigo_municipio}/{ano}...")

            try:
                dados = get_despesa_categoria_economica(codigo_municipio, exercicio_orcamento)
                if not dados:
                    print(f"[INFO] Nenhum dado retornado para {codigo_municipio}/{ano}.")
                    continue

                for item in dados:
                    session.execute(text("""
                        INSERT INTO despesa_categoria_economica (
                            codigo_municipio, exercicio_orcamento, codigo_orgao,
                            codigo_unidade, codigo_elemento_despesa, nome_elemento_despesa,
                            valor_total_fixado
                        ) VALUES (
                            :codigo_municipio, :exercicio_orcamento, :codigo_orgao,
                            :codigo_unidade, :codigo_elemento_despesa, :nome_elemento_despesa,
                            :valor_total_fixado
                        ) ON CONFLICT DO NOTHING
                    """), item)

                registrar_processamento(session, "despesa_categoria_economica", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Despesa Categoria Econômica carregada para {codigo_municipio}/{ano}.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar despesa categoria econômica {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()

def load_liquidacoes():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        codigo_municipio = municipio[0]

        for ano in anos:
            if ja_processado(session, "liquidacoes", codigo_municipio, ano, 0):
                print(f"[SKIP] Liquidações {codigo_municipio}/{ano} já processadas.")
                continue

            exercicio_orcamento = f"{ano}00"
            deslocamento = 0
            print(f"[INFO] Buscando liquidações para {codigo_municipio}/{ano}...")

            try:
                while True:
                    liquidacoes = get_liquidacoes(codigo_municipio, exercicio_orcamento, 100, deslocamento)
                    if not liquidacoes:
                        break

                    for liquidacao in liquidacoes:
                        session.execute(text("""
                            INSERT INTO liquidacoes (
                                codigo_municipio, exercicio_orcamento, codigo_orgao, codigo_unidade,
                                data_emissao_empenho, numero_empenho, data_liquidacao, data_referencia_liquidacao,
                                nome_responsavel_liquidacao, numero_sub_empenho_liquidacao, valor_liquidado,
                                estado_de_estorno, estado_folha
                            ) VALUES (
                                :codigo_municipio, :exercicio_orcamento, :codigo_orgao, :codigo_unidade,
                                :data_emissao_empenho, :numero_empenho, :data_liquidacao, :data_referencia_liquidacao,
                                :nome_responsavel_liquidacao, :numero_sub_empenho_liquidacao, :valor_liquidado,
                                :estado_de_estorno, :estado_folha
                            ) ON CONFLICT DO NOTHING
                        """), liquidacao)
                    
                    deslocamento += 100

                registrar_processamento(session, "liquidacoes", codigo_municipio, ano, 0)
                session.commit()
                print(f"[INFO] Liquidações carregadas para {codigo_municipio}/{ano}.")

            except Exception as e:
                print(f"[ERRO] Falha ao carregar liquidações {codigo_municipio}/{ano}: {e}")
                session.rollback()

    session.close()

def load_notas_empenho():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    municipios = session.execute(text("SELECT codigo_municipio FROM municipio")).fetchall()
    anos = [2023, 2024, 2025]

    for municipio in municipios:
        codigo_municipio = municipio[0]

        for ano in anos:
            for mes in range(1, 13):
                if ja_processado(session, "notas_empenho", codigo_municipio, ano, mes):
                    print(f"[SKIP] Notas de empenho {codigo_municipio}/{ano}/{mes} já processadas.")
                    continue

                data_referencia_empenho = f"{ano}{mes:02}"
                deslocamento = 0
                print(f"[INFO] Buscando notas de empenho para {codigo_municipio}/{data_referencia_empenho}...")

                try:
                    while True:
                        # A API de notas de empenho parece precisar de um código de órgão.
                        # Vou iterar sobre os órgãos do município para o exercício.
                        orgaos = session.execute(text("SELECT codigo_orgao FROM orgao WHERE municipio_id = (SELECT id FROM municipio WHERE codigo_municipio = :codigo_municipio) AND exercicio_orcamento = :exercicio_orcamento"), {"codigo_municipio": codigo_municipio, "exercicio_orcamento": f"{ano}00"}).fetchall()
                        
                        for orgao in orgaos:
                            codigo_orgao = orgao[0]
                            notas_empenho = get_notas_empenho(codigo_municipio, data_referencia_empenho, codigo_orgao, 100, deslocamento)
                            
                            if not notas_empenho:
                                continue

                            for nota in notas_empenho:
                                session.execute(text("""
                                    INSERT INTO notas_empenho (
                                        codigo_municipio, exercicio_orcamento, codigo_orgao, codigo_unidade,
                                        data_emissao_empenho, numero_empenho, data_referencia_empenho,
                                        codigo_funcao, codigo_subfuncao, codigo_programa, codigo_projeto_atividade,
                                        numero_projeto_atividade, numero_subprojeto_atividade, codigo_elemento_despesa,
                                        modalidade_empenho, descricao_empenho, valor_anterior_saldo_dotacao,
                                        valor_empenhado, valor_atual_saldo_dotacao, tipo_processo_licitatorio,
                                        numero_documento_negociante, estado_empenho, numero_nota_anulacao,
                                        data_emissao_empenho_substituto, numero_empenho_substituto, cd_cpf_gestor,
                                        cpf_gestor_contrato, codigo_tipo_negociante, nome_negociante,
                                        endereco_negociante, fone_negociante, cep_negociante,
                                        nome_municipio_negociante, codigo_uf, tipo_fonte, codigo_fonte,
                                        codigo_contrato, data_contrato, numero_licitacao
                                    ) VALUES (
                                        :codigo_municipio, :exercicio_orcamento, :codigo_orgao, :codigo_unidade,
                                        :data_emissao_empenho, :numero_empenho, :data_referencia_empenho,
                                        :codigo_funcao, :codigo_subfuncao, :codigo_programa, :codigo_projeto_atividade,
                                        :numero_projeto_atividade, :numero_subprojeto_atividade, :codigo_elemento_despesa,
                                        :modalidade_empenho, :descricao_empenho, :valor_anterior_saldo_dotacao,
                                        :valor_empenhado, :valor_atual_saldo_dotacao, :tipo_processo_licitatorio,
                                        :numero_documento_negociante, :estado_empenho, :numero_nota_anulacao,
                                        :data_emissao_empenho_substituto, :numero_empenho_substituto, :cd_cpf_gestor,
                                        :cpf_gestor_contrato, :codigo_tipo_negociante, :nome_negociante,
                                        :endereco_negociante, :fone_negociante, :cep_negociante,
                                        :nome_municipio_negociante, :codigo_uf, :tipo_fonte, :codigo_fonte,
                                        :codigo_contrato, :data_contrato, :numero_licitacao
                                    ) ON CONFLICT DO NOTHING
                                """), nota)
                        
                        deslocamento += 100
                        if len(notas_empenho) < 100:
                            break

                    registrar_processamento(session, "notas_empenho", codigo_municipio, ano, mes)
                    session.commit()
                    print(f"[INFO] Notas de empenho carregadas para {codigo_municipio}/{data_referencia_empenho}.")

                except Exception as e:
                    print(f"[ERRO] Falha ao carregar notas de empenho {codigo_municipio}/{data_referencia_empenho}: {e}")
                    session.rollback()

    session.close()
