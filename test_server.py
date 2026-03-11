# HINWEIS:
# Dieser Mock-Server simuliert die Roboter-Kommunikation für lokale Tests.
# Er ermöglicht Entwicklung und Test ohne echte Hardware.
# Für spätere Hardware-Integration kann die Logik angepasst oder ersetzt werden.

import socket
import threading  # type: ignore
import time  # type: ignore

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5000))
    server.listen(5)
    
    print("=" * 50)
    print("✅ Mock-Server läuft auf 127.0.0.1:5000")
    print("⏳ Warte auf Client...")
    print("=" * 50)
    
    try:
        while True:
            client, addr = server.accept()
            print(f"\n✅ Client verbunden: {addr}")
            
            try:
                while True:
                    data = client.recv(256)
                    if not data:
                        break
                    msg = data.decode('utf-8').strip()
                    print(f"  ← {msg}")
            except:
                pass
            finally:
                client.close()
                
    except KeyboardInterrupt:
        print("\n✓ Server beendet")
    finally:
        server.close()

if __name__ == "__main__":
    run_server()