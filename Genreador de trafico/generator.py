import argparse
import time
import random
import socket
import requests
from datetime import datetime
import csv

def poisson_interarrival(lmbda):
    return random.expovariate(lmbda)

def query_cache(_id, host='localhost', port=5000):
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall(f"{_id}\n".encode())
            response = sock.recv(2048).decode().strip()
            return response
    except Exception as e:
        return f"ERROR {str(e)}"

def log_to_csv(filepath, row):
    with open(filepath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def get_ids_from_elastic(elastic_url, index, limit=1000):
    try:
        query = {
            "_source": ["id"],
            "size": limit,
            "query": { "match_all": {} }
        }
        r = requests.post(f"{elastic_url}/{index}/_search", json=query)
        if r.status_code == 200:
            results = r.json()["hits"]["hits"]
            return [doc["_source"]["id"] for doc in results if "id" in doc["_source"]]
        else:
            print("Error al consultar Elasticsearch:", r.text)
            return []
    except Exception as e:
        print("Error:", e)
        return []

def run_generator(lmbda, total_queries, elastic_url, index, cache_host, cache_port):
    ids = get_ids_from_elastic(elastic_url, index)
    if not ids:
        print("⛔ No se encontraron IDs válidos en Elasticsearch.")
        return

    print(f"[Generator] {len(ids)} IDs cargados desde Elastic. Generando {total_queries} consultas (Poisson λ={lmbda})...")
    csv_file = 'traffic_log.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'operation', 'id', 'status', 'latency'])

    for i in range(1, total_queries + 1):
        wait = poisson_interarrival(lmbda)
        time.sleep(wait)

        _id = str(random.choice(ids))
        start = time.time()
        response = query_cache(_id, host=cache_host, port=cache_port)
        latency = time.time() - start
        timestamp = datetime.now().isoformat(timespec='seconds')

        if response.startswith("HIT"):
            status = "HIT"
        elif response.startswith("MISS"):
            status = "MISS"
        elif response.startswith("INVALID_ID"):
            status = "INVALID"
        elif response.startswith("NOTFOUND"):
            status = "NOTFOUND"
        elif response.startswith("ERROR"):
            status = "ERROR"
        else:
            status = "UNKNOWN"

        print(f"[{i:04d}] {_id} → {status} · {latency:.3f}s")
        log_to_csv(csv_file, [timestamp, "GET", _id, status, round(latency, 4)])

    print("[Generator] Finalizado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de tráfico para caché con Elasticsearch")
    parser.add_argument('--lmbda', type=float, default=1.0)
    parser.add_argument('--n', type=int, default=100)
    parser.add_argument('--elastic', type=str, default="http://elasticsearch:9200")
    parser.add_argument('--index', type=str, default="eventos_waze")
    parser.add_argument('--cache_host', type=str, default='localhost')
    parser.add_argument('--cache_port', type=int, default=5000)

    args = parser.parse_args()
    run_generator(args.lmbda, args.n, args.elastic, args.index, args.cache_host, args.cache_port)
