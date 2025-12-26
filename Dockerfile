# Usa una imagen base de Python ligera
FROM python:3.11-slim-bookworm

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# === INICIO DE LA CORRECCIÓN ===
# Crear carpetas de datos (instance) y logs y asegurar permisos de escritura (777)
# Esto garantiza que el proceso de Python pueda escribir la base de datos y los logs.
RUN mkdir -p /usr/src/app/instance \
    && mkdir -p /usr/src/app/logs \
    && chmod -R 777 /usr/src/app/instance \
    && chmod -R 777 /usr/src/app/logs
# === FIN DE LA CORRECCIÓN ===

# Copia los archivos de dependencia e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente del proyecto.,oi
COPY . .

# Expone el puerto que usará el servidor Gunicorn
EXPOSE 8000

# Comando para iniciar el servidor Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]