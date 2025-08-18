import os

API_BASE_URL = "https://api-dados-abertos.tce.ce.gov.br/"

DB_CONFIG = {
    "database": os.getenv("DB_NAME", "tce"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}
