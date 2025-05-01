import argparse
import time
import random
from pymongo import MongoClient
import socket

def poisson_interarrival(lmbda):
    return random.expovariate(lmbda)

def uniform_interarrival(low, high):
    return random.uniform(low, high)

def query_cache(_id, host='localhost', port=5000):
    """Envía un ID al sistema de cache y retorna la respuesta."""
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall(f"{_id}\n".encode())
            return sock.recv(1024).decode().strip()
    except Exception as e:
        return f"ERROR {str(e)}"

def run_generator(dist, params, total_queries, mongo_uri, db_name, coll_name, cache_host, cache_port):
    client = MongoClient(mongo_uri)
    coll = client[db_name][coll_name]
    print(f"[Generator] Conectado a MongoDB → {db_name}.{coll_name}")

    ids = [doc['_id'] for doc in coll.find({}, {'_id': 1})]
    if not ids:
        print("No hay documentos en la colección, saliendo.")
        return

    print(f"[Generator] {len(ids)} IDs cargados. Generando {total_queries} consultas usando '{dist}'...")

    for i in range(1, total_queries + 1):
        wait = poisson_interarrival(params['lmbda']) if dist == 'poisson' else uniform_interarrival(params['low'], params['high'])
        time.sleep(wait)

        _id = random.choice(ids)
        t0 = time.time()
        result = query_cache(str(_id), host=cache_host, port=cache_port)
        latency = time.time() - t0

        print(f"[{i:04d}] Espera={wait:.3f}s · Respuesta={result} · Latencia={latency:.3f}s")

    print("[Generator] ¡Terminado!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de tráfico sintético para Waze events")
    parser.add_argument('--dist', choices=['poisson','uniform'], required=True,
                        help="Tipo de distribución de inter-arrival")
    parser.add_argument('--lmbda', type=float, default=1.0,
                        help="(poisson) Lambda (tasa media) para expovariate")
    parser.add_argument('--low', type=float, default=0.5,
                        help="(uniform) Límite inferior de inter-arrival (segundos)")
    parser.add_argument('--high', type=float, default=2.0,
                        help="(uniform) Límite superior de inter-arrival (segundos)")
    parser.add_argument('--n', type=int, default=100,
                        help="Número total de consultas a generar")
    parser.add_argument('--mongo', type=str, default="mongodb://localhost:27017/",
                        help="URI de conexión a MongoDB")
    parser.add_argument('--db', type=str, default="Waze",
                        help="Nombre de la base de datos")
    parser.add_argument('--coll', type=str, default="Peticiones",
                        help="Nombre de la colección")
    parser.add_argument('--cache_host', type=str, default='localhost',
                        help="Host del sistema de cache (por defecto: localhost)")
    parser.add_argument('--cache_port', type=int, default=5000,
                        help="Puerto del sistema de cache (por defecto: 5000)")

    args = parser.parse_args()
    params = {'lmbda': args.lmbda, 'low': args.low, 'high': args.high}

    run_generator(args.dist, params, args.n, args.mongo, args.db, args.coll, args.cache_host, args.cache_port)
