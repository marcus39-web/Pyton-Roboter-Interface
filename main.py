import json
import os
from pathlib import Path
from datetime import datetime

from basis_class import BrainBotRemote

try:
    from categorization_db import CategorizationDatabase
except Exception:
    CategorizationDatabase = None


def decide_action(distance_cm: int, safe_distance_cm: int = 30) -> str:
    """Einfache KI-Regel: Bei Unterschreitung der Sicherheitsdistanz liegt ein Hindernis vor."""
    if distance_cm <= safe_distance_cm:
        return "OBSTACLE"
    return "CLEAR"


def load_simulation_data() -> tuple[list[int], int]:
    """Lädt Simulationsdaten aus JSON; bei Fehlern werden sichere Standardwerte genutzt."""
    # Fallback-Werte für den Offline-Test ohne Hardware.
    default_distances = [85, 60, 45, 28, 22, 50]
    default_safe_distance = 30
    data_file = Path(__file__).with_name("simulation_data.json")

    if not data_file.exists():
        return default_distances, default_safe_distance

    try:
        with data_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        # Werte aus Datei übernehmen (falls vorhanden), sonst Fallback.
        distances = data.get("distances_cm", default_distances)                                                                                                                                                                                                     
        safe_distance = int(data.get("safe_distance_cm", default_safe_distance))

        # Nur int-Listen zulassen, damit die KI-Regel konsistent bleibt.
        if not isinstance(distances, list) or not all(isinstance(value, int) for value in distances):
            return default_distances, default_safe_distance
                                                                                           
        return distances, safe_distance
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default_distances, default_safe_distance


def log_training_sample(
    distance_cm: int,
    safe_distance_cm: int,
    decision: str,
    command: str,
    room_name: str = "",
    categorization_db: "CategorizationDatabase | None" = None,
) -> None:
    """Speichert einen Trainingsdatensatz (JSONL) für spätere Modell-Trainingsläufe."""
    training_file = Path(__file__).with_name("learning_data.jsonl")
    sample = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "distance_cm": distance_cm,
        "safe_distance_cm": safe_distance_cm,
        "decision": decision,
        "command": command,
        "room_name": room_name,
    }

    try:
        with training_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(sample, ensure_ascii=False) + "\n")
    except OSError:
        pass

    if categorization_db is not None:
        categorization_db.log_decision(
            distance_cm=distance_cm,
            safe_distance_cm=safe_distance_cm,
            decision=decision,
            command=command,
            room_name=room_name,
        )


def main():
    room_name = os.getenv("ROOM_NAME", "Unbekanntes_Zimmer").strip() or "Unbekanntes_Zimmer"

    db = None
    if CategorizationDatabase is not None:
        db = CategorizationDatabase.from_env()
        if db.enabled:
            ok, message = db.initialize()
            print(f"🗄️ MySQL: {message}")

    # 1. Instanz erstellen (für lokalen Test!)
    my_robot = BrainBotRemote(robot_ip="127.0.0.1")

    # 2. Verbindung herstellen
    if not my_robot.connect():
        print("❌ Verbindung fehlgeschlagen - Programm wird beendet")
        print("💡 Starte zuerst den Mock-Server mit: python test_server.py")
        return

    # 3. KI-Entscheidung simulieren (ohne echte Hardware)
    # Distanzwerte + Schwellwert kommen aus simulation_data.json.
    simulated_distances_cm, safe_distance_cm = load_simulation_data()

    for distance_cm in simulated_distances_cm:
        decision = decide_action(distance_cm, safe_distance_cm)

        if decision == "OBSTACLE":
            print(f"🤖 KI: Hindernis bei {distance_cm}cm erkannt -> STOP + TURN_LEFT_90")
            my_robot.send_command("STOP")
            my_robot.send_command("TURN_LEFT_90")
            # Beide gesendeten Kommandos als Trainingsdaten protokollieren.
            log_training_sample(distance_cm, safe_distance_cm, decision, "STOP", room_name, db)
            log_training_sample(distance_cm, safe_distance_cm, decision, "TURN_LEFT_90", room_name, db)
        else:
            print(f"🤖 KI: Strecke frei ({distance_cm}cm) -> MOVE_FORWARD")
            my_robot.send_command("MOVE_FORWARD")
            # Auch Vorwärtsfahrt wird als positiver Lernfall gespeichert.
            log_training_sample(distance_cm, safe_distance_cm, decision, "MOVE_FORWARD", room_name, db)

    print("🧠 Lernmodus: Trainingsdaten wurden in learning_data.jsonl gespeichert")

    # 4. Sauber trennen
    my_robot.disconnect()

if __name__ == "__main__":
    main()