# Imagen base ligera de Python 3.11 (tiene versión ARM64 para la Raspberry Pi 5)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Establecer carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y el dashboard (la API lo servirá como archivos estáticos)
COPY ./app ./app
COPY ./frontend ./frontend

# Carpeta de la base SQLite; en compose se monta como volumen persistente
RUN mkdir -p /app/data

# Exponer el puerto de FastAPI
EXPOSE 8000

# Modo producción (Raspberry Pi). El --reload de desarrollo lo agrega docker-compose.override.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
