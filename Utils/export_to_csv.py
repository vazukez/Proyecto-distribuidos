from pymongo import MongoClient
import csv

# Conexión a MongoDB en el contenedor (expuesto en tu host)
client = MongoClient("mongodb://localhost:27017/")
db = client["Waze"]
collection = db["Peticiones"]

# Exportar CSV
with open("data/incidentes.csv", "w", newline='', encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow([
        "_id", "type", "subtype", "city", "pubMillis",
        "description", "id", "x", "y"
    ])

    for doc in collection.find():
        writer.writerow([
            str(doc.get("_id", "")),
            doc.get("type", ""),
            doc.get("subtype", ""),
            doc.get("city", ""),
            doc.get("pubMillis", ""),
            doc.get("description", "").replace("\n", " ").replace(",", " "),
            doc.get("id", ""),
            doc.get("location", {}).get("x", ""),
            doc.get("location", {}).get("y", "")
        ])
