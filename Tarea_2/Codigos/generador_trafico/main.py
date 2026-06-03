import numpy as np
import time
import json
import uuid
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

ZONAS = ["Z1", "Z2", "Z3", "Z4", "Z5"]
QUERIES = ["q1", "q2", "q3", "q5"] 
TOPICO_PRINCIPAL = "consultas_geoespaciales"

producer = None

def generar_consulta(modo="uniform"):
    if modo == "uniform":
        zona = np.random.choice(ZONAS)
    else:
        idx = (np.random.zipf(1.2) - 1) % len(ZONAS)
        zona = ZONAS[idx]

    tipo_q = np.random.choice(QUERIES)
    conf_min = round(np.random.uniform(0.0, 0.9), 2)
    
    payload = {"type": tipo_q, "zone_id": zona, "confidence_min": conf_min}
    
    if np.random.random() < 0.1:
        z_a, z_b = np.random.choice(ZONAS, 2, replace=False)
        payload = {"type": "q4", "zone_id_a": z_a, "zone_id_b": z_b, "confidence_min": conf_min}
        
    payload["id"] = str(uuid.uuid4())          
    payload["retry_count"] = 0 
    payload["timestamp_creacion"] = time.time() 
    
    return payload

def simular_trafico(iteraciones=1000, modo="zipf"):
    print(f"--- Iniciando Simulación de Tráfico Asíncrono: Modo {modo.upper()} ---")
    for i in range(iteraciones):
        payload = generar_consulta(modo=modo)
        try:
            producer.send(TOPICO_PRINCIPAL, value=payload)
            print(f"[{i}] Publicado con éxito -> ID: {payload['id']} | Tipo: {payload['type']}")
        except Exception as e:
            print(f"[{i}] Error al publicar en Kafka: {e}")
        
        time.sleep(0.05)
    
    producer.flush()

if __name__ == "__main__":
    print("Iniciando fase de conexión con Kafka...")
    
    while True:
        try:
            print("Intentando conectar con el Broker de Kafka (kafka:29092)...")
            producer = KafkaProducer(
                bootstrap_servers=['kafka:29092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=5000  
            )
            print("[ÉXITO] ¡Conectado exitosamente al Broker de Kafka!")
            break  
        except NoBrokersAvailable:
            print("[ESPERA] El Broker de Kafka aún no está disponible. Reintentando en 5 segundos...")
            time.sleep(5)
    
    simular_trafico(iteraciones=1000, modo="uniform")
    
    print("\nCambiando a modo Zipf en 5 segundos...\n")
    time.sleep(5)
    
    simular_trafico(iteraciones=100, modo="zipf")
    
    print("--- Producción de tráfico finalizada ---")
