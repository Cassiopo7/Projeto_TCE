-- Tabela de controle para o processo de ETL
CREATE TABLE IF NOT EXISTS controle_carga (
    id SERIAL PRIMARY KEY,
    tipo_dado VARCHAR(50) NOT NULL,
    codigo_municipio VARCHAR(10) NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    UNIQUE(tipo_dado, codigo_municipio, ano, mes)
);

-- Tabela de Municípios
CREATE TABLE IF NOT EXISTS municipio (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL
);

-- Tabela de Órgãos
CREATE TABLE IF NOT EXISTS orgao (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    nome_orgao VARCHAR(255),
    codigo_tipo_unidade VARCHAR(10),
    cgc_orgao VARCHAR(20)
);

-- Tabela de Receitas
CREATE TABLE IF NOT EXISTS receita (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    ano INTEGER,
    mes INTEGER,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_rubrica VARCHAR(50),
    tipo_balancete VARCHAR(50),
    valor_previsto_orcamento NUMERIC(15, 2),
    valor_arrecadado_no_mes NUMERIC(15, 2),
    valor_arrecadado_ate_mes NUMERIC(15, 2),
    valor_anulacoes_no_mes NUMERIC(15, 2),
    valor_anulacoes_ate_mes NUMERIC(15, 2),
    tipo_fonte VARCHAR(10),
    codigo_fonte VARCHAR(10)
);

-- Tabela de Despesas
CREATE TABLE IF NOT EXISTS despesa (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    ano INTEGER,
    mes INTEGER,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_funcao VARCHAR(10),
    codigo_subfuncao VARCHAR(10),
    codigo_programa VARCHAR(10),
    codigo_projeto_atividade VARCHAR(10),
    numero_projeto_atividade VARCHAR(10),
    numero_subprojeto_atividade VARCHAR(10),
    codigo_elemento_despesa VARCHAR(20),
    tipo_balancete VARCHAR(50),
    valor_fixado_orcamento_bal_despesa NUMERIC(15, 2),
    valor_supl_no_mes NUMERIC(15, 2),
    valor_supl_ate_mes NUMERIC(15, 2),
    valor_anulacoes_dotacao_no_mes NUMERIC(15, 2),
    valor_empenhado_no_mes NUMERIC(15, 2),
    valor_empenhado_ate_mes NUMERIC(15, 2),
    valor_saldo_dotacao NUMERIC(15, 2),
    valor_pago_no_mes NUMERIC(15, 2),
    valor_pago_ate_mes NUMERIC(15, 2),
    valor_empenhado_pagar NUMERIC(15, 2),
    valor_anulacoes_dotacao_ate_mes NUMERIC(15, 2),
    valor_anulacoes_empenhos_no_mes NUMERIC(15, 2),
    valor_anulacoes_empenhos_ate_mes NUMERIC(15, 2),
    valor_liquidado_no_mes NUMERIC(15, 2),
    valor_liquidado_ate_mes NUMERIC(15, 2),
    valor_estornos_liquidacao_no_mes NUMERIC(15, 2),
    valor_estornos_liquidacao_ate_mes NUMERIC(15, 2),
    valor_estornos_pagos_no_mes NUMERIC(15, 2),
    valor_estornos_pagos_ate_mes NUMERIC(15, 2),
    tipo_fonte VARCHAR(10),
    codigo_fonte VARCHAR(10)
);

-- Tabela de Agentes Públicos
CREATE TABLE IF NOT EXISTS agentes_publicos (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    cpf_servidor VARCHAR(20),
    codigo_ingresso VARCHAR(10),
    codigo_vinculo VARCHAR(10),
    codigo_expediente VARCHAR(10),
    situacao_funcional VARCHAR(50),
    codigo_regime_juridico VARCHAR(10),
    codigo_ocupacao_cbo VARCHAR(20),
    tipo_cargo VARCHAR(50),
    data_referencia_agente_publico VARCHAR(10),
    nome_servidor VARCHAR(255),
    nm_tipo_cargo VARCHAR(100)
);

-- Tabela de Licitações
CREATE TABLE IF NOT EXISTS licitacao (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    ano INTEGER,
    tipo_licitacao VARCHAR(50),
    modalidade VARCHAR(100),
    numero_licitacao VARCHAR(50),
    descricao_objeto TEXT,
    valor_estimado NUMERIC(15, 2),
    valor_limite_superior NUMERIC(15, 2),
    cpf_gestor VARCHAR(20),
    data_realizacao DATE,
    status VARCHAR(100)
);

-- Tabela de Prestação de Contas
CREATE TABLE IF NOT EXISTS prestacao_contas (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    ano INTEGER,
    mes INTEGER,
    unidade_gestora VARCHAR(255),
    data_entrega DATE,
    data_limite DATE,
    status_entrega VARCHAR(100),
    descricao_situacao TEXT
);

-- Tabela de Unidades Orçamentárias
CREATE TABLE IF NOT EXISTS unidade_orcamentaria (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_tipo_unidade VARCHAR(10),
    nome_unidade VARCHAR(255),
    tipo_administracao_unidade VARCHAR(100)
);

-- Tabela de Orçamentos
CREATE TABLE IF NOT EXISTS orcamentos (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipio(id),
    exercicio_orcamento VARCHAR(10),
    numero_lei_orcamento VARCHAR(50),
    valor_total_fixado_orcamento NUMERIC(15, 2),
    numero_perc_supl_orcamento NUMERIC(5, 2),
    valor_total_supl_orcamento NUMERIC(15, 2),
    data_envio_loa DATE,
    data_aprov_loa DATE,
    data_public_loa DATE
);

-- Tabela de Balancete de Despesa Extra Orçamentária
CREATE TABLE IF NOT EXISTS balancete_despesa_extra_orcamentaria (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_conta_extraorcamentaria VARCHAR(50),
    data_referencia VARCHAR(10),
    tipo_balancete VARCHAR(50),
    valor_anulacao_no_mes NUMERIC(15, 2),
    valor_anulacao_ate_mes NUMERIC(15, 2),
    valor_pago_no_mes NUMERIC(15, 2),
    valor_pago_ate_mes NUMERIC(15, 2)
);

-- Tabela de Receita Extra Orçamentária
CREATE TABLE IF NOT EXISTS receita_extra_orcamentaria (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_conta_extraorcamentaria VARCHAR(50),
    data_referencia VARCHAR(10),
    tipo_balancete VARCHAR(50),
    valor_anulacoes_empenhos_no_mes NUMERIC(15, 2),
    valor_nulacoes_dotacao_ate_mes NUMERIC(15, 2),
    valor_arrecadacao_empenhos_no_mes NUMERIC(15, 2),
    valor_arrecadacao_dotacao_ate_mes NUMERIC(15, 2)
);

-- Tabela de Orçamento de Receita
CREATE TABLE IF NOT EXISTS orcamento_receita (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_rubrica VARCHAR(50),
    tipo_fonte VARCHAR(10),
    codigo_fonte VARCHAR(10),
    descricao_rubrica TEXT,
    valor_previsto NUMERIC(15, 2)
);

-- Tabela de Despesa por Elemento de Projeto
CREATE TABLE IF NOT EXISTS despesa_elemento_projeto (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_funcao VARCHAR(10),
    codigo_subfuncao VARCHAR(10),
    codigo_programa VARCHAR(10),
    codigo_projeto_atividade VARCHAR(10),
    numero_projeto_atividade VARCHAR(10),
    numero_subprojeto_atividade VARCHAR(10),
    codigo_elemento_despesa VARCHAR(20),
    tipo_fonte VARCHAR(10),
    codigo_fonte VARCHAR(10),
    valor_atual_categoria_economica NUMERIC(15, 2),
    valor_orcado_categoria_economica NUMERIC(15, 2)
);

-- Tabela de Despesa por Projeto e Atividade
CREATE TABLE IF NOT EXISTS despesa_projeto_atividade (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_funcao VARCHAR(10),
    codigo_subfuncao VARCHAR(10),
    codigo_programa VARCHAR(10),
    codigo_projeto_atividade VARCHAR(10),
    numero_projeto_atividade VARCHAR(10),
    numero_subprojeto_atividade VARCHAR(10),
    codigo_tipo_orcamento VARCHAR(10),
    nome_projeto_atividade VARCHAR(255),
    descricao_projeto_atividade TEXT,
    valor_total_fixado_projeto_atividade NUMERIC(15, 2)
);

-- Tabela de Despesa por Categoria Econômica
CREATE TABLE IF NOT EXISTS despesa_categoria_economica (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento VARCHAR(10),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_elemento_despesa VARCHAR(20),
    nome_elemento_despesa VARCHAR(255),
    valor_total_fixado NUMERIC(15, 2)
);

-- Tabela de Liquidações
CREATE TABLE IF NOT EXISTS liquidacoes (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10),
    exercicio_orcamento INTEGER,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    data_emissao_empenho TIMESTAMP,
    numero_empenho VARCHAR(50),
    data_liquidacao TIMESTAMP,
    data_referencia_liquidacao INTEGER,
    nome_responsavel_liquidacao VARCHAR(255),
    numero_sub_empenho_liquidacao VARCHAR(50),
    valor_liquidado NUMERIC(15, 2),
    estado_de_estorno INTEGER,
    estado_folha INTEGER
);

-- Tabela de Notas de Empenho
CREATE TABLE IF NOT EXISTS notas_empenho (
    id SERIAL PRIMARY KEY,
    codigo_municipio INTEGER,
    exercicio_orcamento INTEGER,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    data_emissao_empenho TIMESTAMP,
    numero_empenho VARCHAR(50),
    data_referencia_empenho INTEGER,
    codigo_funcao VARCHAR(10),
    codigo_subfuncao VARCHAR(10),
    codigo_programa VARCHAR(10),
    codigo_projeto_atividade VARCHAR(10),
    numero_projeto_atividade VARCHAR(10),
    numero_subprojeto_atividade VARCHAR(10),
    codigo_elemento_despesa VARCHAR(20),
    modalidade_empenho VARCHAR(50),
    descricao_empenho TEXT,
    valor_anterior_saldo_dotacao NUMERIC(15, 2),
    valor_empenhado NUMERIC(15, 2),
    valor_atual_saldo_dotacao NUMERIC(15, 2),
    tipo_processo_licitatorio VARCHAR(50),
    numero_documento_negociante VARCHAR(20),
    estado_empenho VARCHAR(50),
    numero_nota_anulacao VARCHAR(50),
    data_emissao_empenho_substituto TIMESTAMP,
    numero_empenho_substituto VARCHAR(50),
    cd_cpf_gestor VARCHAR(20),
    cpf_gestor_contrato VARCHAR(20),
    codigo_tipo_negociante VARCHAR(10),
    nome_negociante VARCHAR(255),
    endereco_negociante VARCHAR(255),
    fone_negociante VARCHAR(20),
    cep_negociante VARCHAR(10),
    nome_municipio_negociante VARCHAR(100),
    codigo_uf VARCHAR(2),
    tipo_fonte VARCHAR(10),
    codigo_fonte VARCHAR(10),
    codigo_contrato VARCHAR(50),
    data_contrato TIMESTAMP,
    numero_licitacao VARCHAR(50)
);