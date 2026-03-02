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

**⚠️ SEHR WICHTIG:**

- `root` ohne Passwort ausschließlich lokal auf einem isolierten Entwicklungsrechner verwenden.
- Keine Nutzung in produktiven oder geteilten Netzwerken.
- Für spätere reale Nutzung auf Benutzer mit Passwort und eingeschränkte Rechte umstellen.

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

### Testfall KAT-07: Blockansicht (Tag/Woche/Monat/Jahr)

- **Ziel:** Sicherstellen, dass Kategorisierungen in Zeitblöcken angezeigt werden.
- **Schritte:**
  1. Report-Server starten: `python categorization_report_server.py --host 0.0.0.0 --web-port 8092`
  2. Browser öffnen: `http://127.0.0.1:8092`
  3. Nacheinander `Tag`, `Woche`, `Monat`, `Jahr` auswählen.
- **Erwartung:**
  - Für jeden Zeitraum wird eine Blocktabelle mit Summen angezeigt.
  - `Erstellt am` ist sichtbar.

### Testfall KAT-08: JPG-Export mit Vermaßung und Zimmername

- **Ziel:** Prüfen, ob eine Datei mit Metadaten erzeugt wird.
- **Schritte:**
  1. In der Report-UI `Zimmername`, `Breite (cm)`, `Höhe (cm)` ausfüllen.
  2. Optional `Radius` und `Aussparung` setzen (Seite/Breite/Tiefe).
  2. `JPG EXPORT` auslösen.
  3. Ordner `categorization_exports/` prüfen.
- **Erwartung:**
  - Eine `.jpg` Datei wurde erzeugt.
  - Dateiname enthält Zimmername und Zeitraum.
  - Datei enthält Text: `Erstellt am`, Zimmername, Vermaßung.
  - Datei zeigt Draufsicht des Raums inkl. seitlicher Vermaßung (DIN-ähnlich, schematisch).
  - Bei gesetzten Werten sind Radius/Aussparung in der Zeichnung erkennbar.
  - `DOWNLOAD LETZTER JPG` lädt die zuletzt erstellte Datei direkt herunter.
  - In der Export-Historie erscheint der neue Eintrag mit Download-Link.

## Ergebnisprotokoll (Vorlage)

| Datum | Testfall | Ergebnis | Notizen |
|---|---|---|---|
| YYYY-MM-DD | KAT-01 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-02 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-03 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-04 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-05 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-06 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-07 | PASS/FAIL |  |
| YYYY-MM-DD | KAT-08 | PASS/FAIL |  |

## Abschlusskriterium

Die Kategorisierung gilt als testbar dokumentiert, wenn:

- alle vier Testfälle einmal vollständig ausgeführt wurden,
- für DB-Betrieb zusätzlich KAT-05 und KAT-06 erfolgreich sind,
- für Ausgabe/Export zusätzlich KAT-07 und KAT-08 erfolgreich sind,
- Ergebnisse protokolliert sind,
- bei FAIL ein reproduzierbarer Schritt im Notizfeld vorhanden ist.

## Projektabschluss-Stand (02.03.2026)

- Kategorisierungsausgabe mit Zeitblöcken (Tag/Woche/Monat/Jahr) ist implementiert.
- Raum-Draufsicht mit DIN-ähnlicher Vermaßung (schematisch) ist sichtbar.
- Erweiterte Geometrie (Radius, Aussparung Seite/Breite/Tiefe) ist in UI und JPG-Export integriert.
- Export-Historie und Direkt-Download der JPG-Dateien sind aktiv.
- Lesbarkeitsfix für den unteren Vermaßungstext ist umgesetzt.

Dieser Stand wurde als finaler Dokumentationsstand gespeichert und auf GitHub gepusht.
