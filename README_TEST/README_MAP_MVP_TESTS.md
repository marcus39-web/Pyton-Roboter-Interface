# README Kartierungs-MVP Tests

Diese Anleitung testet das lokale Kartierungs-MVP ohne echten Roboter.

## Ziel

- Kartenansicht im Browser prüfen
- Mehrere virtuelle Roboter sichtbar machen
- Start/Pause/Step/Reset validieren

## Start

```bash
python map_mvp_server.py --host 0.0.0.0 --web-port 8090
```

Browser öffnen:

- PC: `http://127.0.0.1:8090`
- iPhone (gleiches WLAN): `http://<PC-IP>:8090`

## Funktions-Checks

1. Beim Laden müssen 3 Roboter sichtbar sein (R1, R2, R3).
2. Mit `START SIM` laufen die Roboter weiter.
3. Mit `PAUSE SIM` bleibt die Karte stehen.
4. Mit `EIN SCHRITT` bewegt sich die Simulation genau um einen Tick.
5. Mit `RESET` startet die Simulation wieder am Anfang.

## Erwartetes Ergebnis

- Hindernisse bleiben statisch.
- Trails wachsen während `running=true`.
- Status zeigt Tick und Running-Status.

## Troubleshooting

- Port belegt: anderen Port starten (`--web-port 8091`).
- Seite lädt nicht am iPhone: gleiches WLAN und Firewall-Port prüfen.

## Aktueller Stand

- Lokal vollständig ohne Hardware testbar.
- Geeignete Basis für späteren Anschluss echter Positions-/Sensordaten.
