FROM python:3.9-slim
WORKDIR /app
# Instalar dependencias necesarias
RUN pip install flask pandas redis requests numpy
# Copiar el código al contenedor
COPY . .
# Comando para ejecutar
CMD ["python", "main.py"]
