# test/api/index.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os, json, hmac, hashlib, time
from datetime import datetime

app = Flask(__name__, static_folder="../static", template_folder="../templates")
CORS(app)

SIGNING_SECRET = (os.getenv("SIGNING_SECRET") or "").encode()
MAX_SKEW_SECONDS = 300  # 5 minutes


# --- Views / routes (migrate yours here) ---
@app.route("/", methods=['GET', 'POST'] )
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
    return jsonify({"current": curr, "history": temperature_data, "stats": stats})

def _parse_timestamp(ts_str: str) -> float:
    # allow epoch or ISO 8601
    if not ts_str:
        return 0.0
    try:
        if ts_str.replace(".","",1).isdigit():
            return float(ts_str)
        return datetime.fromisoformat(ts_str.replace("Z","")).timestamp()
    except Exception:
        return 0.0

def verify_signature(raw_body: bytes, timestamp: str, signature: str) -> bool:
    if not SIGNING_SECRET:
        return False
    ts = _parse_timestamp(timestamp)
    if ts == 0.0 or abs(time.time() - ts) > MAX_SKEW_SECONDS:
        return False
    msg = timestamp.encode() + b"." + raw_body
    expected = hmac.new(SIGNING_SECRET, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route("/api/ingest", methods=["POST"])
def ingest():
    raw = request.get_data() or b"{}"
    timestamp = request.headers.get("X-Timestamp", "")
    signature = request.headers.get("X-Signature", "")
    device_id = request.headers.get("X-Device-Id", "unknown")

    #if not verify_signature(raw, timestamp, signature):
        #return jsonify({"ok": False, "error": "invalid signature"}), 401

    try:
        payload = json.loads(raw.decode("utf-8"))
        value = float(payload.get("value"))
        ts = payload.get("timestamp") or datetime.utcnow().isoformat()
    except Exception:
        return jsonify({"ok": False, "error": "bad payload"}), 400

    temperature_data.append({"t": ts, "c": value, "device": device_id})
    del temperature_data[:-MAX_READINGS]
    return jsonify({"ok": True, "count": len(temperature_data)})


@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    """Endpoint to receive temperature data"""
    try:
        # data = request.get_json()
        # temp_c = data.get('temperature')
        
        # if temp_c is not None:
        #     # Add timestamp and store the reading
        #     reading = {
        #         'temperature': float(temp_c),
        #         'timestamp': datetime.now().isoformat(),
        #         'temp_f': float(temp_c) * 9/5 + 32  # Also store Fahrenheit
        #     }
            
        #     temperature_data.append(reading)
            
        #     # Keep only the last MAX_READINGS
        #     if len(temperature_data) > MAX_READINGS:
        #         temperature_data.pop(0)
            
        #     return jsonify({'status': 'success', 'message': 'Temperature recorded'})
        # else:
        #     return jsonify({'status': 'error', 'message': 'No temperature data provided'}), 400
        raw = request.get_data() or b"{}"
        timestamp = request.headers.get("X-Timestamp", "")
        signature = request.headers.get("X-Signature", "")
        device_id = request.headers.get("X-Device-Id", "unknown")
    
        #if not verify_signature(raw, timestamp, signature):
            #return jsonify({"ok": False, "error": "invalid signature"}), 401
    
        try:
            payload = json.loads(raw.decode("utf-8"))
            value = float(payload.get("temperature"))
            ts = payload.get("timestamp") or datetime.utcnow().isoformat()
        except Exception:
            return jsonify({"ok": False, "error": "bad payload"}), 400
    
        temperature_data.append({"t": ts, "c": value, "device": device_id})
        del temperature_data[:-MAX_READINGS]
        return jsonify({"ok": True, "count": len(temperature_data)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
