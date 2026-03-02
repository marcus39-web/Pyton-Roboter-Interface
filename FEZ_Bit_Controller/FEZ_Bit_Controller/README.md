# BrainBot AI - FEZ Bit / SITCore Controller (C#)

**TCP Socket Listener für Roboter-Steuerung mit Heartbeat-System**

---

## 📋 Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Hardware-Anforderungen](#hardware-anforderungen)
- [Installation & Setup](#installation--setup)
- [GPIO-Pin-Konfiguration](#gpio-pin-konfiguration)
- [Funktionsweise](#funktionsweise)
- [Heartbeat-System](#heartbeat-system)
- [Befehls-Protokoll](#befehls-protokoll)
- [Sicherheitsfunktionen](#sicherheitsfunktionen)
- [Debugging & Troubleshooting](#debugging--troubleshooting)
- [Erweiterungen](#erweiterungen)

---

## Übersicht

Dieser C#-Code läuft auf dem **FEZ Bit / SITCore** Mikrocontroller und:

- ✅ Empfängt TCP-Befehle vom Python-Interface (PC)
- ✅ Steuert Motoren über GPIO und PWM
- ✅ Überwacht Heartbeat-Signal (5 Sekunden Timeout)
- ✅ Stoppt automatisch bei WLAN-Abbruch
- ✅ Bietet Status-LED für visuelle Rückmeldung

---

## Hardware-Anforderungen

| Komponente            | Beschreibung                      |
| --------------------- | --------------------------------- |
| **FEZ Bit / SITCore** | Mikrocontroller (GHI Electronics) |
| **Motor-Treiber**     | L298N, DRV8833 oder ähnlich       |
| **2x DC-Motoren**     | Für linke/rechte Seite            |
| **WLAN-Modul**        | Für TCP/IP-Kommunikation          |
| **Stromversorgung**   | Batterie/Akku (7.4V empfohlen)    |

---

## Installation & Setup

### Visual Studio Setup erforderlich:

- Visual Studio 2022 oder neuer
- TinyCLR OS Extension
- GHI Electronics TinyCLR Nuget-Pakete

---

## GPIO-Pin-Konfiguration

**⚠️ WICHTIG: Pins müssen an Ihre Hardware angepasst werden!**

```csharp
// Motor Links
_motorLeftForward  = gpio.OpenPin(FEZ.GpioPin.A0);
_motorLeftBackward = gpio.OpenPin(FEZ.GpioPin.A1);

// Motor Rechts
_motorRightForward  = gpio.OpenPin(FEZ.GpioPin.A2);
_motorRightBackward = gpio.OpenPin(FEZ.GpioPin.A3);
```

---

## Heartbeat-System

### Warum wichtig?

```
Ohne Heartbeat:
  WLAN bricht ab → Roboter merkt nichts → läuft weiter! ⚠️

Mit Heartbeat:
  Kein Signal für 5s → Roboter stoppt AUTOMATISCH! ✅
```

### Implementierung:

```csharp
if (timeSinceHeartbeat.TotalMilliseconds > 5000)
{
    MotorStop();           // NOT-STOPP
    DisconnectClient();    // Verbindung trennen
    BlinkStatusLed(5);     // Warnung
}
```

---

## Befehls-Protokoll

| Befehl         | Aktion                   |
| -------------- | ------------------------ |
| **FORWARD**    | Beide Motoren vorwärts   |
| **BACKWARD**   | Beide Motoren rückwärts  |
| **TURN_LEFT**  | Links zurück, rechts vor |
| **TURN_RIGHT** | Links vor, rechts zurück |
| **STOP**       | Alle Motoren aus         |
| **HB**         | Heartbeat (automatisch)  |

---

## Sicherheitsfunktionen

1. ✅ Heartbeat-Timeout (5 Sekunden)
2. ✅ Exception-Handling überall
3. ✅ NOT-STOPP bei Disconnect
4. ✅ Status-LED Feedback
5. ✅ Geschwindigkeitsbegrenzung

---

## Debugging & Troubleshooting

### Häufige Fehler:

**❌ Motor läuft nicht:**

- GPIO-Pins richtig konfiguriert?
- Stromversorgung vorhanden?
- PWM aktiviert?

**❌ Heartbeat-Timeout:**

- Python-Programm läuft?
- WLAN-Verbindung stabil?
- Zu weit entfernt?

---

## Autor

**Marcus Reiser**

- 🐙 GitHub: [marcus39-web](https://github.com/marcus39-web)
- 🎓 Schulprojekt: BrainBot AI
- 📅 Datum: März 2026

---

## Lizenz

MIT License - Frei verwendbar für Bildungszwecke

---

**Viel Erfolg mit dem BrainBot!** 🤖⚡✨
