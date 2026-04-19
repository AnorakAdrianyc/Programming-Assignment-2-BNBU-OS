#!/usr/bin/env python3
import json
import subprocess
import tempfile
import os
import requests # For Ollama API interaction
from typing import List, Dict, Any
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_CONTENT_LENGTH = 100_000

OLLAMA_BASE_URL = "http://localhost:11434"


def compute_fcfs(processes):
    ordered = sorted(processes, key=lambda p: p.get("arrival", 0))
    clock = 0
    timeline = []

    for process in ordered:
        arrival = int(process.get("arrival", 0))
        burst = int(process.get("burst", 0))
        if clock < arrival:
            clock = arrival
        start = clock
        end = start + burst
        timeline.append({
            "name": process.get("name", "P?"),
            "arrival": arrival,
            "burst": burst,
            "start": start,
            "end": end,
            "wait": start - arrival,
            "turnaround": end - arrival,
        })
        clock = end

    return timeline


def validate_c_syntax(code):
    """Validate C code syntax using local gcc (preferred) or helper script."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as tf:
            tf.write(code.encode("utf-8"))
            tf.flush()
            tmp = tf.name

        # Try gcc first
        try:
            result = subprocess.run(
                ["gcc", "-fsyntax-only", tmp],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {"valid": result.returncode == 0, "errors": result.stderr, "warnings": result.stdout}
        except FileNotFoundError:
            # Fallback to provided helper script if gcc not available
            script_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "scripts", "check_c_syntax.sh"))
            try:
                result = subprocess.run(
                    [script_path, tmp],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return {"valid": result.returncode == 0, "errors": result.stderr, "warnings": result.stdout}
            except Exception as e:
                return {"valid": False, "errors": str(e)}
    except Exception as e:
        return {"valid": False, "errors": str(e)}
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except Exception:
                pass


def analyze_scheduling_code(code):
    """Simple heuristics to detect scheduling algorithm patterns in C source."""
    lower = code.lower()
    return {
        "fcfs": "enqueue_process(" in code,
        "sjf": "shortest" in lower or "sjf" in lower,
        "round_robin": "time_quantum" in lower or "quantum" in lower or "round_robin" in lower,
        "priority": "priority" in lower,
        "has_processes": "enqueue_process(" in code,
    }


class BridgeHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET") # Add GET for Ollama models
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET") # Add GET for Ollama models
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/cursor/ollama/models":
            self._list_ollama_models()
        else:
            if self.path in ("/", "/bridge"):
                self._send_json({
                    "message": "This endpoint accepts POST requests. Use POST with application/json.",
                    "example_bridge_post": {"processes": [{"name": "P1", "arrival": 0, "burst": 5}]},
                    "endpoints": ["/bridge (POST)", "/cursor/validate (POST)", "/cursor/analyze (POST)", "/cursor/suggest (POST)"]
                })
                return
            if self.path.startswith("/cursor"):
                self._send_json({
                    "message": "Cursor endpoints accept POST only. Use application/json body.",
                    "endpoints": ["/cursor/validate", "/cursor/analyze", "/cursor/suggest"]
                })
                return
            self._send_json({"error": "not found"}, status=404)

    def _list_ollama_models(self):
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            models_data = response.json().get("models", [])
            models = [{
                "name": m["name"]
            } for m in models_data]
            self._send_json(models)
        except requests.exceptions.RequestException as e:
            self._send_json({"error": f"Failed to fetch Ollama models: {e}"}, status=500)

    def _generate_with_ollama(self, payload):
        try:
            model = payload.get("model")
            prompt = payload.get("prompt")
            if not model or not prompt:
                self._send_json({"error": "Model and prompt are required"}, status=400)
                return

            response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
            response.raise_for_status()
            self._send_json(response.json())
        except requests.exceptions.RequestException as e:
            self._send_json({"error": f"Ollama generation failed: {e}"}, status=500)
        except Exception as e:
            self._send_json({"error": str(e)}, status=400)

    def do_POST(self):
        try:
            # Simple route dispatch for Cursor integration and existing /bridge endpoint
            allowed_paths = ("/bridge", "/cursor/validate", "/cursor/analyze", "/cursor/suggest", "/cursor/ollama/generate")
            if self.path not in allowed_paths:
                self._send_json({"error": "not found"}, status=404)
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > MAX_CONTENT_LENGTH:
                self._send_json({"error": "payload too large"}, status=413)
                return

            raw = self.rfile.read(content_length)
            payload = json.loads(raw.decode("utf-8") if raw else "{}")

            if self.path == "/bridge":
                processes = payload.get("processes", [])
                self._send_json({"timeline": compute_fcfs(processes), "source": "python-bridge"})
                return

            if self.path == "/cursor/validate":
                code = payload.get("code", "")
                result = validate_c_syntax(code)
                self._send_json(result)
                return

            if self.path == "/cursor/analyze":
                code = payload.get("code", "")
                patterns = analyze_scheduling_code(code)
                self._send_json({"patterns": patterns, "code_length": len(code)})
                return

            if self.path == "/cursor/suggest":
                processes = payload.get("processes", [])
                timeline = compute_fcfs(processes)
                avg_wait = sum(p["wait"] for p in timeline) / len(timeline) if timeline else 0
                avg_turnaround = sum(p["turnaround"] for p in timeline) / len(timeline) if timeline else 0
                self._send_json({
                    "suggested_algorithm": "FCFS",
                    "timeline": timeline,
                    "average_wait_time": avg_wait,
                    "average_turnaround": avg_turnaround
                })
                return
            
            if self.path == "/cursor/ollama/generate":
                self._generate_with_ollama(payload)
                return
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON in request body"}, status=400)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)


def run(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), BridgeHandler)
    print(f"Python bridge running at http://{host}:{port}/bridge")
    server.serve_forever()


if __name__ == "__main__":
    run()
