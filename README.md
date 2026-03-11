# BrainBot KI-Roboter-Interface (OOP)

## Einleitung

Dieses Projekt ist ein objektorientiertes Python-Interface zur Fernsteuerung und Kategorisierung des BrainBot-Roboters. Es bietet eine moderne KI-Integration, eine browserbasierte Liveansicht und ist für schulische Prüfungszwecke sowie spätere Hardware-Erweiterung konzipiert.

---

## Voraussetzungen

- **Betriebssystem:** Windows, Linux oder macOS
- **Python:** Version 3.8 oder neuer
- **Editor:** Visual Studio Code (empfohlen)
- **Abhängigkeiten:**
  - Python-Standardbibliothek
  - Optional: `mysql-connector-python`, `Pillow` (für MySQL-Persistenz und Bildexport)
  - Testing: `pytest`, `pytest-cov`

Installiere alle Abhängigkeiten mit:

```bash
pip install -r requirements.txt
```

---

## Netzwerk & WLAN-Anbindung

Die Kommunikation mit dem Roboter erfolgt über TCP/IP – typischerweise per WLAN. Die IP-Adresse des Roboters wird beim Start angegeben (z.B. `192.168.1.100` für WLAN, `127.0.0.1` für lokale Tests). Die Verbindung wird durch die Klasse `BrainBotRemote` aufgebaut:

- **Verbindung:**
  ```python
  robot = BrainBotRemote(robot_ip="192.168.1.100", port=5000)
  robot.connect()
  ```
- **Heartbeat:**
  Ein regelmäßiges Lebenszeichen (Heartbeat) sorgt für Sicherheit: Bei WLAN-Abbruch wird der Roboter automatisch gestoppt.
- **Fehlerbehandlung:**
  - Verbindungsabbrüche (z.B. durch schwaches WLAN) werden erkannt und führen zu Not-Aus.
  - Alle Aktionen und Fehler werden in `robot_log.txt` protokolliert.
- **Tipp:**
  - Bei Problemen: IP-Adresse prüfen, Roboter und PC im selben WLAN, Firewall-Einstellungen kontrollieren.

---

## Installation & Setup

1. **Repository klonen:**
   ```bash
   git clone https://github.com/marcus39-web/Pyton-Roboter-Interface.git
   cd "GHI Python-Roboter-Interface OOP"
   ```
2. **(Optional) MySQL & Docker:**
   - Für große Datenmengen kann die Kategorisierung in MySQL gespeichert werden.
   - Siehe `docker/` und `.env.example` für Konfiguration.

---

## Einstieg & erste Schritte

1. **VS Code öffnen:**
   ```bash
   code .
   ```
2. **Mock-Server starten (Terminal 1):**
   ```bash
   python test_server.py
   ```
3. **Client starten (Terminal 2):**
   ```bash
   python main.py
   ```
4. **Roboter-IP einstellen:**
   - Für lokale Tests: `robot_ip="127.0.0.1"`
   - Für echten Roboter: IP im Netzwerk ermitteln und eintragen

**Beispiel für einen minimalen Testlauf:**

```python
from basis_class import BrainBotRemote
robot = BrainBotRemote(robot_ip="127.0.0.1")
if robot.connect():
    robot.send_command("FORWARD")
    robot.send_command("STOP")
    robot.disconnect()
```

---

## KI-Integration & Datenfluss

- **Lernmodus:** Alle Befehle und Sensordaten werden in `learning_data.jsonl` gespeichert.
- **Trainingsdaten:**
  ```json
  {"timestamp": "2026-03-11T10:00:00", "command": "FORWARD", "distance": 45, "category": "Flur"}
  {"timestamp": "2026-03-11T10:00:02", "command": "STOP", "distance": 20, "category": "Hindernis"}
  ```
- **KI-Workflow:**
  1. Datensammlung im Lernmodus
  2. Training eigener Modelle (z. B. mit scikit-learn)
  3. Integration und Vorhersage im Live-Betrieb

**Beispiel für Modellintegration:**

```python
import joblib
model = joblib.load("mein_modell.pkl")
prediction = model.predict([[distance, ...]])
```

---

## Browser-Liveansicht (Kategorisierung)

Die Weboberfläche zeigt alle Kategorisierungsdaten und Exportfunktionen übersichtlich an.

**Start:**

1. Terminal öffnen:
   ```bash
   python categorization_report_server.py --host 0.0.0.0 --web-port 8092
   ```
2. Im Browser öffnen: [http://127.0.0.1:8092](http://127.0.0.1:8092)

**Features:**

- Blockansicht (Tag/Woche/Monat/Jahr)
- Tabellenansicht mit allen Messwerten
- JPG-Export inkl. Metadaten
- Raum-Draufsicht mit Vermaßung
- Export-Historie und Direkt-Download
- Responsive für PC & Smartphone

**Hinweise:**

- Die Seite ist nur erreichbar, wenn der Python-Server läuft.
- Bei Fehlern: Terminal prüfen, ggf. Browser aktualisieren (F5).

---

## Testen & Entwicklung

- **Alle Tests ausführen:**
  ```bash
  pytest tests/ -v
  ```
- **Testabdeckung:**
  ```bash
  pytest --cov=BrainBot_AI --cov-report=html
  ```
- **Detaillierte Testanleitungen:** Siehe `README_TEST/README_TESTLAEUFE.md`

---

## Fehlerbehandlung & Tipps

- **Häufige Fehler:**
  - Verbindung abgelehnt: Server läuft nicht oder falsche IP/Port
  - Timeout: Netzwerk prüfen, Roboter eingeschaltet?
  - Firewall blockiert: Einstellungen prüfen
- **Debugging:**
  - Logdatei: `robot_log.txt` enthält alle Aktionen
  - Lernmodus: `learning_data.jsonl` für KI-Training
- **Best Practices:**
  - Heartbeat immer aktivieren für Not-Aus
  - Nach jedem Test sauber disconnecten

---

## Lizenz

MIT License – frei verwendbar für Bildungszwecke

---

## Autor

Marcus Reiser (2026) – [marcus39-web](https://github.com/marcus39-web)
