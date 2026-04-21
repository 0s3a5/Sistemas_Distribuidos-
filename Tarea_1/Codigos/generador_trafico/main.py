import numpy as np
import requests
import time
import json

ZONAS = ["Z1", "Z2", "Z3", "Z4", "Z5"]
QUERIES = ["q1", "q2", "q3", "q5"] 
CACHE_URL = "http://sistema_cache:5000/request"

# 1. Precalculamos las probabilidades Zipf truncadas para exactamente 5 zonas.
# Esto evita que np.random.zipf genere números infinitamente grandes y cuelgue el script.
a = 1.2
probabilidades_zipf = np.array([1 / (i**a) for i in range(1, len(ZONAS) + 1)])
probabilidades_zipf /= probabilidades_zipf.sum() # Normalizamos para que sumen 1

def generar_consulta(modo="zipf"):
    # 2. Ignoramos la variable "modo" forzando la elección de zona vía Zipf siempre.
    zona = np.random.choice(ZONAS, p=probabilidades_zipf)

    tipo_q = np.random.choice(QUERIES)
    conf_min = round(np.random.uniform(0.0, 0.9), 2)
    
    payload = {"type": tipo_q, "zone_id": zona, "confidence_min": conf_min}
    
    # 10% de probabilidad de que sea la consulta Q4 (comparación)
    if np.random.random() < 0.1:
        z_a, z_b = np.random.choice(ZONAS, 2, replace=False)
        payload = {"type": "q4", "zone_id_a": z_a, "zone_id_b": z_b, "confidence_min": conf_min}
        
    return payload

def simular_trafico(iteraciones=100, modo="zipf"):
    # Imprimimos un mensaje claro de que estamos forzando Zipf
    print(f"--- Iniciando Simulación de Tráfico: Modo ZIPF (Forzado) ---")
    for i in range(iteraciones):
        payload = generar_consulta(modo="zipf")
        try:
            start_time = time.time()
            response = requests.post(CACHE_URL, json=payload, timeout=10)
            latencia = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                res_data = response.json()
                status_val = res_data.get('status', 'N/A')
                print(f"[{i}] Tipo: {payload['type']} | Status: {status_val} | Latencia: {latencia:.2f}ms")
            else:
                print(f"[{i}] Error: {response.status_code}")
        except Exception as e:
            print(f"[{i}] Error de conexión: {e}")
        time.sleep(0.05)

# ESTA PARTE ES LA QUE DEBE QUEDAR EXACTAMENTE ASÍ:
if __name__ == "__main__":
    print("Esperando 10 segundos a que el sistema inicie...")
    time.sleep(10)
    
    # Ejecución Uniforme
   # simular_trafico(iteraciones=1000, modo="uniform")
    
   # print("\nCambiando a modo Zipf...\n")
    #time.sleep(5)
    
    # Ejecución Zipf
    simular_trafico(iteraciones=1000, modo="zipf")
    
    print("--- Simulación finalizada ---")
