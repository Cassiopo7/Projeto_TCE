# Dockerfile para TCE Frontend (Dashboard)
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependências do sistema para WeasyPrint e outras libs
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    build-essential \
    python3-dev \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY ../requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretório para assets e dados
RUN mkdir -p /app/assets /app/data

# Definir permissões
RUN chmod +x app.py

# Expor porta do Dash
EXPOSE 8040

# Health check para Dash
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8040/ || exit 1

# Comando padrão
CMD ["python", "app.py"]
