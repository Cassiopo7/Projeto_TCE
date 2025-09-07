# 📊 Projeto TCE - Análise de Dados Municipais

Uma plataforma integrada para **extração, processamento e visualização** de dados financeiros municipais do Ceará, utilizando dados da API pública do TCE-CE.

---

## 🎯 **Visão Geral**

Este projeto oferece uma solução completa para análise de dados governamentais municipais, com:

- **Backend ETL**: Extração automatizada de dados via API TCE-CE
- **Frontend Dashboard**: Interface interativa para visualização e análise
- **Monitoramento**: Dashboard em tempo real do status da pipeline
- **Relatórios**: Geração automática de PDFs e CSVs

---

## 🏗️ **Arquitetura do Projeto**

### **Estrutura Geral**
```
/Projeto_DOSSIE/
├── tce_back/           # Backend ETL e Monitoramento
├── tce_front/          # Frontend Dashboard
├── requirements.txt    # Dependências unificadas
└── README.md          # Esta documentação
```

### **tce_back - Backend ETL**
```
tce_back/
├── dashboard.py        # Monitoramento Streamlit
├── main.py            # Orquestrador ETL
├── etl_interface.py   # Interface de consultas
├── config.py          # Configurações globais
├── data_extraction/   # Módulos de extração
├── database/          # Configuração BD e schemas
└── docs/             # Documentação e MER
```

### **tce_front - Frontend Dashboard**
```
tce_front/
├── app.py             # Aplicação Dash principal
├── layout.py          # Layout da interface
├── callbacks.py       # Lógica interativa
├── pages/             # Páginas do dashboard
├── utils/             # Utilitários (BD, gráficos)
└── assets/            # CSS e recursos estáticos
```

---

## 🚀 **Funcionalidades Principais**

### **Backend (ETL)**
✅ **Extração de Dados**: 11 tipos de dados municipais via API TCE-CE
✅ **Monitoramento em Tempo Real**: Dashboard com métricas de progresso
✅ **Controle de Qualidade**: Validação de dados e saúde da pipeline
✅ **Armazenamento Otimizado**: PostgreSQL com índices e views

### **Frontend (Dashboard)**
✅ **Análise Interativa**: 5 abas especializadas com gráficos dinâmicos
✅ **Filtros Inteligentes**: Seleção global de município e ano
✅ **KPIs em Tempo Real**: Métricas calculadas automaticamente
✅ **Relatórios**: Exportação para PDF e CSV
✅ **Comparação**: Até 20 municípios simultaneamente

---

## 📋 **Pré-requisitos**

- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Git**: Para versionamento
- **Brew** (macOS): Para instalar dependências

### **Dependências Python**
```bash
pip install -r requirements.txt
```

Principais bibliotecas:
- **Dash + Plotly**: Interface web e gráficos
- **SQLAlchemy**: ORM para banco de dados
- **Streamlit**: Dashboard de monitoramento
- **Pandas**: Manipulação de dados
- **Requests**: Cliente HTTP para APIs

---

## ⚙️ **Instalação Rápida**

### **Opção 1: Script Automático (Recomendado)**
```bash
# 1. Clonagem e configuração automática
git clone https://github.com/Cassiopo7/Projeto_TCE.git
cd Projeto_DOSSIE

# 2. Executar setup automático (inclui PostgreSQL, venv e dependências)
python3 run_project.py --help  # Ver instruções detalhadas

# 3. Executar projeto completo
python3 run_project.py
```

### **Opção 2: Instalação Manual**

#### **1. Clonagem do Repositório**
```bash
git clone https://github.com/Cassiopo7/Projeto_TCE.git
cd Projeto_DOSSIE
```

#### **2. Configuração do Banco**
```bash
# Instalar PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Criar banco de dados
createdb tce

# Configurar credenciais (opcional)
# Editar tce_back/config.py se necessário
```

#### **3. Ambiente Virtual (Único para todo o projeto)**
```bash
# Criar venv na raiz (já criado automaticamente)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

#### **4. Instalação de Dependências**
```bash
pip install -r requirements.txt
```

#### **5. Configuração do Schema**
```bash
cd tce_back
python3 database/db_setup.py
```

---

## 🎮 **Como Usar**

### **Opção 1: Execução Automática (Recomendado)**
```bash
# Executar projeto completo automaticamente
python3 run_project.py
```

**O que o script faz:**
- ✅ Verifica status da base de dados
- 🔄 Atualiza dados se necessário (ETL automático)
- 📊 Abre dashboard de monitoramento (porta 8050)
- 📈 Abre dashboard de visualização (porta 8040)
- 🛑 Gerencia processos automaticamente

### **Opção 2: Execução Manual**

#### **Executar Backend ETL**
```bash
cd tce_back

# Executar função específica
python3 main.py load_municipios
python3 main.py load_receitas
python3 main.py load_despesas

# Dashboard de monitoramento
streamlit run dashboard.py
```

#### **Executar Frontend Dashboard**
```bash
cd tce_front
python3 app.py
```

### **Acesso aos Dashboards**
- **Dashboard de Visualização**: http://localhost:8040
- **Dashboard de Monitoramento**: http://localhost:8050

---

## 📊 **Funcionalidades Detalhadas**

### **Backend ETL**
| Função | Descrição |
|--------|-----------|
| `load_municipios` | Carrega lista de municípios |
| `load_orgaos` | Órgãos públicos municipais |
| `load_receitas` | Receitas orçamentárias |
| `load_despesas` | Despesas orçamentárias |
| `load_licitacao` | Processos licitatórios |
| `load_prestacao_contas` | Prestação de contas |
| `load_liquidacoes` | Liquidações de despesas |
| `load_notas_empenho` | Notas de empenho |

### **Frontend Dashboard**
| Aba | Descrição |
|-----|-----------|
| **Receitas Detalhadas** | Análise de arrecadação por origem |
| **Despesas Detalhadas** | Gastos por órgão e categoria |
| **Receitas x Despesas** | Comparação e resumo financeiro |
| **Pessoal** | Agentes públicos por órgão |
| **Comparação** | Até 20 municípios lado a lado |

---

## 🎨 **Interface do Dashboard**

### **Recursos Avançados**
- **Filtro Global**: Ano e município aplicados automaticamente
- **Estados de Carregamento**: Spinners durante processamento
- **Cache Inteligente**: Dados cacheados para performance
- **KPIs Dinâmicos**: Cálculos automáticos de variações
- **Visualização MER**: Diagrama do modelo de dados integrado

### **Monitoramento ETL**
- **Saúde da Pipeline**: Status DB/API em tempo real
- **Progresso por Tipo**: Barras de progresso visuais
- **Última Execução**: Timestamp das cargas mais recentes
- **Pendências**: Municípios não carregados por período

---

## 🔧 **Configuração Avançada**

### **Variáveis de Ambiente**
```bash
# Arquivo .env (opcional)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tce
DB_USER=postgres
DB_PASSWORD=postgres
```

### **Personalização**
- **Cores**: Editar `tce_front/assets/style.css`
- **Layout**: Modificar `tce_front/layout.py`
- **Queries**: Ajustar em `tce_front/utils/database.py`

### **Variáveis de Ambiente (.env)**
```bash
# Arquivo .env opcional na raiz do projeto
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tce
DB_USER=postgres
DB_PASSWORD=postgres

DASHBOARD_PORT_FRONTEND=8040
DASHBOARD_PORT_BACKEND=8050
CACHE_TTL_SECONDS=60
ETL_TIMEOUT_SECONDS=300
```

---

## 📈 **Monitoramento e Métricas**

### **Dashboard ETL** (`tce_back/dashboard.py`)
- **Progresso Geral**: Total de registros por tipo
- **Completude**: Percentual por período/ano
- **Saúde**: Status de conectividade DB/API
- **Últimas Execuções**: Timestamp por tipo de dado

### **Performance**
- **Cache**: TTL de 60s para dados frequentes
- **Lazy Loading**: Dados carregados sob demanda
- **Compressão**: Otimização de queries SQL

---

## 🚀 **Deploy e Produção**

### **Docker (Recomendado)**
```dockerfile
# Dockerfile exemplo
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8040 8050

CMD ["python", "tce_front/app.py"]
```

### **Serviços**
- **Frontend**: Porta 8040
- **Backend Dashboard**: Porta 8050 (Streamlit)
- **PostgreSQL**: Porta 5432

---

## 🧪 **Testes e Validação**

### **Testes Básicos**
```bash
# Backend
cd tce_back
python3 -c "from etl_interface import get_progresso_por_tipo; print(len(get_progresso_por_tipo()))"

# Frontend
cd tce_front
python3 -c "from utils.database import get_municipios; print(len(get_municipios()))"
```

### **Validação de Dados**
- Compare totais entre backend e frontend
- Verifique integridade referencial
- Valide formatos de data e valores

---

## 🔮 **Roadmap e Melhorias**

### **Próximas Features**
- [ ] **Autenticação**: Controle de acesso aos dashboards
- [ ] **APIs REST**: Endpoints padronizados FastAPI
- [ ] **Cache Distribuído**: Redis para escalabilidade
- [ ] **Testes Automatizados**: Pytest + CI/CD
- [ ] **Containerização**: Docker Compose completo
- [ ] **Monitoramento Avançado**: Prometheus + Grafana

### **Otimização**
- [ ] **Paralelização**: Processamento assíncrono ETL
- [ ] **Compressão**: Dados históricos comprimidos
- [ ] **Indexação**: Otimização de queries pesadas

---

## 📞 **Suporte e Contribuição**

### **Issues e Bugs**
- Use o GitHub Issues para reportar problemas
- Inclua logs de erro e passos para reproduzir

### **Contribuição**
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 **Licença**

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

## 👥 **Equipe**

**Desenvolvedor Principal**: Cassio Pinheiro
**Contato**: [GitHub](https://github.com/Cassiopo7)

---

## 🔗 **Links Úteis**

- **Repositório**: https://github.com/Cassiopo7/Projeto_TCE
- **API TCE-CE**: https://api-dados-abertos.tce.ce.gov.br/
- **Dash Docs**: https://dash.plotly.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

*Última atualização: Dezembro 2024*
