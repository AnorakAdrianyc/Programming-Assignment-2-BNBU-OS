#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_CONTENT_LENGTH = 100_000


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


class BridgeHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/bridge":
            self._send_json({"error": "not found"}, status=404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > MAX_CONTENT_LENGTH:
                self._send_json({"error": "payload too large"}, status=413)
                return

            raw = self.rfile.read(content_length)
            payload = json.loads(raw.decode("utf-8") if raw else "{}")
            processes = payload.get("processes", [])
            self._send_json({"timeline": compute_fcfs(processes), "source": "python-bridge"})
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
