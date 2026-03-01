# BrainBot AI - Python Roboter-Interface (OOP)

Objektorientierte Python-Schnittstelle zur Fernsteuerung des BrainBot Roboters über TCP/IP.

## ⚠️ Status

**Derzeit ist noch kein Roboter angeschlossen.** Das Projekt befindet sich in der Entwicklungsphase und verwendet Testdaten.

## Features

- ✅ Objektorientierte Architektur mit `BrainBotRemote`-Klasse
- ✅ TCP/IP-Verbindung zum Roboter
- ✅ Automatisches Logging aller Aktionen in `robot_log.txt`
- ✅ Fehlerbehandlung und Statusmeldungen
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

**Hinweis:** Solange kein Roboter angeschlossen ist, wird ein Verbindungsfehler ausgegeben.

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

## Projektstruktur

```
BrainBot_AI/
├── basis_class.py       # Haupt-Klasse für Roboter-Steuerung
├── main.py              # Testprogramm
├── robot_log.txt        # Automatisches Logging (wird ignoriert von Git)
├── requirements.txt     # Python-Abhängigkeiten
├── README.md            # Diese Datei
├── .gitignore          # Git-Ausschlüsse
└── hooks/              # Git Hooks für automatische Workflows
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
```

### Unit-Tests ausführen

```bash
pytest tests/
```

## Anforderungen

- Python 3.8+
- Socket-Bibliothek (Standard)
- pytest (für Tests)

## Roadmap

- [ ] Roboter-Hardware anschließen
- [ ] Erweiterte Befehle (Sensoren, Motoren)
- [ ] GUI für einfache Steuerung
- [ ] Autonomous Mode mit KI
- [ ] Video-Streaming-Support

## Lizenz

MIT License - siehe LICENSE-Datei

## Autor

Marcus Weber  
GitHub: [@marcus39-web](https://github.com/marcus39-web)

## Kontakt

Bei Fragen oder Problemen öffnen Sie bitte ein Issue auf GitHub.
