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
    "soilTemp": -999,
    "ds18b20OK": False,
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SeriFusion - Local Arduino Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        :root {
            --bg: #f5f7f3;
            --surface: #ffffff;
            --card: rgba(255, 255, 255, 0.85);
            --border: rgba(87, 99, 65, 0.15);
            --text: #2d3320;
            --muted: #687550;
            --green: #576341;
            --green-light: #a8b58d;
            --yellow: #d4af37;
            --red: #c94c4c;
            --blue: #4c85c9;
            --teal: #3c4727;
            --accent: #576341;
            --shadow: 0 4px 24px -8px rgba(87, 99, 65, 0.08);
            --shadow-hover: 0 16px 32px -12px rgba(87, 99, 65, 0.2);
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Manrope', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 30px;
            display: flex;
            justify-content: center;
        }
        .container { 
            width: 100%;
            max-width: 900px; 
            animation: fadeIn 0.8s ease-out forwards;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            background: var(--card);
            backdrop-filter: blur(12px);
            padding: 20px 24px;
            border-radius: 16px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
        }
        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-icon {
            width: 44px; height: 44px;
            background: linear-gradient(135deg, var(--green), var(--teal));
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            color: white;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(87, 99, 65, 0.25);
        }
        h1 { font-size: 1.25rem; font-weight: 800; letter-spacing: -0.3px; color: var(--text); }
        .subtitle { font-size: 0.8rem; color: var(--muted); margin-top: 4px; font-weight: 500; }
        
        .status-badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            background: rgba(87, 99, 65, 0.1);
            color: var(--green);
            border: 1px solid rgba(87, 99, 65, 0.2);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: var(--green);
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1; box-shadow: 0 0 0 0 rgba(87,99,65,0.4);} 50%{opacity:0.6; box-shadow: 0 0 0 4px rgba(87,99,65,0);} }

        .section {
            margin-bottom: 24px;
        }
        .section-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }

        .card {
            background: var(--card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-hover);
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: var(--card-accent, var(--green));
        }

        .sensor-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--muted);
            font-weight: 600;
            margin-bottom: 16px;
        }
        .sensor-value-container {
            display: flex;
            align-items: baseline;
            gap: 4px;
        }
        .sensor-value {
            font-size: 3rem;
            font-weight: 800;
            color: var(--text);
            line-height: 1;
            letter-spacing: -1px;
        }
        .sensor-unit { font-size: 1.2rem; color: var(--muted); font-weight: 600; }
        
        .status {
            display: inline-flex; align-items: center; gap: 4px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 16px;
        }
        .status.ok { background: rgba(87,99,65,0.12); color: var(--green); border: 1px solid rgba(87,99,65,0.25); }
        .status.error { background: rgba(201,76,76,0.12); color: var(--red); border: 1px solid rgba(201,76,76,0.25); }
        .status.warning { background: rgba(212,175,55,0.12); color: var(--yellow); border: 1px solid rgba(212,175,55,0.25); }

        .progress-track {
            width: 100%; height: 8px;
            background: rgba(87, 99, 65, 0.1);
            border-radius: 10px; margin-top: 20px; overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--green-light), var(--green));
            transition: width 0.5s ease;
        }

        .system-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px 24px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--blue);
        }
        .system-info strong { font-size: 14px; color: var(--text); display: block; margin-bottom: 4px; }
        .system-info span { font-size: 12px; color: var(--muted); }

        .timestamp {
            text-align: center;
            color: var(--muted);
            font-size: 12px;
            font-weight: 600;
            margin-top: 30px;
        }
        
        @media (max-width: 600px) {
            .header { flex-direction: column; align-items: flex-start; gap: 16px; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        
        <div class="header">
            <div class="header-title">
                <div class="header-icon"><i class="ph ph-cpu"></i></div>
                <div>
                    <h1>Local Arduino Server</h1>
                    <div class="subtitle">Live Sensor Dashboard</div>
                </div>
            </div>
            <div class="status-badge">
                <span class="dot"></span> Live Data: <span id="lastUpdate" style="margin-left:4px">--:--:--</span>
            </div>
        </div>

        <div class="section">
            <div class="section-title"><i class="ph ph-wind"></i> Air Conditions</div>
            <div class="grid">
                <div class="card" style="--card-accent: var(--blue)">
                    <div class="sensor-label">Air Temperature</div>
                    <div class="sensor-value-container">
                        <span class="sensor-value" id="airTemp">--</span>
                        <span class="sensor-unit">°C</span>
                    </div>
                    <div id="airTempStatus" class="status">--</div>
                </div>
                <div class="card" style="--card-accent: var(--teal)">
                    <div class="sensor-label">Humidity</div>
                    <div class="sensor-value-container">
                        <span class="sensor-value" id="airHum">--</span>
                        <span class="sensor-unit">%</span>
                    </div>
                    <div id="airHumStatus" class="status">--</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title"><i class="ph ph-plant"></i> Soil Conditions</div>
            <div class="grid">
                <div class="card" style="--card-accent: var(--yellow)">
                    <div class="sensor-label">Soil Moisture</div>
                    <div class="sensor-value-container">
                        <span class="sensor-value" id="soilMoist">--</span>
                        <span class="sensor-unit">%</span>
                    </div>
                    <div id="soilMoistStatus" class="status">--</div>
                    <div class="progress-track">
                        <div class="progress-fill" id="moistBar" style="width: 0%;"></div>
                    </div>
                </div>
                <div class="card" style="--card-accent: var(--green)">
                    <div class="sensor-label">Soil Temperature</div>
                    <div class="sensor-value-container">
                        <span class="sensor-value" id="soilTemp">--</span>
                        <span class="sensor-unit">°C</span>
                    </div>
                    <div id="soilTempStatus" class="status">--</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title"><i class="ph ph-gear"></i> System Status</div>
            <div class="system-card">
                <div class="system-info">
                    <strong>DHT22 Sensor Connection</strong>
                    <span>Hardware status monitoring</span>
                </div>
                <div id="dhtStatus" class="status">--</div>
            </div>
        </div>

        <div class="timestamp">
            Last server update: <span id="timestamp">Never</span>
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

                    const soilTempVal = data.soilTemp !== undefined ? data.soilTemp : (data.ds18b20Temp !== undefined ? data.ds18b20Temp : (data.ds18b20 !== undefined ? data.ds18b20 : null));
                    const hasSoilTemp = soilTempVal !== null;
                    const ds18b20Ok = data.ds18b20OK !== false && hasSoilTemp;
                    
                    if (hasSoilTemp) {
                        document.getElementById('soilTemp').textContent = soilTempVal.toFixed(1);
                        updateStatus('soilTemp', soilTempVal, 15, 30, ds18b20Ok);
                    } else {
                        document.getElementById('soilTemp').textContent = 'ERR';
                        updateStatus('soilTemp', -999, 15, 30, false);
                    }

                    const dhtStat = document.getElementById('dhtStatus');
                    dhtStat.innerHTML = data.dhtOK ? '<i class="ph ph-check-circle"></i> Connected' : '<i class="ph ph-x-circle"></i> Disconnected';
                    dhtStat.className = 'status ' + (data.dhtOK ? 'ok' : 'error');

                    document.getElementById('timestamp').textContent = data.lastUpdate;
                    document.getElementById('lastUpdate').textContent = data.lastUpdate;
                })
                .catch(e => console.error('Error fetching data:', e));
        }

        function updateStatus(id, value, min, max, ok) {
            const elem = document.getElementById(id + 'Status');
            if (!ok) {
                elem.innerHTML = '<i class="ph ph-warning-circle"></i> ERROR';
                elem.className = 'status error';
            } else if (value < min || value > max) {
                elem.innerHTML = value < min ? '<i class="ph ph-arrow-down"></i> LOW' : '<i class="ph ph-arrow-up"></i> HIGH';
                elem.className = 'status warning';
            } else {
                elem.innerHTML = '<i class="ph ph-check-circle"></i> OK';
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