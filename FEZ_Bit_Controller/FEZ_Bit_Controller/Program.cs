using System;
using System.Diagnostics;
using BrainBot.Robot;

namespace BrainBot
{
    class Program
    {
        static void Main()
        {
            Debug.WriteLine("===========================================");
            Debug.WriteLine("BrainBot AI - FEZ Bit Controller v1.0.0");
            Debug.WriteLine("Autor: Marcus Reiser");
            Debug.WriteLine("Datum: März 2026");
            Debug.WriteLine("===========================================");
            
            try
            {
                // RobotController erstellen und starten
                var controller = new RobotController();
                
                Debug.WriteLine("✓ RobotController initialisiert");
                Debug.WriteLine("⏳ Starte Hauptschleife...");
                
                // Hauptschleife läuft für immer
                controller.Run();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"✗ KRITISCHER FEHLER: {ex.Message}");
                Debug.WriteLine(ex.StackTrace);
            }
        }
    }
}