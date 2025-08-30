// Temperature monitoring dashboard JavaScript

let temperatureChart;
let currentUnit = 'C'; // 'C' for Celsius, 'F' for Fahrenheit

// Initialize the dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    fetchTemperatureData();
    
    // Auto-refresh every 5 seconds
    setInterval(fetchTemperatureData, 1000);
});

// Initialize the temperature chart
function initializeChart() {
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    
    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature (°C)',
                data: [],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#2563eb',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: '#e2e8f0'
                    },
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                },
                x: {
                    grid: {
                        color: '#e2e8f0'
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Fetch temperature data from the server
async function fetchTemperatureData() {
    try {
        const response = await fetch('/api/temperature');
        const data = await response.json();
        
        if (data.current) {
            updateCurrentTemperature(data.current);
            updateStatistics(data.stats);
            updateChart(data.history);
            updateStatus('connected', data.history.length);
        } else {
            document.getElementById('current-temp').textContent = '--';
            document.getElementById('current-temp-f').textContent = '--°F';
            document.getElementById('last-updated').textContent = 'No data available';
            updateStatus('waiting', 0);
        }
    } catch (error) {
        console.error('Error fetching temperature data:', error);
        updateStatus('error', 0);
    }
}

// Update current temperature display
function updateCurrentTemperature(current) {
    const tempC = current.temperature;
    const tempF = current.temp_f;
    const timestamp = new Date(current.timestamp);
    
    if (currentUnit === 'C') {
        document.getElementById('current-temp').textContent = tempC.toFixed(1);
        document.getElementById('current-temp-f').textContent = `${tempF.toFixed(1)}°F`;
    } else {
        document.getElementById('current-temp').textContent = tempF.toFixed(1);
        document.getElementById('current-temp-f').textContent = `${tempC.toFixed(1)}°C`;
    }
    
    document.getElementById('last-updated').textContent = formatTime(timestamp);
    
    // Update temperature color based on value
    const tempDisplay = document.querySelector('.temp-display #current-temp');
    tempDisplay.className = getTemperatureClass(tempC);
}

// Update statistics display
function updateStatistics(stats) {
    if (!stats) return;
    
    const minTemp = currentUnit === 'C' ? stats.min : (stats.min * 9/5 + 32);
    const maxTemp = currentUnit === 'C' ? stats.max : (stats.max * 9/5 + 32);
    const avgTemp = currentUnit === 'C' ? stats.avg : (stats.avg * 9/5 + 32);
    const unit = currentUnit === 'C' ? '°C' : '°F';
    
    document.getElementById('min-temp').textContent = `${minTemp.toFixed(1)}${unit}`;
    document.getElementById('max-temp').textContent = `${maxTemp.toFixed(1)}${unit}`;
    document.getElementById('avg-temp').textContent = `${avgTemp.toFixed(1)}${unit}`;
}

// Update the temperature chart
function updateChart(history) {
    if (!history || history.length === 0) return;
    
    const labels = history.map(reading => {
        const date = new Date(reading.timestamp);
        return date.toLocaleTimeString();
    });
    
    const temperatures = history.map(reading => 
        currentUnit === 'C' ? reading.temperature : reading.temp_f
    );
    
    temperatureChart.data.labels = labels;
    temperatureChart.data.datasets[0].data = temperatures;
    temperatureChart.data.datasets[0].label = `Temperature (°${currentUnit})`;
    temperatureChart.options.scales.y.title.text = `Temperature (°${currentUnit})`;
    
    temperatureChart.update('none'); // Update without animation for smoother real-time updates
}

// Toggle between Celsius and Fahrenheit
function toggleUnit() {
    currentUnit = currentUnit === 'C' ? 'F' : 'C';
    const unitBtn = document.getElementById('unit-btn');
    const tempUnit = document.getElementById('temp-unit');
    
    if (currentUnit === 'F') {
        unitBtn.textContent = 'Switch to °C';
        tempUnit.textContent = '°F';
    } else {
        unitBtn.textContent = 'Switch to °F';
        tempUnit.textContent = '°C';
    }
    
    // Refresh the display with new units
    fetchTemperatureData();
}

// Update system status display
function updateStatus(status, dataCount) {
    const connectionStatus = document.getElementById('connection-status');

    switch (status) {
        case 'connected':
            connectionStatus.textContent = 'Connected';
            connectionStatus.className = 'status-value connected';
            break;
        case 'waiting':
            connectionStatus.textContent = 'Waiting for data...';
            connectionStatus.className = 'status-value';
            break;
        case 'error':
            connectionStatus.textContent = 'Connection error';
            connectionStatus.className = 'status-value disconnected';
            break;
        default:
            connectionStatus.textContent = 'Unknown';
            connectionStatus.className = 'status-value';
    }
}

// Get CSS class for temperature color coding
function getTemperatureClass(tempC) {
    if (tempC < 0) return 'temp-freezing';
    if (tempC < 10) return 'temp-cold';
    if (tempC < 20) return 'temp-cool';
    if (tempC < 30) return 'temp-warm';
    return 'temp-hot';
}

// Format timestamp for display
function formatTime(date) {
    const now = new Date();
    const diffMs = now - Date.parse(date);
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    
    if (diffSecs < 60) {
        return `${diffSecs} seconds ago`;
    } else if (diffMins < 60) {
        return `${diffMins} minutes ago`;
    } else {
        return date.toLocaleString();
    }
}

// Send temperature reading to server (for integration with sensor)
async function sendTemperatureReading(temperature) {
    try {
        const response = await fetch('/api/temperature', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                temperature: temperature
            })
        });
        
        const result = await response.json();
        return result.status === 'success';
    } catch (error) {
        console.error('Error sending temperature reading:', error);
        return false;
    }
}



