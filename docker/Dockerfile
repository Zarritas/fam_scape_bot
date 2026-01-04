# Multi-stage build para imagen optimizada

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar dependencias de construcción
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime
FROM python:3.12-slim as runtime

WORKDIR /app

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash appuser

# Instalar dependencias del sistema para pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/appuser/.local

# Asegurar que pip packages están en PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar código fuente
COPY src/ ./src/
COPY .env.example ./.env.example

# Crear directorio de datos
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check (el bot debe estar corriendo)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Entry point
CMD ["python", "-m", "src.main"]
