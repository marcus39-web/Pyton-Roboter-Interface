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
