FROM python:3.12-slim

WORKDIR /app

# Instalar pandas y numpy necesarios para los cálculos geoespaciales
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expone el puerto 5001 donde escucha tu "main repuesta.py"
EXPOSE 5001

CMD ["python3", "main_respuesta.py"]
