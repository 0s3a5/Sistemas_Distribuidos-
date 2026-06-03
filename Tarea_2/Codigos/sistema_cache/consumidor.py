import json
import time
import requests
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

TOPICO_PRINCIPAL = "consultas_geoespaciales"
TOPICO_REINTENTO = "consultas_reintento"
TOPICO_DLQ = "consultas_dlq"

MAX_RETRIES = 3

consumer = None
producer = None

print("[-] Iniciando fase de conexión del Consumidor con Kafka...")

while True:
    try:
        print("    Intentando conectar consumidor al Broker (kafka:29092)...")
        consumer = KafkaConsumer(
            TOPICO_PRINCIPAL, TOPICO_REINTENTO,
            bootstrap_servers=['kafka:29092'],
            group_id='grupo_procesamiento_geoespacial',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        producer = KafkaProducer(
            bootstrap_servers=['kafka:29092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("[ÉXITO] ¡Consumidor y Productor de Kafka conectados de forma segura!")
        break
    except NoBrokersAvailable:
        print("[ESPERA] El Broker de Kafka no responde aún. Reintentando en 5 segundos...")
        time.sleep(5)

print("[-] Consumidor listo y escuchando eventos distribuidos...")

for message in consumer:
    consulta = message.value
    consulta_id = consulta.get('id')
    
    try:
        cache_url = "http://localhost:5000/request"
        res_cache = requests.post(cache_url, json=consulta, timeout=5)
        
        if res_cache.status_code == 200:
            print(f"[OK] Consulta {consulta_id} procesada exitosamente.")
            continue
        else:
            raise Exception("Error interno del servidor de respuestas")

    except Exception as e:
        print(f"[FALLA] Error en consulta {consulta_id}: {e}")
        consulta['retry_count'] += 1
        
        if consulta['retry_count'] <= MAX_RETRIES:
            print(f"    [REINTENTO] Reenviando a {TOPICO_REINTENTO} ({consulta['retry_count']}/{MAX_RETRIES})") 
            producer.send(TOPICO_REINTENTO, value=consulta)
        else:
            print(f"    [DLQ] Excedió reintentos. Enviando a {TOPICO_DLQ}.") 
            try:
                requests.post("http://localhost:5000/log_dlq", json=consulta)
            except:
                pass
            producer.send(TOPICO_DLQ, value=consulta)
                
        producer.flush()
