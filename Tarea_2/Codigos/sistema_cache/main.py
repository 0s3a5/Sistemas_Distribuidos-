import redis
import requests
import time
import csv
import os
import json
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
cache = redis.Redis(host='redis-service', port=6379, decode_responses=True)

# Rutas exigidas para el volumen de Docker [cite: 156]
METRICS_LOG = '/app/data/log_detalle.csv'
SUMMARY_REPORT = '/app/data/reporte_final.csv'

def inicializar_log():
    os.makedirs(os.path.dirname(METRICS_LOG), exist_ok=True)
    if not os.path.exists(METRICS_LOG):
        with open(METRICS_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            # NUEVO ENCABEZADO EXIGIDO POR LA RÚBRICA 
            writer.writerow(['timestamp', 'status', 'latency_ms', 'retry_count', 'is_dlq', 'is_recovered'])

@app.route('/request', methods=['POST'])
def process_request():
    data = request.json
    q_type = data.get('type')
    zone_key = data.get('zone_id') or data.get('zone_id_a')
    cache_key = f"{q_type}:{zone_key}:{data.get('confidence_min', 0.0)}"
    
    start_time = time.time()
    cached_res = cache.get(cache_key)
    
    # Extraemos los datos de control de Kafka que viajan en el JSON [cite: 94]
    retries_actuales = data.get('retry_count', 0)
    is_recovered = 1 if retries_actuales > 0 else 0

    if cached_res:
        status = "HIT"
        try:
            response_data = json.loads(cached_res)
        except:
            response_data = cached_res
    else:
        status = "MISS"
        # Llamada interna al generador de respuestas [cite: 44]
        resp = requests.post(f"http://response-gen:5001/query/{q_type}", json=data, timeout=5)
        cache.setex(cache_key, 60, resp.text)
        try:
            response_data = resp.json()
        except:
            response_data = resp.text

    latency = (time.time() - start_time) * 1000
    
    # Guardamos el registro con las nuevas métricas de Kafka 
    with open(METRICS_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), status, latency, retries_actuales, 0, is_recovered])

    return jsonify({"status": status, "latency_ms": latency, "data": response_data}), 200

# NUEVO ENDPOINT: El consumidor llamará aquí si una consulta se va a la DLQ [cite: 59]
@app.route('/log_dlq', methods=['POST'])
def log_dlq():
    data = request.json
    with open(METRICS_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        # Registra la consulta fallida en la DLQ [cite: 59, 139]
        writer.writerow([time.time(), "DLQ", 0, data.get('retry_count', 0), 1, 0])
    return jsonify({"status": "DLQ_LOGGED"}), 200

@app.route('/generar_reporte', methods=['GET'])
def generar_reporte():
    if not os.path.exists(METRICS_LOG):
        return jsonify({"error": "No existe el log"}), 400

    data_rows = []
    with open(METRICS_LOG, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_rows.append(row)

    if not data_rows:
        return jsonify({"error": "Log vacío"}), 400

    total = len(data_rows)
    hits = sum(1 for r in data_rows if r['status'] == 'HIT')
    misses = sum(1 for r in data_rows if r['status'] == 'MISS')
    dlqs = sum(1 for r in data_rows if r['is_dlq'] == '1')
    recovered = sum(1 for r in data_rows if r['is_recovered'] == '1' and r['status'] != 'DLQ')
    
    latencias = [float(r['latency_ms']) for r in data_rows if r['status'] != 'DLQ']
    p50 = np.percentile(latencias, 50) if latencias else 0
    p95 = np.percentile(latencias, 95) if latencias else 0
    
    # Cálculos estrictos según las fórmulas de la rúbrica 
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
    throughput = (hits + misses) / (float(data_rows[-1]['timestamp']) - float(data_rows[0]['timestamp'])) if total > 1 else 0
    retry_rate = sum(int(r['retry_count']) for r in data_rows) / total
    dlq_rate = dlqs / total
    recovery_rate = recovered / total

    # Guardar Reporte Final con nombres exactos de la rúbrica 
    with open(SUMMARY_REPORT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metrica', 'Valor'])
        writer.writerow(['Total Consultas', total])
        writer.writerow(['Hit Rate', round(hit_rate, 4)])
        writer.writerow(['Throughput (req/s)', round(throughput, 2)])
        writer.writerow(['Latencia p50 (ms)', round(p50, 2)])
        writer.writerow(['Latencia p95 (ms)', round(p95, 2)])
        writer.writerow(['Retry Rate', round(retry_rate, 4)])
        writer.writerow(['Recovery Rate', round(recovery_rate, 4)])
        writer.writerow(['DLQ Rate', round(dlq_rate, 4)])
        f.flush()

    return jsonify({"mensaje": "Reporte completo generado exitosamente."}), 200

if __name__ == '__main__':
    inicializar_log()
    app.run(host='0.0.0.0', port=5000)
