import os
import csv
import requests

ELASTIC_URL = "http://localhost:9200"
OUTPUT_DIR = "data/output"

# Mapas para personalizar nombre de índice y estructura de campos
INDEX_MAP = {
    "top_comunas": ["comuna", "cantidad"],
    "top_tipos": ["tipo", "cantidad"],
    "tipo": ["tipo", "cantidad"],
    "comuna": ["comuna", "cantidad"],
    "tipo_comuna": ["tipo", "comuna", "cantidad"],
    "usuarios_por_zona": ["x_zone", "y_zone", "cantidad"],
    "zona_mas_concurrida": ["x_zone", "y_zone", "cantidad"]
}

def index_csv(file_path, index_name, fields):
    print(f"→ Indexando {file_path} → índice: {index_name}")
    # Eliminar índice anterior si existe
    requests.delete(f"{ELASTIC_URL}/{index_name}")
    
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != len(fields):
                print(f"  ⚠️ Fila inválida en {index_name}: {row}")
                continue
            doc = {field: try_parse(value) for field, value in zip(fields, row)}
            requests.post(f"{ELASTIC_URL}/{index_name}/_doc", json=doc)

def try_parse(val):
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val.strip()

# Buscar archivo válido dentro de cada subcarpeta
for folder, fields in INDEX_MAP.items():
    folder_path = os.path.join(OUTPUT_DIR, folder)
    if not os.path.isdir(folder_path):
        print(f"⛔ Carpeta no encontrada: {folder_path}")
        continue

    found = False
    for file in os.listdir(folder_path):
        if file.startswith("part-"):
            full_path = os.path.join(folder_path, file)
            index_csv(full_path, folder, fields)
            found = True
            break

    if not found:
        print(f"⛔ No se encontró archivo 'part-*' en: {folder_path}")
