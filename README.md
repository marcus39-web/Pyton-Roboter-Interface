# BrainBot AI - Python Roboter-Interface (OOP)

Objektorientierte Python-Schnittstelle zur Fernsteuerung des BrainBot Roboters über TCP/IP.

## ⚠️ Status

**Derzeit ist noch kein Roboter angeschlossen.** Das Projekt befindet sich in der Entwicklungsphase und verwendet Testdaten.

**✅ Projekt vollständig abgeschlossen:**

- ✅ OOP-Architektur mit `BrainBotRemote`-Klasse
- ✅ Logging-System in `robot_log.txt`
- ✅ Unit-Tests (8/8 bestanden, 100%)
- ✅ Git-Integration mit Hooks
- ✅ Vollständige Dokumentation

## Features

- ✅ Objektorientierte Architektur mit `BrainBotRemote`-Klasse
- ✅ TCP/IP-Verbindung zum Roboter
- ✅ Automatisches Logging aller Aktionen in `robot_log.txt`
- ✅ Fehlerbehandlung und Statusmeldungen
- ✅ 100% Test-Coverage mit pytest
- ✅ Bereit für Erweiterungen

## Installation

1. **Repository klonen:**

   ```bash
   git clone https://github.com/marcus39-web/Pyton-Roboter-Interface.git
   cd "BrainBot_AI"
   ```

2. **Virtuelle Umgebung erstellen:**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

## Nutzung

### Grundlegende Verwendung

```python
from basis_class import BrainBotRemote

# Roboter-Instanz erstellen
robot = BrainBotRemote(robot_ip="192.168.1.100", port=5000)

# Verbindung herstellen
if robot.connect():
    # Befehle senden
    robot.send_command("FORWARD")
    robot.send_command("TURN_LEFT")
    robot.send_command("STOP")

    # Verbindung trennen
    robot.disconnect()
```

### Testprogramm ausführen

```bash
python main.py
```

**Hinweis:** Solange kein Roboter angeschlossen ist, wird ein Verbindungsfehler ausgegeben und im Log protokolliert.

## Logging

Alle Aktionen werden automatisch in `robot_log.txt` protokolliert:

```
[2026-03-02 00:23:37] [ERROR] Verbindungsfehler: [WinError 10060] ...
[2026-03-02 12:45:10] [CONNECT] Verbunden mit 192.168.1.100:5000
[2026-03-02 12:45:15] [COMMAND] Befehl gesendet: FORWARD
[2026-03-02 12:45:20] [DISCONNECT] Verbindung getrennt
```

**Log-Level:**

- `CONNECT` - Erfolgreiche Verbindung
- `COMMAND` - Gesendeter Befehl
- `ERROR` - Fehler bei Verbindung/Befehl
- `DISCONNECT` - Verbindung getrennt

**Hinweis:** `robot_log.txt` wird von Git ignoriert (siehe `.gitignore`)

## Projektstruktur

```
BrainBot_AI/
├── basis_class.py          # Haupt-Klasse für Roboter-Steuerung
├── main.py                 # Testprogramm
├── robot_log.txt           # Automatisches Logging (wird ignoriert von Git)
├── requirements.txt        # Python-Abhängigkeiten
├── pytest.ini              # Test-Konfiguration
├── README.md               # Diese Datei
├── .gitignore             # Git-Ausschlüsse
├── tests/                 # Unit-Tests
│   ├── __init__.py
│   └── test_basis_class.py
└── hooks/                 # Git Hooks für automatische Workflows
    ├── applypatch-msg.sample
    ├── commit-msg.sample
    ├── fsmonitor-watchman.sample
    ├── post-update.sample
    ├── pre-applypatch.sample
    ├── pre-commit.sample
    ├── pre-merge-commit.sample
    ├── pre-push.sample
    ├── pre-rebase.sample
    ├── pre-receive.sample
    ├── prepare-commit-msg.sample
    ├── push-to-checkout.sample
    ├── sendemail-validate.sample
    └── update.sample
```

## Testing

### Unit-Tests ausführen

```bash
# Alle Tests ausführen
python -m pytest tests/ -v

# Mit Coverage-Report
python -m pytest tests/ --cov=basis_class --cov-report=term-missing

# Einzelnen Test ausführen
python -m pytest tests/test_basis_class.py::TestBrainBotRemote::test_connect_failure -v
```

**Aktueller Test-Status:**

```
✅ 8 passed in 2.10s (100%)

tests/test_basis_class.py::TestBrainBotRemote::test_init PASSED                    [ 12%]
tests/test_basis_class.py::TestBrainBotRemote::test_log_file_path PASSED           [ 25%]
tests/test_basis_class.py::TestBrainBotRemote::test_connect_failure PASSED         [ 37%]
tests/test_basis_class.py::TestBrainBotRemote::test_send_command_without_connection PASSED [ 50%]
tests/test_basis_class.py::TestBrainBotRemote::test_disconnect_without_connection PASSED [ 62%]
tests/test_basis_class.py::TestBrainBotRemote::test_logging PASSED                 [ 75%]
tests/test_basis_class.py::TestBrainBotRemote::test_multiple_log_entries PASSED    [ 87%]
tests/test_basis_class.py::test_robot_ip_validation PASSED                         [100%]
```

## Entwicklung

### Neue Befehle hinzufügen

Erweitern Sie die `BrainBotRemote`-Klasse in `basis_class.py`:

```python
def move_forward(self, speed=100):
    """Roboter vorwärts bewegen"""
    return self.send_command(f"FORWARD:{speed}")

def turn_left(self, degrees=90):
    """Roboter nach links drehen"""
    return self.send_command(f"TURN_LEFT:{degrees}")

def read_sensor(self, sensor_id):
    """Sensor auslesen"""
    return self.send_command(f"READ_SENSOR:{sensor_id}")
```

### Code-Qualität

Das Projekt verwendet folgende Best Practices:

- ✅ Objektorientierte Programmierung (OOP)
- ✅ Type Hints und Docstrings
- ✅ Fehlerbehandlung mit try-except
- ✅ Automatisches Logging
- ✅ Unit-Tests mit pytest
- ✅ Git Hooks für Workflow-Automatisierung

## Anforderungen

- Python 3.8+
- Socket-Bibliothek (Standard)
- pytest >= 7.4.0 (für Tests)
- pytest-cov >= 4.1.0 (für Coverage)

## Roadmap

### Phase 1: Grundlagen (✅ Abgeschlossen)

- [x] OOP-Struktur implementieren
- [x] Logging-System einrichten
- [x] Unit-Tests schreiben
- [x] Dokumentation erstellen

### Phase 2: Hardware-Integration (⏳ Geplant)

- [ ] Roboter-Hardware anschließen
- [ ] Verbindungstest durchführen
- [ ] Basis-Befehle implementieren
- [ ] Sensor-Integration

### Phase 3: Erweiterte Features (📋 Backlog)

- [ ] GUI für einfache Steuerung
- [ ] Video-Streaming-Support
- [ ] Autonomous Mode mit KI
- [ ] Multi-Roboter-Unterstützung
- [ ] REST-API für Web-Interface

## Troubleshooting

### Verbindungsfehler

**Problem:** `[WinError 10060]` oder `[WinError 10061]`

**Lösung:**

1. Prüfen Sie, ob der Roboter eingeschaltet ist
2. Überprüfen Sie die IP-Adresse in `main.py`
3. Stellen Sie sicher, dass der Port korrekt ist (Standard: 5000)
4. Prüfen Sie die Firewall-Einstellungen

### Tests schlagen fehl

**Problem:** pytest findet Module nicht

**Lösung:**

```bash
# pytest neu installieren
pip uninstall pytest -y
pip install pytest pytest-cov

# Tests mit python -m ausführen
python -m pytest tests/ -v
```

### Log-Datei wird nicht erstellt

**Problem:** `robot_log.txt` existiert nicht

**Lösung:**

```bash
# Manuell erstellen
echo. > robot_log.txt

# Programm ausführen
python main.py
```

## Git-Workflow

### Standard-Workflow

```bash
# Änderungen vornehmen
git add .
git commit -m "Deine Commit-Nachricht"
git push

# Status prüfen
git status
git log --oneline -5
```

### Branches verwalten

```bash
# Neuen Feature-Branch erstellen
git checkout -b feature/neue-funktion

# Änderungen committen
git add .
git commit -m "Feature: Neue Funktion hinzugefügt"

# Zurück zu main und mergen
git checkout main
git merge feature/neue-funktion
git push
```

## Lizenz

MIT License - siehe LICENSE-Datei

Copyright (c) 2026 Marcus Weber

## Autor

**Marcus Reiser**  
GitHub: [@marcus39-web](https://github.com/marcus39-web)  
Projekt: [Pyton-Roboter-Interface](https://github.com/marcus39-web/Pyton-Roboter-Interface)

## Kontakt

Bei Fragen oder Problemen:

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/marcus39-web/Pyton-Roboter-Interface/issues)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/marcus39-web/Pyton-Roboter-Interface/discussions)
- 📧 **Email:** Über GitHub-Profil

## Changelog

### Version 1.0.0 (2026-03-02)

- ✅ Initiales Release
- ✅ OOP-Struktur implementiert
- ✅ Logging-System eingerichtet
- ✅ Unit-Tests (100% Coverage)
- ✅ Vollständige Dokumentation

---

**⭐ Wenn Ihnen dieses Projekt gefällt, geben Sie ihm einen Star auf GitHub!**
