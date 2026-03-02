# README Keyboard-Only Tests

Kurzanleitung für reine Tastatur-Tests der BrainBot-Steuerung (ohne Roboter, mit Mock-Server).

## Ziel

- Steuerung nur über Tastatur prüfen
- Befehle im Mock-Server nachvollziehen
- Start/Stop/Disconnect sicher testen

## Setup

### Terminal 1: Mock-Server

```bash
python test_server.py
```

### Terminal 2: Web-Steuerung

```bash
python web_control_server.py --host 127.0.0.1 --web-port 8080 --robot-ip 127.0.0.1 --robot-port 5000
```

### Browser öffnen

```text
http://127.0.0.1:8080
```

Wichtig: Einmal in die Webseite klicken, damit Tastaturfokus aktiv ist.

## Tastenbelegung

- `W` → `FORWARD`
- `A` → `TURN_LEFT_90`
- `S` → `BACKWARD`
- `D` → `TURN_RIGHT_90`
- `E` → Connect (`START`)
- `Leertaste` → `STOP`
- `Q` → Disconnect

## Testablauf (Empfohlen)

1. `E` drücken → Verbindung herstellen
2. `W`, `A`, `D`, `S` nacheinander drücken
3. `Leertaste` drücken (Not-Stopp)
4. `Q` drücken (Disconnect)
5. Verbindung aktivieren, dann Browserfenster wechseln → Auto-Not-Aus prüfen

## Erwartetes Ergebnis

Im Mock-Server erscheinen die Befehle in derselben Reihenfolge.

Beim Fenster-/Tab-Wechsel während aktiver Verbindung wird zusätzlich ein `STOP` ausgelöst.

Beispiel:

```text
← FORWARD
← TURN_LEFT_90
← TURN_RIGHT_90
← BACKWARD
← STOP
```

## Fehlerbilder

### Keine Reaktion auf Tasten

- Browser-Fokus fehlt → in die Seite klicken
- Falsches Fenster aktiv → Browserfenster fokussieren

### Keine Verbindung bei `E`

- Prüfen, ob `test_server.py` läuft
- Port 5000 belegt? Dann freien Port nutzen und beide Starts anpassen

## Abschluss

Wenn alle Eingaben wie erwartet ankommen, ist die Keyboard-Steuerung freigegeben.
