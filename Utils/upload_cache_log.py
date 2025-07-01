import csv
import requests

ELASTIC_URL = "http://localhost:9200"
INDEX_NAME = "trafico_cache"
CSV_FILE = "traffic_log.csv"

# 1. Borrar índice anterior si existe
print(f"🧹 Eliminando índice anterior '{INDEX_NAME}' si existe...")
requests.delete(f"{ELASTIC_URL}/{INDEX_NAME}")

# 2. Crear nuevo índice con mapping
mapping = {
    "mappings": {
        "properties": {
            "timestamp": { "type": "date" },
            "operation": { "type": "keyword" },
            "id": { "type": "keyword" },
            "status": { "type": "keyword" },
            "latency": { "type": "float" }
        }
    }
}
print(f"📦 Creando índice '{INDEX_NAME}'...")
res = requests.put(f"{ELASTIC_URL}/{INDEX_NAME}", json=mapping)
if res.status_code != 200:
    print("⛔ Error creando índice:", res.text)
    exit(1)

# 3. Leer el CSV y subir a Elasticsearch
print(f"📤 Subiendo registros desde {CSV_FILE}...")
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        doc = {
            "timestamp": row["timestamp"],
            "operation": row["operation"],
            "id": row["id"],
            "status": row["status"],
            "latency": float(row["latency"])
        }
        r = requests.post(f"{ELASTIC_URL}/{INDEX_NAME}/_doc", json=doc)
        if r.status_code not in (200, 201):
            print("⛔ Error al subir doc:", r.text)

print("✅ Upload completado.")
