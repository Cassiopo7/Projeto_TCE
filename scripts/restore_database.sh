#!/bin/bash

# Script de Restauração do Banco de Dados TCE
# Uso: ./scripts/restore_database.sh <arquivo_backup> [ambiente]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar argumentos
if [ $# -lt 1 ]; then
    echo "Uso: $0 <arquivo_backup> [ambiente]"
    echo ""
    echo "Exemplos:"
    echo "  $0 backups/tce_backup_production_20241201_143000.sql"
    echo "  $0 backups/tce_backup_development_20241201_143000.sql development"
    exit 1
fi

BACKUP_FILE="$1"
ENVIRONMENT=${2:-"development"}

# Verificar se o arquivo de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    error "Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

log "Iniciando restauração do banco de dados..."
log "Arquivo: $BACKUP_FILE"
log "Ambiente: $ENVIRONMENT"

# Verificar se estamos em ambiente Docker ou local
if [ -n "$DOCKER_CONTAINER" ] || [ -f "/.dockerenv" ]; then
    log "Executando dentro do container Docker"
    DB_HOST=${DB_HOST:-"postgres"}
    DB_PORT=${DB_PORT:-"5432"}
    DB_NAME=${DB_NAME:-"tce"}
    DB_USER=${DB_USER:-"tce_user"}
    DB_PASSWORD=${DB_PASSWORD:-"tce_password"}
else
    log "Executando em ambiente local"
    # Carregar variáveis do .env se existir
    if [ -f ".env" ]; then
        source .env
    fi

    DB_HOST=${DB_HOST:-"localhost"}
    DB_PORT=${DB_PORT:-"5432"}
    DB_NAME=${DB_NAME:-"tce"}
    DB_USER=${DB_USER:-"postgres"}
    DB_PASSWORD=${DB_PASSWORD:-"postgres"}
fi

# Verificar conexão com o banco
log "Verificando conexão com o banco..."
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    error "Não foi possível conectar ao banco de dados"
    exit 1
fi

success "Conexão com banco estabelecida"

# AVISO IMPORTANTE
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ⚠️  AVISO IMPORTANTE ⚠️                   ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║ Esta operação irá APAGAR todos os dados atuais do banco!   ║"
echo "║ Certifique-se de ter um backup dos dados atuais se precisar.║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
read -p "Tem certeza que deseja continuar? (digite 'SIM' para confirmar): " -r
if [[ ! $REPLY =~ ^[Ss][Ii][Mm]$ ]]; then
    log "Operação cancelada pelo usuário"
    exit 0
fi

# Criar backup automático antes da restauração
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
AUTO_BACKUP="./backups/auto_backup_before_restore_${TIMESTAMP}.sql"

log "Criando backup automático antes da restauração..."
if ./scripts/backup_database.sh "${ENVIRONMENT}_pre_restore" >/dev/null 2>&1; then
    success "Backup automático criado"
else
    warning "Falha ao criar backup automático (continuando...)"
fi

# Parar aplicações que usam o banco (se estiverem rodando)
log "Verificando se há aplicações usando o banco..."

# Função para verificar e parar containers
stop_containers() {
    if command -v docker &> /dev/null && docker ps | grep -q tce; then
        log "Parando containers TCE..."
        docker-compose stop tce_backend tce_frontend 2>/dev/null || true
    fi
}

# Parar containers se estiverem rodando
stop_containers

# Executar restauração
log "Executando restauração do backup..."
log "Isso pode levar alguns minutos..."

# Determinar o tipo de arquivo de backup
if [[ "$BACKUP_FILE" == *.sql ]]; then
    # Arquivo SQL plain
    log "Restaurando arquivo SQL..."
    if PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -f "$BACKUP_FILE" \
        2>/dev/null; then
        success "Restauração do arquivo SQL concluída"
    else
        error "Falha na restauração do arquivo SQL"
        exit 1
    fi
else
    # Arquivo custom format
    log "Restaurando arquivo custom format..."
    if pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --clean \
        --if-exists \
        --create \
        --verbose \
        "$BACKUP_FILE" \
        2>/dev/null; then
        success "Restauração do arquivo custom concluída"
    else
        error "Falha na restauração do arquivo custom"
        exit 1
    fi
fi

# Verificar se a restauração foi bem-sucedida
log "Verificando restauração..."

# Teste básico de conectividade
if PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -c "SELECT version();" \
    >/dev/null 2>&1; then
    success "Conectividade com banco verificada"
else
    error "Problemas de conectividade após restauração"
    exit 1
fi

# Contar tabelas após restauração
TABLE_COUNT=$(PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" \
    2>/dev/null)

log "Estatísticas após restauração:"
echo "  📊 Tabelas encontradas: ${TABLE_COUNT:-'N/A'}"

# Reiniciar containers se estavam rodando
if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
    log "Reiniciando containers..."
    docker-compose start tce_backend tce_frontend 2>/dev/null || true
fi

# Criar arquivo de log da restauração
LOG_FILE="./backups/restore_log_$(date +"%Y%m%d_%H%M%S").log"
{
    echo "=== TCE Database Restore Log ==="
    echo "Timestamp: $(date)"
    echo "Environment: $ENVIRONMENT"
    echo "Database: $DB_NAME@$DB_HOST:$DB_PORT"
    echo "Backup File: $BACKUP_FILE"
    echo "Tables After Restore: ${TABLE_COUNT:-'Unknown'}"
    echo "Status: SUCCESS"
} > "$LOG_FILE"

success "Log da restauração criado: $LOG_FILE"

# Resumo final
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  RESTAURAÇÃO CONCLUÍDA                      ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║ Arquivo: $(basename "$BACKUP_FILE")"
echo "║ Ambiente: $ENVIRONMENT"
echo "║ Tabelas: ${TABLE_COUNT:-'N/A'}"
echo "║ Status: ✅ SUCESSO"
echo "╚══════════════════════════════════════════════════════════════╝"

log "Restauração concluída com sucesso! 🎉"
