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

METRICS_LOG = '/app/data/log_detalle.csv'
SUMMARY_REPORT = '/app/data/reporte_final.csv'

# Mantenemos estas listas globales
tiempos_hit = []
tiempos_miss = []

def inicializar_log():
    os.makedirs(os.path.dirname(METRICS_LOG), exist_ok=True)
    if not os.path.exists(METRICS_LOG):
        with open(METRICS_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'status', 'latency_ms'])

@app.route('/request', methods=['POST'])
def process_request():
    data = request.json
    q_type = data.get('type')
    zone_key = data.get('zone_id') or data.get('zone_id_a')
    cache_key = f"{q_type}:{zone_key}:{data.get('confidence_min', 0.0)}"
    
    start_time = time.time()
    cached_res = cache.get(cache_key)
    
    if cached_res:
        status = "HIT"
        try:
            response_data = json.loads(cached_res)
        except:
            response_data = cached_res
        tiempos_hit.append((time.time() - start_time) * 1000)
    else:
        status = "MISS"
        resp = requests.post(f"http://response-gen:5001/query/{q_type}", json=data)
        cache.setex(cache_key, 60, resp.text)
        try:
            response_data = resp.json()
        except:
            response_data = resp.text
        tiempos_miss.append((time.time() - start_time) * 1000)

    latency = (time.time() - start_time) * 1000
    
    # Registro con flush inmediato para que no se pierda nada
    with open(METRICS_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), status, latency])

    return jsonify({
        "status": status,
        "latency_ms": latency,
        "data": response_data
    }), 200

@app.route('/generar_reporte', methods=['GET'])
def generar_reporte():
    if not os.path.exists(METRICS_LOG):
        return jsonify({"error": "No existe el log detallado"}), 400

    data_rows = []
    # Usamos listas temporales basadas en el archivo por si las globales fallan
    l_hits = []
    l_misses = []

    with open(METRICS_LOG, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_rows.append(row)
            lat = float(row['latency_ms'])
            if row['status'] == 'HIT':
                l_hits.append(lat)
            else:
                l_misses.append(lat)

    if not data_rows:
        return jsonify({"error": "Log vacío"}), 400

    total = len(data_rows)
    hits_count = len(l_hits)
    misses_count = len(l_misses)
    
    hit_rate = hits_count / total
    throughput = total / (float(data_rows[-1]['timestamp']) - float(data_rows[0]['timestamp'])) if total > 1 else 0
    
    all_latencies = [float(r['latency_ms']) for r in data_rows]
    p50 = np.percentile(all_latencies, 50)
    p95 = np.percentile(all_latencies, 95)
    
    # Eficiencia usando los datos reales del archivo
    t_c = np.mean(l_hits) if l_hits else 0
    t_d = np.mean(l_misses) if l_misses else 0
    efficiency = (hits_count * t_c - misses_count * t_d) / total

    # ESCRITURA FORZADA DEL REPORTE
    with open(SUMMARY_REPORT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metrica', 'Valor'])
        writer.writerow(['Total Consultas', total])
        writer.writerow(['Hit Rate', round(hit_rate, 4)])
        writer.writerow(['Throughput (req/s)', round(throughput, 2)])
        writer.writerow(['Latencia p50 (ms)', round(p50, 2)])
        writer.writerow(['Latencia p95 (ms)', round(p95, 2)])
        writer.writerow(['Cache Efficiency', round(efficiency, 4)])
        f.flush() # Forzamos la escritura al disco

    return jsonify({"mensaje": f"Reporte exitoso con {total} registros"}), 200

if __name__ == '__main__':
    inicializar_log()
    app.run(host='0.0.0.0', port=5000)
