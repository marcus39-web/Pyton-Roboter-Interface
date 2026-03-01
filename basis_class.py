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
    
    Example:
        >>> robot = BrainBotRemote(robot_ip="192.168.1.100", port=5000)
        >>> if robot.connect():
        ...     robot.send_command("FORWARD")
        ...     robot.disconnect()
    """
    
    def __init__(self, robot_ip: str, port: int = 5000) -> None:
        """
        Initialisiert eine neue BrainBotRemote-Instanz
        
        Args:
            robot_ip (str): IP-Adresse des Roboters (z.B. "192.168.1.100")
            port (int, optional): Port-Nummer für die Verbindung. Standard: 5000
        
        Note:
            Die Log-Datei wird automatisch im selben Verzeichnis wie diese
            Klassendatei erstellt.
        """
        # Roboter-Verbindungsparameter speichern
        self.robot_ip: str = robot_ip
        self.port: int = port
        
        # Socket-Objekt initialisieren (None = keine aktive Verbindung)
        self.socket: Optional[socket.socket] = None
        
        # Pfad zur Log-Datei bestimmen (im selben Verzeichnis wie diese Datei)
        self.log_file: Path = Path(__file__).parent / "robot_log.txt"
    
    def _log(self, level: str, message: str) -> None:
        """
        Interne Methode zum Schreiben von Log-Einträgen
        
        Diese Methode wird von allen anderen Methoden aufgerufen, um
        Aktionen und Fehler zu protokollieren. Jeder Eintrag enthält
        einen Timestamp, das Log-Level und die Nachricht.
        
        Args:
            level (str): Log-Level (z.B. "CONNECT", "ERROR", "COMMAND")
            message (str): Die zu loggende Nachricht
        
        Log-Format:
            [YYYY-MM-DD HH:MM:SS] [LEVEL] Nachricht
        
        Example:
            [2026-03-02 12:34:56] [CONNECT] Verbunden mit 192.168.1.100:5000
        
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

    def disconnect(self) -> None:
        """
        Trennt die Verbindung zum Roboter
        
        Diese Methode schließt die Socket-Verbindung und setzt die
        Socket-Referenz zurück. Die Trennung wird geloggt.
        
        Example:
            >>> robot = BrainBotRemote("192.168.1.100")
            >>> robot.connect()
            >>> robot.send_command("STOP")
            >>> robot.disconnect()
        
        Note:
            - Kann auch ohne aktive Verbindung aufgerufen werden
            - Nach disconnect() muss connect() erneut aufgerufen werden
            - Das Socket-Objekt wird vollständig freigegeben
        """
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
    # Dieses Beispiel zeigt die grundlegende Verwendung der Klasse
    print("BrainBot Remote Control - Beispiel")
    print("=" * 40)
    
    # Roboter-Instanz erstellen
    robot: BrainBotRemote = BrainBotRemote(robot_ip="192.168.1.100", port=5000)
    
    # Verbindung herstellen
    if robot.connect():
        # Bei Erfolg: Befehle senden
        robot.send_command("FORWARD")
        robot.send_command("TURN_LEFT")
        robot.send_command("STOP")
        
        # Verbindung trennen
        robot.disconnect()
    else:
        # Bei Fehler: Hinweis ausgeben
        print("\n⚠ Tipp: Prüfen Sie die Roboter-IP und stellen Sie sicher,")
        print("   dass der Roboter eingeschaltet und erreichbar ist.")