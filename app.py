from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Store temperature data in memory (in production, use a database)
temperature_data = []
MAX_READINGS = 50  # Keep last 50 readings

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    """Endpoint to receive temperature data"""
    try:
        data = request.get_json()
        temp_c = data.get('temperature')
        
        if temp_c is not None:
            # Add timestamp and store the reading
            reading = {
                'temperature': float(temp_c),
                'timestamp': datetime.now().isoformat(),
                'temp_f': float(temp_c) * 9/5 + 32  # Also store Fahrenheit
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

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    """Get current and historical temperature data"""
    if not temperature_data:
        return jsonify({
            'current': None,
            'history': [],
            'stats': None
        })
    
    # Current temperature (latest reading)
    current = temperature_data[-1]
    
    # Calculate some basic statistics
    temps = [reading['temperature'] for reading in temperature_data]
    stats = {
        'min': min(temps),
        'max': max(temps),
        'avg': sum(temps) / len(temps)
    }
    
    return jsonify({
        'current': current,
        'history': temperature_data,
        'stats': stats
    })

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
