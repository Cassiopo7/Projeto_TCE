CREATE TABLE IF NOT EXISTS municipio (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(10) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS orgao (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER NOT NULL,
    exercicio_orcamento VARCHAR(6) NOT NULL,
    codigo_orgao VARCHAR(10) NOT NULL,
    nome_orgao VARCHAR(255) NOT NULL,
    codigo_tipo_unidade VARCHAR(5),
    cgc_orgao VARCHAR(20),
    CONSTRAINT fk_municipio FOREIGN KEY (municipio_id) REFERENCES municipio (id)
);


CREATE TABLE IF NOT EXISTS receita (
    id SERIAL PRIMARY KEY,
    municipio_id INT REFERENCES municipio(id),
    ano INT,
    mes INT,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_rubrica VARCHAR(20),
    tipo_balancete VARCHAR(2),
    valor_previsto_orcamento NUMERIC,
    valor_arrecadado_no_mes NUMERIC,
    valor_arrecadado_ate_mes NUMERIC,
    valor_anulacoes_no_mes NUMERIC,
    valor_anulacoes_ate_mes NUMERIC,
    tipo_fonte VARCHAR(5),
    codigo_fonte VARCHAR(20)
);


CREATE TABLE IF NOT EXISTS despesa (
    id SERIAL PRIMARY KEY,
    municipio_id INT REFERENCES municipio(id),
    ano INT,
    mes INT,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_funcao VARCHAR(10),
    codigo_subfuncao VARCHAR(10),
    codigo_programa VARCHAR(10),
    codigo_projeto_atividade VARCHAR(10),
    numero_projeto_atividade VARCHAR(10),
    numero_subprojeto_atividade VARCHAR(10),
    codigo_elemento_despesa VARCHAR(20),
    tipo_balancete VARCHAR(5),
    valor_fixado_orcamento_bal_despesa NUMERIC,
    valor_supl_no_mes NUMERIC,
    valor_supl_ate_mes NUMERIC,
    valor_anulacoes_dotacao_no_mes NUMERIC,
    valor_empenhado_no_mes NUMERIC,
    valor_empenhado_ate_mes NUMERIC,
    valor_saldo_dotacao NUMERIC,
    valor_pago_no_mes NUMERIC,
    valor_pago_ate_mes NUMERIC,
    valor_empenhado_pagar NUMERIC,
    valor_anulacoes_dotacao_ate_mes NUMERIC,
    valor_anulacoes_empenhos_no_mes NUMERIC,
    valor_anulacoes_empenhos_ate_mes NUMERIC,
    valor_liquidado_no_mes NUMERIC,
    valor_liquidado_ate_mes NUMERIC,
    valor_estornos_liquidacao_no_mes NUMERIC,
    valor_estornos_liquidacao_ate_mes NUMERIC,
    valor_estornos_pagos_no_mes NUMERIC,
    valor_estornos_pagos_ate_mes NUMERIC,
    tipo_fonte VARCHAR(10),
    codigo_fonte VARCHAR(20)
);


CREATE TABLE IF NOT EXISTS agentes_publicos (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER NOT NULL,
    exercicio_orcamento VARCHAR(6) NOT NULL,
    codigo_orgao VARCHAR(10) NOT NULL,
    codigo_unidade VARCHAR(10),
    cpf_servidor VARCHAR(15),
    codigo_ingresso VARCHAR(5),
    codigo_vinculo VARCHAR(5),
    codigo_expediente VARCHAR(5),
    situacao_funcional VARCHAR(5),
    codigo_regime_juridico VARCHAR(5),
    codigo_ocupacao_cbo VARCHAR(10),
    tipo_cargo VARCHAR(5),
    data_referencia_agente_publico VARCHAR(6),
    nome_servidor VARCHAR(255),
    nm_tipo_cargo VARCHAR(100),
    CONSTRAINT fk_municipio FOREIGN KEY (municipio_id) REFERENCES municipio (id)
);


CREATE TABLE IF NOT EXISTS licitacao (
    id SERIAL PRIMARY KEY,
    municipio_id INT REFERENCES municipio(id),
    ano INT,
    tipo_licitacao VARCHAR(50),
    modalidade VARCHAR(50),
    numero_licitacao VARCHAR(50),
    descricao_objeto TEXT,
    valor_estimado NUMERIC,
    valor_limite_superior NUMERIC,
    cpf_gestor VARCHAR(15),
    data_realizacao DATE,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS prestacao_contas (
    id SERIAL PRIMARY KEY,
    municipio_id INT REFERENCES municipio(id),
    ano INT,
    mes INT,
    unidade_gestora VARCHAR(50),
    data_entrega DATE,
    data_limite DATE,
    status_entrega VARCHAR(50),
    descricao_situacao TEXT
);

CREATE TABLE IF NOT EXISTS unidade_orcamentaria (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER NOT NULL,
    exercicio_orcamento INTEGER NOT NULL,
    codigo_orgao VARCHAR(10) NOT NULL,
    codigo_unidade VARCHAR(10) NOT NULL,
    codigo_tipo_unidade VARCHAR(10),
    nome_unidade VARCHAR(255),
    tipo_administracao_unidade CHAR(1),
    CONSTRAINT unidade_orcamentaria_unique UNIQUE (
        municipio_id, exercicio_orcamento, codigo_orgao, codigo_unidade
    ),
    CONSTRAINT fk_municipio FOREIGN KEY (municipio_id) REFERENCES municipio (id)
);

CREATE TABLE IF NOT EXISTS orcamentos (
    id SERIAL PRIMARY KEY,
    municipio_id INT REFERENCES municipio(id),
    exercicio_orcamento INT NOT NULL,
    numero_lei_orcamento VARCHAR(20),
    valor_total_fixado_orcamento NUMERIC,
    numero_perc_supl_orcamento INT,
    valor_total_supl_orcamento NUMERIC,
    data_envio_loa TIMESTAMP,
    data_aprov_loa TIMESTAMP,
    data_public_loa TIMESTAMP
);

CREATE TABLE IF NOT EXISTS balancete_despesa_extra_orcamentaria (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(3) NOT NULL,
    exercicio_orcamento VARCHAR(6) NOT NULL,
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_conta_extraorcamentaria BIGINT NOT NULL,
    data_referencia VARCHAR(6) NOT NULL,
    tipo_balancete CHAR(1),
    valor_anulacao_no_mes NUMERIC,
    valor_anulacao_ate_mes NUMERIC,
    valor_pago_no_mes NUMERIC,
    valor_pago_ate_mes NUMERIC
);

CREATE TABLE IF NOT EXISTS receita_extra_orcamentaria (
    id SERIAL PRIMARY KEY,
    codigo_municipio VARCHAR(5),
    exercicio_orcamento VARCHAR(6),
    codigo_orgao VARCHAR(10),
    codigo_unidade VARCHAR(10),
    codigo_conta_extraorcamentaria VARCHAR(20),
    data_referencia VARCHAR(6),
    tipo_balancete CHAR(1),
    valor_anulacoes_empenhos_no_mes NUMERIC,
    valor_nulacoes_dotacao_ate_mes NUMERIC,
    valor_arrecadacao_empenhos_no_mes NUMERIC,
    valor_arrecadacao_dotacao_ate_mes NUMERIC
);