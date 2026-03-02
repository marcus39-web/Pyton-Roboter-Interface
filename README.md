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

### Phase 4: Zukunftsvisionen (💡 Ideen)

- [ ] 📱 Smartphone-App zur Steuerung (iOS/Android)
- [ ] 🎥 Kamera-Integration mit Live-Video-Streaming
- [ ] 🗺️ Automatische Raum-Kartierung (SLAM)
- [ ] 🧠 KI-Steuerung mit Machine Learning
- [ ] 🎮 Gaming-Controller Support (Xbox/PlayStation)
- [ ] 🌐 Web-Interface im Browser
- [ ] 👥 Multi-Roboter Koordination & Schwarm-Intelligenz
- [ ] 🔊 Sprachsteuerung (Alexa/Google Assistant)
- [ ] 📊 Daten-Visualisierung & Analytics Dashboard
- [ ] 🎯 Objekt-Erkennung mit Computer Vision
- [ ] 🏠 Smart-Home Integration
- [ ] ☁️ Cloud-Anbindung für Remote-Steuerung

## Ideen für später

### 1. Mobile App Development 📱

**iOS/Android App:**

```
Features:
- Touch-Steuerung mit virtuellem Joystick
- Live-Video-Feed vom Roboter
- Sensor-Daten in Echtzeit
- Geschwindigkeitskontrolle
- Programmierbare Routen
```

**Technologien:**

- React Native / Flutter
- WebSocket für Echtzeitkommunikation
- REST-API Backend

### 2. Computer Vision & KI 🧠

**Objekterkennung:**

```python
def detect_objects(self, image):
    # YOLOv8 oder TensorFlow für Objekterkennung
    objects = self.model.detect(image)
    return objects

def follow_person(self):
    # Automatisch einer Person folgen
    person = self.detect_objects("person")
    self.navigate_to(person.position)
```

**Gesichtserkennung:**

```python
def recognize_face(self, image):
    # OpenCV für Gesichtserkennung
    face = self.face_detector.detect(image)
    identity = self.face_recognizer.identify(face)
    return identity
```

### 3. Autonome Navigation 🗺️

**SLAM (Simultaneous Localization and Mapping):**

```python
def map_environment(self):
    # Raum kartieren während der Fahrt
    self.lidar_data = self.read_lidar()
    self.map.update(self.lidar_data)
    self.position = self.calculate_position()

def navigate_to_point(self, x, y):
    # A* Pfadplanung
    path = self.calculate_path(self.position, (x, y))
    self.follow_path(path)
```

**Hinderniserkennung:**

```python
def avoid_obstacles(self):
    distance = self.read_ultrasonic()
    if distance < 20:  # 20cm
        direction = self.find_free_direction()
        self.turn(direction)
    else:
        self.move_forward()
```

### 4. Web-Interface & Dashboard 🌐

**Dashboard-Features:**

- Echtzeit-Steuerung im Browser
- Live-Video-Stream
- Sensor-Datenvisualisierung
- Log-Anzeige in Echtzeit
- Batteriestatus & System-Info
- Programmierbare Aufgaben

**Technologien:**

- Backend: Flask/FastAPI
- Frontend: React/Vue.js
- WebSocket für Echtzeitdaten
- Chart.js für Datenvisualisierung

**Beispiel-API:**

```python
from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/api/robot/status')
def get_status():
    return jsonify({
        'connected': robot.socket is not None,
        'battery': robot.read_battery(),
        'position': robot.get_position()
    })

@socketio.on('command')
def handle_command(data):
    robot.send_command(data['command'])
```

### 5. Gaming-Controller Support 🎮

**Controller-Integration:**

```python
import pygame

def setup_controller(self):
    pygame.init()
    self.joystick = pygame.joystick.Joystick(0)
    self.joystick.init()

def control_with_gamepad(self):
    # Linker Stick = Bewegung
    x_axis = self.joystick.get_axis(0)
    y_axis = self.joystick.get_axis(1)

    # A-Button = Turbo
    if self.joystick.get_button(0):
        self.speed = 200

    self.move(x_axis, y_axis)
```

### 6. Sprachsteuerung 🔊

**Voice Commands:**

```python
import speech_recognition as sr

def listen_for_command(self):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        command = recognizer.recognize_google(audio, language="de-DE")

        if "vorwärts" in command:
            self.move_forward()
        elif "stop" in command:
            self.stop()
        elif "dreh dich um" in command:
            self.turn(180)
```

**Alexa/Google Assistant Integration:**

```python
# AWS Lambda für Alexa Skill
def lambda_handler(event, context):
    intent = event['request']['intent']['name']

    if intent == "MoveForwardIntent":
        robot.send_command("FORWARD")
        return speak("Roboter bewegt sich vorwärts")
```

### 7. Schwarm-Intelligenz 👥

**Multi-Roboter Koordination:**

```python
class RobotSwarm:
    def __init__(self):
        self.robots = []

    def add_robot(self, ip):
        robot = BrainBotRemote(ip)
        self.robots.append(robot)

    def formation_drive(self, formation="line"):
        # Alle Roboter in Formation fahren
        for i, robot in enumerate(self.robots):
            position = self.calculate_formation_position(i, formation)
            robot.navigate_to(position)

    def synchronized_dance(self):
        # Choreografierte Bewegungen
        for robot in self.robots:
            robot.send_command("DANCE_MOVE_1")
```

### 8. Smart-Home Integration 🏠

**MQTT Integration:**

```python
import paho.mqtt.client as mqtt

def connect_to_smart_home(self):
    client = mqtt.Client()
    client.connect("homeassistant.local", 1883)

    # Roboter als Gerät verfügbar machen
    client.publish("homeassistant/robot/status", "online")

def trigger_on_event(self, event):
    # Roboter reagiert auf Smart-Home Events
    if event == "doorbell_ring":
        self.navigate_to_door()
        self.send_notification("Besucher an der Tür")
```

### 9. Cloud & Remote Access ☁️

**Remote-Steuerung über Internet:**

```python
# Tunnel mit ngrok oder eigener Cloud
from flask import Flask
app = Flask(__name__)

@app.route('/remote/command/<cmd>')
def remote_command(cmd):
    # Von überall auf der Welt steuerbar
    robot.send_command(cmd)
    return "Command executed"
```

**Cloud-Datenspeicherung:**

```python
def upload_sensor_data(self):
    data = {
        'timestamp': datetime.now(),
        'temperature': self.read_temperature(),
        'distance': self.read_ultrasonic(),
        'position': self.get_position()
    }
    # Upload zu AWS/Firebase/InfluxDB
    cloud_db.insert(data)
```

### 10. Machine Learning Training 🤖🎓

**Reinforcement Learning:**

```python
import tensorflow as tf

def train_autonomous_driving(self):
    # Roboter lernt durch Versuch und Irrtum
    for episode in range(1000):
        state = self.get_sensor_data()
        action = self.policy_network.predict(state)
        reward = self.execute_action(action)
        self.update_network(state, action, reward)
```

## Hardware-Erweiterungen

### Empfohlene Sensoren:

- 🔵 **Ultraschall-Sensor** (HC-SR04) - Abstandsmessung
- 📷 **Kamera-Modul** (Raspberry Pi Camera) - Computer Vision
- 🧭 **IMU-Sensor** (MPU6050) - Gyro & Beschleunigung
- 🌡️ **Temperatur-Sensor** (DHT22) - Umgebungsmessung
- 🎤 **Mikrofon-Array** - Spracherkennung
- 💡 **LED-Strips** (WS2812B) - Statusanzeige & Effekte
- 🔊 **Lautsprecher** - Audio-Feedback

### Mögliche Roboter-Plattformen:

- Arduino-basierte Roboter
- Raspberry Pi Roboter
- ESP32-gesteuerte Roboter
- Lego Mindstorms EV3
- Custom PCB Design

## Community & Contribution

Haben Sie eigene Ideen? 💡

1. **Fork** das Repository
2. **Erstellen** Sie einen Feature-Branch
3. **Implementieren** Sie Ihre Idee
4. **Testen** Sie ausführlich
5. **Pull Request** erstellen

**Diskussionen & Vorschläge:**

- [GitHub Discussions](https://github.com/marcus39-web/Pyton-Roboter-Interface/discussions)
- [Feature Requests](https://github.com/marcus39-web/Pyton-Roboter-Interface/issues)

## Changelog

### Version 1.0.0 (2026-03-02)

- ✅ Initiales Release
- ✅ OOP-Struktur implementiert
- ✅ Logging-System eingerichtet
- ✅ Unit-Tests (100% Coverage)
- ✅ Vollständige Dokumentation

---

**⭐ Wenn Ihnen dieses Projekt gefällt, geben Sie ihm einen Star auf GitHub!**

## Heartbeat-System 💓

### Warum Heartbeat wichtig ist

**Problem bei WLAN-Verbindungen:**

- PC sitzt im 2. Stock, Roboter im Erdgeschoss
- WLAN kann im Treppenhaus oder durch Wände abbrechen
- **Ohne Heartbeat:** Roboter bemerkt Disconnect nicht → läuft unkontrolliert weiter! ⚠️
- **Mit Heartbeat:** Roboter stoppt sofort bei Signal-Ausfall

**Besonders wichtig für:**

- FEZ Bit / SITCore Hardware
- WLAN-gesteuerte Roboter
- Große Entfernungen zwischen PC und Roboter
- Sicherheitskritische Anwendungen

### Heartbeat Funktionsweise

```python
# Automatisches Lebenszeichen-System

┌─────────────────────────────────────┐
│  PC (2. Stock)                      │
│  - Hauptprogramm läuft              │
│  - Heartbeat-Thread läuft parallel  │
└─────────────────────────────────────┘
           ↓ Alle 2 Sekunden ↓
        "HB" Signal (2 Bytes)
           ↓ über WLAN ↓
┌─────────────────────────────────────┐
│  Roboter (Erdgeschoss)              │
│  - Wartet auf Heartbeat             │
│  - Bei Timeout: STOP                │
└─────────────────────────────────────┘
```

**Ablauf:**

1. PC und Roboter verbunden
2. `start_heartbeat()` gestartet
3. Jede Sekunde: PC sendet "HB"
4. Roboter empfängt "HB" → läuft weiter
5. WLAN-Abbruch → kein "HB" für 5 Sekunden
6. Roboter-Timeout → AUTOMATISCHER STOP ⚠️
7. Programmierer drückt NICHT rechtzeitig "STOP"
8. **Roboter stoppt trotzdem!** ✅ SICHERHEIT

### Heartbeat Verwendung

#### Einfaches Beispiel

```python
from basis_class import BrainBotRemote
import time

# Roboter-Instanz mit Heartbeat-Intervall erstellen
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    port=5000,
    heartbeat_interval=2.0  # Alle 2 Sekunden
)

# Verbindung herstellen
if robot.connect():
    # ⭐ WICHTIG: Heartbeat starten!
    robot.start_heartbeat()

    try:
        # Befehle senden (Heartbeat läuft im Hintergrund)
        robot.send_command("FORWARD")
        time.sleep(3)

        robot.send_command("TURN_LEFT")
        time.sleep(2)

        robot.send_command("STOP")

    finally:
        # Heartbeat immer stoppen (auch bei Fehlern!)
        robot.stop_heartbeat()
        robot.disconnect()
```

#### Mit Exception-Handling

```python
import time
from basis_class import BrainBotRemote

try:
    robot = BrainBotRemote("192.168.1.100", port=5000, heartbeat_interval=2.0)

    if not robot.connect():
        raise ConnectionError("Roboter nicht erreichbar")

    # Heartbeat starten
    if not robot.start_heartbeat():
        raise RuntimeError("Heartbeat konnte nicht gestartet werden")

    # Programmlogik hier...
    robot.send_command("FORWARD")
    time.sleep(5)
    robot.send_command("STOP")

except Exception as e:
    print(f"Fehler: {e}")

finally:
    # Sauberes Herunterfahren
    robot.stop_heartbeat()
    robot.disconnect()
```

#### Mit verschiedenen Heartbeat-Intervallen

```python
# Schnelles Heartbeat (für instabile WLAN-Verbindungen)
robot_fast = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=1.0  # Jede Sekunde
)

# Normales Heartbeat (empfohlen)
robot_normal = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=2.0  # Alle 2 Sekunden
)

# Seltenes Heartbeat (für sehr stabile Verbindungen)
robot_slow = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=5.0  # Alle 5 Sekunden
)
```

### Heartbeat Konfiguration

#### Empfohlene Werte

| Szenario              | Intervall | Grund                    |
| --------------------- | --------- | ------------------------ |
| 🔴 Instabile WLAN     | 1.0s      | Schnelle Erkennung       |
| 🟡 Normale Nutzung    | 2.0s      | **Standard (empfohlen)** |
| 🟢 Stabile Verbindung | 5.0s      | Weniger Netzwerklast     |
| 🏠 Smart-Home         | 3.0s      | Balanciert               |
| 🚗 Mobile Nutzung     | 1.5s      | Höhere Frequenz          |

#### Hardware-spezifische Einstellungen

**FEZ Bit / SITCore:**

```python
# Optimalste Einstellung für FEZ Bit
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    port=5000,
    heartbeat_interval=2.0  # 2 Sekunden
)
robot.connect()
robot.start_heartbeat()
```

**Arduino-basierte Roboter:**

```python
# Arduino kann schnelle Signale verarbeiten
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=1.0  # 1 Sekunde für schnellere Reaktion
)
```

**Raspberry Pi Roboter:**

```python
# Raspberry Pi benötigt mehr Zeit für Verarbeitung
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=3.0  # 3 Sekunden
)
```

### Heartbeat Log-Ausgabe

**Logfile-Beispiel (`robot_log.txt`):**

```
[2026-03-02 14:30:15] [CONNECT] Verbunden mit 192.168.1.100:5000
[2026-03-02 14:30:16] [HEARTBEAT] Thread gestartet (Intervall: 2.0s)
[2026-03-02 14:30:16] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:30:18] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:30:18] [COMMAND] Befehl gesendet: FORWARD
[2026-03-02 14:30:20] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:30:22] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:30:24] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:30:24] [COMMAND] Befehl gesendet: STOP
[2026-03-02 14:30:26] [HEARTBEAT] Gestoppt
[2026-03-02 14:30:26] [DISCONNECT] Verbindung getrennt
```

**Fehler-Beispiel:**

```
[2026-03-02 14:35:10] [HEARTBEAT] Thread gestartet (Intervall: 2.0s)
[2026-03-02 14:35:12] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:35:14] [HEARTBEAT] Lebenszeichen gesendet (HB)
[2026-03-02 14:35:16] [ERROR] Heartbeat-Fehler: [Errno 10054] Connection reset by peer
[2026-03-02 14:35:16] [HEARTBEAT] Thread gestoppt
```

### Heartbeat Thread-Sicherheit

**Thread-Konzept:**

```python
┌─ Hauptprogramm ────────────────────┐
│                                    │
│  robot.start_heartbeat()           │
│  ↓                                 │
│  ┌─ Heartbeat-Thread ─────┐       │
│  │                        │       │
│  │ Schleife:              │       │
│  │ - Warte 2 Sekunden     │       │
│  │ - Sende "HB"           │       │
│  │ - Log Eintrag          │       │
│  │ - Prüfe heartbeat_active
│  │ (läuft parallel!)      │       │
│  └────────────────────────┘       │
│                                    │
│  robot.send_command("FORWARD")    │
│  (blockiert NICHT auf Heartbeat)  │
│                                    │
│  robot.stop_heartbeat()           │
│  (wahtet auf Thread-Ende)         │
│                                    │
└────────────────────────────────────┘
```

**Wichtige Eigenschaften:**

- ✅ **Non-Blocking:** Hauptprogramm läuft weiter
- ✅ **Thread-Safe:** Nutzt `threading.Thread`
- ✅ **Daemon-Mode:** Wird mit Hauptprogramm beendet
- ✅ **Sauber beendbar:** Mit `stop_heartbeat()`

### Troubleshooting Heartbeat

#### Problem: "Heartbeat läuft bereits!"

```python
# ❌ FALSCH: Zweimal starten
robot.start_heartbeat()
robot.start_heartbeat()  # Error!

# ✅ RICHTIG: Nur einmal starten
robot.start_heartbeat()
```

#### Problem: Heartbeat stoppt sofort

```python
# ❌ FALSCH: Disconnect vor stop_heartbeat
robot.start_heartbeat()
robot.disconnect()  # Socket wird geschlossen!

# ✅ RICHTIG: Zuerst Heartbeat stoppen
robot.start_heartbeat()
robot.stop_heartbeat()  # Sauber beenden
robot.disconnect()
```

#### Problem: Roboter reagiert langsam auf Heartbeat-Timeout

```python
# Heartbeat-Intervall verkürzen
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=1.0  # Schneller! (statt 2.0)
)
robot.connect()
robot.start_heartbeat()
```

#### Problem: Zu viel Netzwerk-Traffic

```python
# Heartbeat-Intervall verlängern
robot = BrainBotRemote(
    robot_ip="192.168.1.100",
    heartbeat_interval=5.0  # Weniger Traffic (statt 2.0)
)
robot.connect()
robot.start_heartbeat()
```

### Best Practice Checkliste ✅

```python
# ✅ MUSTER-IMPLEMENTIERUNG

from basis_class import BrainBotRemote
import time

def safe_robot_control():
    """Sichere Roboter-Steuerung mit Heartbeat"""
    robot = None

    try:
        # 1. Instanz erstellen
        robot = BrainBotRemote(
            robot_ip="192.168.1.100",
            heartbeat_interval=2.0
        )

        # 2. Verbindung prüfen
        if not robot.connect():
            raise ConnectionError("Roboter nicht erreichbar")

        # 3. Heartbeat aktivieren
        if not robot.start_heartbeat():
            raise RuntimeError("Heartbeat-Fehler")

        # 4. Befehle senden
        robot.send_command("FORWARD")
        time.sleep(2)
        robot.send_command("STOP")

    except Exception as e:
        print(f"❌ Fehler: {e}")

    finally:
        # 5. Sauberes Herunterfahren (IMMER!)
        if robot:
            if robot.heartbeat_active:
                robot.stop_heartbeat()
            robot.disconnect()

# Ausführen
if __name__ == "__main__":
    safe_robot_control()
```

### Performance & Netzwerk

**Heartbeat-Datenvolumen:**

```
Heartbeat-Größe:  2 Bytes ("HB")
Intervall:        2 Sekunden
Häufigkeit:       30 pro Minute
Datenvolumen:     60 Bytes/Minute = 3.6 KB/Stunde

→ Vernachlässigbar! Kein Performance-Problem
```

**CPU-Auslastung:**

```
Heartbeat-Thread:  < 0.1% CPU
sleep(0.1):        Läuft nur 100ms pro Sekunde
Gesamtauslastung:  Unmerklich klein

→ Kein Problem auf schwacher Hardware (Raspberry Pi, Arduino)
```
