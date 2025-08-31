from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os, json, hmac, hashlib, time
from datetime import datetime

app = Flask(__name__, static_folder="../static", template_folder="../templates")
CORS(app)

# --- Views / routes (migrate yours here) ---
@app.route("/", methods=['GET'] )
def home():
    return render_template("index.html")

# In-memory store (replace with DB later if you want)
temperature_data = []
MAX_READINGS = 50

@app.route("/api/temperature", methods=["GET"])
def temperature():
    if not temperature_data:
        return jsonify({"current": None, "history": [], "stats": None})

    curr = temperature_data[-1]["c"]
    vals = [d["c"] for d in temperature_data]
    stats = {
        "min": min(vals),
        "max": max(vals),
        "avg": sum(vals) / len(vals),
        "count": len(vals),
    }

    reading = {}
    if curr is not None:
        # Add timestamp and store the reading
        reading = {
            'temperature': float(curr),
            'timestamp': datetime.now().isoformat(),
            'temp_f': float(curr) * 9/5 + 32  # Also store Fahrenheit
        }
    return jsonify({"current": reading, "history": temperature_data, "stats": stats})

@app.route('/api/receive_temperature', methods=['POST'])
def receive_temperature():
    """Endpoint to receive temperature data"""
    try:
        data = request.get_json()
        temp_c = data.get('temperature')
        reading = {}
        if temp_c is not None:
            # Add timestamp and store the reading
            reading = {
                'c': float(temp_c),
                # 'timestamp': datetime.now().isoformat(),
                'temp_f': float(temp_c) * 9/5 + 32,
                't': datetime.now().isoformat()
            }
            
            temperature_data.append(reading)
            
            # Keep only the last MAX_READINGS
            if len(temperature_data) > MAX_READINGS:
                temperature_data.pop(0)
            
            return jsonify({'status': 'success', 'message': 'Temperature recorded'})
        else:
            return jsonify({'status': 'error', 'message': 'No temperature data provided'}), 400
        
        # data = request.get_json()


        # raw = request.get_data() or b"{}"
        # timestamp = request.headers.get("X-Timestamp", "")
        # signature = request.headers.get("X-Signature", "")
        # device_id = request.headers.get("X-Device-Id", "unknown")
    
        # try:
        #     payload = json.loads(raw.decode("utf-8"))
        #     value = float(payload.get("temperature"))
        #     ts = payload.get("timestamp") or datetime.utcnow().isoformat()
        #     temp_f = float(value) * 9/5 + 32  # Also store Fahrenheit
        # except Exception:
        #     return jsonify({"ok": False, "error": "bad payload"}), 400
    
        # temperature_data.append({"t": ts, "c": value, "device": device_id, "timestamp":ts, "temperature":value,"temp_f":temp_f})
        # del temperature_data[:-MAX_READINGS]
        # return jsonify({"status": "success", "message": "Temperature recorded" })
        # return jsonify({"ok": True, "count": len(temperature_data)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
