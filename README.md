# Temperature Monitor

A real-time temperature monitoring system built with Flask and deployed on Vercel. This project allows you to monitor temperature readings from MAX6675 thermocouple sensors on a Raspberry Pi and display them on a beautiful web dashboard.

## 🌟 Features

- **Real-time Temperature Monitoring**: Live temperature readings displayed on a responsive web dashboard
- **Temperature History**: Interactive charts showing temperature trends over time
- **Statistics**: Min, max, and average temperature calculations
- **Unit Conversion**: Switch between Celsius and Fahrenheit
- **Responsive Design**: Beautiful, modern UI that works on desktop and mobile
- **API Endpoints**: RESTful API for receiving and retrieving temperature data
- **Raspberry Pi Integration**: Scripts for reading from MAX6675 thermocouple sensors
- **Simulation Mode**: Test data generator for development and demonstration

## 🚀 Live Demo

The application is deployed on Vercel: [https://new-church.vercel.app/](https://new-church.vercel.app/)

## 📋 Tech Stack

- **Backend**: Flask, Python 3
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Deployment**: Vercel
- **Hardware**: Raspberry Pi with MAX6675 thermocouple sensor
- **Dependencies**: Flask-CORS, requests

## 🏗️ Project Structure

```
new_church/
├── api/
│   └── index.py              # Flask API routes and main application
├── static/
│   ├── css/
│   │   └── style.css         # Dashboard styling
│   └── js/
│       └── app.js            # Frontend JavaScript
├── templates/
│   └── index.html            # Main dashboard template
├── raspberry_pi/
│   ├── test.py               # Raspberry Pi thermocouple reader
│   └── sample_data_generator.py  # Test data generator
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
└── README.md                # This file
```

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/eric-feng14/new_church.git
   cd new_church
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application**
   ```bash
   python api/index.py
   ```
   Or use Flask's development server:
   ```bash
   export FLASK_APP=api/index.py
   flask run
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000` to view the dashboard

### Raspberry Pi Setup

1. **Install dependencies on Raspberry Pi**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   pip3 install spidev requests
   ```

2. **Enable SPI interface**
   ```bash
   sudo raspi-config
   # Navigate to Interfacing Options > SPI > Enable
   ```

3. **Connect MAX6675 thermocouple sensor**
   - VCC → 3.3V
   - GND → Ground
   - SCK → GPIO 11 (SCLK)
   - CS → GPIO 8 (CE0)
   - SO → GPIO 9 (MISO)

4. **Run the temperature reader**
   ```bash
   cd raspberry_pi/
   python3 test.py
   ```

### Test Data Generation

For development and testing without hardware:

```bash
cd raspberry_pi/
python3 sample_data_generator.py [mode]
```

Available modes:
- `realistic`: Natural daily temperature variations (default)
- `random`: Random temperatures between 15°C - 35°C
- `demo`: Rapid changes for demonstration

## 📡 API Endpoints

### GET `/api/temperature`
Retrieve current temperature data and statistics.

**Response:**
```json
{
  "current": {
    "temperature": 23.5,
    "timestamp": "2024-01-15T10:30:00",
    "temp_f": 74.3
  },
  "history": [...],
  "stats": {
    "min": 20.1,
    "max": 25.8,
    "avg": 22.9,
    "count": 50
  }
}
```

### POST `/api/receive_temperature`
Submit new temperature readings.

**Request Body:**
```json
{
  "temperature": 23.5,
  "timestamp": "2024-01-15T10:30:00"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temperature recorded"
}
```

## 🎨 Dashboard Features

- **Current Temperature Display**: Large, prominent temperature reading with Celsius/Fahrenheit toggle
- **Statistics Panel**: Min, max, and average temperature calculations
- **Interactive Chart**: Real-time temperature history with Chart.js
- **System Status**: Connection status and data availability indicators
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## ⚙️ Configuration

### Environment Variables

- `SIGNING_SECRET`: (Optional) Secret key for request signature verification
- `FLASK_ENV`: Set to `development` for debug mode

### Vercel Configuration

The `vercel.json` file configures:
- Serverless functions for Python files in `/api`
- Static file caching for `/static` directory
- URL rewrites for proper routing

## 🚢 Deployment

### Deploy to Vercel

1. **Connect your GitHub repository to Vercel**
2. **Import your project**
3. **Deploy automatically**

The project is configured for zero-config deployment on Vercel with the included `vercel.json` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Troubleshooting

### Common Issues

1. **SPI Permission Denied**: Make sure your user is in the `gpio` group
   ```bash
   sudo usermod -a -G gpio $USER
   ```

2. **Connection Refused**: Ensure the Flask server is running and accessible

3. **Thermocouple Not Detected**: Check wiring connections and SPI configuration

4. **Chart Not Loading**: Verify Chart.js CDN is accessible

### Support

If you encounter any issues, please check the console logs and create an issue on GitHub with:
- Error messages
- Steps to reproduce
- System information (OS, Python version, etc.)

## 🙏 Acknowledgments

- Chart.js for beautiful interactive charts
- Flask team for the excellent web framework
- Vercel for seamless deployment platform
