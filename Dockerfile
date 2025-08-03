# Utiliza una imagen base ligera de Python 3.10
FROM python:3.10-slim

# Información del autor
LABEL author="Xardax"

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo los archivos de dependencias primero para aprovechar el cache de Docker
COPY requirements.txt ./

# Actualiza pip e instala las dependencias del proyecto
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia el resto del código fuente al contenedor
COPY . /app

# Expone el puerto 8080 (opcional, solo si tu app lo necesita)
EXPOSE 8080

# Comando por defecto para ejecutar la aplicación principal
CMD ["python", "main.py"]
