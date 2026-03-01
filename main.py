# Wir importieren deine Klasse aus basis_class.py
from basis_class import BrainBotRemote

def main():
    # 1. Instanz erstellen (Objekt-Orientiert!)
    # Ersetze '192.168.1.100' später durch die IP deines FEZ Bit
    my_robot = BrainBotRemote(robot_ip="192.168.1.100")

    # 2. Verbindung herstellen
    # Deine 3 Antennen suchen jetzt das Signal im Haus
    if not my_robot.connect():
        print("❌ Verbindung fehlgeschlagen - Programm wird beendet")
        return

    # 3. KI-Entscheidung simulieren
    # Stell dir vor, eine KI-Kamera erkennt ein Hindernis
    obstacle_detected = True 
    
    if obstacle_detected:
        print("🤖 KI meldet: Hindernis erkannt! Sende Stopp-Befehl...")
        my_robot.send_command("STOP")
        my_robot.send_command("TURN_LEFT_90")
    else:
        my_robot.send_command("MOVE_FORWARD")

    # 4. Sauber trennen
    my_robot.disconnect()

if __name__ == "__main__":
    main()