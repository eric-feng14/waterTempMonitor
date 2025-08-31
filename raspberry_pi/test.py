#Run this file on the raspberry pi!
import spidev
import time
import requests
from datetime import datetime
import sys
import signal

# Flask server configuration
#FLASK_SERVER_URL = "http://192.168.2.34:5000"
#FLASK_SERVER_URL = "https://church-nu-eight.vercel.app"
FLASK_SERVER_URL = "https://new-church.vercel.app/"
API_ENDPOINT = f"{FLASK_SERVER_URL}/api/receive_temperature"

# Global variables
spi = None
running = True

def signal_handler(sig, frame):
    """Handle graceful shutdown on Ctrl+C"""
    global running, spi
    print('\n\nShutting down gracefully...')
    running = False
    if spi:
        spi.close()
        print('SPI connection closed.')
    sys.exit(0)

def initialize_spi():
    """Initialize SPI connection to MAX6675"""
    global spi
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)  # Bus 0, Device 0 (CE0)
        spi.max_speed_hz = 500000
        spi.mode = 0
        print("✓ SPI connection initialized")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize SPI: {e}")
        return False

def read_temp():
    """Read temperature from MAX6675 thermocouple sensor"""
    global spi
    if not spi:
        return None
    
    try:
        # MAX6675 returns 2 bytes
        raw = spi.readbytes(2)
        value = ((raw[0] << 8) | raw[1]) >> 3
        
        # Check fault bit
        if value & 0x8000:
            return None
            
        # Convert to temperature in Celsius
        return value * 0.25
    except Exception as e:
        print(f"✗ Error reading temperature: {e}")
        return None

def send_temperature_to_server(temp_c):
    """Send temperature reading to Flask web server"""
    try:
        payload = {
            "temperature": temp_c,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return True
            else:
                print(f"Server error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to web server at {FLASK_SERVER_URL}")
        return False
    except requests.exceptions.Timeout:
        print("Request timeout when sending to server")
        return False
    except Exception as e:
        print(f"Error sending data to server: {e}")
        return False

def main():
    global running
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Temperature Monitor - MAX6675 Thermocouple Sensor")
    print("=" * 50)
    print(f"Web server URL: {FLASK_SERVER_URL}")
    print("Press Ctrl+C to stop\n")
    
    # Initialize SPI
    if not initialize_spi():
        print("Failed to initialize sensor. Exiting...")
        return
    
    consecutive_failures = 0
    server_failures = 0
    max_server_failures = 10
    
    try:
        while running:
            # Read temperature from sensor
            temp_c = read_temp()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if temp_c is not None:
                temp_f = temp_c * 9/5 + 32
                print(f"[{timestamp}] Temperature: {temp_c:.2f}°C ({temp_f:.2f}°F)", end=" ")
                
                # Send to web server
                if send_temperature_to_server(temp_c):
                    print("✓ Sent to server")
                    consecutive_failures = 0
                    server_failures = 0
                else:
                    print("✗ Failed to send")
                    server_failures += 1
                    
                    # Show warning if server is consistently unreachable
                    if server_failures >= max_server_failures:
                        print(f"⚠️  Warning: Web server unreachable for {server_failures} attempts")
                        print("   Temperature readings will continue locally")
                        server_failures = 0  # Reset to avoid spam
                        
            else:
                print(f"[{timestamp}] ✗ Thermocouple error (not connected or faulty)")
                consecutive_failures += 1
                
                # Show warning for persistent sensor issues
                if consecutive_failures >= 5:
                    print("⚠️  Warning: Multiple sensor read failures - check thermocouple connection")
                    consecutive_failures = 0  # Reset counter
            
            # Wait before next reading
            time.sleep(1)
            
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
