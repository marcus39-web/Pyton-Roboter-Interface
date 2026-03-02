import argparse
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from basis_class import BrainBotRemote


class RobotGateway:
    """Thread-sichere Brücke zwischen Web-API und BrainBotRemote."""

    def __init__(self, robot_ip: str, robot_port: int) -> None:
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self._robot = BrainBotRemote(robot_ip=robot_ip, port=robot_port)
        self._lock = threading.Lock()
        self.connected = False

    def connect(self) -> tuple[bool, str]:
        with self._lock:
            if self.connected:
                return True, "bereits verbunden"
            self.connected = self._robot.connect()
            if self.connected:
                return True, f"verbunden mit {self.robot_ip}:{self.robot_port}"
            return False, "Verbindung fehlgeschlagen"

    def disconnect(self) -> tuple[bool, str]:
        with self._lock:
            if not self.connected:
                return True, "bereits getrennt"

            # Vor dem Trennen sicherheitshalber einen STOP senden.
            self._robot.send_command("STOP")
            self._robot.disconnect()
            self.connected = False
            return True, "Verbindung getrennt"

    def send(self, command: str) -> tuple[bool, str]:
        with self._lock:
            if not self.connected:
                return False, "nicht verbunden (erst START drücken)"
            success = self._robot.send_command(command)
            if success:
                return True, f"Befehl gesendet: {command}"

            # Bei Sendeproblem Zustand auf getrennt setzen,
            # damit UI keine weiteren Bewegungsbefehle im Blindflug sendet.
            self._robot.disconnect()
            self.connected = False
            return False, f"Senden fehlgeschlagen: {command}"

    def emergency_stop(self) -> tuple[bool, str]:
        """Not-Aus: Stoppt Bewegung sofort und trennt die Verbindung kontrolliert."""
        with self._lock:
            if not self.connected:
                return True, "Not-Aus bestätigt (bereits getrennt)"

            stop_ok = self._robot.send_command("STOP")
            self._robot.disconnect()
            self.connected = False

            if stop_ok:
                return True, "Not-Aus ausgeführt: STOP gesendet und Verbindung getrennt"
            return False, "Not-Aus versucht: Verbindung getrennt, STOP-Bestätigung fehlt"


class ControlHandler(BaseHTTPRequestHandler):
    """HTTP-Handler für Web-UI und API-Endpunkte."""

    gateway: RobotGateway | None = None
    web_dir = Path(__file__).with_name("web_control")

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
        # Liefert ausschließlich die Steueroberfläche unter '/'.
        if self.path != "/":
            self._send_json({"ok": False, "message": "not found"}, status=HTTPStatus.NOT_FOUND)
            return

        index_file = self.web_dir / "index.html"
        if not index_file.exists():
            self._send_json({"ok": False, "message": "index.html fehlt"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_html(index_file.read_text(encoding="utf-8"))

    def do_POST(self) -> None:
        # API-Endpunkte: connect, disconnect, command.
        if self.gateway is None:
            self._send_json({"ok": False, "message": "gateway nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if self.path == "/api/status":
            self._send_json({"ok": True, "message": "status", "connected": self.gateway.connected})
            return

        if self.path == "/api/connect":
            ok, message = self.gateway.connect()
            self._send_json({"ok": ok, "message": message, "connected": self.gateway.connected})
            return

        if self.path == "/api/disconnect":
            ok, message = self.gateway.disconnect()
            self._send_json({"ok": ok, "message": message, "connected": self.gateway.connected})
            return

        if self.path == "/api/emergency-stop":
            # Unabhängig vom Request-Body immer sofort Not-Aus ausführen.
            ok, message = self.gateway.emergency_stop()
            self._send_json({"ok": ok, "message": message, "connected": self.gateway.connected})
            return

        if self.path == "/api/command":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json({"ok": False, "message": "ungültiges JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            command = str(payload.get("command", "")).strip()
            if not command:
                self._send_json({"ok": False, "message": "command fehlt"}, status=HTTPStatus.BAD_REQUEST)
                return

            ok, message = self.gateway.send(command)
            self._send_json({"ok": ok, "message": message, "connected": self.gateway.connected})
            return

        self._send_json({"ok": False, "message": "not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return


def run_server(host: str, web_port: int, robot_ip: str, robot_port: int) -> None:
    """Startet die Web-Steuerung und bindet sie an den Robot-Gateway."""
    gateway = RobotGateway(robot_ip=robot_ip, robot_port=robot_port)
    ControlHandler.gateway = gateway

    server = ThreadingHTTPServer((host, web_port), ControlHandler)
    print("=" * 58)
    print(f"🌐 Web-Steuerung läuft: http://{host}:{web_port}")
    print(f"🤖 Ziel-Roboter: {robot_ip}:{robot_port}")
    print("💡 Für iPhone im WLAN: nutze die PC-IP statt 127.0.0.1")
    print("=" * 58)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Web-Server beendet")
    finally:
        gateway.disconnect()
        server.server_close()


def main() -> None:
    # Kommandozeilenparameter für lokale und WLAN-Tests.
    parser = argparse.ArgumentParser(description="BrainBot Web-Steuerung (Maus + Touch + Tastatur)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind-Adresse des Web-Servers")
    parser.add_argument("--web-port", type=int, default=8080, help="Port für die Weboberfläche")
    parser.add_argument("--robot-ip", default="127.0.0.1", help="IP des Roboters/Mock-Servers")
    parser.add_argument("--robot-port", type=int, default=5000, help="Port des Roboters/Mock-Servers")
    args = parser.parse_args()

    run_server(
        host=args.host,
        web_port=args.web_port,
        robot_ip=args.robot_ip,
        robot_port=args.robot_port,
    )


if __name__ == "__main__":
    main()
