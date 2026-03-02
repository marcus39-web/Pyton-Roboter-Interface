# README Web-Steuerung Tests

Diese Anleitung beschreibt die Testläufe für die Web-Steuerung (Maus + iPhone Touch + Tastatur) **ohne echten Roboter**.

## Ziel

- Verbindung über `web_control_server.py` testen
- Steuerbefehle über Browser senden
- Befehlsfluss im Mock-Server sichtbar prüfen
- Tastatursteuerung validieren

## Voraussetzungen

- Python installiert
- Projekt-Abhängigkeiten installiert
- Zwei Terminals geöffnet
- PC und iPhone im gleichen WLAN (für iPhone-Test)

## Schnellstart

### Terminal 1: Mock-Server starten

```bash
python test_server.py
```

Erwartete Ausgabe:

- `Mock-Server läuft auf 127.0.0.1:5000`
- `Warte auf Client...`

### Terminal 2: Web-Steuerung starten

```bash
python web_control_server.py --host 0.0.0.0 --web-port 8080 --robot-ip 127.0.0.1 --robot-port 5000
```

Erwartete Ausgabe:

- `Web-Steuerung läuft: http://0.0.0.0:8080`
- `Ziel-Roboter: 127.0.0.1:5000`

## Oberfläche öffnen

- PC: `http://127.0.0.1:8080`
- iPhone (gleiches WLAN): `http://<PC-IP>:8080`

PC-IP prüfen (Windows):

```powershell
ipconfig
```

## Funktions-Tests

### Test 1: Verbindung

1. In der Weboberfläche `START` drücken.
2. Status sollte `verbunden` anzeigen.
3. Im Mock-Server erscheint `Client verbunden`.

### Test 2: Richtungsbefehle

1. `VOR`, `LINKS`, `RECHTS`, `ZURÜCK` drücken.
2. Mock-Server zeigt die gesendeten Befehle (`FORWARD`, `TURN_LEFT_90`, `TURN_RIGHT_90`, `BACKWARD`).

### Test 3: Not-Stopp

1. `STOP` drücken.
2. Mock-Server zeigt `STOP`.

### Test 4: Tastatur

- `W` = Vor (`FORWARD`)
- `A` = Links (`TURN_LEFT_90`)
- `S` = Zurück (`BACKWARD`)
- `D` = Rechts (`TURN_RIGHT_90`)
- `E` = Start (Connect)
- `Leertaste` = Stop
- `Q` = Disconnect

### Test 5: Disconnect

1. `DISCONNECT` drücken.
2. Status sollte `Verbindung getrennt` anzeigen.

## Troubleshooting

### Keine Verbindung

- Läuft `test_server.py` wirklich?
- Stimmt `--robot-ip 127.0.0.1 --robot-port 5000`?
- Ist Port `5000` frei oder bereits belegt von anderem Prozess?

### iPhone erreicht Seite nicht

- Ist der Web-Server mit `--host 0.0.0.0` gestartet?
- Sind PC und iPhone im gleichen WLAN?
- Firewall erlaubt eingehend Port `8080`?

### Tasten reagieren nicht

- Vorher einmal in die Webseite klicken (Fokus setzen).

## Abschluss

Wenn alle fünf Tests erfolgreich sind, ist die Web-Steuerung für den späteren Robotereinsatz vorbereitet.
