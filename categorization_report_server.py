import argparse
import json
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote

from categorization_db import CategorizationDatabase

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:
    Image = None
    ImageDraw = None
    ImageFont = None


def _parse_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.now()

    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1]

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.now()


def _period_key(timestamp: datetime, period: str) -> str:
    if period == "day":
        return timestamp.strftime("%Y-%m-%d")
    if period == "week":
        iso_year, iso_week, _ = timestamp.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    if period == "month":
        return timestamp.strftime("%Y-%m")
    if period == "year":
        return timestamp.strftime("%Y")
    return timestamp.strftime("%Y-%m-%d")


def aggregate_blocks(entries: list[dict], period: str) -> list[dict]:
    grouped: dict[str, dict] = {}

    for entry in entries:
        timestamp = _parse_datetime(entry.get("created_at"))
        key = _period_key(timestamp, period)
        decision = str(entry.get("decision", "UNKNOWN")).upper()

        if key not in grouped:
            grouped[key] = {"block": key, "total": 0, "OBSTACLE": 0, "CLEAR": 0, "OTHER": 0}

        grouped[key]["total"] += 1
        if decision in ("OBSTACLE", "CLEAR"):
            grouped[key][decision] += 1
        else:
            grouped[key]["OTHER"] += 1

    return [grouped[key] for key in sorted(grouped.keys(), reverse=True)]


def calculate_totals(entries: list[dict]) -> dict:
    totals = {"total": 0, "OBSTACLE": 0, "CLEAR": 0, "OTHER": 0}
    for entry in entries:
        decision = str(entry.get("decision", "UNKNOWN")).upper()
        totals["total"] += 1
        if decision in ("OBSTACLE", "CLEAR"):
            totals[decision] += 1
        else:
            totals["OTHER"] += 1
    return totals


class CategorizationRepository:
    def __init__(self) -> None:
        self.learning_file = Path(__file__).with_name("learning_data.jsonl")
        self.db = CategorizationDatabase.from_env()

    def _load_from_mysql(self, limit: int) -> tuple[bool, list[dict], str]:
        if not self.db.enabled:
            return False, [], "MySQL deaktiviert"

        ok, entries, message = self.db.fetch_recent_predictions(limit=limit)
        if not ok:
            return False, [], message

        normalized: list[dict] = []
        for row in entries:
            normalized.append(
                {
                    "created_at": _parse_datetime(row.get("created_at")).isoformat(timespec="seconds"),
                    "decision": row.get("decision", "UNKNOWN"),
                    "command": row.get("command", ""),
                    "distance_cm": int(row.get("distance_cm", 0)),
                    "safe_distance_cm": int(row.get("safe_distance_cm", 0)),
                    "room_name": row.get("room_name", ""),
                    "confidence": float(row.get("confidence", 1.0)),
                }
            )
        return True, normalized, "mysql"

    def _load_from_jsonl(self, limit: int) -> list[dict]:
        if not self.learning_file.exists():
            return []

        entries: list[dict] = []
        for line in self.learning_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            entries.append(
                {
                    "created_at": _parse_datetime(payload.get("timestamp")).isoformat(timespec="seconds"),
                    "decision": payload.get("decision", "UNKNOWN"),
                    "command": payload.get("command", ""),
                    "distance_cm": int(payload.get("distance_cm", 0)),
                    "safe_distance_cm": int(payload.get("safe_distance_cm", 0)),
                    "room_name": payload.get("room_name", ""),
                    "confidence": 1.0,
                }
            )

        return list(reversed(entries[-limit:]))

    def load_entries(self, limit: int = 1000) -> tuple[list[dict], str]:
        ok, entries, source = self._load_from_mysql(limit=limit)
        if ok and entries:
            return entries, source

        return self._load_from_jsonl(limit=limit), "jsonl"


class CategorizationReportService:
    def __init__(self) -> None:
        self.repo = CategorizationRepository()
        self.export_dir = Path(__file__).with_name("categorization_exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def build_summary(self, limit: int = 1000) -> dict:
        entries, source = self.repo.load_entries(limit=limit)
        return {
            "ok": True,
            "source": source,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "totals": calculate_totals(entries),
            "blocks": {
                "day": aggregate_blocks(entries, "day"),
                "week": aggregate_blocks(entries, "week"),
                "month": aggregate_blocks(entries, "month"),
                "year": aggregate_blocks(entries, "year"),
            },
            "recent": entries[:50],
        }

    def export_jpg(self, room_name: str, room_width_cm: int, room_height_cm: int, period: str) -> tuple[bool, dict]:
        if Image is None:
            return False, {"ok": False, "message": "Pillow nicht installiert (pip install -r requirements.txt)"}

        summary = self.build_summary(limit=2000)
        blocks = summary.get("blocks", {}).get(period, [])[:12]
        totals = summary.get("totals", {})

        image_width = 1400
        image_height = 900
        image = Image.new("RGB", (image_width, image_height), (250, 250, 250))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        created_at = datetime.now().isoformat(timespec="seconds")
        draw.text((40, 30), "BrainBot Kategorisierung - Report", fill=(0, 0, 0), font=font)
        draw.text((40, 60), f"Erstellt am: {created_at}", fill=(0, 0, 0), font=font)
        draw.text((40, 90), f"Zimmer: {room_name}", fill=(0, 0, 0), font=font)
        draw.text((40, 120), f"Vermaßung: {room_width_cm}cm x {room_height_cm}cm", fill=(0, 0, 0), font=font)
        draw.text((40, 150), f"Blockansicht: {period.upper()}", fill=(0, 0, 0), font=font)

        draw.text((40, 200), f"Gesamt: {totals.get('total', 0)}", fill=(0, 0, 0), font=font)
        draw.text((40, 225), f"OBSTACLE: {totals.get('OBSTACLE', 0)}", fill=(0, 0, 0), font=font)
        draw.text((40, 250), f"CLEAR: {totals.get('CLEAR', 0)}", fill=(0, 0, 0), font=font)
        draw.text((40, 275), f"OTHER: {totals.get('OTHER', 0)}", fill=(0, 0, 0), font=font)

        chart_x = 400
        chart_y = 230
        chart_w = 930
        chart_h = 500
        draw.rectangle((chart_x, chart_y, chart_x + chart_w, chart_y + chart_h), outline=(30, 30, 30), width=2)

        if blocks:
            max_total = max(item.get("total", 0) for item in blocks) or 1
            bar_w = max(20, int((chart_w - 30) / max(1, len(blocks))))

            for index, item in enumerate(reversed(blocks)):
                total = int(item.get("total", 0))
                bar_h = int((total / max_total) * (chart_h - 80))
                x1 = chart_x + 15 + index * bar_w
                y1 = chart_y + chart_h - 40 - bar_h
                x2 = x1 + max(8, bar_w - 8)
                y2 = chart_y + chart_h - 40
                draw.rectangle((x1, y1, x2, y2), fill=(66, 133, 244), outline=(40, 40, 40))
                draw.text((x1, y2 + 5), str(item.get("block", ""))[-7:], fill=(0, 0, 0), font=font)
                draw.text((x1, y1 - 14), str(total), fill=(0, 0, 0), font=font)

        room_name_clean = "".join(ch for ch in room_name.strip().replace(" ", "_") if ch.isalnum() or ch in ("_", "-"))
        if not room_name_clean:
            room_name_clean = "Unbekannt"

        filename = f"cat_report_{room_name_clean}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output_file = self.export_dir / filename
        image.save(output_file, format="JPEG", quality=92)

        log_file = self.export_dir / "exports_log.jsonl"
        export_log = {
            "created_at": created_at,
            "filename": filename,
            "room_name": room_name,
            "room_width_cm": room_width_cm,
            "room_height_cm": room_height_cm,
            "period": period,
            "totals": totals,
        }
        with log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(export_log, ensure_ascii=False) + "\n")

        return True, {
            "ok": True,
            "message": f"JPG-Report erstellt: {filename}",
            "filename": filename,
            "download_url": f"/exports/{filename}",
            "created_at": created_at,
            "room_name": room_name,
            "room_width_cm": room_width_cm,
            "room_height_cm": room_height_cm,
            "period": period,
        }


class CategorizationHandler(BaseHTTPRequestHandler):
    service: CategorizationReportService | None = None
    web_dir = Path(__file__).with_name("web_categorization")

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
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_jpg_file(self, file_path: Path) -> None:
        raw = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path.startswith("/exports/"):
            if self.service is None:
                self._send_json({"ok": False, "message": "service nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            requested_name = unquote(parsed.path.removeprefix("/exports/")).strip()
            safe_name = Path(requested_name).name
            if not safe_name.lower().endswith(".jpg"):
                self._send_json({"ok": False, "message": "nur JPG erlaubt"}, status=HTTPStatus.BAD_REQUEST)
                return

            target = self.service.export_dir / safe_name
            if not target.exists():
                self._send_json({"ok": False, "message": "Datei nicht gefunden"}, status=HTTPStatus.NOT_FOUND)
                return

            self._send_jpg_file(target)
            return

        if parsed.path in ("/", "/index.html"):
            index_file = self.web_dir / "index.html"
            if not index_file.exists():
                self._send_json({"ok": False, "message": "index.html fehlt"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            self._send_html(index_file.read_text(encoding="utf-8"))
            return

        if parsed.path == "/api/summary":
            if self.service is None:
                self._send_json({"ok": False, "message": "service nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["1000"])[0])
            self._send_json(self.service.build_summary(limit=limit))
            return

        self._send_json({"ok": False, "message": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.service is None:
            self._send_json({"ok": False, "message": "service nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if self.path == "/api/export-jpg":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json({"ok": False, "message": "ungültiges JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            room_name = str(payload.get("room_name", "")).strip() or "Unbekanntes_Zimmer"
            period = str(payload.get("period", "month")).strip().lower()
            if period not in ("day", "week", "month", "year"):
                self._send_json({"ok": False, "message": "period ungültig"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                room_width_cm = int(payload.get("room_width_cm", 0))
                room_height_cm = int(payload.get("room_height_cm", 0))
            except ValueError:
                self._send_json({"ok": False, "message": "Vermaßung muss ganzzahlig sein"}, status=HTTPStatus.BAD_REQUEST)
                return

            if room_width_cm <= 0 or room_height_cm <= 0:
                self._send_json({"ok": False, "message": "Vermaßung muss > 0 sein"}, status=HTTPStatus.BAD_REQUEST)
                return

            ok, result = self.service.export_jpg(
                room_name=room_name,
                room_width_cm=room_width_cm,
                room_height_cm=room_height_cm,
                period=period,
            )
            self._send_json(result, status=HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json({"ok": False, "message": "not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return


def run_server(host: str, web_port: int) -> None:
    service = CategorizationReportService()
    CategorizationHandler.service = service

    server = ThreadingHTTPServer((host, web_port), CategorizationHandler)
    print("=" * 62)
    print(f"📊 Kategorisierung-Report läuft: http://{host}:{web_port}")
    print("🧾 Blöcke: Tag/Woche/Monat/Jahr + JPG-Export mit Vermaßung")
    print("=" * 62)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Kategorisierung-Report beendet")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="BrainBot Kategorisierung Report (lokal)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind-Adresse des Web-Servers")
    parser.add_argument("--web-port", type=int, default=8092, help="Port für die Kategorisierungs-Ansicht")
    args = parser.parse_args()

    run_server(host=args.host, web_port=args.web_port)


if __name__ == "__main__":
    main()
