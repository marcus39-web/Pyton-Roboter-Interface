import socket

class BrainBotRemote:
    """Klasse zur Fernsteuerung des BrainBot Roboters"""
    
    def __init__(self, robot_ip, port=5000):
        self.robot_ip = robot_ip
        self.port = port
        self.socket = None
    
    def connect(self):
        """Verbindung zum Roboter herstellen"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.robot_ip, self.port))
            print(f"✓ Verbunden mit {self.robot_ip}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Verbindungsfehler: {e}")
            return False
    
    def send_command(self, command):
        """Befehl an den Roboter senden"""
        if self.socket:
            try:
                self.socket.send(command.encode())
                print(f"→ Befehl gesendet: {command}")
                return True
            except Exception as e:
                print(f"✗ Sendefehler: {e}")
                return False
        else:
            print("✗ Keine Verbindung zum Roboter")
            return False
    
    def disconnect(self):
        """Verbindung trennen"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("✓ Verbindung getrennt")