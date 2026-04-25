FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Crear usuario sin privilegios
RUN groupadd -r appuser && useradd -r -g appuser -s /sbin/nologin -c "Docker image user" appuser

WORKDIR /app

# Copiar dependencias primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar herramientas, compilar librerías de Python y purgar compiladores en un solo paso
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el código fuente
COPY . .

# Cambiar propiedad de archivos
RUN chown -R appuser:appuser /app

# Cambiar al usuario seguro
USER appuser

# Exponer el puerto unificado
EXPOSE 8000

# Ejecutar la aplicación
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]