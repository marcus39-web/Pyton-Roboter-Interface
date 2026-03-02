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


def normalize_room_geometry(payload: dict) -> tuple[bool, dict, str]:
    try:
        width_cm = int(payload.get("room_width_cm", 0))
        height_cm = int(payload.get("room_height_cm", 0))
        corner_radius_cm = int(payload.get("corner_radius_cm", 0))
        cutout_width_cm = int(payload.get("cutout_width_cm", 0))
        cutout_depth_cm = int(payload.get("cutout_depth_cm", 0))
    except (TypeError, ValueError):
        return False, {}, "Vermaßung muss ganzzahlig sein"

    cutout_side = str(payload.get("cutout_side", "none")).strip().lower()
    if cutout_side not in ("none", "left", "right", "top", "bottom"):
        return False, {}, "cutout_side ungültig"

    if width_cm <= 0 or height_cm <= 0:
        return False, {}, "Länge/Breite muss > 0 sein"

    if corner_radius_cm < 0:
        return False, {}, "Radius darf nicht negativ sein"

    max_radius = max(0, min(width_cm, height_cm) // 2)
    corner_radius_cm = min(corner_radius_cm, max_radius)

    if cutout_side == "none":
        cutout_width_cm = 0
        cutout_depth_cm = 0
    else:
        if cutout_width_cm <= 0 or cutout_depth_cm <= 0:
            return False, {}, "Aussparung muss > 0 sein"

        side_length = width_cm if cutout_side in ("top", "bottom") else height_cm
        orthogonal_length = height_cm if cutout_side in ("top", "bottom") else width_cm

        if cutout_width_cm >= side_length:
            return False, {}, "Aussparungsbreite muss kleiner als Seitenlänge sein"
        if cutout_depth_cm >= orthogonal_length:
            return False, {}, "Aussparungstiefe muss kleiner als Raumtiefe sein"

    return True, {
        "room_width_cm": width_cm,
        "room_height_cm": height_cm,
        "corner_radius_cm": corner_radius_cm,
        "cutout_side": cutout_side,
        "cutout_width_cm": cutout_width_cm,
        "cutout_depth_cm": cutout_depth_cm,
    }, "ok"


def _draw_dimension_horizontal(draw, x1: int, x2: int, y: int, ref_y1: int, ref_y2: int, label: str, font) -> None:
    draw.line((x1, ref_y1, x1, y), fill=(30, 30, 30), width=1)
    draw.line((x2, ref_y2, x2, y), fill=(30, 30, 30), width=1)
    draw.line((x1, y, x2, y), fill=(30, 30, 30), width=1)
    draw.polygon([(x1, y), (x1 + 6, y - 3), (x1 + 6, y + 3)], fill=(30, 30, 30))
    draw.polygon([(x2, y), (x2 - 6, y - 3), (x2 - 6, y + 3)], fill=(30, 30, 30))
    draw.text(((x1 + x2) // 2 - 25, y - 16), label, fill=(30, 30, 30), font=font)


def _draw_dimension_vertical(draw, x: int, y1: int, y2: int, ref_x1: int, ref_x2: int, label: str, font) -> None:
    draw.line((ref_x1, y1, x, y1), fill=(30, 30, 30), width=1)
    draw.line((ref_x2, y2, x, y2), fill=(30, 30, 30), width=1)
    draw.line((x, y1, x, y2), fill=(30, 30, 30), width=1)
    draw.polygon([(x, y1), (x - 3, y1 + 6), (x + 3, y1 + 6)], fill=(30, 30, 30))
    draw.polygon([(x, y2), (x - 3, y2 - 6), (x + 3, y2 - 6)], fill=(30, 30, 30))
    draw.text((x - 55, (y1 + y2) // 2 - 8), label, fill=(30, 30, 30), font=font)


def _draw_room_plan(draw, left: int, top: int, max_w: int, max_h: int, geometry: dict, font) -> None:
    room_w = geometry["room_width_cm"]
    room_h = geometry["room_height_cm"]
    radius_cm = geometry["corner_radius_cm"]
    cutout_side = geometry["cutout_side"]
    cutout_w_cm = geometry["cutout_width_cm"]
    cutout_d_cm = geometry["cutout_depth_cm"]

    scale = min(max_w / room_w, max_h / room_h)
    room_px_w = int(room_w * scale)
    room_px_h = int(room_h * scale)

    x1 = left + (max_w - room_px_w) // 2
    y1 = top + (max_h - room_px_h) // 2
    x2 = x1 + room_px_w
    y2 = y1 + room_px_h

    radius_px = int(min(radius_cm * scale, min(room_px_w, room_px_h) / 4))
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius_px, outline=(20, 20, 20), width=3, fill=(233, 238, 245))

    if cutout_side != "none" and cutout_w_cm > 0 and cutout_d_cm > 0:
        cutout_w_px = int(cutout_w_cm * scale)
        cutout_d_px = int(cutout_d_cm * scale)
        if cutout_side in ("top", "bottom"):
            cx = (x1 + x2) // 2
            c1 = cx - (cutout_w_px // 2)
            c2 = c1 + cutout_w_px
            if cutout_side == "top":
                draw.rectangle((c1, y1, c2, y1 + cutout_d_px), fill=(250, 250, 250), outline=(20, 20, 20), width=2)
            else:
                draw.rectangle((c1, y2 - cutout_d_px, c2, y2), fill=(250, 250, 250), outline=(20, 20, 20), width=2)
        else:
            cy = (y1 + y2) // 2
            c1 = cy - (cutout_w_px // 2)
            c2 = c1 + cutout_w_px
            if cutout_side == "left":
                draw.rectangle((x1, c1, x1 + cutout_d_px, c2), fill=(250, 250, 250), outline=(20, 20, 20), width=2)
            else:
                draw.rectangle((x2 - cutout_d_px, c1, x2, c2), fill=(250, 250, 250), outline=(20, 20, 20), width=2)

    _draw_dimension_horizontal(draw, x1, x2, y1 - 28, y1, y1, f"L = {room_w} cm", font)
    _draw_dimension_vertical(draw, x1 - 34, y1, y2, x1, x1, f"B = {room_h} cm", font)

    if cutout_side != "none" and cutout_w_cm > 0 and cutout_d_cm > 0:
        draw.text((x1, y2 + 12), f"Aussparung: Seite={cutout_side.upper()} | Breite={cutout_w_cm} cm | Tiefe={cutout_d_cm} cm", fill=(30, 30, 30), font=font)

    draw.text((x1, y2 + 30), f"Eckradius R = {radius_cm} cm", fill=(30, 30, 30), font=font)
    draw.text((x1, y2 + 48), "DIN-ähnliche Vermaßung (schematisch, nicht normgeprüft)", fill=(30, 30, 30), font=font)


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

    def list_recent_exports(self, limit: int = 10) -> list[dict]:
        log_file = self.export_dir / "exports_log.jsonl"
        if not log_file.exists():
            return []

        items: list[dict] = []
        for line in log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            filename = str(payload.get("filename", "")).strip()
            safe_name = Path(filename).name
            if not safe_name.lower().endswith(".jpg"):
                continue

            target = self.export_dir / safe_name
            if not target.exists():
                continue

            items.append(
                {
                    "filename": safe_name,
                    "created_at": payload.get("created_at", ""),
                    "room_name": payload.get("room_name", ""),
                    "period": payload.get("period", ""),
                    "download_url": f"/exports/{safe_name}",
                }
            )

        return list(reversed(items))[:max(1, int(limit))]

    def export_jpg(self, room_name: str, geometry: dict, period: str) -> tuple[bool, dict]:
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
        room_width_cm = geometry["room_width_cm"]
        room_height_cm = geometry["room_height_cm"]
        draw.text((40, 30), "BrainBot Kategorisierung - Report", fill=(0, 0, 0), font=font)
        draw.text((40, 60), f"Erstellt am: {created_at}", fill=(0, 0, 0), font=font)
        draw.text((40, 90), f"Zimmer: {room_name}", fill=(0, 0, 0), font=font)
        draw.text((40, 120), f"Vermaßung: {room_width_cm}cm x {room_height_cm}cm", fill=(0, 0, 0), font=font)
        draw.text((40, 150), f"Blockansicht: {period.upper()}", fill=(0, 0, 0), font=font)

        draw.text((40, 200), f"Gesamt: {totals.get('total', 0)}", fill=(0, 0, 0), font=font)
        draw.text((40, 225), f"OBSTACLE: {totals.get('OBSTACLE', 0)}", fill=(0, 0, 0), font=font)
        draw.text((40, 250), f"CLEAR: {totals.get('CLEAR', 0)}", fill=(0, 0, 0), font=font)
        draw.text((40, 275), f"OTHER: {totals.get('OTHER', 0)}", fill=(0, 0, 0), font=font)

        _draw_room_plan(draw, left=40, top=330, max_w=320, max_h=500, geometry=geometry, font=font)

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
            "corner_radius_cm": geometry["corner_radius_cm"],
            "cutout_side": geometry["cutout_side"],
            "cutout_width_cm": geometry["cutout_width_cm"],
            "cutout_depth_cm": geometry["cutout_depth_cm"],
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
            "corner_radius_cm": geometry["corner_radius_cm"],
            "cutout_side": geometry["cutout_side"],
            "cutout_width_cm": geometry["cutout_width_cm"],
            "cutout_depth_cm": geometry["cutout_depth_cm"],
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

        if parsed.path == "/api/exports":
            if self.service is None:
                self._send_json({"ok": False, "message": "service nicht initialisiert"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["10"])[0])
            self._send_json({"ok": True, "exports": self.service.list_recent_exports(limit=limit)})
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

            is_valid, geometry, error_message = normalize_room_geometry(payload)
            if not is_valid:
                self._send_json({"ok": False, "message": error_message}, status=HTTPStatus.BAD_REQUEST)
                return

            ok, result = self.service.export_jpg(
                room_name=room_name,
                geometry=geometry,
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
