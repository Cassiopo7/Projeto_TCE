CREATE TABLE forma_ingresso_servico_publico (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL
);

INSERT INTO forma_ingresso_servico_publico (codigo, descricao) VALUES
('C', 'Nomeação de Cargo Efetivo'),
('M', 'Admissão em Emprego Público'),
('N', 'Nomeação de Cargo Comissionado'),
('T', 'Contratação por Tempo Determinado'),
('R', 'Regime Especial'),
('G', 'Estágio ou Bolsa'),
('E', 'Eleição'),
('P', 'Beneficiário de Pensão'),
('V', 'Convênio'),
('S', 'Cargo Político Administrativo');

CREATE TABLE tipo_relacao_servico_publico (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL
);

INSERT INTO tipo_relacao_servico_publico (codigo, descricao) VALUES
('J', 'Cargo Efetivo'),
('M', 'Emprego Público'),
('E', 'Cargo Comissionado'),
('L', 'Cargo Eletivo'),
('F', 'Estagiário ou Bolsista'),
('H', 'Prestação de Serviço (contratos)'),
('I', 'Regime Especial'),
('P', 'Pensionista'),
('V', 'Conveniado'),
('S', 'Cargo Político Administrativo'),
('A', 'Cargo Efetivo – Atividade Adicional'),
('B', 'Emprego Público – Atividade Adicional'),
('C', 'Prestação de Serviço (contratos) – Atividade Adicional'),
('D', 'Regime Especial – Atividade Adicional');


CREATE TABLE situacao_funcional (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL
);


INSERT INTO situacao_funcional (codigo, descricao) VALUES
('1', 'Ativo'),
('2', 'Inativo'),
('3', 'Pensionista'),
('4', 'Em Disponibilidade'),
('5', 'À Disposição'),
('6', 'Ex-Segurado'),
('7', 'Ex-Agente Público'),
('8', 'Ex-Agente Político'),
('9', 'Disponibilizado por Convênio');



CREATE VIEW vw_detalhes_agentes_publicos AS
SELECT 
    m.codigo_municipio AS codigo_municipio,
    ap.exercicio_orcamento,
    o.nome_orgao AS orgao,
    fi.descricao AS ingresso,
    tr.descricao AS vinculo,
    sf.descricao AS status,
    ap.nome_servidor,
    ap.cpf_servidor,
    ap.nm_tipo_cargo
FROM 
    agentes_publicos ap
JOIN 
    municipio m ON ap.municipio_id = m.id
JOIN 
    orgao o ON ap.codigo_orgao = o.codigo_orgao AND ap.municipio_id = o.municipio_id
LEFT JOIN 
    forma_ingresso_servico_publico fi ON ap.codigo_ingresso = fi.codigo
LEFT JOIN 
    tipo_relacao_servico_publico tr ON ap.codigo_vinculo = tr.codigo
LEFT JOIN 
    situacao_funcional sf ON ap.situacao_funcional = sf.codigo;

CREATE OR REPLACE VIEW receita_detalhada AS
SELECT
    r.municipio_id,
    r.ano,
    r.mes,
    r.codigo_orgao,
    o.nome_orgao,
    r.codigo_unidade,
    u.nome_unidade,
    r.codigo_rubrica,
    r.tipo_balancete,
    CASE
        WHEN r.tipo_balancete = 'C' THEN 'Balancete Consolidado'
        WHEN r.tipo_balancete = 'P' THEN 'Balancete de Unidades Gestoras geridas pelo Prefeito'
        WHEN r.tipo_balancete = 'G' THEN 'Balancetes de Outras Unidades Gestoras'
        ELSE 'Não Definido'
    END AS descricao_balancete,
    r.valor_previsto_orcamento,
    r.valor_arrecadado_no_mes,
    r.valor_arrecadado_ate_mes,
    r.valor_anulacoes_no_mes,
    r.valor_anulacoes_ate_mes,
    r.tipo_fonte,
    CASE
        WHEN r.tipo_fonte = '1' THEN 'Recursos do Exercício Corrente'
        WHEN r.tipo_fonte = '2' THEN 'Recursos de Exercícios Anteriores'
        WHEN r.tipo_fonte = '9' THEN 'Recursos Condicionados'
        ELSE 'Não Definido'
    END AS descricao_tipo_fonte,
    r.codigo_fonte
FROM
    receita r
LEFT JOIN orgao o
    ON r.municipio_id = o.municipio_id
    AND r.codigo_orgao = o.codigo_orgao
LEFT JOIN unidade_orcamentaria u
    ON r.municipio_id = u.municipio_id
    AND r.codigo_orgao = u.codigo_orgao
    AND r.codigo_unidade = u.codigo_unidade
    AND r.ano = u.exercicio_orcamento;

CREATE OR REPLACE VIEW despesa_detalhada AS
SELECT
    d.municipio_id,
    d.ano,
    d.mes,
    d.codigo_orgao,
    o.nome_orgao,
    d.codigo_unidade,
    u.nome_unidade,
    d.codigo_funcao,
    d.codigo_subfuncao,
    d.codigo_programa,
    d.codigo_projeto_atividade,
    d.numero_projeto_atividade,
    d.numero_subprojeto_atividade,
    d.codigo_elemento_despesa,
    d.tipo_balancete,
    CASE
        WHEN d.tipo_balancete = 'C' THEN 'Balancete Consolidado'
        WHEN d.tipo_balancete = 'P' THEN 'Balancete de Unidades Gestoras geridas pelo Prefeito'
        WHEN d.tipo_balancete = 'G' THEN 'Balancetes de Outras Unidades Gestoras'
        ELSE 'Não Definido'
    END AS descricao_balancete,
    d.valor_fixado_orcamento_bal_despesa,
    d.valor_supl_no_mes,
    d.valor_supl_ate_mes,
    d.valor_anulacoes_dotacao_no_mes,
    d.valor_empenhado_no_mes,
    d.valor_empenhado_ate_mes,
    d.valor_saldo_dotacao,
    d.valor_pago_no_mes,
    d.valor_pago_ate_mes,
    d.valor_empenhado_pagar,
    d.valor_anulacoes_dotacao_ate_mes,
    d.valor_anulacoes_empenhos_no_mes,
    d.valor_anulacoes_empenhos_ate_mes,
    d.valor_liquidado_no_mes,
    d.valor_liquidado_ate_mes,
    d.valor_estornos_liquidacao_no_mes,
    d.valor_estornos_liquidacao_ate_mes,
    d.valor_estornos_pagos_no_mes,
    d.valor_estornos_pagos_ate_mes,
    d.tipo_fonte,
    CASE
        WHEN d.tipo_fonte = '1' THEN 'Recursos do Exercício Corrente'
        WHEN d.tipo_fonte = '2' THEN 'Recursos de Exercícios Anteriores'
        WHEN d.tipo_fonte = '9' THEN 'Recursos Condicionados'
        ELSE 'Não Definido'
    END AS descricao_tipo_fonte,
    d.codigo_fonte
FROM
    despesa d
LEFT JOIN orgao o
    ON d.municipio_id = o.municipio_id
    AND d.codigo_orgao = o.codigo_orgao
LEFT JOIN unidade_orcamentaria u
    ON d.municipio_id = u.municipio_id
    AND d.codigo_orgao = u.codigo_orgao
    AND d.codigo_unidade = u.codigo_unidade
    AND d.ano = u.exercicio_orcamento;

CREATE OR REPLACE VIEW receita_e_receita_extra_merged AS
SELECT
    COALESCE(r.municipio_id, re.codigo_municipio::INT) AS municipio_id,
    COALESCE(r.ano, re.exercicio_orcamento::INT / 100) AS ano,
    COALESCE(r.mes, re.data_referencia::INT % 100) AS mes,
    COALESCE(r.codigo_orgao, re.codigo_orgao) AS codigo_orgao,
    COALESCE(r.codigo_unidade, re.codigo_unidade) AS codigo_unidade,
    COALESCE(r.tipo_balancete, re.tipo_balancete) AS tipo_balancete,
    CASE
        WHEN COALESCE(r.tipo_balancete, re.tipo_balancete) = 'C' THEN 'Balancete Consolidado'
        WHEN COALESCE(r.tipo_balancete, re.tipo_balancete) = 'P' THEN 'Balancete de Unidades Gestoras geridas pelo Prefeito'
        WHEN COALESCE(r.tipo_balancete, re.tipo_balancete) = 'G' THEN 'Balancetes de Outras Unidades Gestoras'
        ELSE 'Não Definido'
    END AS descricao_balancete,
    r.valor_previsto_orcamento,
    r.valor_arrecadado_no_mes,
    r.valor_arrecadado_ate_mes,
    r.valor_anulacoes_no_mes,
    r.valor_anulacoes_ate_mes,
    r.tipo_fonte,
    CASE
        WHEN r.tipo_fonte = '1' THEN 'Recursos do Exercício Corrente'
        WHEN r.tipo_fonte = '2' THEN 'Recursos de Exercícios Anteriores'
        WHEN r.tipo_fonte = '9' THEN 'Recursos Condicionados'
        ELSE 'Não Definido'
    END AS descricao_tipo_fonte,
    r.codigo_fonte,
    re.codigo_conta_extraorcamentaria,
    re.valor_anulacoes_empenhos_no_mes,
    re.valor_nulacoes_dotacao_ate_mes,
    re.valor_arrecadacao_empenhos_no_mes,
    re.valor_arrecadacao_dotacao_ate_mes
FROM
    receita r
FULL JOIN receita_extra_orcamentaria re
    ON r.municipio_id = re.codigo_municipio::INT
    AND r.ano = re.exercicio_orcamento::INT / 100
    AND r.mes = re.data_referencia::INT % 100;


CREATE OR REPLACE VIEW despesa_despesa_extra_balancete_merged AS
SELECT
    COALESCE(d.municipio_id, b.codigo_municipio::INT) AS municipio_id,
    COALESCE(d.ano, b.exercicio_orcamento::INT / 100) AS ano,
    COALESCE(d.mes, b.data_referencia::INT % 100) AS mes,
    COALESCE(d.codigo_orgao, b.codigo_orgao) AS codigo_orgao,
    COALESCE(d.codigo_unidade, b.codigo_unidade) AS codigo_unidade,
    COALESCE(d.tipo_balancete, b.tipo_balancete) AS tipo_balancete,
    CASE
        WHEN COALESCE(d.tipo_balancete, b.tipo_balancete) = 'C' THEN 'Balancete Consolidado'
        WHEN COALESCE(d.tipo_balancete, b.tipo_balancete) = 'P' THEN 'Balancete de Unidades Gestoras geridas pelo Prefeito'
        WHEN COALESCE(d.tipo_balancete, b.tipo_balancete) = 'G' THEN 'Balancetes de Outras Unidades Gestoras'
        ELSE 'Não Definido'
    END AS descricao_balancete,
    d.valor_fixado_orcamento_bal_despesa,
    d.valor_supl_no_mes,
    d.valor_supl_ate_mes,
    d.valor_anulacoes_dotacao_no_mes,
    d.valor_empenhado_no_mes,
    d.valor_empenhado_ate_mes,
    d.valor_saldo_dotacao,
    d.valor_pago_no_mes AS valor_pago_no_mes_despesa,
    d.valor_pago_ate_mes AS valor_pago_ate_mes_despesa,
    b.valor_pago_no_mes AS valor_pago_no_mes_balancete,
    b.valor_pago_ate_mes AS valor_pago_ate_mes_balancete,
    d.valor_empenhado_pagar,
    d.valor_anulacoes_dotacao_ate_mes,
    d.valor_anulacoes_empenhos_no_mes AS valor_anulacoes_empenhos_no_mes_despesa,
    b.valor_anulacao_no_mes AS valor_anulacao_no_mes_balancete,
    d.valor_anulacoes_empenhos_ate_mes AS valor_anulacoes_empenhos_ate_mes_despesa,
    b.valor_anulacao_ate_mes AS valor_anulacao_ate_mes_balancete,
    d.valor_liquidado_no_mes,
    d.valor_liquidado_ate_mes,
    d.valor_estornos_liquidacao_no_mes,
    d.valor_estornos_liquidacao_ate_mes,
    d.valor_estornos_pagos_no_mes,
    d.valor_estornos_pagos_ate_mes,
    d.tipo_fonte,
    CASE
        WHEN d.tipo_fonte = '1' THEN 'Recursos do Exercício Corrente'
        WHEN d.tipo_fonte = '2' THEN 'Recursos de Exercícios Anteriores'
        WHEN d.tipo_fonte = '9' THEN 'Recursos Condicionados'
        ELSE 'Não Definido'
    END AS descricao_tipo_fonte,
    d.codigo_fonte,
    b.codigo_conta_extraorcamentaria
FROM
    despesa d
FULL JOIN balancete_despesa_extra_orcamentaria b
    ON d.municipio_id = b.codigo_municipio::INT
    AND d.ano = b.exercicio_orcamento::INT / 100
    AND d.mes = b.data_referencia::INT % 100;

VACUUM ANALYZE despesa;
VACUUM ANALYZE balancete_despesa_extra_orcamentaria;