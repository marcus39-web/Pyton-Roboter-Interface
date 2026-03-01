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
    
    def __init__(self, robot_ip, port=5000):
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
        self.robot_ip = robot_ip
        self.port = port
        
        # Socket-Objekt initialisieren (None = keine aktive Verbindung)
        self.socket = None
        
        # Pfad zur Log-Datei bestimmen (im selben Verzeichnis wie diese Datei)
        self.log_file = Path(__file__).parent / "robot_log.txt"
    
    def _log(self, level, message):
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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log-Eintrag formatieren: [Timestamp] [Level] Nachricht
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            # Log-Datei im Append-Modus öffnen (erstellt Datei falls nicht vorhanden)
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠ Logging-Fehler: {e}")
    
    def connect(self):
        """Verbindung zum Roboter herstellen"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.robot_ip, self.port))
            message = f"Verbunden mit {self.robot_ip}:{self.port}"
            print(f"✓ {message}")
            self._log("CONNECT", message)
            return True
        except Exception as e:
            message = f"Verbindungsfehler: {e}"
            print(f"✗ {message}")
            self._log("ERROR", message)
            # Socket zurücksetzen bei Fehler
            if self.socket:
                self.socket.close()
                self.socket = None
            return False

    def send_command(self, command):
        """Befehl an den Roboter senden"""
        if self.socket:
            try:
                self.socket.send(command.encode())
                message = f"Befehl gesendet: {command}"
                print(f"→ {message}")
                self._log("COMMAND", message)
                return True
            except Exception as e:
                message = f"Sendefehler: {e}"
                print(f"✗ {message}")
                self._log("ERROR", message)
                return False
        else:
            message = "Keine Verbindung zum Roboter"
            print(f"✗ {message}")
            self._log("ERROR", message)
            return False

    def disconnect(self):
        """Verbindung trennen"""
        if self.socket:
            self.socket.close()
            self.socket = None
            message = "Verbindung getrennt"
            print(f"✓ {message}")
            self._log("DISCONNECT", message)