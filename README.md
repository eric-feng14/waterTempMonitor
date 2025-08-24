# Temperature Monitor Web Application

A Flask-based web application for real-time monitoring of temperature data from MAX6675 thermocouple sensors with a professional dashboard interface.

## Features

- 📊 Real-time temperature monitoring with live charts
- 🌡️ Support for both Celsius and Fahrenheit display
- 📈 Historical data visualization with Chart.js
- 📱 Responsive design optimized for all devices
- 🔄 Auto-refresh every 1 second
- 📊 Live statistics (min, max, average temperatures)
- 🔗 Integrated hardware sensor data collection
- 🎲 **Sample data generator for testing without hardware**
- ⚡ Production-ready with error handling and graceful shutdown

## Hardware Requirements (Optional)

**For actual sensor readings:**
- Raspberry Pi (or compatible SPI-capable device)
- MAX6675 thermocouple amplifier module
- K-type thermocouple probe
- Proper SPI connections (Bus 0, Device 0)

**For testing/demo:**
- Any computer with Python 3.6+ (no hardware required)

## Files Structure

```
├── app.py                    # Flask web application with API
├── test.py                   # Hardware sensor script (for real MAX6675)
├── sample_data_generator.py  # Sample data generator (no hardware needed)
├── startup.sh               # Easy startup script
├── templates/
│   └── index.html           # Professional dashboard template
├── static/
│   ├── css/
│   │   └── style.css        # Modern dashboard styling
│   └── js/
│       └── app.js           # Real-time dashboard JavaScript
└── README.md                # Documentation
```

## Quick Start (No Hardware Required!)

### Option 1: Easy Startup (Recommended)

```bash
# Make startup script executable (first time only)
chmod +x startup.sh

# Start everything with one command
./startup.sh start
```

This will:
1. Start the Flask web server
2. Ask if you want initial historical data
3. Let you choose simulation mode (realistic/random/demo)
4. Begin sending sample temperature data

### Option 2: Manual Startup

#### 1. Start the Web Application

```bash
python3 app.py
```

The web server will start on `http://localhost:5000`

#### 2. View the Dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

#### 3. Start Sample Data Generation (Choose One)

**Realistic simulation (recommended):**
```bash
python3 sample_data_generator.py realistic
```

**Random temperatures:**
```bash
python3 sample_data_generator.py random
```

**Demo mode (rapid changes):**
```bash
python3 sample_data_generator.py demo
```

## Sample Data Modes

### 🌡️ Realistic Mode (Default)
- Simulates natural daily temperature variations
- Follows a sine wave pattern with random noise
- Base temperature around 22°C with ±5°C daily swing
- Most realistic for demonstration purposes

### 🎲 Random Mode
- Generates random temperatures between 15°C - 35°C
- Good for testing edge cases
- Unpredictable patterns

### 🚀 Demo Mode
- Creates rapid temperature changes for demonstrations
- Shows warming and cooling cycles
- Perfect for showing off the real-time capabilities

## Using with Real Hardware
If you have the actual MAX6675 hardware, you can use the original sensor script:

```bash
python3 test.py
```

### Hardware Setup

### SPI Connection Configuration:
- **Bus**: 0
- **Device**: 0 (CE0)
- **Max Speed**: 500kHz
- **Mode**: 0

### Typical Raspberry Pi Wiring:
- VCC → 3.3V
- GND → Ground
- SCK → GPIO 11 (SPI0 SCLK)
- CS → GPIO 8 (SPI0 CE0)
- SO → GPIO 9 (SPI0 MISO)

## Management Commands

### Check Status
```bash
./startup.sh status
```

### Start Only Web Server
```bash
./startup.sh server-only
```

### Stop All Processes
```bash
./startup.sh stop
```

## API Endpoints

### POST /api/temperature
Receive temperature data from the sensor.

**Request Body:**
```json
{
    "temperature": 25.6,
    "timestamp": "2025-08-23T10:30:00"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Temperature recorded"
}
```

### GET /api/temperature
Get current temperature data and historical readings.

**Response:**
```json
{
    "current": {
        "temperature": 25.6,
        "temp_f": 78.08,
        "timestamp": "2025-08-23T10:30:00"
    },
    "history": [...],
    "stats": {
        "min": 22.5,
        "max": 28.3,
        "avg": 25.1
    }
}
```

## Production Features

### Error Handling
- Graceful shutdown with Ctrl+C
- Automatic SPI connection management
- Server connection retry logic
- Sensor fault detection and reporting

### Monitoring
- Real-time connection status display
- Data point counter
- Automatic reconnection attempts
- Visual indicators for system health

## Customization

### Update Frequency
Change the sensor reading interval in `test.py`:
```python
time.sleep(2)  # Read every 2 seconds
```

Change the dashboard refresh rate in `static/js/app.js`:
```javascript
setInterval(fetchTemperatureData, 5000); // Update every 5 seconds
```

### Data Retention
Modify `MAX_READINGS` in `app.py`:
```python
MAX_READINGS = 50  # Keep last 50 readings
```

## Troubleshooting

### Web Server Issues
- Verify port 5000 is available
- Check Flask server logs for errors
- Ensure Python virtual environment is activated

### Sensor Connection Issues
- Verify SPI wiring connections
- Check thermocouple probe connection
- Monitor console output for fault messages
- Test SPI communication with `lsmod | grep spi`

### No Data on Dashboard
- Confirm sensor script is running
- Check network connectivity between sensor and web server
- Verify API endpoint URLs match
- Look for error messages in both sensor and web server logs

## Technical Details

**Backend**: Flask with CORS support
**Frontend**: HTML5, CSS3, JavaScript ES6
**Charts**: Chart.js for real-time visualization
**Hardware Interface**: SpiDev for MAX6675 communication
**Data Storage**: In-memory with configurable retention
