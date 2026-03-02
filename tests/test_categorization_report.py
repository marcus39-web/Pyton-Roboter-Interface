from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from categorization_report_server import aggregate_blocks, calculate_totals, CategorizationReportService


def test_aggregate_blocks_by_periods():
    entries = [
        {"created_at": "2026-03-01T10:00:00", "decision": "OBSTACLE"},
        {"created_at": "2026-03-01T11:00:00", "decision": "CLEAR"},
        {"created_at": "2026-03-08T11:00:00", "decision": "OBSTACLE"},
        {"created_at": "2026-02-14T12:00:00", "decision": "OTHER"},
        {"created_at": "2025-12-31T23:00:00", "decision": "CLEAR"},
    ]

    day_blocks = aggregate_blocks(entries, "day")
    week_blocks = aggregate_blocks(entries, "week")
    month_blocks = aggregate_blocks(entries, "month")
    year_blocks = aggregate_blocks(entries, "year")

    assert len(day_blocks) >= 3
    assert len(week_blocks) >= 3
    assert len(month_blocks) >= 3
    assert len(year_blocks) == 2

    first_day = day_blocks[0]
    assert "block" in first_day
    assert "total" in first_day
    assert "OBSTACLE" in first_day
    assert "CLEAR" in first_day
    assert "OTHER" in first_day


def test_calculate_totals_counts_categories():
    entries = [
        {"decision": "OBSTACLE"},
        {"decision": "OBSTACLE"},
        {"decision": "CLEAR"},
        {"decision": "UNKNOWN"},
    ]

    totals = calculate_totals(entries)
    assert totals["total"] == 4
    assert totals["OBSTACLE"] == 2
    assert totals["CLEAR"] == 1
    assert totals["OTHER"] == 1


def test_list_recent_exports_returns_latest_jpgs(tmp_path):
    service = CategorizationReportService()
    service.export_dir = tmp_path
    service.export_dir.mkdir(parents=True, exist_ok=True)

    file_old = service.export_dir / "old.jpg"
    file_new = service.export_dir / "new.jpg"
    file_old.write_bytes(b"old")
    file_new.write_bytes(b"new")

    log_file = service.export_dir / "exports_log.jsonl"
    log_file.write_text(
        "\n".join(
            [
                json.dumps({"created_at": "2026-03-01T10:00:00", "filename": "old.jpg", "room_name": "R1", "period": "month"}),
                json.dumps({"created_at": "2026-03-02T10:00:00", "filename": "new.jpg", "room_name": "R2", "period": "year"}),
            ]
        ),
        encoding="utf-8",
    )

    exports = service.list_recent_exports(limit=10)
    assert len(exports) == 2
    assert exports[0]["filename"] == "new.jpg"
    assert exports[1]["filename"] == "old.jpg"
    assert exports[0]["download_url"] == "/exports/new.jpg"
