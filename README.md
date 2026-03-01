# Pyton-Roboter-Interface (BrainBot_AI)

Kleines Python-OOP-Projekt zur Fernsteuerung eines BrainBot-Roboters.

## Dateien

- `basis_class.py` – Klasse `BrainBotRemote` (Connect, Command, Disconnect)
- `main.py` – Beispiel-Ablauf mit einfacher KI-Entscheidungslogik

## Start

1. Python 3 installieren
2. Im Projektordner ausführen:

```bash
python main.py
```

## Hinweis

In `main.py` ggf. die Roboter-IP anpassen:

- `robot_ip="192.168.1.100"`

## Beispiel: Sensor-Daten empfangen und Sicherheits-Check

```python
# 1. Schritt: Erstelle eine Funktion, die Sensordaten vom Roboter empfängt
def receive_sensor_data(connection):
    data = connection.recv(1024).decode('utf-8')
    return data

# 2. Schritt: Wenn die Distanz unter 20cm ist, sende den Befehl 'STOP'
def check_safety(distance_string):
    dist = float(distance_string.split(":")[1])
    if dist < 20.0:
        return "CMD:STOP"
    return "CMD:OK"
```

**Hinweis:**  
Erwartetes Format für `distance_string`: `DIST:18.5`

## Beispiel: KI-Entscheidung und STOP-Befehl (PC-Seite)

```python
# EMPFANG: Wir warten auf Daten vom SC20100S Modul
raw_data = socket.receive()

# ANALYSE: Die KI prüft den Wert (Machine Learning Modell)
prediction = my_model.predict(raw_data)

# KORREKTUR: Wenn Gefahr > 80%, sende STOP-Befehl per WLAN
if prediction > 0.8:
    socket.send("CMD_STOP")
```

## Beispiel: Ausführung auf dem Roboter (C#-Seite)

```csharp
// EMPFANG: Der Befehl kommt vom PC über die 3 Antennen rein
string command = wifiModule.Read();

// REAKTION: C# setzt den KI-Befehl direkt in Strom für die Motoren um
if (command == "CMD_STOP") {
    MotorDriver.Halt();              // Sofortiger Stopp
    LedRing.SetColor(Orange);        // LED-Ring zeigt 'Eingriff der KI'
}
```
