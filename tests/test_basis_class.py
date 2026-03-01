import pytest
from pathlib import Path
import sys

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

from basis_class import BrainBotRemote


class TestBrainBotRemote:
    """Unit-Tests für die BrainBotRemote-Klasse"""
    
    def setup_method(self):
        """Wird vor jedem Test ausgeführt"""
        self.robot = BrainBotRemote(robot_ip="127.0.0.1", port=5000)
    
    def teardown_method(self):
        """Wird nach jedem Test ausgeführt"""
        if self.robot.socket:
            self.robot.disconnect()
    
    def test_init(self):
        """Test: Initialisierung"""
        assert self.robot.robot_ip == "127.0.0.1"
        assert self.robot.port == 5000
        assert self.robot.socket is None
        assert self.robot.log_file.name == "robot_log.txt"
    
    def test_log_file_path(self):
        """Test: Log-Datei wird im richtigen Ordner erstellt"""
        expected_path = Path(__file__).parent.parent / "robot_log.txt"
        assert self.robot.log_file == expected_path
    
    def test_connect_failure(self):
        """Test: Verbindung schlägt fehl (kein Server)"""
        result = self.robot.connect()
        assert result is False
        assert self.robot.socket is None
    
    def test_send_command_without_connection(self):
        """Test: Befehl senden ohne Verbindung"""
        result = self.robot.send_command("TEST")
        assert result is False
    
    def test_disconnect_without_connection(self):
        """Test: Trennen ohne bestehende Verbindung"""
        self.robot.disconnect()  # Sollte keine Exception werfen
        assert self.robot.socket is None
    
    def test_logging(self, tmp_path):
        """Test: Logging-Funktionalität"""
        # Temporäre Log-Datei verwenden
        self.robot.log_file = tmp_path / "test_log.txt"
        
        # Log-Eintrag erstellen
        self.robot._log("TEST", "Test-Nachricht")
        
        # Log-Datei prüfen
        assert self.robot.log_file.exists()
        content = self.robot.log_file.read_text(encoding="utf-8")
        assert "[TEST]" in content
        assert "Test-Nachricht" in content
    
    def test_multiple_log_entries(self, tmp_path):
        """Test: Mehrere Log-Einträge nacheinander"""
        self.robot.log_file = tmp_path / "test_log.txt"
        
        self.robot._log("INFO", "Erste Nachricht")
        self.robot._log("ERROR", "Zweite Nachricht")
        
        content = self.robot.log_file.read_text(encoding="utf-8")
        assert content.count("[INFO]") == 1
        assert content.count("[ERROR]") == 1


def test_robot_ip_validation():
    """Test: IP-Adresse wird korrekt gespeichert"""
    robot = BrainBotRemote(robot_ip="192.168.1.100", port=8080)
    assert robot.robot_ip == "192.168.1.100"
    assert robot.port == 8080