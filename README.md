# BrainBot AI - Python Roboter-Interface (OOP)

Objektorientierte Python-Schnittstelle zur Fernsteuerung des BrainBot Roboters über TCP/IP.

## ⚠️ Status

**Derzeit ist noch kein Roboter angeschlossen.** Das Projekt befindet sich in der Entwicklungsphase und verwendet Testdaten.

**✅ Projekt vollständig abgeschlossen (v1.0.1):**

- ✅ OOP-Architektur mit `BrainBotRemote`-Klasse
- ✅ TCP/IP-Kommunikation mit Mock-Server
- ✅ Logging-System in `robot_log.txt`
- ✅ Unit-Tests (8/8 bestanden, 100%)
- ✅ Git-Integration mit Hooks
- ✅ Testlauf-Dokumentation (`README_TEST/README_TESTLAEUFE.md`)
- ✅ Vollständige Dokumentation

## Features

- ✅ Objektorientierte Architektur mit `BrainBotRemote`-Klasse
- ✅ TCP/IP-Verbindung zum Roboter (mit Mock-Server für Tests)
- ✅ Heartbeat-System für sichere Kommunikation
- ✅ Automatisches Logging aller Aktionen in `robot_log.txt`
- ✅ Simulationsdaten über `simulation_data.json` konfigurierbar
- ✅ Lernmodus mit Datenspeicherung in `learning_data.jsonl`
- ✅ Optionale, erweiterbare MySQL-Persistenz für Kategorisierung (`Docker + MySQL 8`)
- ✅ Fehlerbehandlung und Statusmeldungen
- ✅ 100% Test-Coverage mit pytest
- ✅ Lokale Testläufe ohne Hardware
- ✅ Bereit für Erweiterungen

## Installation & Setup

### Voraussetzungen

**Hardware:**

- 🖥️ Windows/Linux/macOS Computer
- 🤖 BrainBot Roboter (FEZ Bit / SITCore)
- 🌐 WLAN-fähiger Roboter
- 🔌 USB-Kabel (für Entwicklung)

**Software:**

- 🐍 Python 3.8+
- 📦 pip (Python Package Manager)
- 🔧 Visual Studio Code (empfohlen)
- 🌳 Git
- 🐳 Docker + Docker Compose (für MySQL-Betrieb)

### Python Installation

**Windows:**

```powershell
# Python 3.11+ herunterladen von python.org
# Bei Installation: "Add Python to PATH" aktivieren!

# Prüfen
python --version
pip --version
```

**Linux/macOS:**

```bash
# Python installieren
brew install python3  # macOS
sudo apt-get install python3 python3-pip  # Linux

# Prüfen
python3 --version
pip3 --version
```

### Projekt-Setup

**1. Repository klonen:**

```bash
git clone https://github.com/marcus39-web/Pyton-Roboter-Interface.git
cd "GHI Python-Roboter-Interface OOP"
cd BrainBot_AI
```

### Optional: Docker + MySQL für Kategorisierung

Für größere Erweiterungen kann die Kategorisierung in MySQL persistiert werden.

**1. Umgebungsdatei anlegen:**

```bash
cp .env.example .env
```

**2. Container starten:**

```bash
docker compose up -d
```

Enthalten:

- `mysql` (Port `3306`)
- `adminer` für DB-Ansicht (Port `8081`, Browser: `http://127.0.0.1:8081`)

Standard-Zugang für diese Konfiguration:

- User: `root`
- Passwort: *(leer)*

**⚠️ SEHR WICHTIG:**

- Diese Konfiguration ist **nur für lokale Entwicklung auf dem eigenen Rechner** gedacht.
- **Nie** in produktiven oder fremden/geteilten Netzwerken mit `root` und leerem Passwort betreiben.
- Für reale Nutzung: eigenen DB-User mit Passwort und minimalen Rechten verwenden.

**3. Python-Seite aktivieren:**

In `.env` muss `APP_USE_MYSQL=1` gesetzt sein. Dann initialisiert `main.py` beim Start das Schema und schreibt Entscheidungen zusätzlich in MySQL.

## Lokale Testläufe (OHNE Hardware)

### ✅ Mock-Server für Entwicklung

Testen Sie die komplette Kommunikation **lokal** ohne echten Roboter:

**Terminal 1 - Mock-Server starten:**

```bash
python test_server.py
```

**Terminal 2 - Client starten:**

```bash
python main.py
```

### 📱 Web-Steuerung (Maus + iPhone Touch + Tastatur)

Die Datei `web_control_server.py` stellt eine lokale Steuer-Webseite bereit.

**Terminal 1 - Mock-Server:**

```bash
python test_server.py
```

**Terminal 2 - Web-Steuerung starten:**

```bash
python web_control_server.py --host 0.0.0.0 --web-port 8080 --robot-ip 127.0.0.1 --robot-port 5000
```

**Steuerung öffnen:**

- PC: `http://127.0.0.1:8080`
- iPhone (gleiches WLAN): `http://<PC-IP>:8080`

**Eingaben:**

- Touch/Maus-Bewegung: **Gedrückt halten = fahren, Loslassen = STOP**
- Touch/Maus-Buttons: Vor, Links, Rechts, Zurück, Start, Stop
- Tastatur: `W/A/S/D` halten = Bewegung, loslassen = Stop, `E` = Start, `Leertaste` = Stop, `Q` = Disconnect
- Not-Aus überall: `STOP`/`HALT` nutzen API-Notaus; bei Tab-Wechsel/Fokusverlust/API-Fehler wird ebenfalls automatisch Not-Aus ausgeführt

📖 **Detaillierte Web-Tests:** Siehe `README_TEST/README_WEB_STEUERUNG_TESTS.md`
📖 **Keyboard-Only Tests:** Siehe `README_TEST/README_KEYBOARD_TESTS.md`
📖 **Kartierungs-MVP Tests:** Siehe `README_TEST/README_MAP_MVP_TESTS.md`
📖 **Kategorisierungstests:** Siehe `README_TEST/README_KATAGO__TESTS.md`

### 📊 Kategorisierungsausgabe (Tag/Woche/Monat/Jahr + JPG)

Mit `categorization_report_server.py` gibt es eine einfache visuelle Ausgabe der Kategorisierung:

- Blockansicht in Tag/Woche/Monat/Jahr
- Tabellenansicht mit `Erstellt am`, `Zimmername`, Distanz, Kategorie, Kommando
- JPG-Export mit Metadaten (`Erstellt am`, Zimmername, Vermaßung)

**Start:**

```bash
python categorization_report_server.py --host 0.0.0.0 --web-port 8092
```

**Öffnen:**

- PC: `http://127.0.0.1:8092`
- iPhone (gleiches WLAN): `http://<PC-IP>:8092`

**Export-Dateien:**

- JPG-Ausgaben liegen lokal unter `categorization_exports/`
- Export-Log für spätere Erweiterungen: `categorization_exports/exports_log.jsonl`

**Aktueller Stand (02.03.2026):**

- ✅ Web-Steuerung, Hold-Logik und globaler Not-Aus sind implementiert
- ✅ Lokale PC-Tests sind erfolgreich
- ⏸️ iPhone-Realtest wurde pausiert (Schulumgebung: PC nur LAN, kein gemeinsames WLAN)
- ▶️ Wiedereinstieg zuhause: PC+iPhone ins gleiche WLAN, dann Web-Tests laut `README_TEST/README_WEB_STEUERUNG_TESTS.md`

### 🧠 Simulation & Lernmodus (ohne Roboter)

### 🗺️ Kartierungs-MVP (lokal, ohne Roboter)

Mit `map_mvp_server.py` läuft eine lokale Karten-Simulation mit 3 virtuellen Robotern.

**Start:**

```bash
python map_mvp_server.py --host 0.0.0.0 --web-port 8090
```

**Öffnen:**

- PC: `http://127.0.0.1:8090`
- iPhone (gleiches WLAN): `http://<PC-IP>:8090`

**Funktionen im MVP:**

- Live-Karte mit Grid + Hindernissen
- 3 simulierte Roboter inkl. Trails
- Start / Pause / Ein Schritt / Reset
- Snapshot-Speicherung als JSON (Speichern/Laden/Liste)
- Vorbereitet für spätere echte Positionsdaten

`main.py` nutzt Testdaten aus `simulation_data.json`:

```json
{
    "safe_distance_cm": 30,
    "distances_cm": [85, 60, 45, 28, 22, 50]
}
```

Beispielvorlage: `simulation_data.example.json` (bei Bedarf nach `simulation_data.json` kopieren und Werte anpassen).

- `safe_distance_cm`: Sicherheitsabstand in cm
- `distances_cm`: Simulierte Sensor-Messwerte

Beim Lauf schreibt der Lernmodus zusätzlich Trainingsdaten nach `learning_data.jsonl` (ein JSON-Eintrag pro gesendetem Befehl).

Wenn `APP_USE_MYSQL=1` aktiv ist, werden dieselben Entscheidungen zusätzlich in MySQL gespeichert (`categories`, `samples`, `predictions`, `feedback`).

📖 **Detaillierte Anleitung:** Siehe `README_TEST/README_TESTLAEUFE.md`
📖 **MySQL-Kategorisierungstests:** Siehe `README_TEST/README_KATAGO__TESTS.md`

**2. Virtual Environment erstellen:**

```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

**3. Dependencies installieren:**

```bash
pip install -r requirements.txt
```

**4. Tests ausführen:**

```bash
pytest tests/ -v
```

**5. (Optional) Visual Studio Code öffnen:**

```bash
code .
```

## Erste Schritte

### Verbindung zum Roboter herstellen

**Schritt 1: Roboter-IP finden**

```python
# Option A: Im Router suchen nach "BrainBot"
# Option B: Auf dem Roboter-Display prüfen
# Option C: Mit Netzwerk-Scanner (Advanced)

roboter_ip = "192.168.1.100"  # ERSETZEN mit echte IP!
```

**Schritt 2: Einfaches Test-Skript**

Erstellen Sie `test_robot.py`:

```python
from basis_class import BrainBotRemote
import time

# Roboter-Instanz erstellen
robot = BrainBotRemote(
    robot_ip="192.168.1.100",  # ← IHRE ROBOTER-IP!
    port=5000,
    heartbeat_interval=2.0
)

# Verbindung versuchen
if robot.connect():
    print("✅ Roboter verbunden!")

    # Heartbeat starten (WICHTIG!)
    robot.start_heartbeat()

    try:
        # Befehle senden
        print("→ Sende FORWARD...")
        robot.send_command("FORWARD")
        time.sleep(3)

        print("→ Sende STOP...")
        robot.send_command("STOP")

    finally:
        # Sauberes Herunterfahren
        robot.stop_heartbeat()
        robot.disconnect()
        print("✅ Disconnected")
else:
    print("❌ Roboter nicht erreichbar!")
    print("Tipps:")
    print("  1. Ist der Roboter eingeschaltet?")
    print("  2. Ist die richtige IP eingestellt?")
    print("  3. Sind Sie im gleichen WLAN-Netz?")
```

**Schritt 3: Ausführen**

```bash
python test_robot.py
```

## Befehls-Referenz

### Standard-Befehle

| Befehl       | Funktion           | Beispiel                           |
| ------------ | ------------------ | ---------------------------------- |
| `FORWARD`    | Vorwärts fahren    | `robot.send_command("FORWARD")`    |
| `BACKWARD`   | Rückwärts fahren   | `robot.send_command("BACKWARD")`   |
| `TURN_LEFT`  | Nach links drehen  | `robot.send_command("TURN_LEFT")`  |
| `TURN_RIGHT` | Nach rechts drehen | `robot.send_command("TURN_RIGHT")` |
| `STOP`       | Sofort stoppen     | `robot.send_command("STOP")`       |
| `ROTATE_180` | 180° Drehung       | `robot.send_command("ROTATE_180")` |

### Erweiterte Befehle (Hardware-abhängig)

```python
# Geschwindigkeit setzen (0-255)
robot.send_command("SPEED:150")

# LED-Farbe (RGB)
robot.send_command("LED:255:0:0")  # Rot

# Sensor-Abfrage
robot.send_command("SENSOR:ULTRASONIC")

# Servo-Motor (0-180°)
robot.send_command("SERVO:90")

# Summer/Buzzer
robot.send_command("BUZZ:1000")  # 1000ms
```

## Logging & Debugging

### Log-Dateien

Die `robot_log.txt` wird automatisch erstellt und alle Aktionen protokolliert:

```
[2026-03-02 14:30:15] [CONNECT] Verbunden mit 192.168.1.100:5000
[2026-03-02 14:30:16] [HEARTBEAT] Thread gestartet (Intervall: 2.0s)
[2026-03-02 14:30:18] [COMMAND] Befehl gesendet: FORWARD
[2026-03-02 14:30:20] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:30:24] [COMMAND] Befehl gesendet: STOP
[2026-03-02 14:30:26] [DISCONNECT] Verbindung getrennt
```

Zusätzlich erzeugt der Lernmodus die Datei `learning_data.jsonl` für spätere KI-Trainingsläufe.

**Log-Datei anschauen:**

```bash
# Windows
type robot_log.txt
type learning_data.jsonl

# Linux/macOS
cat robot_log.txt
cat learning_data.jsonl

# Live-Anzeige (Windows)
Get-Content robot_log.txt -Wait

# Live-Anzeige (Linux/macOS)
tail -f robot_log.txt
```

### Debug-Modus

```python
# Verbose Output für Debugging
robot = BrainBotRemote("192.168.1.100")

# Alle Aktionen werden automatisch geloggt
if robot.connect():
    robot.start_heartbeat()

    # Überprüfen Sie robot_log.txt für Details

    robot.stop_heartbeat()
    robot.disconnect()
```

## Häufige Fehlermeldungen

### ❌ "Connection refused"

```
Fehler: [Errno 10061] No connection could be made because the target machine actively refused it
```

**Ursachen & Lösungen:**

1. ❌ Roboter nicht eingeschaltet → **Roboter einschalten!**
2. ❌ Falsche IP-Adresse → **IP prüfen (Router oder Display)**
3. ❌ Falscher Port → **Port 5000 verwenden**
4. ❌ Firewall blockiert → **Firewall prüfen**

### ❌ "Connection timeout"

```
Fehler: [Errno 10060] A connection attempt failed because the connected party did not properly respond
```

**Ursachen & Lösungen:**

1. ❌ WLAN zu schwach → **Näher an Roboter gehen**
2. ❌ Roboter offline → **Verbindung überprüfen**
3. ❌ Router-Problem → **Router neu starten**

### ⚠️ "Heartbeat-Fehler"

```
[ERROR] Heartbeat-Fehler: [Errno 10054] Connection reset by peer
```

**Ursachen & Lösungen:**

1. ❌ WLAN abgebrochen → **Verbindung prüfen**
2. ❌ Roboter überlastet → **Weniger Befehle senden**
3. ❌ Heartbeat-Intervall zu kurz → **Auf 3-5s erhöhen**

### ❌ "Keine Verbindung"

```
✗ Keine Verbindung zum Roboter
```

**Schnell-Checklist:**

- [ ] Roboter eingeschaltet?
- [ ] WLAN verbunden?
- [ ] Richtige IP eingegeben?
- [ ] Firewall deaktiviert?
- [ ] Kabel sitzen fest?
- [ ] Roboter nicht zu weit weg?

## Performance-Tipps

### Optimale Einstellungen

```python
# Schnelle, stabile Verbindung
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    port=5000,
    heartbeat_interval=2.0  # Optimal
)
```

### Best Practices

```python
# ✅ GUT: Befehle mit Pausen
robot.send_command("FORWARD")
time.sleep(2)
robot.send_command("TURN_LEFT")
time.sleep(1)
robot.send_command("STOP")

# ❌ SCHLECHT: Zu viele Befehle hintereinander
robot.send_command("FORWARD")
robot.send_command("TURN_LEFT")  # Zu schnell!
robot.send_command("STOP")
```

### CPU & RAM

```
Speicher-Nutzung:   ~30-50 MB (minimal)
CPU-Auslastung:     <1% (negligible)
Netzwerk-Traffic:   <1 KB/s (sehr gering)

→ Auch auf Raspberry Pi oder schwacher Hardware möglich!
```

## Erweiterte Verwendung

### Mit Sensor-Daten arbeiten

```python
def drive_until_obstacle():
    """Fährt bis zum Hindernis"""
    robot.send_command("FORWARD")

    while True:
        distance = robot.read_distance()

        if distance < 20:  # 20cm
            robot.send_command("STOP")
            break

        time.sleep(0.5)
```

### Programmierbare Routen

```python
def square_route():
    """Rechteck fahren"""
    for _ in range(4):
        robot.send_command("FORWARD")
        time.sleep(2)

        robot.send_command("TURN_RIGHT")
        time.sleep(1)

    robot.send_command("STOP")

# Ausführen
robot.connect()
robot.start_heartbeat()
square_route()
robot.stop_heartbeat()
robot.disconnect()
```

### Mit Mehreren Robotern arbeiten

```python
# Mehrere Roboter-Instanzen
robot1 = BrainBotRemote("192.168.1.100")
robot2 = BrainBotRemote("192.168.1.101")
robot3 = BrainBotRemote("192.168.1.102")

# Alle verbinden
robots = [robot1, robot2, robot3]
for robot in robots:
    robot.connect()
    robot.start_heartbeat()

try:
    # Koordinierte Befehle
    for robot in robots:
        robot.send_command("FORWARD")

    time.sleep(3)

    for robot in robots:
        robot.send_command("STOP")

finally:
    # Alle sauber beenden
    for robot in robots:
        robot.stop_heartbeat()
        robot.disconnect()
```

## Sicherheit & Best Practices

### Kritische Sicherheitsregeln ⚠️

```python
# ❌ NICHT MACHEN:
robot.connect()
robot.send_command("FORWARD")
# Fehler tritt auf → Roboter läuft weiter!

# ✅ RICHTIG:
robot.connect()
robot.start_heartbeat()  # Heartbeat = Notbremse

try:
    robot.send_command("FORWARD")
except:
    robot.stop_heartbeat()
    robot.disconnect()
    raise

robot.stop_heartbeat()
robot.disconnect()
```

### Timeout-Handling

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Programm zu lange ausgeführt")

# Nach 30 Sekunden Abbruch
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

try:
    robot.connect()
    robot.start_heartbeat()
    # ... Code hier ...
    signal.alarm(0)  # Timer annullieren
except TimeoutError:
    print("⚠️ Timeout! Roboter wird gestoppt...")
    robot.stop_heartbeat()
finally:
    robot.disconnect()
```

## Entwickler-Tipps

### Code-Style & Conventions

```python
# Folgen Sie PEP 8
# https://www.python.org/dev/peps/pep-0008/

# Type Hints verwenden
def calculate_distance(x1: float, y1: float,
                      x2: float, y2: float) -> float:
    """Berechnet Distanz zwischen zwei Punkten"""
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

# Docstrings schreiben
class RobotController:
    """Kontrolliert den BrainBot Roboter"""
    pass
```

### Testing

```bash
# Alle Tests ausführen
pytest tests/ -v

# Nur einen Test-File
pytest tests/test_basis_class.py -v

# Mit Coverage-Report
pytest tests/ --cov=BrainBot_AI --cov-report=html
```

### Versionskontrolle

```bash
# Vor jedem Commit prüfen
git status
git diff

# Hook einmalig pro Clone aktivieren
git config core.hooksPath hooks

# Beim Push werden automatisch geprüft:
# - Port 5000 frei
# - Syntax (py_compile)
# - Tests (pytest)

# Commits mit aussagekräftigen Messages
git commit -m "Feature: Heartbeat-System implementiert"

# Nicht: "Update" oder "Fix"
```

## Support & Issues

### Problem melden

1. **GitHub Issues:** https://github.com/marcus39-web/Pyton-Roboter-Interface/issues
2. **Beschreibung:** Was haben Sie versucht?
3. **Error-Message:** Komplette Fehlermeldung kopieren
4. **Log-Datei:** robot_log.txt anhängen
5. **Umgebung:** Python-Version, Betriebssystem, etc.

### Community

- 💬 **Discussions:** GitHub Discussions öffnen
- 📧 **Email:** marcus39-web@github.com
- 🐛 **Bug-Report:** Mit robot_log.txt
- 💡 **Feature-Request:** Mit Use-Case beschreiben

## Lizenz

Dieses Projekt ist ein **Schulprojekt** von Marcus Reiser (2026).

```
MIT License - Frei verwendbar für Bildungszwecke
```

## Autor

**Marcus Reiser**

- 🐙 GitHub: [marcus39-web](https://github.com/marcus39-web)
- 🎓 Schulprojekt: BrainBot AI OOP Interface
- 📅 Datum: 02 März 2026
- ⭐ Version: 1.0.1

---

## Danksagungen

Spezial-Dank an:

- 🎯 **GitHub Copilot** für Code-Unterstützung
- 🤖 **FEZ Bit/SITCore** Community
- 🏫 Schule für Hardware-Bereitstellung
- 👥 Alle Tester und Mitwirkenden

---

**Viel Erfolg mit BrainBot AI!** 🚀⭐
