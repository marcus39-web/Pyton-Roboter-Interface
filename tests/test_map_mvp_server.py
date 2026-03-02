from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).parent.parent))

from map_mvp_server import MapSimulation


def test_snapshot_save_list_load_restores_state(tmp_path):
    simulation = MapSimulation()
    simulation.snapshot_dir = tmp_path
    simulation.snapshot_dir.mkdir(parents=True, exist_ok=True)

    expected_obstacles = [{"x": 10, "y": 20, "w": 30, "h": 40}]
    expected_robots = [
        {
            "id": "RX",
            "color": "#ffffff",
            "x": 123.4,
            "y": 234.5,
            "heading": 1.2,
            "speed": 2.3,
            "trail": [[120.0, 230.0], [123.4, 234.5]],
        }
    ]

    with simulation._lock:
        simulation.width = 1111
        simulation.height = 777
        simulation.tick = 42
        simulation.running = False
        simulation.obstacles = expected_obstacles
        simulation.robots = expected_robots

    save_ok, save_message, filename = simulation.save_snapshot(name="regression test")
    assert save_ok is True
    assert "Snapshot gespeichert" in save_message
    assert filename is not None
    assert (tmp_path / filename).exists()

    snapshots = simulation.list_snapshots()
    assert len(snapshots) == 1
    assert snapshots[0]["filename"] == filename

    with simulation._lock:
        simulation.width = 10
        simulation.height = 10
        simulation.tick = 0
        simulation.running = True
        simulation.obstacles = []
        simulation.robots = []

    load_ok, load_message = simulation.load_snapshot(filename)
    assert load_ok is True
    assert "Snapshot geladen" in load_message

    with simulation._lock:
        assert simulation.width == 1111
        assert simulation.height == 777
        assert simulation.tick == 42
        assert simulation.running is False
        assert simulation.obstacles == expected_obstacles
        assert simulation.robots == expected_robots


def test_snapshot_load_rejects_invalid_filename(tmp_path):
    simulation = MapSimulation()
    simulation.snapshot_dir = tmp_path
    simulation.snapshot_dir.mkdir(parents=True, exist_ok=True)

    ok, message = simulation.load_snapshot("kein_snapshot")
    assert ok is False
    assert message == "Ungültiger Snapshot-Dateiname"
