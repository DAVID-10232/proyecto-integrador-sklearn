"""
Prueba de carga del servicio IA — versión corregida.
Usa httpx con keep-alive + 127.0.0.1 para evitar overhead de Windows.

Uso:
    python scripts/load_test.py --url http://127.0.0.1:8000 --requests 200 --concurrency 20
"""
import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
import httpx


def login(base_url: str, email: str, password: str) -> str:
    with httpx.Client() as client:
        resp = client.post(
            f"{base_url}/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


def run(base_url: str, requests: int, concurrency: int):
    print("=" * 60)
    print("PRUEBA DE CARGA — AI SERVICE")
    print("=" * 60)

    print(f"\nLogin...")
    token = login(base_url, "admin@rikinode.com", "admin123")
    print(f"✓ Token obtenido")

    texts = [
        "I love this product",
        "This is terrible",
        "Amazing quality!",
        "Do not buy",
        "Highly recommended",
    ] * (requests // 5 + 1)
    texts = texts[:requests]

    # Cliente HTTP compartido → reutiliza conexiones TCP (evita overhead)
    http = httpx.Client(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )

    print(f"\nWarmup (5 requests)...")
    for t in texts[:5]:
        http.post("/api/v1/predict/", json={"text": t})

    print(f"Enviando {requests} requests con concurrencia={concurrency}...\n")

    latencies = []
    successes = 0

    def do_request(text: str):
        start = time.perf_counter()
        try:
            resp = http.post("/api/v1/predict/", json={"text": text})
            ok = resp.status_code == 200
        except Exception:
            ok = False
        return time.perf_counter() - start, ok

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(do_request, t) for t in texts]
        for f in futures:
            elapsed, ok = f.result()
            latencies.append(elapsed)
            if ok:
                successes += 1
    total = time.perf_counter() - start
    http.close()

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print("=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"Requests totales:     {requests}")
    print(f"Exitosos:             {successes} ({successes/requests*100:.1f}%)")
    print(f"Fallidos:             {requests - successes}")
    print(f"Duración total:       {total:.2f} s")
    print(f"Throughput:           {requests/total:.1f} req/s")
    print(f"\nLatencia:")
    print(f"  P50:                {p50*1000:.1f} ms")
    print(f"  P95:                {p95*1000:.1f} ms")
    print(f"  P99:                {p99*1000:.1f} ms")
    print(f"  Min:                {min(latencies)*1000:.1f} ms")
    print(f"  Max:                {max(latencies)*1000:.1f} ms")
    print(f"  Promedio:           {statistics.mean(latencies)*1000:.1f} ms")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")   # ← IPv4
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()

    run(args.url, args.requests, args.concurrency)