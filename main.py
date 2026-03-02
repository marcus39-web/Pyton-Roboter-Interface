from basis_class import BrainBotRemote

def main():
    # 1. Instanz erstellen (für lokalen Test!)
    my_robot = BrainBotRemote(robot_ip="127.0.0.1")

    # 2. Verbindung herstellen
    if not my_robot.connect():
        print("❌ Verbindung fehlgeschlagen - Programm wird beendet")
        return

    # 3. KI-Entscheidung simulieren
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