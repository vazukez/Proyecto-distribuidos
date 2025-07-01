from pymongo import MongoClient
import requests
import time

MONGO_URI = "host.docker.internal:27017"
ELASTIC_URL = "http://localhost:9200"
INDEX_NAME = "eventos_waze"

# 1. Eliminar índice anterior si existe
print(f"🧹 Borrando índice anterior '{INDEX_NAME}' si existe...")
requests.delete(f"{ELASTIC_URL}/{INDEX_NAME}")

# 2. Crear índice con mapping correcto
print("📦 Creando índice con mapping 'geo_point'...")
mapping = {
    "mappings": {
        "properties": {
            "location": { "type": "geo_point" },
            "timestamp": { "type": "date" }
        }
    }
}
r = requests.put(f"{ELASTIC_URL}/{INDEX_NAME}", json=mapping)
if r.status_code != 200:
    print("⛔ Error creando índice:", r.text)
    exit(1)

# 3. Conexión a MongoDB
print("🔌 Conectando a MongoDB...")
client = MongoClient(MONGO_URI)
collection = client["Waze"]["Eventos"]

# 4. Insertar documentos en Elasticsearch
print("🚀 Indexando documentos...")

for doc in collection.find():
    location = doc.get("location", {})
    x = location.get("x", None)
    y = location.get("y", None)

    pubMillis = doc.get("pubMillis")
    if isinstance(pubMillis, dict) and "$numberLong" in pubMillis:
        pubMillis = int(pubMillis["$numberLong"])
    elif isinstance(pubMillis, str):
        try:
            pubMillis = int(pubMillis)
        except:
            pubMillis = None

    doc_clean = {
        "id": doc.get("id", ""),
        "type": doc.get("type", ""),
        "subtype": doc.get("subtype", ""),
        "city": doc.get("city", ""),
        "timestamp": doc.get("timestamp", ""),
        "pubMillis": pubMillis,
        "x": x,
        "y": y,
        "location": f"{y},{x}" if x is not None and y is not None else None  # geo_point formato correcto
    }

    try:
        r = requests.post(f"{ELASTIC_URL}/{INDEX_NAME}/_doc", json=doc_clean)
        if r.status_code not in (200, 201):
            print("⛔ Error al indexar:", r.text)
    except Exception as e:
        print("💥 Error:", e)

    time.sleep(0.05)

print("✅ Indexación completada.")
