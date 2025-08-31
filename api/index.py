from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone

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

    curr = temperature_data[-1]["temperature"]
    vals = [d["temperature"] for d in temperature_data]
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
            'timestamp': datetime.now(timezone.utc).isoformat(),
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
                'temperature': float(temp_c), #same as value
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'temp_f': float(temp_c) * 9/5 + 32,
            }
            
            temperature_data.append(reading)
            
            # Keep only the last MAX_READINGS
            if len(temperature_data) > MAX_READINGS:
                temperature_data.pop(0)
            
            return jsonify({'status': 'success', 'message': 'Temperature recorded'})
        else:
            return jsonify({'status': 'error', 'message': 'No temperature data provided'}), 400
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
