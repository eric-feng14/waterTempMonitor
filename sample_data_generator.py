#!/usr/bin/env python3
"""
Sample Temperature Data Generator
Simulates temperature readings for testing the temperature monitoring system
without requiring actual MAX6675 thermocouple hardware.
"""

import time
import requests
import json
from datetime import datetime
import sys
import signal
import random
import math

# Flask server configuration
FLASK_SERVER_URL = "http://localhost:5000"
API_ENDPOINT = f"{FLASK_SERVER_URL}/api/temperature"

# Global variables
running = True

def signal_handler(sig, frame):
    """Handle graceful shutdown on Ctrl+C"""
    global running
    print('\n\nShutting down gracefully...')
    running = False
    sys.exit(0)

class TemperatureSimulator:
    """Simulates realistic temperature readings with various patterns"""
    
    def __init__(self):
        self.base_temp = 22.0  # Base temperature in Celsius
        self.time_offset = 0
        self.noise_amplitude = 0.5  # Random noise amplitude
        self.daily_variation = 5.0  # Daily temperature swing
        self.trend_factor = 0.0  # Gradual warming/cooling trend
        
    def get_temperature(self):
        """Generate a realistic temperature reading"""
        # Time-based daily variation (sine wave over 24 hours)
        daily_cycle = math.sin(self.time_offset / 3600.0) * self.daily_variation
        
        # Add some random noise
        noise = random.gauss(0, self.noise_amplitude)
        
        # Optional slow trend over time
        trend = self.trend_factor * (self.time_offset / 3600.0)
        
        # Calculate final temperature
        temperature = self.base_temp + daily_cycle + noise + trend
        
        # Increment time (simulate time passing)
        self.time_offset += 1
        
        return round(temperature, 2)
    
    def get_random_temperature(self, min_temp=15.0, max_temp=35.0):
        """Generate a random temperature within a range"""
        return round(random.uniform(min_temp, max_temp), 2)

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

def run_simulation_mode(mode="realistic"):
    """Run different simulation modes"""
    global running
    
    simulator = TemperatureSimulator()
    
    if mode == "realistic":
        print("📊 Running realistic temperature simulation")
        print("   (Simulates daily temperature variations with noise)")
    elif mode == "random":
        print("🎲 Running random temperature simulation")
        print("   (Generates random temperatures between 15°C - 35°C)")
    elif mode == "demo":
        print("🚀 Running demo mode")
        print("   (Rapid temperature changes for demonstration)")
    
    consecutive_failures = 0
    server_failures = 0
    max_server_failures = 10
    reading_count = 0
    
    try:
        while running:
            # Generate temperature based on mode
            if mode == "realistic":
                temp_c = simulator.get_temperature()
            elif mode == "random":
                temp_c = simulator.get_random_temperature()
            elif mode == "demo":
                # Demo mode: create interesting patterns
                reading_count += 1
                if reading_count < 20:
                    temp_c = 20 + (reading_count * 0.5)  # Warming up
                elif reading_count < 40:
                    temp_c = 30 - ((reading_count - 20) * 0.3)  # Cooling down
                else:
                    temp_c = simulator.get_temperature()  # Back to realistic
                    if reading_count >= 60:
                        reading_count = 0  # Reset cycle
            else:
                temp_c = simulator.get_temperature()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                    print("   Please make sure the Flask server is running on http://localhost:5000")
                    server_failures = 0  # Reset to avoid spam
            
            # Adjust sleep time based on mode
            sleep_time = 2 if mode == "demo" else 1
            time.sleep(sleep_time)
            
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        signal_handler(None, None)

def populate_initial_data():
    """Send some initial historical data to the server"""
    print("📈 Populating initial historical data...")
    
    simulator = TemperatureSimulator()
    base_time = datetime.now()
    
    # Generate 30 readings spanning the last 30 minutes
    for i in range(30):
        temp_c = simulator.get_temperature()
        
        # Create timestamps going backwards in time
        timestamp = datetime.fromtimestamp(base_time.timestamp() - (30 - i) * 60)
        
        payload = {
            "temperature": temp_c,
            "timestamp": timestamp.isoformat()
        }
        
        try:
            response = requests.post(API_ENDPOINT, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"  ✓ Added reading: {temp_c:.2f}°C at {timestamp.strftime('%H:%M:%S')}")
            else:
                print(f"  ✗ Failed to add reading: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error adding reading: {e}")
        
        time.sleep(0.1)  # Small delay to avoid overwhelming server
    
    print("✅ Initial data population complete!\n")

def main():
    global running
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🌡️  Temperature Monitor - Sample Data Generator")
    print("=" * 60)
    print(f"Web server URL: {FLASK_SERVER_URL}")
    print("Available modes:")
    print("  • realistic : Natural daily temperature variations")
    print("  • random    : Random temperatures (15°C - 35°C)")  
    print("  • demo      : Rapid changes for demonstration")
    print("\nPress Ctrl+C to stop\n")
    
    # Check command line arguments for mode
    mode = "realistic"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode not in ["realistic", "random", "demo"]:
            print(f"❌ Unknown mode '{mode}'. Using 'realistic' mode.")
            mode = "realistic"
    
    print(f"🎯 Selected mode: {mode}")
    
    # Ask if user wants to populate initial data
    try:
        populate = input("\n📊 Would you like to populate some initial historical data? (y/n): ").lower().strip()
        if populate == 'y' or populate == 'yes':
            populate_initial_data()
    except KeyboardInterrupt:
        print("\nStarting simulation without initial data...\n")
    
    # Start the simulation
    run_simulation_mode(mode)

if __name__ == "__main__":
    main()
