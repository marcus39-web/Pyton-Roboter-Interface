# BrainBot AI – Testläufe

## Ziel
Lokale Prüfung der Client-Server-Kommunikation zwischen `main.py` und `test_server.py`.

## Voraussetzungen
- Python 3.8+
- Arbeitsordner: `D:\01_Eigene_Projekte\GHI Python-Roboter-Interface OOP\BrainBot_AI`

## Testablauf

### 1. Mock-Server starten (Terminal 1)
```powershell
python test_server.py
```

Erwartet:
- `Mock-Server läuft auf 127.0.0.1:5000`
- `Warte auf Client...`

### 2. Client starten (Terminal 2)
```powershell
python main.py
```

Erwartet:
- `Verbunden mit 127.0.0.1:5000`
- `Befehl gesendet: STOP`
- `Befehl gesendet: TURN_LEFT_90`
- `Verbindung getrennt`

### 3. Server-Empfang prüfen (Terminal 1)
Erwartet:
- `Client verbunden`
- Empfang von `STOP`
- Empfang von `TURN_LEFT_90`

## Häufige Fehler

### WinError 10060
Ursachen:
- Server nicht gestartet
- Falsche IP in `main.py`

Fix:
- Server zuerst starten
- In `main.py` für lokalen Test:
```python
my_robot = BrainBotRemote(robot_ip="127.0.0.1")
```

## Beenden
- Server in Terminal 1 mit `Ctrl+C` stoppen.

## Teststatus
- Lokaler Test (127.0.0.1:5000): **erfolgreich**.
