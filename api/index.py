# test/api/index.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os, json

app = Flask(__name__, static_folder="../static", template_folder="../templates")
CORS(app)

# --- Views / routes (migrate yours here) ---
@app.route("/")
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

# --- Hardened ingest (device will post here). You will add HMAC verification in step 5. ---
@app.route("/api/ingest", methods=["POST"])
def ingest():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        value = float(payload.get("value"))
    except Exception:
        return jsonify({"ok": False, "error": "bad payload"}), 400
    ts = payload.get("timestamp") or __import__("datetime").datetime.utcnow().isoformat()
    device_id = payload.get("deviceId", "unknown")
    temperature_data.append({"t": ts, "c": value, "device": device_id})
    del temperature_data[:-MAX_READINGS]
    return jsonify({"ok": True, "count": len(temperature_data)})
