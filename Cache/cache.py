from collections import OrderedDict, defaultdict
from pymongo import MongoClient
from bson import ObjectId
import socket
import time
import argparse

class CacheBase:
    def __init__(self, size):
        self.size = size
        self.cache = {}

    def get(self, key):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

class LRUCache(CacheBase):
    def __init__(self, size):
        super().__init__(size)
        self.order = OrderedDict()

    def get(self, key):
        if key in self.order:
            self.order.move_to_end(key)
            return self.cache[key]
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

class LFUCache(CacheBase):
    def __init__(self, size):
        super().__init__(size)
        self.freq = defaultdict(int)

    def get(self, key):
        if key in self.cache:
            self.freq[key] += 1
            return self.cache[key]
        return None

    def put(self, key, value):
        if key not in self.cache and len(self.cache) >= self.size:
            least_used = min(self.freq, key=lambda k: self.freq[k])
            del self.cache[least_used]
            del self.freq[least_used]
        self.cache[key] = value
        self.freq[key] += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--policy', choices=['lru', 'lfu'], required=True)
    parser.add_argument('--size', type=int, default=100)
    parser.add_argument('--mongo', default='mongodb://localhost:27017/')
    parser.add_argument('--db', default='Waze')
    parser.add_argument('--coll', default='Peticiones')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    print(f"[Cache] Iniciando con política {args.policy.upper()} y tamaño {args.size}")
    cache = LRUCache(args.size) if args.policy == 'lru' else LFUCache(args.size)

    client = MongoClient(args.mongo)
    collection = client[args.db][args.coll]

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

            start = time.time()
            doc = cache.get(key)
            if doc:
                latency = time.time() - start
                conn.sendall(f"HIT {key} ({latency:.4f}s)\n".encode())
            else:
                try:
                    object_id = ObjectId(key)
                except Exception:
                    conn.sendall(f"INVALID_ID {key}\n".encode())
                    continue

                doc = collection.find_one({"_id": object_id})
                if doc:
                    cache.put(key, doc)
                    latency = time.time() - start
                    conn.sendall(f"MISS {key} ({latency:.4f}s)\n".encode())
                else:
                    conn.sendall(f"NOTFOUND {key}\n".encode())

if __name__ == "__main__":
    main()
