import time, json, requests
from pymongo import MongoClient

# Configuración bounding box RM Santiago
WAZE_URL = "https://www.waze.com/live-map/api/georss"
PARAMS = {
    "top": -33.44827714887085,
    "bottom": -33.45230544015461,
    "left": -70.6570887565613,
    "right": -70.64704656600954,
    "env": "row",
    "types": "alerts,traffic,users"
}

# Conexión a MongoDB
print("Conectando a MongoDB…")
client = MongoClient("mongodb://mongo:27017/")
db = client["Waze"]
collection = db["Peticiones"]
print("Conexión a MongoDB exitosa.")

def fetch_events():
    r = requests.get(WAZE_URL, params=PARAMS, timeout=15)
    r.raise_for_status()
    data = r.json()
    events = []
    for section in ("alerts", "traffic", "users"):
        events.extend(data.get(section, []))
    return events

def main():
    while True:
        try:
            events = fetch_events()
            if events:
                print(f"Eventos capturados: {len(events)}")
                ts = time.time()
                for e in events:
                    e["timestamp"] = ts
                collection.insert_many(events)
                print(f"Eventos insertados en MongoDB: {len(events)}")
            else:
                print("No se capturaron eventos esta vez.")
        except Exception as e:
            print("Error al obtener o insertar eventos:", e)
        time.sleep(60)

if __name__ == "__main__":
    main()
