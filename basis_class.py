import socket
from datetime import datetime
from pathlib import Path

class BrainBotRemote:
    """Klasse zur Fernsteuerung des BrainBot Roboters"""
    
    def __init__(self, robot_ip, port=5000):
        self.robot_ip = robot_ip
        self.port = port
        self.socket = None
        self.log_file = Path(__file__).parent / "robot_log.txt"
    
    def _log(self, level, message):
        """Interne Logging-Methode"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
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