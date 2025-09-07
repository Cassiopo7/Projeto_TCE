#!/usr/bin/env python3
"""
Script principal para executar o projeto TCE completo.
Verifica status da base, atualiza dados se necessário e abre dashboards.
"""

import os
import sys
import time
import subprocess
import signal
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Adicionar diretórios ao path
sys.path.append('tce_back')
sys.path.append('tce_front')

try:
    from tce_back.etl_interface import (
        get_progresso_por_tipo,
        get_progresso_por_periodo,
        get_total_municipios,
        get_municipios_pendentes,
        get_funcoes_etl_disponiveis
    )
    from tce_back.config import DB_CONFIG
    from tce_front.utils.database import query_db
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que está executando na raiz do projeto e instalou as dependências.")
    sys.exit(1)


class ProjectRunner:
    """Classe para orquestrar a execução completa do projeto TCE."""

    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.ano_atual = datetime.now().year
        self.mes_atual = datetime.now().month

        # Configurações de execução
        self.min_completude = 80.0  # Percentual mínimo de completude
        self.timeout_execucao = 300  # 5 minutos por execução

    def verificar_conexao_bd(self) -> bool:
        """Verifica se consegue conectar ao banco de dados."""
        try:
            result = query_db("SELECT 1")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão com BD: {e}")
            return False

    def verificar_status_base(self) -> Dict:
        """Verifica o status atual da base de dados."""
        status = {
            'total_municipios': 0,
            'progresso_geral': {},
            'completude_atual': 0.0,
            'tipos_carregados': 0,
            'municipios_carregados': 0,
            'atualizada': False
        }

        try:
            # Total de municípios
            status['total_municipios'] = get_total_municipios()

            # Progresso por tipo
            progresso = get_progresso_por_tipo()
            status['progresso_geral'] = {item['tipo_dado']: item['total'] for item in progresso}
            status['tipos_carregados'] = len(progresso)

            # Completude do período atual
            progresso_periodo = get_progresso_por_periodo('receitas', self.ano_atual, self.mes_atual)
            status['completude_atual'] = progresso_periodo.get('percentual', 0.0)
            status['municipios_carregados'] = progresso_periodo.get('carregados', 0)

            # Verificar se está atualizada
            status['atualizada'] = status['completude_atual'] >= self.min_completude

        except Exception as e:
            print(f"⚠️ Erro ao verificar status da base: {e}")

        return status

    def executar_etl(self, tipo_dado: str) -> bool:
        """Executa uma função ETL específica."""
        try:
            print(f"🔄 Executando ETL: {tipo_dado}")

            # Comando para executar ETL
            cmd = [sys.executable, 'tce_back/main.py', tipo_dado]

            # Executar com timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_execucao,
                cwd=os.getcwd()
            )

            if result.returncode == 0:
                print(f"✅ ETL {tipo_dado} executado com sucesso")
                return True
            else:
                print(f"❌ Erro na execução do ETL {tipo_dado}")
                print(f"Saída: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout na execução do ETL {tipo_dado}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado no ETL {tipo_dado}: {e}")
            return False

    def atualizar_base_dados(self) -> bool:
        """Atualiza a base de dados executando ETLS necessários."""
        print("\n🔄 Iniciando atualização da base de dados...")

        # Funções ETL prioritárias
        funcoes_prioritarias = [
            'load_municipios',
            'load_receitas',
            'load_despesas',
            'load_orgaos'
        ]

        funcoes_opcionais = [
            'load_licitacao',
            'load_prestacao_contas',
            'load_liquidacoes',
            'load_notas_empenho'
        ]

        sucesso = True

        # Executar funções prioritárias
        for funcao in funcoes_prioritarias:
            if not self.executar_etl(funcao):
                sucesso = False

        # Executar funções opcionais apenas se prioritárias foram OK
        if sucesso:
            for funcao in funcoes_opcionais:
                self.executar_etl(funcao)

        return sucesso

    def iniciar_dashboard_backend(self) -> subprocess.Popen:
        """Inicia o dashboard de monitoramento do backend."""
        try:
            print("🚀 Iniciando dashboard de monitoramento (tce_back)...")

            cmd = [sys.executable, '-m', 'streamlit', 'run', 'tce_back/dashboard.py']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )

            # Aguardar um pouco para o servidor iniciar
            time.sleep(3)

            # Verificar se está rodando
            if process.poll() is None:
                print("✅ Dashboard backend iniciado: http://localhost:8050")
                return process
            else:
                print("❌ Falha ao iniciar dashboard backend")
                return None

        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard backend: {e}")
            return None

    def iniciar_dashboard_frontend(self) -> subprocess.Popen:
        """Inicia o dashboard do frontend."""
        try:
            print("🚀 Iniciando dashboard frontend (tce_front)...")

            cmd = [sys.executable, 'tce_front/app.py']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )

            # Aguardar um pouco para o servidor iniciar
            time.sleep(5)

            # Verificar se está rodando
            if process.poll() is None:
                print("✅ Dashboard frontend iniciado: http://localhost:8040")
                return process
            else:
                print("❌ Falha ao iniciar dashboard frontend")
                return None

        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard frontend: {e}")
            return None

    def parar_processos(self):
        """Para todos os processos em execução."""
        print("\n🛑 Encerrando processos...")

        for process in self.processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

        self.processes.clear()

    def exibir_status(self, status: Dict):
        """Exibe o status da base de dados."""
        print("\n📊 STATUS DA BASE DE DADOS")
        print("=" * 50)
        print(f"📅 Período analisado: {self.mes_atual}/{self.ano_atual}")
        print(f"🏛️ Total de municípios: {status['total_municipios']}")
        print(f"📊 Tipos de dados carregados: {status['tipos_carregados']}")
        print(f"📈 Municípios com dados: {status['municipios_carregados']}")
        print(f"📈 Completude atual: {status['completude_atual']:.1f}%")
        if status['atualizada']:
            print("✅ Status: BASE ATUALIZADA")
        else:
            print("⚠️ Status: BASE DESATUALIZADA - será atualizada")

        print("\n📋 Progresso por tipo:")
        for tipo, total in status['progresso_geral'].items():
            print(f"  {tipo}: {total} registros")
        print()

    def executar(self):
        """Executa o fluxo completo do projeto."""
        print("🚀 INICIANDO PROJETO TCE")
        print("=" * 50)
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        try:
            # 1. Verificar conexão com BD
            print("\n🔍 Verificando conexão com banco de dados...")
            if not self.verificar_conexao_bd():
                print("❌ Não foi possível conectar ao banco de dados.")
                print("Verifique se o PostgreSQL está rodando e as credenciais estão corretas.")
                return False

            print("✅ Conexão com banco estabelecida")

            # 2. Verificar status da base
            print("\n🔍 Verificando status da base de dados...")
            status = self.verificar_status_base()
            self.exibir_status(status)

            # 3. Atualizar base se necessário
            if not status['atualizada']:
                print("\n🔄 Atualizando base de dados...")
                if self.atualizar_base_dados():
                    print("✅ Base de dados atualizada com sucesso!")
                    # Re-verificar status após atualização
                    status = self.verificar_status_base()
                    self.exibir_status(status)
                else:
                    print("⚠️ Houve problemas na atualização, mas continuando...")

            # 4. Iniciar dashboards
            print("\n🚀 Iniciando dashboards...")

            # Dashboard backend (monitoramento)
            backend_process = self.iniciar_dashboard_backend()
            if backend_process:
                self.processes.append(backend_process)

            # Dashboard frontend (visualização)
            frontend_process = self.iniciar_dashboard_frontend()
            if frontend_process:
                self.processes.append(frontend_process)

            # 5. Manter execução
            if self.processes:
                print("\n🎉 Projeto TCE executando!")
                print("📊 Dashboard de monitoramento: http://localhost:8050")
                print("📈 Dashboard de visualização: http://localhost:8040")
                print("\n💡 Pressione Ctrl+C para encerrar...")

                # Aguardar sinal de interrupção
                try:
                    while True:
                        time.sleep(1)
                        # Verificar se processos ainda estão rodando
                        self.processes = [p for p in self.processes if p.poll() is None]
                        if not self.processes:
                            print("⚠️ Todos os processos foram encerrados inesperadamente")
                            break

                except KeyboardInterrupt:
                    print("\n👋 Encerrando projeto TCE...")

            else:
                print("❌ Nenhum dashboard conseguiu iniciar")
                return False

        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

        finally:
            self.parar_processos()

        return True


def main():
    """Função principal."""
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("""
🚀 PROJETO TCE - Script de Execução

Este script automatiza a execução completa do projeto TCE, verificando
e atualizando a base de dados e abrindo os dashboards de visualização.

📋 PRÉ-REQUISITOS:
- PostgreSQL rodando localmente
- Python 3.8+ instalado
- Dependências instaladas (pip install -r requirements.txt)

🎯 FUNCIONALIDADES:
- ✅ Verifica status da base de dados
- 🔄 Atualiza dados se necessário (ETL)
- 📊 Abre dashboard de monitoramento (tce_back)
- 📈 Abre dashboard de visualização (tce_front)
- 🛑 Gerenciamento automático de processos

📊 USO:
    python3 run_project.py          # Executa o projeto completo
    python3 run_project.py --help   # Mostra esta ajuda

⚙️ CONFIGURAÇÕES:
- Mínima completude: 80%
- Timeout ETL: 300s (5 minutos)
- Portas: Backend=8050, Frontend=8040

📞 SUPORTE:
Para problemas, verifique:
1. Conexão com PostgreSQL
2. Credenciais no arquivo config.py
3. Dependências instaladas

        """)
        sys.exit(0)

    # Verificar se está na raiz do projeto
    if not os.path.exists('tce_back') or not os.path.exists('tce_front'):
        print("❌ Execute este script na raiz do projeto (onde estão tce_back/ e tce_front/)")
        print("💡 Dica: Execute 'python3 run_project.py --help' para mais informações")
        sys.exit(1)

    # Verificar se requirements.txt existe
    if not os.path.exists('requirements.txt'):
        print("❌ Arquivo requirements.txt não encontrado")
        print("💡 Execute: pip install -r requirements.txt")
        sys.exit(1)

    # Executar projeto
    runner = ProjectRunner()
    success = runner.executar()

    if success:
        print("\n✅ Projeto TCE finalizado com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Projeto TCE finalizado com erros!")
        sys.exit(1)


if __name__ == "__main__":
    # Configurar handler para SIGTERM
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))

    main()
