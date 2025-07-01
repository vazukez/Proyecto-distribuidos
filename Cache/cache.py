from collections import OrderedDict
import socket
import time
import argparse
import json
import requests

class LRUCache:
    def __init__(self, size):
        self.size = size
        self.cache = {}
        self.order = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.order:
            self.order.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key, value):
        if key in self.order:
            self.order.move_to_end(key)
        else:
            if len(self.order) >= self.size:
                old_key = next(iter(self.order))
                self.order.pop(old_key)
                self.cache.pop(old_key)
            self.order[key] = None
        self.cache[key] = value

    def stats(self):
        return {"hits": self.hits, "misses": self.misses}

def fetch_from_elastic(elastic_url, index, doc_id):
    try:
        url = f"{elastic_url}/{index}/_search"
        query = {
            "query": {
                "term": {
                    "id.keyword": doc_id
                }
            }
        }
        res = requests.post(url, json=query)
        if res.status_code == 200:
            hits = res.json().get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_source"]
        return None
    except Exception as e:
        print(f"[Elastic] Error al consultar '{doc_id}': {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=100)
    parser.add_argument('--elastic', default='http://elasticsearch:9200')
    parser.add_argument('--index', default='eventos_waze')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    print(f"[Cache] LRU Cache iniciado con tamaño {args.size}")
    print(f"[Cache] Consultando Elasticsearch en {args.elastic}, índice '{args.index}'")

    cache = LRUCache(args.size)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", args.port))
    server.listen(5)
    print(f"[Cache] Esperando conexiones en puerto {args.port}...")

    while True:
        conn, addr = server.accept()
        with conn:
            key = conn.recv(1024).decode().strip()
            if not key:
                continue

            if key.upper() == "STATS":
                stats = cache.stats()
                conn.sendall(json.dumps(stats).encode())
                continue

            start = time.time()
            doc = cache.get(key)
            if doc:
                latency = time.time() - start
                response = f"HIT {key} ({latency:.4f}s)\n{json.dumps(doc)}\n"
                conn.sendall(response.encode())
            else:
                doc = fetch_from_elastic(args.elastic, args.index, key)
                if doc:
                    cache.put(key, doc)
                    latency = time.time() - start
                    response = f"MISS {key} ({latency:.4f}s)\n{json.dumps(doc)}\n"
                    conn.sendall(response.encode())
                else:
                    conn.sendall(f"NOTFOUND {key}\n".encode())

if __name__ == "__main__":
    main()
