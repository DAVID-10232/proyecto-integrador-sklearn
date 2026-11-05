"""
════════════════════════════════════════════════════════════════════════
  TEST COMPLETO DEL SISTEMA INTELIGENTE
  RikiNode AI Service — Proyecto Integrador
════════════════════════════════════════════════════════════════════════

Verifica:
  ✅ Health check
  ✅ Info del modelo
  ✅ Autenticación JWT (login válido/inválido)
  ✅ Predicción individual
  ✅ Predicción por lote
  ✅ Validación de datos
  ✅ Seguridad (sin token)
  ✅ Métricas Prometheus
  ✅ Rendimiento (latencia, throughput)

Genera un reporte con puntuación total (0-100).

Uso:
    python scripts/test_completo.py --url http://127.0.0.1:8000
"""
import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Tuple

import httpx


# ═══════════════════════════════════════════════════════════════════
# UTILIDADES DE PRESENTACIÓN
# ═══════════════════════════════════════════════════════════════════

class Colors:
    """Colores ANSI para terminal."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"
    GRAY = "\033[90m"


def header(title: str):
    print(f"\n{Colors.CYAN}{'═' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.CYAN}{'═' * 70}{Colors.END}")


def section(title: str):
    print(f"\n{Colors.BLUE}▶ {title}{Colors.END}")


def ok(msg: str):
    print(f"  {Colors.GREEN}✅ {msg}{Colors.END}")


def fail(msg: str):
    print(f"  {Colors.RED}❌ {msg}{Colors.END}")


def warn(msg: str):
    print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.END}")


def info(msg: str):
    print(f"  {Colors.GRAY}ℹ  {msg}{Colors.END}")


# ═══════════════════════════════════════════════════════════════════
# RESULTADO GLOBAL
# ═══════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.total = 0
        self.details: List[Tuple[str, str, str]] = []

    def add_pass(self, name: str, detail: str = ""):
        self.passed += 1
        self.total += 1
        self.details.append(("PASS", name, detail))

    def add_fail(self, name: str, detail: str = ""):
        self.failed += 1
        self.total += 1
        self.details.append(("FAIL", name, detail))

    def add_warn(self, name: str, detail: str = ""):
        self.warnings += 1
        self.total += 1
        self.details.append(("WARN", name, detail))

    @property
    def score(self) -> float:
        if self.total == 0:
            return 0.0
        # PASS = 1 punto, WARN = 0.5, FAIL = 0
        points = self.passed + (self.warnings * 0.5)
        return round((points / self.total) * 100, 1)

    @property
    def rating(self) -> str:
        if self.score >= 95:
            return "EXCELENTE"
        elif self.score >= 85:
            return "MUY BUENO"
        elif self.score >= 70:
            return "BUENO"
        elif self.score >= 50:
            return "ACEPTABLE"
        return "DEFICIENTE"


# ═══════════════════════════════════════════════════════════════════
# TEST SUITE
# ═══════════════════════════════════════════════════════════════════

class SystemTester:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.token: str = ""
        self.result = TestResult()
        self.performance_data: Dict = {}

    # ─────────────────────────────────────────────────────────────
    # 1. HEALTH & INFO
    # ─────────────────────────────────────────────────────────────
    def test_health(self):
        section("1. HEALTH CHECK")
        try:
            r = httpx.get(f"{self.base_url}/health", timeout=10)
            if r.status_code == 200:
                data = r.json()
                ok(f"GET /health → 200 OK")
                info(f"   status      = {data.get('status')}")
                info(f"   version     = {data.get('version')}")
                info(f"   model_loaded= {data.get('model_loaded')}")
                info(f"   model_name  = {data.get('model_name')}")

                if data.get("model_loaded"):
                    self.result.add_pass("Health check", "model_loaded=true")
                else:
                    self.result.add_fail("Health check", "model_loaded=false")
            else:
                fail(f"GET /health → {r.status_code}")
                self.result.add_fail("Health check", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Health check", str(e))

    def test_info(self):
        try:
            r = httpx.get(f"{self.base_url}/api/v1/info", timeout=10)
            if r.status_code == 200:
                data = r.json()
                ok(f"GET /api/v1/info → 200 OK")
                info(f"   service = {data.get('service')}")
                info(f"   model   = {data.get('model')}")
                self.result.add_pass("Info endpoint", "OK")
            else:
                fail(f"GET /api/v1/info → {r.status_code}")
                self.result.add_fail("Info endpoint", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Info endpoint", str(e))

    # ─────────────────────────────────────────────────────────────
    # 2. AUTENTICACIÓN
    # ─────────────────────────────────────────────────────────────
    def test_auth(self):
        section("2. AUTENTICACIÓN JWT")

        # 2.1 Login válido
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": self.email, "password": self.password},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                self.token = data.get("access_token", "")
                ok(f"POST /auth/login (válido) → 200 OK")
                info(f"   token      = {self.token[:40]}...")
                info(f"   token_type = {data.get('token_type')}")
                info(f"   expires_in = {data.get('expires_in')}s")
                self.result.add_pass("Login válido", "JWT obtenido")
            else:
                fail(f"POST /auth/login → {r.status_code}")
                self.result.add_fail("Login válido", f"status={r.status_code}")
                return
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Login válido", str(e))
            return

        # 2.2 Login con password incorrecta
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": self.email, "password": "wrong_pass"},
                timeout=10,
            )
            if r.status_code == 401:
                ok(f"POST /auth/login (incorrecto) → 401 Unauthorized ✅")
                self.result.add_pass("Rechazo de credenciales inválidas", "401")
            else:
                fail(f"POST /auth/login (incorrecto) → {r.status_code} (esperado 401)")
                self.result.add_fail("Rechazo de credenciales inválidas", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Rechazo de credenciales inválidas", str(e))

    # ─────────────────────────────────────────────────────────────
    # 3. PREDICCIÓN INDIVIDUAL
    # ─────────────────────────────────────────────────────────────
    def _auth_headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def test_predict_single(self):
        section("3. PREDICCIÓN INDIVIDUAL")

        # 3.1 POSITIVE
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/",
                headers=self._auth_headers(),
                json={"text": "I love this product, it is amazing!"},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                ok(f"POST /predict/ (positivo) → 200 OK")
                info(f"   label = {data.get('label')}")
                info(f"   score = {data.get('score')}")
                info(f"   model = {data.get('model')}")

                if data.get("label") == "POSITIVE":
                    self.result.add_pass("Predicción POSITIVE", f"label={data.get('label')}")
                else:
                    self.result.add_fail("Predicción POSITIVE", f"label={data.get('label')}")

                # Verificar campo score
                if "score" in data and isinstance(data["score"], (int, float)):
                    self.result.add_pass("Campo 'score' presente", f"score={data['score']}")
                else:
                    self.result.add_fail("Campo 'score' presente", "score ausente")
            else:
                fail(f"POST /predict/ → {r.status_code}")
                self.result.add_fail("Predicción POSITIVE", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Predicción POSITIVE", str(e))

        # 3.2 NEGATIVE
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/",
                headers=self._auth_headers(),
                json={"text": "This is terrible, I hate it."},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                ok(f"POST /predict/ (negativo) → 200 OK")
                info(f"   label = {data.get('label')}")
                info(f"   score = {data.get('score')}")

                if data.get("label") == "NEGATIVE":
                    self.result.add_pass("Predicción NEGATIVE", f"label={data.get('label')}")
                else:
                    self.result.add_fail("Predicción NEGATIVE", f"label={data.get('label')}")
            else:
                fail(f"POST /predict/ → {r.status_code}")
                self.result.add_fail("Predicción NEGATIVE", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Predicción NEGATIVE", str(e))

    # ─────────────────────────────────────────────────────────────
    # 4. PREDICCIÓN BATCH
    # ─────────────────────────────────────────────────────────────
    def test_predict_batch(self):
        section("4. PREDICCIÓN POR LOTE")

        try:
            texts = [
                "Amazing quality, highly recommended",
                "Terrible service, do not buy",
                "Excellent product",
                "Worst purchase ever",
            ]
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/batch",
                headers=self._auth_headers(),
                json={"texts": texts},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                ok(f"POST /predict/batch → 200 OK")
                info(f"   requests = {len(texts)}")
                info(f"   results  = {len(results)}")
                for i, res in enumerate(results, 1):
                    info(f"   [{i}] {res.get('label'):9s} score={res.get('score')}")

                if len(results) == len(texts):
                    self.result.add_pass("Batch predictions", f"{len(results)} resultados")
                else:
                    self.result.add_fail("Batch predictions", f"esperado {len(texts)}, obtenido {len(results)}")
            else:
                fail(f"POST /predict/batch → {r.status_code}")
                self.result.add_fail("Batch predictions", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Batch predictions", str(e))

    # ─────────────────────────────────────────────────────────────
    # 5. VALIDACIÓN DE DATOS
    # ─────────────────────────────────────────────────────────────
    def test_validation(self):
        section("5. VALIDACIÓN DE DATOS")

        # 5.1 Texto vacío → 422
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/",
                headers=self._auth_headers(),
                json={"text": ""},
                timeout=10,
            )
            if r.status_code == 422:
                ok(f"POST /predict/ (texto vacío) → 422 ✅")
                self.result.add_pass("Validación texto vacío", "422")
            else:
                fail(f"POST /predict/ (texto vacío) → {r.status_code} (esperado 422)")
                self.result.add_fail("Validación texto vacío", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Validación texto vacío", str(e))

        # 5.2 Campo faltante → 422
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/",
                headers=self._auth_headers(),
                json={},
                timeout=10,
            )
            if r.status_code == 422:
                ok(f"POST /predict/ (sin 'text') → 422 ✅")
                self.result.add_pass("Validación campo faltante", "422")
            else:
                fail(f"POST /predict/ (sin 'text') → {r.status_code} (esperado 422)")
                self.result.add_fail("Validación campo faltante", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Validación campo faltante", str(e))

        # 5.3 Batch vacío → 422
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/batch",
                headers=self._auth_headers(),
                json={"texts": []},
                timeout=10,
            )
            if r.status_code == 422:
                ok(f"POST /predict/batch (lista vacía) → 422 ✅")
                self.result.add_pass("Validación batch vacío", "422")
            else:
                fail(f"POST /predict/batch (lista vacía) → {r.status_code} (esperado 422)")
                self.result.add_fail("Validación batch vacío", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Validación batch vacío", str(e))

    # ─────────────────────────────────────────────────────────────
    # 6. SEGURIDAD
    # ─────────────────────────────────────────────────────────────
    def test_security(self):
        section("6. SEGURIDAD Y CONTROL DE ACCESO")

        # 6.1 Sin token → 401/403
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/",
                json={"text": "test"},
                timeout=10,
            )
            if r.status_code in (401, 403):
                ok(f"POST /predict/ (sin token) → {r.status_code} ✅")
                self.result.add_pass("Rechazo sin token", f"status={r.status_code}")
            else:
                fail(f"POST /predict/ (sin token) → {r.status_code} (esperado 401/403)")
                self.result.add_fail("Rechazo sin token", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Rechazo sin token", str(e))

        # 6.2 Token inválido → 401/403
        try:
            r = httpx.post(
                f"{self.base_url}/api/v1/predict/",
                headers={"Authorization": "Bearer token_falso_12345"},
                json={"text": "test"},
                timeout=10,
            )
            if r.status_code in (401, 403):
                ok(f"POST /predict/ (token inválido) → {r.status_code} ✅")
                self.result.add_pass("Rechazo token inválido", f"status={r.status_code}")
            else:
                fail(f"POST /predict/ (token inválido) → {r.status_code} (esperado 401/403)")
                self.result.add_fail("Rechazo token inválido", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Rechazo token inválido", str(e))

    # ─────────────────────────────────────────────────────────────
    # 7. MÉTRICAS PROMETHEUS
    # ─────────────────────────────────────────────────────────────
    def test_metrics(self):
        section("7. MÉTRICAS PROMETHEUS")

        try:
            r = httpx.get(f"{self.base_url}/metrics", timeout=10)
            if r.status_code == 200:
                text = r.text

                # Métricas esperadas
                checks = [
                    ("ai_predictions_total", "Contador de predicciones"),
                    ("ai_prediction_latency_seconds", "Histograma de latencia"),
                    ("ai_model_loaded", "Gauge del modelo"),
                    ("http_requests_total", "Contador HTTP (auto)"),
                ]

                for metric_name, desc in checks:
                    if metric_name in text:
                        ok(f"Métrica '{metric_name}' presente ({desc})")
                        self.result.add_pass(f"Métrica {metric_name}", "presente")
                    else:
                        warn(f"Métrica '{metric_name}' ausente")
                        self.result.add_warn(f"Métrica {metric_name}", "ausente")

                # Extraer valor de ai_predictions_total
                for line in text.split("\n"):
                    if line.startswith("ai_predictions_total{") and "POSITIVE" in line:
                        info(f"   {line.strip()}")
                    if line.startswith("ai_predictions_total{") and "NEGATIVE" in line:
                        info(f"   {line.strip()}")
                    if line.startswith("ai_model_loaded "):
                        info(f"   {line.strip()}")
            else:
                fail(f"GET /metrics → {r.status_code}")
                self.result.add_fail("Endpoint /metrics", f"status={r.status_code}")
        except Exception as e:
            fail(f"Error: {e}")
            self.result.add_fail("Endpoint /metrics", str(e))

    # ─────────────────────────────────────────────────────────────
    # 8. RENDIMIENTO
    # ─────────────────────────────────────────────────────────────
    def test_performance(self, requests: int = 100, concurrency: int = 10):
        section(f"8. RENDIMIENTO ({requests} req, concurrencia {concurrency})")

        texts = [
            "I love this product",
            "This is terrible",
            "Amazing quality!",
            "Do not buy",
            "Highly recommended",
        ] * (requests // 5 + 1)
        texts = texts[:requests]

        http = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        # Warmup
        for t in texts[:5]:
            http.post("/api/v1/predict/", json={"text": t})

        latencies = []
        successes = 0

        def do_request(text: str):
            start = time.perf_counter()
            try:
                resp = http.post("/api/v1/predict/", json={"text": text})
                ok_flag = resp.status_code == 200
            except Exception:
                ok_flag = False
            return time.perf_counter() - start, ok_flag

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(do_request, t) for t in texts]
            for f in futures:
                elapsed, ok_flag = f.result()
                latencies.append(elapsed)
                if ok_flag:
                    successes += 1
        total = time.perf_counter() - start
        http.close()

        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg = statistics.mean(latencies)
        throughput = requests / total

        self.performance_data = {
            "requests": requests,
            "successes": successes,
            "failures": requests - successes,
            "duration_s": round(total, 2),
            "throughput_rps": round(throughput, 1),
            "p50_ms": round(p50 * 1000, 1),
            "p95_ms": round(p95 * 1000, 1),
            "p99_ms": round(p99 * 1000, 1),
            "avg_ms": round(avg * 1000, 1),
            "min_ms": round(min(latencies) * 1000, 1),
            "max_ms": round(max(latencies) * 1000, 1),
        }

        info(f"   Requests exitosos: {successes}/{requests} ({successes/requests*100:.1f}%)")
        info(f"   Duración total:    {total:.2f} s")
        info(f"   Throughput:        {throughput:.1f} req/s")
        info(f"   P50:               {p50*1000:.1f} ms")
        info(f"   P95:               {p95*1000:.1f} ms")
        info(f"   P99:               {p99*1000:.1f} ms")
        info(f"   Promedio:          {avg*1000:.1f} ms")

        # Criterios de aceptación
        if successes == requests:
            self.result.add_pass("Throughput 100% exitoso", f"{successes}/{requests}")
        else:
            self.result.add_fail("Throughput 100% exitoso", f"{successes}/{requests}")

        if p95 * 1000 < 500:
            self.result.add_pass("P95 < 500 ms", f"{p95*1000:.1f} ms")
        elif p95 * 1000 < 1000:
            self.result.add_warn("P95 < 500 ms", f"{p95*1000:.1f} ms (aceptable)")
        else:
            self.result.add_fail("P95 < 500 ms", f"{p95*1000:.1f} ms")

        if throughput >= 30:
            self.result.add_pass("Throughput ≥ 30 req/s", f"{throughput:.1f} req/s")
        elif throughput >= 10:
            self.result.add_warn("Throughput ≥ 30 req/s", f"{throughput:.1f} req/s")
        else:
            self.result.add_fail("Throughput ≥ 30 req/s", f"{throughput:.1f} req/s")

    # ─────────────────────────────────────────────────────────────
    # REPORTE FINAL
    # ─────────────────────────────────────────────────────────────
    def run_all(self, perf_requests: int = 100, perf_concurrency: int = 10):
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║      TEST COMPLETO — RikiNode AI Service                        ║")
        print("║      Proyecto Integrador — Implementación de Sistemas IA        ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        info(f"URL:       {self.base_url}")
        info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.test_health()
        self.test_info()
        self.test_auth()
        self.test_predict_single()
        self.test_predict_batch()
        self.test_validation()
        self.test_security()
        self.test_metrics()
        self.test_performance(perf_requests, perf_concurrency)

        self.print_report()

    def print_report(self):
        header("📊 REPORTE FINAL")

        # Detalle por test
        print(f"\n{Colors.BOLD}Detalle de cada prueba:{Colors.END}\n")
        for status, name, detail in self.result.details:
            if status == "PASS":
                icon = f"{Colors.GREEN}✅{Colors.END}"
            elif status == "FAIL":
                icon = f"{Colors.RED}❌{Colors.END}"
            else:
                icon = f"{Colors.YELLOW}⚠️ {Colors.END}"

            line = f"  {icon}  {name:42s}"
            if detail:
                line += f" {Colors.GRAY}({detail}){Colors.END}"
            print(line)

        # Resumen
        print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}")
        print(f"{Colors.BOLD}  RESUMEN{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
        print(f"  Total de pruebas:  {self.result.total}")
        print(f"  {Colors.GREEN}✅ Exitosas:       {self.result.passed}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠️  Advertencias:   {self.result.warnings}{Colors.END}")
        print(f"  {Colors.RED}❌ Fallidas:       {self.result.failed}{Colors.END}")

        # Score
        score = self.result.score
        rating = self.result.rating

        print(f"\n{Colors.BOLD}  PUNTUACIÓN FINAL:{Colors.END}")

        if score >= 85:
            color = Colors.GREEN
        elif score >= 70:
            color = Colors.YELLOW
        else:
            color = Colors.RED

        bar_filled = int(score / 2)  # 50 caracteres max
        bar = "█" * bar_filled + "░" * (50 - bar_filled)
        print(f"  {color}{bar}{Colors.END}")
        print(f"  {color}{Colors.BOLD}  {score}/100  →  {rating}{Colors.END}")

        # Performance summary
        if self.performance_data:
            print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}")
            print(f"{Colors.BOLD}  RENDIMIENTO{Colors.END}")
            print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
            p = self.performance_data
            print(f"  Requests:      {p['requests']} ({p['successes']} OK, {p['failures']} FAIL)")
            print(f"  Duración:      {p['duration_s']} s")
            print(f"  Throughput:    {p['throughput_rps']} req/s")
            print(f"  Latencia P50:  {p['p50_ms']} ms")
            print(f"  Latencia P95:  {p['p95_ms']} ms")
            print(f"  Latencia P99:  {p['p99_ms']} ms")
            print(f"  Promedio:      {p['avg_ms']} ms")

        # Veredicto
        print(f"\n{Colors.CYAN}{'═' * 70}{Colors.END}")
        if score >= 85:
            print(f"{Colors.GREEN}{Colors.BOLD}  ✅ SISTEMA APROBADO — Cumple con los requisitos{Colors.END}")
        elif score >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}  ⚠️  SISTEMA ACEPTABLE — Revisar advertencias{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}  ❌ SISTEMA CON FALLAS — Corregir antes de entregar{Colors.END}")
        print(f"{Colors.CYAN}{'═' * 70}{Colors.END}\n")

        # Código de salida
        sys.exit(0 if score >= 70 else 1)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Test completo del sistema inteligente"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="URL base del servicio",
    )
    parser.add_argument(
        "--email",
        default="admin@rikinode.com",
        help="Email del usuario admin",
    )
    parser.add_argument(
        "--password",
        default="admin123",
        help="Password del usuario admin",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Requests para prueba de carga",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Concurrencia para prueba de carga",
    )
    args = parser.parse_args()

    tester = SystemTester(args.url, args.email, args.password)
    tester.run_all(args.requests, args.concurrency)


if __name__ == "__main__":
    main()