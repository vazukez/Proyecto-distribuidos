import time
import json
import requests
from pymongo import MongoClient
from datetime import datetime

# API pública antigua de Waze (sigue funcionando en modo limitado)
WAZE_URL = "https://www.waze.com/live-map/api/georss"

# Región Metropolitana — zona más amplia (ajustable)
PARAMS = {
    "top": -33.3,
    "bottom": -33.6,
    "left": -70.8,
    "right": -70.5,
    "env": "row",
    "types": "alerts,traffic,users"
}

print("Conectando a MongoDB...")
client = MongoClient("mongodb://mongo:27017/")
db = client["Waze"]
collection = db["Eventos"]
print("Conexión a MongoDB exitosa.")

def fetch_events():
    r = requests.get(WAZE_URL, params=PARAMS, timeout=10)
    r.raise_for_status()
    data = r.json()
    events = []
    for section in ("alerts", "traffic", "users"):
        for e in data.get(section, []):
            e["type"] = section
            e["timestamp"] = datetime.utcnow().isoformat()
            events.append(e)
    return events

def main():
    while True:
        try:
            events = fetch_events()
            if events:
                print(f"[{datetime.now()}] Eventos capturados: {len(events)}")
                collection.insert_many(events)
                print(f"[{datetime.now()}] Insertados en MongoDB.")
            else:
                print(f"[{datetime.now()}] No se capturaron eventos.")
        except Exception as e:
            print(f"[{datetime.now()}] Error:", e)
        time.sleep(60)

if __name__ == "__main__":
    main()
