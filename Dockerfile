# 1. Imagen base oficial de Python 3.11 en versión ligera (Linux Debian)
FROM python:3.11-slim

# 2. Evitar que Python escriba archivos .pyc y forzar que imprima logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar librerías de sistema necesarias (compiladores y git por si dbt los requiere)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalar dependencias de Python (aprovechando el caché de capas de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
pip install --no-cache-dir --upgrade pip 

# 6. Copiar todo el código de tu proyecto al contenedor
COPY . .

# 7. Comando predeterminado al arrancar
CMD ["python", "--version"]