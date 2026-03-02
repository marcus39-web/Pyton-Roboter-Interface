import argparse
import json
import math
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class MapSimulation:
    """Lokale Kartierungs-Simulation für mehrere virtuelle Roboter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.width = 900
        self.height = 600
        self.running = True
        self.tick = 0
        # Snapshot-Speicher lokal im Projekt (ohne externe DB).
        self.snapshot_dir = Path(__file__).with_name("map_snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._init_world()

    def _init_world(self) -> None:
        # Feste Hindernisse für reproduzierbare Tests.
        self.obstacles = [
            {"x": 220, "y": 120, "w": 140, "h": 90},
            {"x": 520, "y": 200, "w": 180, "h": 80},
            {"x": 300, "y": 390, "w": 120, "h": 120},
        ]

        # Drei virtuelle Roboter mit eigener Spur.
        self.robots = [
            {
                "id": "R1",
                "color": "#4dabf7",
                "x": 80.0,
                "y": 80.0,
                "heading": 0.0,
                "speed": 2.4,
                "trail": [],
            },
            {
                "id": "R2",
                "color": "#69db7c",
                "x": 780.0,
                "y": 100.0,
                "heading": math.pi,
                "speed": 2.0,
                "trail": [],
            },
            {
                "id": "R3",
                "color": "#ffd43b",
                "x": 450.0,
                "y": 520.0,
                "heading": -math.pi / 2,
                "speed": 2.2,
                "trail": [],
            },
        ]

    def set_running(self, running: bool) -> None:
        with self._lock:
            self.running = running

    def reset(self) -> None:
        with self._lock:
            self.tick = 0
            self.running = True
            self._init_world()

    def step(self) -> None:
        with self._lock:
            self._step_unlocked()

    def _step_unlocked(self) -> None:
        self.tick += 1

        for index, robot in enumerate(self.robots):
            # Sanfte, unterschiedliche Kurvenbewegung pro Roboter.
            robot["heading"] += 0.02 + (index * 0.005)
            nx = robot["x"] + math.cos(robot["heading"]) * robot["speed"]
            ny = robot["y"] + math.sin(robot["heading"]) * robot["speed"]

            # Kartenrand-Kollision -> Richtung invertieren.
            if nx < 20 or nx > self.width - 20:
                robot["heading"] = math.pi - robot["heading"]
                nx = max(20, min(self.width - 20, nx))
            if ny < 20 or ny > self.height - 20:
                robot["heading"] = -robot["heading"]
                ny = max(20, min(self.height - 20, ny))

            robot["x"] = nx
            robot["y"] = ny
            robot["trail"].append([round(nx, 2), round(ny, 2)])

            # Spur begrenzen, damit die JSON-Antwort klein bleibt.
            if len(robot["trail"]) > 180:
                robot["trail"] = robot["trail"][-180:]

    def get_state(self) -> dict:
        with self._lock:
            if self.running:
                self._step_unlocked()

            return {
                "ok": True,
                "timestamp": int(time.time()),
                "tick": self.tick,
                "running": self.running,
                "map": {
                    "width": self.width,
                    "height": self.height,
                    "obstacles": self.obstacles,
                },
                "robots": self.robots,
            }

    def _snapshot_payload_unlocked(self) -> dict:
        """Erzeugt einen serialisierbaren Stand der aktuellen Simulation."""
        return {
            "version": 1,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "tick": self.tick,
            "running": self.running,
            "map": {
                "width": self.width,
                "height": self.height,
                "obstacles": self.obstacles,
            },
            "robots": self.robots,
        }

    def list_snapshots(self) -> list[dict]:
        """Liefert vorhandene Snapshot-Dateien (neueste zuerst)."""
        items: list[dict] = []
        for file in sorted(self.snapshot_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            items.append(
                {
                    "filename": file.name,
                    "modified": int(file.stat().st_mtime),
                    "size": file.stat().st_size,
                }
            )
        return items

    def save_snapshot(self, name: str | None = None) -> tuple[bool, str, str | None]:
        """Speichert den aktuellen Kartenstand in eine JSON-Datei."""
        with self._lock:
            clean_name = (name or "").strip().replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if clean_name:
                filename = f"map_{clean_name}_{timestamp}.json"
            else:
                filename = f"map_snapshot_{timestamp}.json"

            # Dateiname defensiv begrenzen.
            filename = "".join(ch for ch in filename if ch.isalnum() or ch in ("_", "-", "."))
            if not filename.endswith(".json"):
                filename += ".json"

            target = self.snapshot_dir / filename
            payload = self._snapshot_payload_unlocked()

            try:
                target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError:
                return False, "Snapshot konnte nicht gespeichert werden", None

            return True, f"Snapshot gespeichert: {filename}", filename

    def load_snapshot(self, filename: str) -> tuple[bool, str]:
        """Lädt einen Snapshot und setzt den Simulationszustand zurück."""
        # Pfadmanipulation verhindern.
        safe_name = Path(filename).name
        if not safe_name.endswith(".json"):
            return False, "Ungültiger Snapshot-Dateiname"

        target = self.snapshot_dir / safe_name
        if not target.exists():
            return False, "Snapshot nicht gefunden"

        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False, "Snapshot-Datei ist ungültig"

        try:
            map_data = payload["map"]
            robots = payload["robots"]

            # Gültigkeitsprüfung der wichtigsten Felder.
            width = int(map_data["width"])
            height = int(map_data["height"])
            obstacles = map_data["obstacles"]
            running = bool(payload.get("running", False))
            tick = int(payload.get("tick", 0))

            if not isinstance(obstacles, list) or not isinstance(robots, list):
                return False, "Snapshot-Struktur ungültig"
        except (KeyError, TypeError, ValueError):
            return False, "Snapshot-Struktur unvollständig"

        with self._lock:
            self.width = width
            self.height = height
            self.obstacles = obstacles
            self.robots = robots
            self.running = running
            self.tick = tick

        return True, f"Snapshot geladen: {safe_name}"


class MapHandler(BaseHTTPRequestHandler):
    """HTTP-Handler für Kartierungs-UI und Simulations-API."""

    simulation: MapSimulation | None = None
    web_dir = Path(__file__).with_name("web_map")

    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            index_file = self.web_dir / "index.html"
            if not index_file.exists():
                self._send_json({"ok": False, "message": "index.html fehlt"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            self._send_html(index_file.read_text(encoding="utf-8"))
            return

        if self.path == "/api/map-state":
            if self.simulation is None:
                self._send_json({"ok": False, "message": "simulation nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            self._send_json(self.simulation.get_state())
            return

        if self.path == "/api/snapshots":
            self._send_json({"ok": True, "snapshots": self.simulation.list_snapshots()})
            return

        self._send_json({"ok": False, "message": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.simulation is None:
            self._send_json({"ok": False, "message": "simulation nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if self.path == "/api/run":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json({"ok": False, "message": "ungültiges JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            running = bool(payload.get("running", True))
            self.simulation.set_running(running)
            self._send_json({"ok": True, "message": f"running={running}"})
            return

        if self.path == "/api/reset":
            self.simulation.reset()
            self._send_json({"ok": True, "message": "Simulation zurückgesetzt"})
            return

        if self.path == "/api/step":
            self.simulation.step()
            self._send_json({"ok": True, "message": "Ein Schritt ausgeführt"})
            return

        if self.path == "/api/save":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json({"ok": False, "message": "ungültiges JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            name = str(payload.get("name", "")).strip()
            ok, message, filename = self.simulation.save_snapshot(name=name)
            self._send_json(
                {
                    "ok": ok,
                    "message": message,
                    "filename": filename,
                    "snapshots": self.simulation.list_snapshots(),
                }
            )
            return

        if self.path == "/api/load":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json({"ok": False, "message": "ungültiges JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            filename = str(payload.get("filename", "")).strip()
            if not filename:
                self._send_json({"ok": False, "message": "filename fehlt"}, status=HTTPStatus.BAD_REQUEST)
                return

            ok, message = self.simulation.load_snapshot(filename)
            self._send_json({"ok": ok, "message": message, "snapshots": self.simulation.list_snapshots()})
            return

        self._send_json({"ok": False, "message": "not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return


def run_server(host: str, web_port: int) -> None:
    """Startet die lokale Kartierungs-Weboberfläche."""
    simulation = MapSimulation()
    MapHandler.simulation = simulation

    server = ThreadingHTTPServer((host, web_port), MapHandler)
    print("=" * 58)
    print(f"🗺️  Kartierungs-MVP läuft: http://{host}:{web_port}")
    print("🤖 Virtuelle Roboter aktiv: R1, R2, R3")
    print("=" * 58)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Kartierungs-Server beendet")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="BrainBot Kartierungs-MVP (lokal)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind-Adresse des Web-Servers")
    parser.add_argument("--web-port", type=int, default=8090, help="Port für das Kartierungs-Webinterface")
    args = parser.parse_args()

    run_server(host=args.host, web_port=args.web_port)


if __name__ == "__main__":
    main()
