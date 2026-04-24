import pandas as pd
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
ZONAS_BBOX = {
    "Z1": {"name": "Providencia", "area_km2": 4.5},
    "Z2": {"name": "Las Condes", "area_km2": 6.2},
    "Z3": {"name": "Maipú", "area_km2": 8.1},
    "Z4": {"name": "Santiago Centro", "area_km2": 3.8},
    "Z5": {"name": "Pudahuel", "area_km2": 9.5}
}

def cargar_datos():
    """
    Carga el dataset Google Open Buildings en memoria[cite: 45].
    Busca el archivo en la ruta montada por el volumen de Docker.
    """
    try:
              df = pd.read_csv('/app/data/buildings.csv') 
        print(f"Éxito: {len(df)} edificaciones cargadas en memoria[cite: 91].")
        return df
    except FileNotFoundError:
        print("ERROR: No se encontró '/app/data/buildings.csv'. Revisa el volumen en Docker.")
        return pd.DataFrame()

df_edificios = cargar_datos()

@app.route('/query/q1', methods=['POST'])
def query_q1():
    """Conteo de edificios en una zona[cite: 97, 98, 99]."""
    data = request.json
    try:
        subset = df_edificios[(df_edificios['zone_id'] == data['zone_id']) & 
                              (df_edificios['confidence'] >= data.get('confidence_min', 0.0))]
        return jsonify({"result": int(len(subset))}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query/q2', methods=['POST'])
def query_q2():
    """Área promedio y total de edificaciones[cite: 109, 110]."""
    data = request.json
    try:
        subset = df_edificios[(df_edificios['zone_id'] == data['zone_id']) & 
                              (df_edificios['confidence'] >= data.get('confidence_min', 0.0))]
        if subset.empty:
            return jsonify({"avg_area": 0, "total_area": 0, "n": 0}), 200

        return jsonify({
            "avg_area": float(subset['area_in_meters'].mean()),
            "total_area": float(subset['area_in_meters'].sum()),
            "n": int(len(subset))
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query/q3', methods=['POST'])
def query_q3():
    """Densidad de edificaciones por km²[cite: 121, 122, 123]."""
    data = request.json
    try:
        subset = df_edificios[(df_edificios['zone_id'] == data['zone_id']) & 
                              (df_edificios['confidence'] >= data.get('confidence_min', 0.0))]
        area_km2 = ZONAS_BBOX.get(data['zone_id'], {}).get('area_km2', 1.0)
        density = len(subset) / area_km2
        return jsonify({"density": float(density)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query/q4', methods=['POST'])
def query_q4():
    """Comparación de densidad entre dos zonas[cite: 134, 135]."""
    data = request.json
    try:
        def get_density(z_id):
            sub = df_edificios[(df_edificios['zone_id'] == z_id) & 
                               (df_edificios['confidence'] >= data.get('confidence_min', 0.0))]
            return len(sub) / ZONAS_BBOX.get(z_id, {}).get('area_km2', 1.0)

        d_a = get_density(data['zone_id_a'])
        d_b = get_density(data['zone_id_b'])

        return jsonify({
            "zone_a": float(d_a),
            "zone_b": float(d_b),
            "winner": data['zone_id_a'] if d_a > d_b else data['zone_id_b']
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query/q5', methods=['POST'])
def query_q5():
    """Distribución de confianza en una zona[cite: 146, 147]."""
    data = request.json
    try:
        subset = df_edificios[df_edificios['zone_id'] == data['zone_id']]
        bins = data.get('bins', 5)
        counts, edges = np.histogram(subset['confidence'], bins=bins, range=(0, 1))

        distribucion = []
        for i in range(len(counts)):
            distribucion.append({
                "bucket": i,
                "min": float(edges[i]),
                "max": float(edges[i+1]),
                "count": int(counts[i])
            })
        return jsonify(distribucion), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
