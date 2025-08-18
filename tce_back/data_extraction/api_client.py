# api_client.py
import requests
from config import API_BASE_URL
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException, SSLError
import logging

def fetch_data(url):
    """Faz a requisição à API e retorna os dados."""
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        connect=5,
        read=5
    )
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        print(f"[INFO] Fazendo requisição para: {url}")
        response = session.get(url, verify=False, timeout=30)  # Desabilitando SSL por enquanto
        response.raise_for_status()  # Levanta exceção para qualquer status de erro HTTP
        data = response.json()  # Processa a resposta JSON

        # Verifica se os dados retornados são válidos
        if not data:
            print(f"[WARNING] Nenhum dado retornado de: {url}")
        else:
            print(f"[INFO] Dados retornados com sucesso de: {url}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Falha na requisição para: {url} - {e}")
        logging.error(f"Falha na requisição para: {url} - {e}")
        return None

    except ValueError as e:
        print(f"[ERROR] Erro ao decodificar o JSON da resposta: {e}")
        logging.error(f"Erro ao decodificar JSON da resposta para {url}: {e}")
        return None

def get_all_municipios():
    """Obtém os dados de municípios."""
    municipios = fetch_data("https://api-dados-abertos.tce.ce.gov.br/municipios")
    
    # Caso a resposta seja None (erro de requisição), retorna uma lista vazia
    if municipios is None:
        print("[ERROR] Não foi possível carregar os dados dos municípios.")
        return []
    
    # Verificar se a resposta é um dicionário e contém a chave 'data'
    if isinstance(municipios, dict) and "data" in municipios:
        return municipios["data"]
    
    # Caso a resposta seja uma lista, retorna diretamente a lista
    elif isinstance(municipios, list):
        print("[INFO] A resposta é uma lista, retornando como está.")
        return municipios
    
    # Caso a resposta seja inesperada, retorna uma lista vazia
    else:
        print("[ERROR] Estrutura de resposta inesperada.")
        return []

def get_orgaos(codigo_municipio, exercicio_orcamento):
    """Obtém dados de órgãos para um município e exercício orçamentário."""
    endpoint = f"https://api-dados-abertos.tce.ce.gov.br/orgaos?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
    response = fetch_data(endpoint)
    return response["data"] if response and "data" in response else []

def get_receitas(codigo_municipio, exercicio_orcamento, data_referencia):
    """Obtém dados de receitas orçamentárias de um município."""
    endpoint = f"balancete_receita_orcamentaria?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}&data_referencia={data_referencia}"
    response = fetch_data(f"{API_BASE_URL}{endpoint}")
    return response.get("data", []) if response else []

def get_despesas(codigo_municipio, exercicio_orcamento, data_referencia, deslocamento=0, quantidade=100):
    """Obtém dados de despesas orçamentárias de um município."""
    
    endpoint = (
        f"https://api-dados-abertos.tce.ce.gov.br/balancete_despesa_orcamentaria?"
        f"codigo_municipio={codigo_municipio}&"
        f"exercicio_orcamento={exercicio_orcamento}&"
        f"data_referencia={data_referencia}&"
        f"quantidade={quantidade}&"
        f"deslocamento={deslocamento}"
    )
    response = fetch_data(endpoint)
    return response

def get_agentes_publicos(codigo_municipio, exercicio_orcamento, deslocamento=0, quantidade=100):
    """Obtém dados de agentes públicos de um município."""
    endpoint = f"agentes_publicos?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}&quantidade={quantidade}&deslocamento={deslocamento}"
    session = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(f"{API_BASE_URL}{endpoint}", timeout=10, verify=False)

        response.raise_for_status()

        response_json = response.json()

        if isinstance(response_json, dict) and "data" in response_json:
            data_section = response_json["data"]
            if isinstance(data_section, dict) and "data" in data_section:
                agentes = data_section["data"]
                total = data_section.get("total", len(agentes))
                print(f"[INFO] {len(agentes)} agentes públicos encontrados. Total esperado: {total}")
                return {"agentes": agentes, "total": total}
            elif isinstance(data_section, list):
                print(f"[INFO] Dados retornados em formato de lista.")
                return {"agentes": data_section, "total": len(data_section)}
            else:
                print(f"[WARNING] Estrutura inesperada de 'data': {data_section}")
                return {"agentes": [], "total": 0}
        elif isinstance(response_json, list):
            print(f"[WARNING] Retorno inesperado em formato de lista: {response_json}")
            return {"agentes": response_json, "total": len(response_json)}
        else:
            print(f"[ERROR] Estrutura de resposta não esperada: {type(response_json)}")
            return {"agentes": [], "total": 0}

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Falha na requisição: {e}")
        logging.error(f"Falha na requisição: {e}")
        return {"agentes": [], "total": 0}

    except ValueError as e:
        print(f"[ERROR] Erro ao decodificar JSON: {e}")
        logging.error(f"Erro ao decodificar JSON: {e}")
        return {"agentes": [], "total": 0}

    except Exception as e:
        print(f"[ERROR] Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
        return {"agentes": [], "total": 0}

def get_licitacao(codigo_municipio, data_inicio="2023-01-01", data_fim="2025-03-30"):
    """Obtém dados de licitações para um município."""
    endpoint = f"licitacoes?codigo_municipio={codigo_municipio}&data_realizacao_autuacao_licitacao={data_inicio}_{data_fim}"
    response = fetch_data(f"{API_BASE_URL}{endpoint}")
    return response.get("data", []) if response else []

def get_prestacao_contas(codigo_municipio):
    """Obtém dados de prestação de contas para um município."""
    endpoint = f"https://api-dados-abertos.tce.ce.gov.br/situacao-remessa?codigo_municipio={codigo_municipio}"
    response = fetch_data(endpoint)
    return response.get("data", []) if response else []

def get_unidade_orcamentaria(codigo_municipio, exercicio_orcamento, quantidade=100, deslocamento=0):
    """Obtém dados de unidades orçamentárias para um município."""
    endpoint = (
        f"https://api-dados-abertos.tce.ce.gov.br/unidades_orcamentarias?"
        f"codigo_municipio={codigo_municipio}&"
        f"exercicio_orcamento={exercicio_orcamento}&"
        f"quantidade={quantidade}&"
        f"deslocamento={deslocamento}"
    )
    response = fetch_data(endpoint)
    return response.get("data", []) if response else []

def get_orcamentos(codigo_municipio, exercicio_orcamento):
    """Obtém dados de orçamentos para um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/dados_orcamentos?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []

def get_balancete_despesa_extra_orcamentaria(codigo_municipio, exercicio_orcamento, data_referencia):
    """Obtém dados de balancetes de despesa extra orçamentária."""
    url = f"https://api-dados-abertos.tce.ce.gov.br/balancete_despesa_extra_orcamentaria"
    params = {
        "codigo_municipio": codigo_municipio,
        "exercicio_orcamento": exercicio_orcamento,
        "data_referencia": data_referencia
    }
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[ERROR] Falha na requisição para {url}: {e}")
        return []

def get_receita_extra_orcamentaria(codigo_municipio, exercicio_orcamento, data_referencia, quantidade=100, deslocamento=0):
    """Obtém dados de receita extra orçamentária."""
    base_url = "https://api-dados-abertos.tce.ce.gov.br/balancete_receita_extra_orcamentaria"
    params = {
        "codigo_municipio": codigo_municipio,
        "exercicio_orcamento": exercicio_orcamento,
        "data_referencia": data_referencia,
        "quantidade": quantidade,
        "deslocamento": deslocamento
    }
    try:
        response = requests.get(base_url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.RequestException as e:
        print(f"[ERROR] Falha ao buscar dados de receita extra orçamentária: {e}")
        return []

# NOVOS

def get_orcamentos_receita(codigo_municipio, exercicio_orcamento):
    """Obtém dados de orçamentos de receita para um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/orcamento_receita?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []

def get_despesa_elemento_projeto(codigo_municipio, exercicio_orcamento):
    """Obtém dados de despesas por elemento de projeto para um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/despesa_elemento_projeto?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []

def get_despesa_projeto_atividade(codigo_municipio, exercicio_orcamento):
    """Obtém dados de despesas por projeto e atividade para um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/despesa_projeto_atividade?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []

def get_despesa_categoria_economica(codigo_municipio, exercicio_orcamento):
    """Obtém dados de despesas por categoria econômica para um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/despesa_categoria_economica?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []

def get_liquidacoes(codigo_municipio, exercicio_orcamento, quantidade, deslocamento):
    """Obtém dados de liquidações de despesas de um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/liquidacoes?codigo_municipio={codigo_municipio}&exercicio_orcamento={exercicio_orcamento}&quantidade={quantidade}&deslocamento={deslocamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []

def get_notas_empenho(codigo_municipio, data_referencia_empenho, codigo_orgao, quantidade, deslocamento):
    """Obtém dados de notas de empenho de um município."""
    try:
        endpoint = f"https://api-dados-abertos.tce.ce.gov.br/notas_empenhos?codigo_municipio={codigo_municipio}&data_referencia_empenho={data_referencia_empenho}&codigo_orgao={codigo_orgao}&quantidade={quantidade}&deslocamento={deslocamento}"
        response = fetch_data(endpoint)
        return response.get("data", []) if response else []
    except Exception as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return []
