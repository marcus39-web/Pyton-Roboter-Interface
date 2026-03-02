# README_KATAGO__TESTS.md

## Zweck

Diese Datei dokumentiert den **manuellen Testablauf für die Kategorisierung** im Projekt.
Der Fokus liegt auf reproduzierbaren Schritten, klaren Eingaben und erwarteten Ergebnissen.

## Voraussetzungen

- Python ist installiert
- Abhängigkeiten sind installiert (`pip install -r requirements.txt`)
- Projektordner ist geöffnet
- Optional für DB-Tests: Docker + Docker Compose

## Docker/MySQL Setup (erweiterbar)

1. `.env` aus Vorlage erstellen:

```bash
cp .env.example .env
```

2. MySQL + Adminer starten:

```bash
docker compose up -d
```

3. Erreichbarkeit prüfen:

- MySQL: `127.0.0.1:3306`
- Adminer: `http://127.0.0.1:8081`
- Login: User `root`, Passwort leer

4. Kategorisierungs-Persistenz aktivieren:

- In `.env`: `APP_USE_MYSQL=1`

## Schnellcheck (Basis)

1. Tests ausführen:

```bash
pytest tests/ -v
```

2. Erwartung:

- Alle bestehenden Unit-Tests laufen erfolgreich durch.

## Kategorisierung – Manueller Testablauf

> Hinweis: Falls die Kategorisierung aktuell über simulierte Daten läuft, dieselben Schritte mit den Simulationseingaben durchführen.

### Testfall KAT-01: Eindeutiger Standardfall

- **Ziel:** Prüfen, ob ein klarer Eingabefall konsistent einer Kategorie zugeordnet wird.
- **Schritte:**
  1. Anwendung/Funktion mit einem bekannten, eindeutigen Testinput starten.
  2. Kategorie-Ergebnis notieren.
  3. Den identischen Input mindestens 3x wiederholen.
- **Erwartung:**
  - Die zurückgegebene Kategorie ist in allen Wiederholungen identisch.

### Testfall KAT-02: Grenzbereich

- **Ziel:** Verhalten an Entscheidungsgrenzen prüfen.
- **Schritte:**
  1. Einen Input knapp unter dem Grenzwert ausführen.
  2. Einen Input exakt auf dem Grenzwert ausführen.
  3. Einen Input knapp über dem Grenzwert ausführen.
- **Erwartung:**
  - Die Kategorisierung ist nachvollziehbar und stabil (kein zufälliges Umspringen).

### Testfall KAT-03: Ungültige Eingaben

- **Ziel:** Robustheit bei fehlerhaften Inputs.
- **Schritte:**
  1. Leere Eingabe testen.
  2. Falschen Datentyp testen.
  3. Fehlende Pflichtfelder testen.
- **Erwartung:**
  - Kein Absturz.
  - Saubere Fehlermeldung oder definierter Fallback.

### Testfall KAT-04: Wiederanlauf / Lernmodus

- **Ziel:** Prüfen, ob Ergebnisse über mehrere Läufe konsistent bleiben.
- **Schritte:**
  1. Anwendung einmal komplett durchlaufen lassen.
  2. Anwendung neu starten.
  3. Dieselben Eingaben erneut prüfen.
- **Erwartung:**
  - Kategorien bleiben bei gleichen Eingaben konsistent.

### Testfall KAT-05: MySQL Persistenz

- **Ziel:** Prüfen, ob Kategorisierungsereignisse dauerhaft in MySQL landen.
- **Schritte:**
  1. Mock-Server starten: `python test_server.py`
  2. Client starten: `python main.py`
  3. In Adminer anmelden (Server `mysql`, DB `brainbot_ai`, User `root`, Passwort leer).
  4. Tabellen `samples` und `predictions` öffnen.
- **Erwartung:**
  - Neue Datensätze in `samples` und `predictions` nach jedem Lauf.
  - `decision_text` enthält z. B. `OBSTACLE`/`CLEAR`.

### Testfall KAT-06: Kategorie-Referenzdaten

- **Ziel:** Sicherstellen, dass Referenzkategorien gepflegt sind.
- **Schritte:**
  1. Tabelle `categories` öffnen.
  2. Einträge `OBSTACLE` und `CLEAR` prüfen.
- **Erwartung:**
  - Beide Kategorien vorhanden.
  - Bei neuen Entscheidungswerten werden Kategorien automatisch ergänzt.

## Ergebnisprotokoll (Vorlage)

| Datum | Testfall | Ergebnis | Notizen |
|---|---|---|---|
| YYYY-MM-DD | KAT-01 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-02 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-03 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-04 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-05 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-06 | PASS/FAIL |  |

## Abschlusskriterium

Die Kategorisierung gilt als testbar dokumentiert, wenn:

- alle vier Testfälle einmal vollständig ausgeführt wurden,
- für DB-Betrieb zusätzlich KAT-05 und KAT-06 erfolgreich sind,
- Ergebnisse protokolliert sind,
- bei FAIL ein reproduzierbarer Schritt im Notizfeld vorhanden ist.
