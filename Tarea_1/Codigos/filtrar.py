import pandas as pd
ZONAS = {
    "Z1": {"lat_min": -33.445, "lat_max": -33.420, "lon_min": -70.640, "lon_max": -70.600},
    "Z2": {"lat_min": -33.420, "lat_max": -33.390, "lon_min": -70.600, "lon_max": -70.550},
    "Z3": {"lat_min": -33.530, "lat_max": -33.490, "lon_min": -70.790, "lon_max": -70.740},
    "Z4": {"lat_min": -33.460, "lat_max": -33.430, "lon_min": -70.670, "lon_max": -70.630},
    "Z5": {"lat_min": -33.470, "lat_max": -33.430, "lon_min": -70.810, "lon_max": -70.760}
}

def filtrar_edificios(input_csv, output_csv):
    print("Cargando dataset original (esto puede tardar)...")
    chunks = pd.read_csv(input_csv, chunksize=100000)
    
    lista_final = []

    for chunk in chunks:
        for z_id, coord in ZONAS.items():
            mask = (
                (chunk['latitude'] >= coord['lat_min']) & 
                (chunk['latitude'] <= coord['lat_max']) & 
                (chunk['longitude'] >= coord['lon_min']) & 
                (chunk['longitude'] <= coord['lon_max'])
            )
            df_zona = chunk[mask].copy()
            if not df_zona.empty:
                df_zona['zone_id'] = z_id 
                lista_final.append(df_zona)

    if lista_final:
        df_final = pd.concat(lista_final)
        df_final.to_csv(output_csv, index=False)
        print(f"Éxito! Archivo filtrado guardado en: {output_csv}")
        print(f"Total de edificios encontrados en las 5 zonas: {len(df_final)}")
    else:
        print("Error: No se encontraron edificios en las coordenadas especificadas.")

if __name__ == "__main__":
    filtrar_edificios('967_buildings.csv', 'metricas/buildings.csv')
