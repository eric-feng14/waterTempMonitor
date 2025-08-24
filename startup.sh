#!/bin/bash

# Temperature Monitor Startup Script
# This script starts the Flask web server and sample data generator

echo "🌡️  Temperature Monitor - Startup Script"
echo "========================================"
echo ""

# Function to check if a process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        return 0  # Process is running
    else
        return 1  # Process is not running
    fi
}

# Function to start Flask server
start_flask_server() {
    echo "🚀 Starting Flask web server..."
    
    # Check if Flask server is already running
    if check_process "app.py"; then
        echo "   ⚠️  Flask server is already running"
    else
        # Start Flask server in the background
        python3 app.py &
        FLASK_PID=$!
        
        # Wait a moment and check if it started successfully
        sleep 2
        if kill -0 $FLASK_PID 2>/dev/null; then
            echo "   ✅ Flask server started successfully (PID: $FLASK_PID)"
            echo "   📱 Web dashboard: http://localhost:5000"
        else
            echo "   ❌ Failed to start Flask server"
            return 1
        fi
    fi
    return 0
}

# Function to start sample data generator
start_data_generator() {
    echo ""
    echo "📊 Starting sample data generator..."
    
    # Check if data generator is already running
    if check_process "sample_data_generator.py"; then
        echo "   ⚠️  Data generator is already running"
        return 0
    fi
    
    # Choose mode
    echo ""
    echo "Available simulation modes:"
    echo "  1) realistic - Natural daily temperature variations (recommended)"
    echo "  2) random    - Random temperatures between 15°C - 35°C"
    echo "  3) demo      - Rapid temperature changes for demonstration"
    echo ""
    
    read -p "Choose mode (1-3) [default: 1]: " mode_choice
    
    case $mode_choice in
        2)
            MODE="random"
            ;;
        3)
            MODE="demo"
            ;;
        *)
            MODE="realistic"
            ;;
    esac
    
    echo "   🎯 Selected mode: $MODE"
    echo "   🔄 Starting data generator... (Press Ctrl+C to stop)"
    echo ""
    
    # Start data generator (this will run in foreground)
    python3 sample_data_generator.py $MODE
}

# Function to stop all processes
stop_all() {
    echo ""
    echo "🛑 Stopping all processes..."
    
    # Stop Flask server
    if check_process "app.py"; then
        pkill -f "app.py"
        echo "   ✅ Flask server stopped"
    fi
    
    # Stop data generator
    if check_process "sample_data_generator.py"; then
        pkill -f "sample_data_generator.py"
        echo "   ✅ Data generator stopped"
    fi
    
    echo "   🏁 All processes stopped"
}

# Function to show status
show_status() {
    echo "📊 System Status:"
    echo "==============="
    
    if check_process "app.py"; then
        echo "   Flask Server: ✅ Running"
        echo "   Dashboard:   📱 http://localhost:5000"
    else
        echo "   Flask Server: ❌ Not running"
    fi
    
    if check_process "sample_data_generator.py"; then
        echo "   Data Generator: ✅ Running"
    else
        echo "   Data Generator: ❌ Not running"
    fi
}

# Main script logic
case "$1" in
    "start")
        start_flask_server
        if [ $? -eq 0 ]; then
            start_data_generator
        fi
        ;;
    "stop")
        stop_all
        ;;
    "status")
        show_status
        ;;
    "server-only")
        start_flask_server
        if [ $? -eq 0 ]; then
            echo ""
            echo "🌐 Flask server is running!"
            echo "   📱 Open http://localhost:5000 in your browser"
            echo "   🔄 Run './startup.sh start' to also start sample data"
            echo "   🛑 Run './startup.sh stop' to stop the server"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status|server-only}"
        echo ""
        echo "Commands:"
        echo "  start       - Start both Flask server and data generator"
        echo "  server-only - Start only the Flask web server"
        echo "  stop        - Stop all running processes"
        echo "  status      - Show current system status"
        echo ""
        echo "Quick start:"
        echo "  1. Run: ./startup.sh start"
        echo "  2. Open: http://localhost:5000"
        echo "  3. Watch live temperature data!"
        exit 1
        ;;
esac
