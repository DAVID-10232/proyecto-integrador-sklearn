"""
Prueba de carga del servicio IA.
Mide latencia (P50, P95, P99), throughput y tasa de éxito.

Uso:
    python scripts/load_test.py --url http://localhost:8000 --requests 100
"""
import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import urllib.parse
import json


def login(base_url: str, email: str, password: str) -> str:
    data = urllib.parse.urlencode({"username": email, "password": password}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def predict_once(base_url: str, token: str, text: str) -> tuple:
    start = time.perf_counter()
    ok = False
    try:
        body = json.dumps({"text": text}).encode()
        req = urllib.request.Request(
            f"{base_url}/api/v1/predict/",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()
            ok = resp.status == 200
    except Exception:
        ok = False
    elapsed = time.perf_counter() - start
    return elapsed, ok


def run(base_url: str, requests: int, concurrency: int, email: str, password: str):
    print("=" * 60)
    print("PRUEBA DE CARGA — AI SERVICE")
    print("=" * 60)

    print("\nLogin...")
    token = login(base_url, email, password)
    print("✓ Token obtenido")

    texts = [
        "I love this product",
        "This is terrible",
        "Amazing quality!",
        "Do not buy",
        "Highly recommended",
    ] * (requests // 5 + 1)
    texts = texts[:requests]

    print(f"\nEnviando {requests} requests con concurrencia={concurrency}...")
    latencies = []
    successes = 0

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(predict_once, base_url, token, t)
            for t in texts
        ]
        for f in futures:
            elapsed, ok = f.result()
            latencies.append(elapsed)
            if ok:
                successes += 1
    total = time.perf_counter() - start

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[min(int(len(latencies) * 0.95), len(latencies) - 1)]
    p99 = latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)]

    print(f"\n{'=' * 60}")
    print("RESULTADOS")
    print(f"{'=' * 60}")
    print(f"Requests totales:     {requests}")
    print(f"Exitosos:             {successes} ({successes/requests*100:.1f}%)")
    print(f"Fallidos:             {requests - successes}")
    print(f"Duración total:       {total:.2f} s")
    print(f"Throughput:           {requests/total:.1f} req/s")
    print("\nLatencia:")
    print(f"  P50:                {p50*1000:.1f} ms")
    print(f"  P95:                {p95*1000:.1f} ms")
    print(f"  P99:                {p99*1000:.1f} ms")
    print(f"  Min:                {min(latencies)*1000:.1f} ms")
    print(f"  Max:                {max(latencies)*1000:.1f} ms")
    print(f"  Promedio:           {statistics.mean(latencies)*1000:.1f} ms")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--email", default="admin@rikinode.com")
    parser.add_argument("--password", default="admin123")
    args = parser.parse_args()

    run(args.url, args.requests, args.concurrency, args.email, args.password)
