import argparse
import time
import random
import socket
from pymongo import MongoClient
from datetime import datetime
import csv

def poisson_interarrival(lmbda):
    return random.expovariate(lmbda)

def uniform_interarrival(low, high):
    return random.uniform(low, high)

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

def run_generator(dist, params, total_queries, mongo_uri, db_name, coll_name, cache_host, cache_port):
    client = MongoClient(mongo_uri)
    coll = client[db_name][coll_name]
    ids = [doc['_id'] for doc in coll.find({}, {'_id': 1})]

    if not ids:
        print("No se encontraron documentos.")
        return

    print(f"[Generator] {len(ids)} IDs cargados. Generando {total_queries} consultas usando '{dist}'...")
    csv_file = 'traffic_log.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'operation', 'id', 'status', 'latency'])

    for i in range(1, total_queries + 1):
        wait = poisson_interarrival(params['lmbda']) if dist == 'poisson' else uniform_interarrival(params['low'], params['high'])
        time.sleep(wait)

        _id = str(random.choice(ids))
        start = time.time()
        response = query_cache(_id, host=cache_host, port=cache_port)
        latency = time.time() - start
        timestamp = datetime.now().isoformat(timespec='seconds')

        if response.startswith("HIT"):
            operation, *_ = response.split()
            status = "HIT"
        elif response.startswith("MISS"):
            operation, *_ = response.split()
            status = "MISS"
        elif response.startswith("INVALID_ID"):
            operation = "GET"
            status = "INVALID"
        elif response.startswith("NOTFOUND"):
            operation = "GET"
            status = "NOTFOUND"
        elif response.startswith("ERROR"):
            operation = "GET"
            status = "ERROR"
        else:
            operation = "GET"
            status = "UNKNOWN"

        print(f"[{i:04d}] {operation} {_id} → {status} · {latency:.3f}s")
        log_to_csv(csv_file, [timestamp, operation, _id, status, round(latency, 4)])

    print("[Generator] Finalizado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de tráfico sintético para Waze events")
    parser.add_argument('--dist', choices=['poisson','uniform'], required=True)
    parser.add_argument('--lmbda', type=float, default=1.0)
    parser.add_argument('--low', type=float, default=0.5)
    parser.add_argument('--high', type=float, default=2.0)
    parser.add_argument('--n', type=int, default=100)
    parser.add_argument('--mongo', type=str, default="mongodb://localhost:27017/")
    parser.add_argument('--db', type=str, default="Waze")
    parser.add_argument('--coll', type=str, default="Peticiones")
    parser.add_argument('--cache_host', type=str, default='localhost')
    parser.add_argument('--cache_port', type=int, default=5000)

    args = parser.parse_args()
    params = {'lmbda': args.lmbda, 'low': args.low, 'high': args.high}
    run_generator(args.dist, params, args.n, args.mongo, args.db, args.coll, args.cache_host, args.cache_port)
