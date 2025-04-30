FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clonar el repositorio
RUN git clone https://github.com/bot1004/descargavideos.git .

# Copiar los archivos de configuración
COPY requirements.txt .
COPY app.py .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpeta temporal para descargas
RUN mkdir -p /tmp/downloads

# Exponer el puerto que usará la aplicación
EXPOSE $PORT

# Comando para iniciar la aplicación
CMD gunicorn --bind 0.0.0.0:$PORT app:app