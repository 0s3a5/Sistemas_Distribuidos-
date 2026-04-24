FROM python:3.9-slim
WORKDIR /app
RUN pip install flask pandas redis requests numpy
COPY . .
CMD ["python", "main.py"]
