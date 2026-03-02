"""
BrainBot Remote Control Module
===============================

Dieses Modul stellt die Hauptklasse zur Fernsteuerung des BrainBot Roboters bereit.
Die Kommunikation erfolgt über TCP/IP Socket-Verbindungen.

Autor: Marcus Reiser
Datum: 2026-03-02
Version: 1.0.0
"""

import socket
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class BrainBotRemote:
    """
    Klasse zur Fernsteuerung des BrainBot Roboters
    
    Diese Klasse ermöglicht die Verbindung zu einem BrainBot Roboter über TCP/IP
    und das Senden von Steuerbefehlen. Alle Aktionen werden automatisch in einer
    Log-Datei protokolliert.
    
    Attributes:
        robot_ip (str): IP-Adresse des Roboters
        port (int): Port-Nummer für die TCP-Verbindung (Standard: 5000)
        socket (socket.socket | None): Socket-Objekt für die Verbindung
        log_file (Path): Pfad zur Log-Datei
        heartbeat_interval (float): Intervall für Heartbeat-Signale in Sekunden
        heartbeat_active (bool): Status des Heartbeat-Threads
        heartbeat_thread (threading.Thread | None): Heartbeat-Thread
    
    Example:
        >>> robot = BrainBotRemote(robot_ip="192.168.1.100", port=5000)
        >>> if robot.connect():
        ...     robot.start_heartbeat(interval=2.0)  # Heartbeat alle 2 Sekunden
        ...     robot.send_command("FORWARD")
        ...     robot.stop_heartbeat()
        ...     robot.disconnect()
    """
    
    def __init__(self, robot_ip: str, port: int = 5000, heartbeat_interval: float = 2.0) -> None:
        """
        Initialisiert eine neue BrainBotRemote-Instanz
        
        Args:
            robot_ip (str): IP-Adresse des Roboters (z.B. "192.168.1.100")
            port (int, optional): Port-Nummer für die Verbindung. Standard: 5000
            heartbeat_interval (float, optional): Intervall für Heartbeat-Signale in Sekunden.
                                                  Standard: 2.0
        
        Note:
            Die Log-Datei wird automatisch im selben Verzeichnis wie diese
            Klassendatei erstellt. Der Heartbeat ist wichtig für die Sicherheit
            bei WLAN-Problemen und Netzwerkunterbrechungen.
        """
        # Roboter-Verbindungsparameter speichern
        self.robot_ip: str = robot_ip
        self.port: int = port
        
        # Socket-Objekt initialisieren (None = keine aktive Verbindung)
        self.socket: Optional[socket.socket] = None
        
        # Pfad zur Log-Datei bestimmen (im selben Verzeichnis wie diese Datei)
        self.log_file: Path = Path(__file__).parent / "robot_log.txt"
        
        # ==================== HEARTBEAT-KONFIGURATION ====================
        # Heartbeat-Einstellungen für Netzwerkstabilität
        # Problem: WLAN-Abbruch im Treppenhaus → Roboter läuft unkontrolliert weiter
        # Lösung: PC sendet regelmäßig "Bist du noch da?"-Signal
        
        # Zeitintervall zwischen Heartbeat-Signalen (in Sekunden)
        # Typische Werte:
        #   - 1.0s  = Sehr häufig (höhere Netzwerklast, schnellere Reaktion)
        #   - 2.0s  = Empfohlen (gutes Gleichgewicht)
        #   - 5.0s  = Selten (für stabile Verbindungen)
        self.heartbeat_interval: float = heartbeat_interval
        
        # Flag: Ist der Heartbeat-Thread aktiv?
        # True = Heartbeat läuft und sendet regelmäßig Signale
        # False = Heartbeat gestoppt
        self.heartbeat_active: bool = False
        
        # Python-Thread für asynchrone Heartbeat-Signale
        # Ein separater Thread verhindert, dass Heartbeat die Hauptprogramm blockiert
        self.heartbeat_thread: Optional[threading.Thread] = None
    
    def _log(self, level: str, message: str) -> None:
        """
        Interne Methode zum Schreiben von Log-Einträgen
        
        Diese Methode wird von allen anderen Methoden aufgerufen, um
        Aktionen und Fehler zu protokollieren. Jeder Eintrag enthält
        einen Timestamp, das Log-Level und die Nachricht.
        
        Args:
            level (str): Log-Level (z.B. "CONNECT", "ERROR", "COMMAND", "HEARTBEAT")
            message (str): Die zu loggende Nachricht
        
        Log-Format:
            [YYYY-MM-DD HH:MM:SS] [LEVEL] Nachricht
        
        Example:
            [2026-03-02 12:34:56] [CONNECT] Verbunden mit 192.168.1.100:5000
            [2026-03-02 12:34:57] [HEARTBEAT] Lebenszeichen gesendet
        
        Note:
            Falls beim Schreiben der Log-Datei ein Fehler auftritt, wird
            eine Warnung auf der Konsole ausgegeben, aber das Programm
            läuft weiter.
        """
        # Aktuellen Timestamp erstellen (Format: YYYY-MM-DD HH:MM:SS)
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log-Eintrag formatieren: [Timestamp] [Level] Nachricht
        log_entry: str = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            # Log-Datei im Append-Modus öffnen (erstellt Datei falls nicht vorhanden)
            with self.log_file.open("a", encoding="utf-8") as f:
                # Log-Eintrag in Datei schreiben
                f.write(log_entry)
        except Exception as e:
            # Bei Fehler: Warnung ausgeben, aber Programm nicht abbrechen
            print(f"⚠ Logging-Fehler: {e}")
    
    def connect(self) -> bool:
        """
        Stellt eine Verbindung zum Roboter her
        
        Diese Methode erstellt ein TCP-Socket und versucht, sich mit dem
        Roboter zu verbinden. Bei Erfolg wird die Verbindung geloggt.
        
        Returns:
            bool: True bei erfolgreicher Verbindung, False bei Fehler
        
        Raises:
            Keine - Exceptions werden intern behandelt
        
        Example:
            >>> robot = BrainBotRemote("192.168.1.100")
            >>> if robot.connect():
            ...     print("Verbunden!")
            ... else:
            ...     print("Verbindung fehlgeschlagen")
        
        Note:
            - Bei Verbindungsfehler wird das Socket zurückgesetzt
            - Timeout-Fehler werden als WinError 10060 geloggt
            - Connection-Refused-Fehler als WinError 10061
        """
        try:
            # TCP/IP Socket erstellen (AF_INET = IPv4, SOCK_STREAM = TCP)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Verbindung zum Roboter herstellen (IP + Port)
            self.socket.connect((self.robot_ip, self.port))
            
            # Erfolgs-Nachricht erstellen
            message: str = f"Verbunden mit {self.robot_ip}:{self.port}"
            
            # Erfolg auf Konsole ausgeben (✓ = Unicode-Häkchen)
            print(f"✓ {message}")
            
            # Erfolgreiche Verbindung loggen
            self._log("CONNECT", message)
            
            # True zurückgeben = Verbindung erfolgreich
            return True
            
        except Exception as e:
            # Fehler-Nachricht erstellen (enthält Exception-Details)
            message: str = f"Verbindungsfehler: {e}"
            
            # Fehler auf Konsole ausgeben (✗ = Unicode-Kreuz)
            print(f"✗ {message}")
            
            # Fehler loggen
            self._log("ERROR", message)
            
            # Socket bereinigen bei Fehler (wichtig für Tests!)
            if self.socket:
                self.socket.close()  # Socket schließen
                self.socket = None   # Referenz zurücksetzen
            
            # False zurückgeben = Verbindung fehlgeschlagen
            return False

    def send_command(self, command: str) -> bool:
        """
        Sendet einen Befehl an den Roboter
        
        Diese Methode sendet einen Textbefehl über die bestehende Socket-Verbindung
        an den Roboter. Der Befehl wird als UTF-8 kodierter String übertragen.
        
        Args:
            command (str): Der zu sendende Befehl (z.B. "FORWARD", "TURN_LEFT")
        
        Returns:
            bool: True bei erfolgreichem Senden, False bei Fehler
        
        Example:
            >>> robot = BrainBotRemote("192.168.1.100")
            >>> robot.connect()
            >>> robot.send_command("FORWARD")
            True
            >>> robot.send_command("STOP")
            True
        
        Note:
            - Es muss eine aktive Verbindung bestehen (socket != None)
            - Der Befehl wird automatisch als UTF-8 kodiert
            - Bei Fehler wird das Socket NICHT geschlossen
        """
        # Prüfen, ob eine Verbindung besteht
        if self.socket:
            try:
                # Befehl als UTF-8 Bytes kodieren und über Socket senden
                self.socket.send(command.encode())
                
                # Erfolgs-Nachricht erstellen
                message: str = f"Befehl gesendet: {command}"
                
                # Erfolg auf Konsole ausgeben (→ = Unicode-Pfeil)
                print(f"→ {message}")
                
                # Befehl loggen
                self._log("COMMAND", message)
                
                # True zurückgeben = Befehl erfolgreich gesendet
                return True
                
            except Exception as e:
                # Fehler-Nachricht erstellen (z.B. bei Verbindungsabbruch)
                message: str = f"Sendefehler: {e}"
                
                # Fehler auf Konsole ausgeben
                print(f"✗ {message}")
                
                # Fehler loggen
                self._log("ERROR", message)
                
                # False zurückgeben = Befehl konnte nicht gesendet werden
                return False
        else:
            # Keine Verbindung vorhanden
            message: str = "Keine Verbindung zum Roboter"
            
            # Fehler auf Konsole ausgeben
            print(f"✗ {message}")
            
            # Fehler loggen
            self._log("ERROR", message)
            
            # False zurückgeben = keine Verbindung
            return False

    def _heartbeat_worker(self) -> None:
        """
        Interne Worker-Funktion für den Heartbeat-Thread
        
        Diese Methode läuft in einem separaten Thread und sendet alle
        heartbeat_interval Sekunden ein kurzes "HEARTBEAT"-Signal an den Roboter.
        
        **Wichtig für Hardware-Integration (FEZ Bit/SITCore):**
        
        Problem bei WLAN-Ausfällen:
        - PC sitzt im 2. Stock, Roboter im Erdgeschoss
        - WLAN kann im Treppenhaus abbrechen
        - Ohne Heartbeat: Roboter bemerkt Trennung nicht und läuft weiter!
        
        Lösung mit Heartbeat:
        - Alle 2 Sekunden: PC sendet "HEARTBEAT" an Roboter
        - Roboter erkennt Signalverlust sofort
        - Roboter stoppt automatisch bei Timeout
        - SICHERHEIT: Kein unkontrolliertes Umherfahren! ⚠️
        
        Note:
            - Diese Funktion sollte NICHT direkt aufgerufen werden
            - Stattdessen start_heartbeat() verwenden
            - Der Thread läuft, bis heartbeat_active = False gesetzt wird
        """
        # Banner für Debug-Info
        print(f"♥ Heartbeat-Thread gestartet (Intervall: {self.heartbeat_interval}s)")
        self._log("HEARTBEAT", f"Thread gestartet (Intervall: {self.heartbeat_interval}s)")
        
        # Heartbeat-Schleife: Läuft, solange heartbeat_active = True ist
        while self.heartbeat_active:
            try:
                # Warte heartbeat_interval Sekunden
                # (nicht in einem Rutsch, sondern in kurzen Schritten prüfen)
                for _ in range(int(self.heartbeat_interval * 10)):
                    if not self.heartbeat_active:
                        # Abbruch signalisiert
                        break
                    time.sleep(0.1)  # 100ms warten
                
                # Nur Heartbeat senden, wenn Verbindung noch aktiv ist
                if self.heartbeat_active and self.socket:
                    try:
                        # Sehr kurzes Signal senden: "HB" (2 Bytes)
                        # FEZ Bit erwartet kompakte Daten!
                        self.socket.send(b"HB")
                        
                        # Heartbeat-Signal loggen (mit UTC-Timestamp)
                        self._log("HEARTBEAT", "Lebenszeichen gesendet (HB)")
                        
                    except Exception as e:
                        # Heartbeat konnte nicht gesendet werden
                        # Das bedeutet: WLAN ist weg oder Roboter offline!
                        error_msg: str = f"Heartbeat-Fehler: {e}"
                        print(f"⚠ {error_msg}")
                        self._log("ERROR", error_msg)
                        
                        # Heartbeat stoppen bei kritischem Fehler
                        self.heartbeat_active = False
                        
            except Exception as e:
                # Thread-Fehler (sollte nicht vorkommen)
                print(f"✗ Kritischer Heartbeat-Fehler: {e}")
                self._log("ERROR", f"Heartbeat-Thread Fehler: {e}")
                self.heartbeat_active = False
        
        # Heartbeat beendet
        print("♡ Heartbeat-Thread gestoppt")
        self._log("HEARTBEAT", "Thread gestoppt")

    def start_heartbeat(self) -> bool:
        """
        Startet den automatischen Heartbeat
        
        Diese Methode startet einen separaten Thread, der alle heartbeat_interval
        Sekunden ein Lebenszeichen-Signal ("HB") an den Roboter sendet.
        
        **Warum ist das wichtig?**
        
        Bei der Hardware-Integration mit FEZ Bit (SITCore):
        - WLAN-Verbindung kann unterbrochen werden (Treppenhaus-Effekt)
        - Ohne Heartbeat: Roboter bemerkt es nicht → läuft weiter!
        - Mit Heartbeat: Roboter stoppt bei Signal-Ausfall
        - SICHERHEIT FIRST! ⚠️
        
        Returns:
            bool: True wenn Heartbeat gestartet, False bei Fehler
        
        Example:
            >>> robot = BrainBotRemote("192.168.1.100")
            >>> robot.connect()
            >>> robot.start_heartbeat()  # Läuft jetzt im Hintergrund
            >>> robot.send_command("FORWARD")
            >>> # Heartbeat sendet automatisch alle 2 Sekunden HB
            >>> robot.stop_heartbeat()
        
        Note:
            - Muss NACH connect() aufgerufen werden
            - Läuft in separatem Thread (nicht-blockierend)
            - heartbeat_interval muss positiv sein
        """
        # Prüfen, ob bereits ein Heartbeat läuft
        if self.heartbeat_active:
            print("⚠ Heartbeat läuft bereits!")
            return False
        
        # Prüfen, ob Verbindung vorhanden ist
        if not self.socket:
            print("✗ Keine Verbindung zum Roboter - Heartbeat kann nicht starten")
            self._log("ERROR", "Heartbeat gestartet ohne Verbindung (fehlgeschlagen)")
            return False
        
        # Heartbeat aktivieren
        self.heartbeat_active = True
        
        # Neuen Thread erstellen und starten
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_worker,  # Funktion, die der Thread ausführt
            daemon=True                      # Daemon-Thread: Wird mit Hauptprogramm beendet
        )
        self.heartbeat_thread.start()
        
        # Erfolg-Meldung
        print(f"✓ Heartbeat gestartet (Intervall: {self.heartbeat_interval}s)")
        self._log("HEARTBEAT", f"Gestartet (Intervall: {self.heartbeat_interval}s)")
        
        return True

    def stop_heartbeat(self) -> bool:
        """
        Stoppt den automatischen Heartbeat
        
        Diese Methode stoppt den Heartbeat-Thread sauber und wartet,
        bis der Thread beendet ist.
        
        Returns:
            bool: True wenn Heartbeat gestoppt, False wenn nicht lief
        
        Example:
            >>> robot.start_heartbeat()
            >>> time.sleep(10)  # Heartbeat läuft
            >>> robot.stop_heartbeat()  # Jetzt gestoppt
        
        Note:
            - Der Thread wird sauber beendet (nicht mit force())
            - Nach dem Aufruf ist heartbeat_active = False
            - Kann sicher mehrfach aufgerufen werden
        """
        # Prüfen, ob Heartbeat läuft
        if not self.heartbeat_active:
            print("⚠ Heartbeat läuft nicht")
            return False
        
        # Flag setzen: Thread soll beenden
        self.heartbeat_active = False
        
        # Auf Thread-Ende warten (mit Timeout)
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5.0)
        
        # Erfolg-Meldung
        print("✓ Heartbeat gestoppt")
        self._log("HEARTBEAT", "Gestoppt")
        
        return True

    def disconnect(self) -> None:
        """
        Trennt die Verbindung zum Roboter
        
        Diese Methode schließt die Socket-Verbindung und setzt die
        Socket-Referenz zurück. Die Trennung wird geloggt.
        
        **Wichtig:** Stoppt auch automatisch den Heartbeat!
        
        Example:
            >>> robot = BrainBotRemote("192.168.1.100")
            >>> robot.connect()
            >>> robot.start_heartbeat()
            >>> robot.send_command("STOP")
            >>> robot.disconnect()  # Stoppt auch Heartbeat!
        
        Note:
            - Kann auch ohne aktive Verbindung aufgerufen werden
            - Nach disconnect() muss connect() erneut aufgerufen werden
            - Das Socket-Objekt wird vollständig freigegeben
        """
        # Heartbeat stoppen (wichtig!)
        if self.heartbeat_active:
            self.stop_heartbeat()
        
        # Prüfen, ob eine Verbindung besteht
        if self.socket:
            # Socket schließen (TCP-Verbindung beenden)
            self.socket.close()
            
            # Socket-Referenz zurücksetzen
            self.socket = None
            
            # Erfolgs-Nachricht erstellen
            message: str = "Verbindung getrennt"
            
            # Erfolg auf Konsole ausgeben
            print(f"✓ {message}")
            
            # Trennung loggen
            self._log("DISCONNECT", message)


# Beispiel-Nutzung (wird nur ausgeführt, wenn Datei direkt gestartet wird)
if __name__ == "__main__":
    # Dieses Beispiel zeigt die grundlegende Verwendung mit Heartbeat
    print("BrainBot Remote Control - Mit Heartbeat")
    print("=" * 50)
    
    # Roboter-Instanz erstellen (Heartbeat alle 2 Sekunden)
    robot: BrainBotRemote = BrainBotRemote(
        robot_ip="192.168.1.100",
        port=5000,
        heartbeat_interval=2.0
    )
    
    # Verbindung herstellen
    if robot.connect():
        # Heartbeat starten (WICHTIG für Sicherheit!)
        robot.start_heartbeat()
        
        try:
            # Befehle senden (Heartbeat läuft im Hintergrund)
            robot.send_command("FORWARD")
            time.sleep(2)
            
            robot.send_command("TURN_LEFT")
            time.sleep(2)
            
            robot.send_command("STOP")
            
        finally:
            # Sicherstellen, dass Heartbeat stoppt
            robot.stop_heartbeat()
            robot.disconnect()
    else:
        # Bei Fehler: Hinweis ausgeben
        print("\n⚠ Tipp: Prüfen Sie die Roboter-IP und stellen Sie sicher,")
        print("   dass der Roboter eingeschaltet und erreichbar ist.")