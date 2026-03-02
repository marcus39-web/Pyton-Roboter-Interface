// FEZ Bit / SITCore - TCP Socket Listener mit Heartbeat-Timeout
// Autor: Marcus Reiser
// Datum: März 2026
// Version: 1.0.0

using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using GHIElectronics.TinyCLR.Devices.Gpio;
using GHIElectronics.TinyCLR.Devices.Pwm;
using GHIElectronics.TinyCLR.Pins;

namespace BrainBot.Robot
{
    /// <summary>
    /// Hauptklasse für BrainBot Roboter-Steuerung
    /// Empfängt TCP-Befehle vom Python-Interface und steuert Motoren
    /// </summary>
    public class RobotController
    {
        // ==================== NETZWERK-KONFIGURATION ====================
        private const int PORT = 5000;                    // Port für TCP-Verbindung
        private const int HEARTBEAT_TIMEOUT_MS = 5000;    // 5 Sekunden Timeout
        
        private TcpListener _listener;
        private TcpClient _client;
        private NetworkStream _stream;
        
        // ==================== HEARTBEAT-VARIABLEN ====================
        private DateTime _lastHeartbeat;
        private bool _isConnected = false;
        
        // ==================== MOTOR-STEUERUNG ====================
        // GPIO-Pins für Motor-Steuerung (anpassen für Ihr Board!)
        private GpioPin _motorLeftForward;
        private GpioPin _motorLeftBackward;
        private GpioPin _motorRightForward;
        private GpioPin _motorRightBackward;
        
        // PWM für Geschwindigkeitssteuerung
        private PwmChannel _pwmLeft;
        private PwmChannel _pwmRight;
        
        // Aktuelle Geschwindigkeit (0.0 - 1.0)
        private double _currentSpeed = 0.7;  // Standard: 70%
        
        // ==================== STATUS-LED ====================
        private GpioPin _statusLed;
        
        /// <summary>
        /// Konstruktor - Initialisiert GPIO und Netzwerk
        /// </summary>
        public RobotController()
        {
            InitializeGPIO();
            InitializePWM();
            InitializeNetwork();
        }
        
        /// <summary>
        /// Initialisiert GPIO-Pins für Motoren und Status-LED
        /// </summary>
        private void InitializeGPIO()
        {
            var gpio = GpioController.GetDefault();
            
            // Motor Links (Pins anpassen!)
            _motorLeftForward = gpio.OpenPin(FEZ.GpioPin.A0);
            _motorLeftForward.SetDriveMode(GpioPinDriveMode.Output);
            
            _motorLeftBackward = gpio.OpenPin(FEZ.GpioPin.A1);
            _motorLeftBackward.SetDriveMode(GpioPinDriveMode.Output);
            
            // Motor Rechts (Pins anpassen!)
            _motorRightForward = gpio.OpenPin(FEZ.GpioPin.A2);
            _motorRightForward.SetDriveMode(GpioPinDriveMode.Output);
            
            _motorRightBackward = gpio.OpenPin(FEZ.GpioPin.A3);
            _motorRightBackward.SetDriveMode(GpioPinDriveMode.Output);
            
            // Status-LED (optional)
            _statusLed = gpio.OpenPin(FEZ.GpioPin.Led1);
            _statusLed.SetDriveMode(GpioPinDriveMode.Output);
            _statusLed.Write(GpioPinValue.Low);
            
            Debug.WriteLine("✓ GPIO initialisiert");
        }
        
        /// <summary>
        /// Initialisiert PWM für Geschwindigkeitssteuerung
        /// </summary>
        private void InitializePWM()
        {
            var pwmController = PwmController.FromName(FEZ.PwmChannel.Controller1.Id);
            
            // PWM-Frequenz: 1000 Hz (typisch für Motoren)
            pwmController.SetDesiredFrequency(1000);
            
            // PWM-Kanäle für linken und rechten Motor
            _pwmLeft = pwmController.OpenChannel(FEZ.PwmChannel.Controller1.D0);
            _pwmRight = pwmController.OpenChannel(FEZ.PwmChannel.Controller1.D1);
            
            // Initial aus
            _pwmLeft.SetActiveDutyCyclePercentage(0);
            _pwmRight.SetActiveDutyCyclePercentage(0);
            
            _pwmLeft.Start();
            _pwmRight.Start();
            
            Debug.WriteLine("✓ PWM initialisiert");
        }
        
        /// <summary>
        /// Initialisiert TCP-Listener auf Port 5000
        /// </summary>
        private void InitializeNetwork()
        {
            try
            {
                _listener = new TcpListener(IPAddress.Any, PORT);
                _listener.Start();
                
                Debug.WriteLine($"✓ TCP-Listener gestartet auf Port {PORT}");
                Debug.WriteLine("⏳ Warte auf Verbindung vom PC...");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"✗ Netzwerk-Fehler: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Hauptschleife - Wartet auf Verbindung und verarbeitet Befehle
        /// </summary>
        public void Run()
        {
            while (true)
            {
                try
                {
                    // Warte auf Client-Verbindung
                    if (!_isConnected)
                    {
                        _client = _listener.AcceptTcpClient();
                        _stream = _client.GetStream();
                        _isConnected = true;
                        _lastHeartbeat = DateTime.Now;
                        
                        // Status-LED an
                        _statusLed.Write(GpioPinValue.High);
                        
                        Debug.WriteLine("✓ Client verbunden!");
                    }
                    
                    // Befehle empfangen
                    if (_stream.DataAvailable)
                    {
                        byte[] buffer = new byte[256];
                        int bytesRead = _stream.Read(buffer, 0, buffer.Length);
                        
                        if (bytesRead > 0)
                        {
                            string command = Encoding.UTF8.GetString(buffer, 0, bytesRead).Trim();
                            ProcessCommand(command);
                        }
                    }
                    
                    // ==================== HEARTBEAT-TIMEOUT-PRÜFUNG ====================
                    // WICHTIG: Sicherheitsfunktion!
                    // Wenn kein Heartbeat für 5 Sekunden → NOT-STOPP
                    
                    TimeSpan timeSinceHeartbeat = DateTime.Now - _lastHeartbeat;
                    
                    if (timeSinceHeartbeat.TotalMilliseconds > HEARTBEAT_TIMEOUT_MS)
                    {
                        // KRITISCH: Heartbeat-Timeout!
                        Debug.WriteLine("⚠ HEARTBEAT-TIMEOUT! Roboter wird gestoppt!");
                        
                        // Sofort stoppen
                        MotorStop();
                        
                        // Verbindung trennen
                        DisconnectClient();
                        
                        // Status-LED blinken (Warnung)
                        BlinkStatusLed(5);
                    }
                    
                    // Kurze Pause (CPU-Last reduzieren)
                    Thread.Sleep(50);
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"✗ Fehler in Hauptschleife: {ex.Message}");
                    
                    // Bei Fehler: Sicher stoppen
                    MotorStop();
                    DisconnectClient();
                    
                    Thread.Sleep(1000);
                }
            }
        }
        
        /// <summary>
        /// Verarbeitet empfangene Befehle vom Python-Interface
        /// </summary>
        /// <param name="command">Befehl als String (z.B. "FORWARD", "HB")</param>
        private void ProcessCommand(string command)
        {
            Debug.WriteLine($"→ Befehl empfangen: {command}");
            
            // ==================== HEARTBEAT ====================
            if (command == "HB")
            {
                // Heartbeat empfangen → Timer zurücksetzen
                _lastHeartbeat = DateTime.Now;
                return;  // Kein weiteres Processing nötig
            }
            
            // ==================== BEWEGUNGS-BEFEHLE ====================
            switch (command)
            {
                case "FORWARD":
                    MotorForward();
                    break;
                    
                case "BACKWARD":
                    MotorBackward();
                    break;
                    
                case "TURN_LEFT":
                    MotorTurnLeft();
                    break;
                    
                case "TURN_RIGHT":
                    MotorTurnRight();
                    break;
                    
                case "STOP":
                    MotorStop();
                    break;
                    
                case "ROTATE_180":
                    MotorRotate180();
                    break;
                    
                default:
                    // Erweiterte Befehle (z.B. "SPEED:150")
                    ProcessExtendedCommand(command);
                    break;
            }
        }
        
        /// <summary>
        /// Verarbeitet erweiterte Befehle (z.B. Geschwindigkeit, LED, Servo)
        /// </summary>
        private void ProcessExtendedCommand(string command)
        {
            // Geschwindigkeit setzen: "SPEED:150" (0-255)
            if (command.StartsWith("SPEED:"))
            {
                try
                {
                    int speed = int.Parse(command.Substring(6));
                    _currentSpeed = Math.Min(255, Math.Max(0, speed)) / 255.0;
                    Debug.WriteLine($"Geschwindigkeit gesetzt: {_currentSpeed:P0}");
                }
                catch
                {
                    Debug.WriteLine("✗ Ungültiger SPEED-Befehl");
                }
                return;
            }
            
            // LED-Farbe setzen: "LED:255:0:0" (RGB)
            if (command.StartsWith("LED:"))
            {
                // TODO: RGB-LED-Steuerung implementieren
                Debug.WriteLine($"LED-Befehl: {command}");
                return;
            }
            
            // Unbekannter Befehl
            Debug.WriteLine($"⚠ Unbekannter Befehl: {command}");
        }
        
        // ==================== MOTOR-STEUERUNGSFUNKTIONEN ====================
        
        /// <summary>
        /// Fährt vorwärts
        /// </summary>
        private void MotorForward()
        {
            Debug.WriteLine("→ FORWARD");
            
            // Linker Motor vorwärts
            _motorLeftForward.Write(GpioPinValue.High);
            _motorLeftBackward.Write(GpioPinValue.Low);
            _pwmLeft.SetActiveDutyCyclePercentage(_currentSpeed);
            
            // Rechter Motor vorwärts
            _motorRightForward.Write(GpioPinValue.High);
            _motorRightBackward.Write(GpioPinValue.Low);
            _pwmRight.SetActiveDutyCyclePercentage(_currentSpeed);
        }
        
        /// <summary>
        /// Fährt rückwärts
        /// </summary>
        private void MotorBackward()
        {
            Debug.WriteLine("→ BACKWARD");
            
            // Linker Motor rückwärts
            _motorLeftForward.Write(GpioPinValue.Low);
            _motorLeftBackward.Write(GpioPinValue.High);
            _pwmLeft.SetActiveDutyCyclePercentage(_currentSpeed);
            
            // Rechter Motor rückwärts
            _motorRightForward.Write(GpioPinValue.Low);
            _motorRightBackward.Write(GpioPinValue.High);
            _pwmRight.SetActiveDutyCyclePercentage(_currentSpeed);
        }
        
        /// <summary>
        /// Dreht nach links (linker Motor rückwärts, rechter Motor vorwärts)
        /// </summary>
        private void MotorTurnLeft()
        {
            Debug.WriteLine("→ TURN_LEFT");
            
            // Linker Motor rückwärts
            _motorLeftForward.Write(GpioPinValue.Low);
            _motorLeftBackward.Write(GpioPinValue.High);
            _pwmLeft.SetActiveDutyCyclePercentage(_currentSpeed);
            
            // Rechter Motor vorwärts
            _motorRightForward.Write(GpioPinValue.High);
            _motorRightBackward.Write(GpioPinValue.Low);
            _pwmRight.SetActiveDutyCyclePercentage(_currentSpeed);
        }
        
        /// <summary>
        /// Dreht nach rechts (linker Motor vorwärts, rechter Motor rückwärts)
        /// </summary>
        private void MotorTurnRight()
        {
            Debug.WriteLine("→ TURN_RIGHT");
            
            // Linker Motor vorwärts
            _motorLeftForward.Write(GpioPinValue.High);
            _motorLeftBackward.Write(GpioPinValue.Low);
            _pwmLeft.SetActiveDutyCyclePercentage(_currentSpeed);
            
            // Rechter Motor rückwärts
            _motorRightForward.Write(GpioPinValue.Low);
            _motorRightBackward.Write(GpioPinValue.High);
            _pwmRight.SetActiveDutyCyclePercentage(_currentSpeed);
        }
        
        /// <summary>
        /// Stoppt alle Motoren sofort
        /// </summary>
        private void MotorStop()
        {
            Debug.WriteLine("→ STOP");
            
            // Alle Motor-Pins ausschalten
            _motorLeftForward.Write(GpioPinValue.Low);
            _motorLeftBackward.Write(GpioPinValue.Low);
            _motorRightForward.Write(GpioPinValue.Low);
            _motorRightBackward.Write(GpioPinValue.Low);
            
            // PWM auf 0
            _pwmLeft.SetActiveDutyCyclePercentage(0);
            _pwmRight.SetActiveDutyCyclePercentage(0);
        }
        
        /// <summary>
        /// Dreht um 180° (Zeit-basiert)
        /// </summary>
        private void MotorRotate180()
        {
            Debug.WriteLine("→ ROTATE_180");
            
            // Drehe links für ca. 1 Sekunde (Zeit anpassen!)
            MotorTurnLeft();
            Thread.Sleep(1000);
            MotorStop();
        }
        
        // ==================== HILFSFUNKTIONEN ====================
        
        /// <summary>
        /// Trennt Client-Verbindung sauber
        /// </summary>
        private void DisconnectClient()
        {
            if (_isConnected)
            {
                try
                {
                    _stream?.Close();
                    _client?.Close();
                }
                catch { }
                
                _isConnected = false;
                _statusLed.Write(GpioPinValue.Low);
                
                Debug.WriteLine("✓ Client getrennt");
            }
        }
        
        /// <summary>
        /// Lässt Status-LED blinken (für Warnungen)
        /// </summary>
        /// <param name="times">Anzahl der Blink-Zyklen</param>
        private void BlinkStatusLed(int times)
        {
            for (int i = 0; i < times; i++)
            {
                _statusLed.Write(GpioPinValue.High);
                Thread.Sleep(200);
                _statusLed.Write(GpioPinValue.Low);
                Thread.Sleep(200);
            }
        }
    }
}