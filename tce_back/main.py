
# main.py
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from database.db_setup import setup_database
from database.db_config import get_db_engine
from data_extraction.data_loader import load_municipios, load_receitas, load_despesas, load_agentes_publicos, load_licitacao, load_prestacao_contas, load_orgaos, load_unidade_orcamentaria, load_orcamentos, load_balancete_despesa_extra_orcamentaria, load_receita_extra_orcamentaria, load_orcamentos_receita, load_despesa_elemento_projeto, load_despesa_projeto_atividade, load_despesa_categoria_economica, load_liquidacoes, load_notas_empenho
from sqlalchemy.orm import sessionmaker

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("[INFO] Configurando o banco de dados...")
    setup_database()

    # Cria a conexão com o banco de dados
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    
    print("[INFO] Carregando dados de municípios...")
    load_municipios()

    print("[INFO] Carregando dados de órgãos...")
    load_orgaos() 
    
    print("[INFO] Carregando dados de receitas...")
    load_receitas()
    
    print("[INFO] Carregando dados de despesas...")
    load_despesas()
    
    print("[INFO] Carregando dados de agentes públicos...")
    load_agentes_publicos()

    print("[INFO] Carregando dados de licitações...")
    load_licitacao()
    
    print("[INFO] Carregando dados de prestação de contas...")
    load_prestacao_contas()
    
    print("[INFO] Carregando dados unidade orcamentaria...")
    load_unidade_orcamentaria()

    print("[INFO] Carregando dados de orcamentos...")
    load_orcamentos()

    print("[INFO] Carregando dados de despesa extra orcamentaria...")
    load_balancete_despesa_extra_orcamentaria()

    print("[INFO] Carregando dados de receita extra orcamentaria...")
    load_receita_extra_orcamentaria()

    print("[INFO] Carregando dados de orcamentos receitas...")
    load_orcamentos_receita()

    print("[INFO] Carregando dados de elementos dos projetos...")
    load_despesa_elemento_projeto()

    print("[INFO] Carregando dados de despesa projeto atividade...")
    load_despesa_projeto_atividade()

    print("[INFO] Carregando dados de despesa categoria economia...")
    load_despesa_categoria_economica()

    print("[INFO] Carregando dados de liquidacoes...")
    load_liquidacoes()

    print("[INFO] Carregando dados de notas de empenho...")
    load_notas_empenho()

    print("[INFO] Processo concluído com sucesso!")

if __name__ == "__main__":
    main()


