FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache de layers
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/
COPY main.py .
COPY config/ ./config/

# Criar diretórios necessários
RUN mkdir -p logs models data

# Criar usuário não-root
RUN useradd -m -u 1000 trader && chown -R trader:trader /app
USER trader

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PAPER_MODE=true
ENV LOG_LEVEL=INFO

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expor porta de métricas
EXPOSE 8000

# Comando padrão
CMD ["python", "main.py"]
