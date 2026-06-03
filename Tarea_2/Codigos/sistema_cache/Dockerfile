FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar librerías si se requiere
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la caché y el consumidor
COPY . .

# EXIGENCIA TAREA 2: Arrancar la API de métricas Y el consumidor en paralelo
CMD python3 main.py & python3 consumidor.py
