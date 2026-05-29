#!/usr/bin/env python3
"""
Arduino Sensor Dashboard - Local Web Server
Fixed version with better error handling
"""

from flask import Flask, render_template_string, jsonify
import serial
import json
import threading
from datetime import datetime
import time

# ═══════════════════════════════════════════════════
#  CONFIGURATION - CHANGE THIS
# ═══════════════════════════════════════════════════
SERIAL_PORT = 'COM3'      # Change to your Arduino COM port
BAUD_RATE = 9600

# ═══════════════════════════════════════════════════
#  GLOBAL DATA
# ═══════════════════════════════════════════════════
latest_data = {
    "airTemp": -999,
    "airHumidity": -999,
    "soilMoisture": 0,
    "soilRaw": 0,
    "dhtOK": False,
    "timestamp": 0,
    "lastUpdate": "Never"
}

ser = None

# ═══════════════════════════════════════════════════
#  FLASK APP
# ═══════════════════════════════════════════════════
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def api_data():
    return jsonify(latest_data)

# ═══════════════════════════════════════════════════
#  SERIAL READER FUNCTION
# ═══════════════════════════════════════════════════
def read_serial_data():
    global latest_data, ser
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"\n[OK] Connected to {SERIAL_PORT}\n")
        
        while True:
            try:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    # Only process JSON lines
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            data = json.loads(line)
                            latest_data = data
                            latest_data['lastUpdate'] = datetime.now().strftime("%H:%M:%S")
                            print(f"[OK] {latest_data}")
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.1)
                
    except serial.SerialException as e:
        print(f"\n[X] Cannot connect to {SERIAL_PORT}")
        print(f"   Error: {e}\n")
        print("TROUBLESHOOTING:")
        print("1. Check your COM port (COM3, COM4, etc)")
        print("2. Check Arduino is connected via USB")
        print("3. Check Arduino code is uploaded")
        print("4. Close Arduino Serial Monitor (port conflict)")
        print("5. Check Device Manager for Arduino port")
        print()

# ═══════════════════════════════════════════════════
#  HTML DASHBOARD
# ═══════════════════════════════════════════════════
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Arduino Sensor Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-bar {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            border: 2px solid rgba(255,255,255,0.2);
        }
        .section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 12px;
        }
        .sensor-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        @media (max-width: 768px) {
            .sensor-row { grid-template-columns: 1fr; }
        }
        .sensor {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #667eea;
        }
        .sensor-label {
            font-size: 11px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .sensor-value {
            font-size: 40px;
            font-weight: bold;
            color: #333;
        }
        .sensor-unit {
            font-size: 16px;
            color: #999;
            margin-left: 5px;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 8px;
        }
        .status.ok { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.warning { background: #fff3cd; color: #856404; }
        .progress-bar {
            width: 100%;
            height: 35px;
            background: #e9ecef;
            border-radius: 20px;
            overflow: hidden;
            margin-top: 12px;
            border: 2px solid #667eea;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.5s ease;
        }
        .timestamp {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌿 Arduino Sensor Dashboard</h1>
        
        <div class="status-bar">
            🟢 Live Data <span id="lastUpdate">(updating...)</span>
        </div>

        <div class="section">
            <h2>🏠 Air Conditions</h2>
            <div class="sensor-row">
                <div class="sensor">
                    <div class="sensor-label">Temperature</div>
                    <div class="sensor-value">
                        <span id="airTemp">--</span>
                        <span class="sensor-unit">°C</span>
                    </div>
                    <div id="airTempStatus" class="status">--</div>
                </div>
                <div class="sensor">
                    <div class="sensor-label">Humidity</div>
                    <div class="sensor-value">
                        <span id="airHum">--</span>
                        <span class="sensor-unit">%</span>
                    </div>
                    <div id="airHumStatus" class="status">--</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🌱 Soil Conditions</h2>
            <div class="sensor-row">
                <div class="sensor">
                    <div class="sensor-label">Soil Moisture</div>
                    <div class="sensor-value">
                        <span id="soilMoist">--</span>
                        <span class="sensor-unit">%</span>
                    </div>
                    <div id="soilMoistStatus" class="status">--</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="moistBar" style="width: 0%;">
                            <span id="moistPercent">0%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>⚙️ System</h2>
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <strong>DHT22 Sensor:</strong>
                <div id="dhtStatus" class="status" style="display: block; margin-top: 8px;">--</div>
            </div>
        </div>

        <div class="timestamp">
            Last update: <span id="timestamp">Never</span>
        </div>
    </div>

    <script>
        function updateData() {
            fetch('/api/data')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('airTemp').textContent = 
                        data.airTemp === -999 ? 'ERR' : data.airTemp.toFixed(1);
                    updateStatus('airTemp', data.airTemp, 23, 28, data.dhtOK);

                    document.getElementById('airHum').textContent = 
                        data.airHumidity === -999 ? 'ERR' : data.airHumidity.toFixed(1);
                    updateStatus('airHum', data.airHumidity, 70, 85, data.dhtOK);

                    document.getElementById('soilMoist').textContent = data.soilMoisture;
                    updateStatus('soilMoist', data.soilMoisture, 40, 70, true);

                    document.getElementById('moistBar').style.width = data.soilMoisture + '%';
                    document.getElementById('moistPercent').textContent = data.soilMoisture + '%';

                    document.getElementById('dhtStatus').textContent = 
                        data.dhtOK ? '✓ Connected' : '✗ Disconnected';
                    document.getElementById('dhtStatus').className = 
                        'status ' + (data.dhtOK ? 'ok' : 'error');

                    document.getElementById('timestamp').textContent = data.lastUpdate;
                    document.getElementById('lastUpdate').textContent = data.lastUpdate;
                })
                .catch(e => console.error(e));
        }

        function updateStatus(id, value, min, max, ok) {
            const elem = document.getElementById(id + 'Status');
            if (!ok) {
                elem.textContent = '✗ ERROR';
                elem.className = 'status error';
            } else if (value < min || value > max) {
                elem.textContent = value < min ? '↓ LOW' : '↑ HIGH';
                elem.className = 'status warning';
            } else {
                elem.textContent = '✓ OK';
                elem.className = 'status ok';
            }
        }

        updateData();
        setInterval(updateData, 1000);
    </script>
</body>
</html>
'''

# ═══════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Arduino Sensor Dashboard - Web Server")
    print("="*50)
    print(f"\nSerial Port: {SERIAL_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    print("\nDashboard: http://localhost:5000")
    print("\nStarting server...")
    print("="*50 + "\n")
    
    # Start serial reader thread
    serial_thread = threading.Thread(target=read_serial_data, daemon=True)
    serial_thread.start()
    
    time.sleep(2)
    
    print("Opening browser: http://localhost:5000\n")
    print("Press Ctrl+C to stop\n")
    
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        if ser:
            ser.close()