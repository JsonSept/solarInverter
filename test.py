from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import requests

app = Flask(__name__)

API_KEY = 'e945d7f71eb0e5e621a7dfcce2cb1a43'
CITY = 'Cape Town'

# In-memory storage (acts like a battery)
battery_storage = []

# Function to fetch temperature from OpenWeatherMap
def get_temperature():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data['main']['temp']
    else:
        return None

# Data generation function with user input
def generate_data(voltage, current, power, panel_area, efficiency):
    current_time = datetime.now()
    openweather_temp = get_temperature()

    # Assume constant solar irradiance for now (W/m²)
    irradiance = 1000  
    efficiency_in_decimal = efficiency / 100
    
    # Calculate total energy in kWh
    total_energy_output = (irradiance * panel_area * efficiency_in_decimal * power) / 1000  # kWh

    data = {
        "timestamp": current_time.isoformat(),
        "voltage": voltage,
        "current": current,
        "power": power,
        "temperature": openweather_temp if openweather_temp is not None else "N/A",
        "total_energy_output_kwh": round(total_energy_output, 2)
    }

    # Store data in battery storage
    battery_storage.append(data)
    return data

# Function to calculate the stored energy (sum of power)
def calculate_stored_energy():
    return sum(item['power'] for item in battery_storage)

# HTML template for displaying data and input form
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Solar Inverter Data</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 0; 
            background-color: #f9f9f9; 
        }
        header {
            background-color: #4CAF50; 
            color: white; 
            padding: 15px 0; 
            text-align: center;
        }
        h1 { 
            margin: 0; 
        }
        form {
            max-width: 600px; 
            margin: 20px auto; 
            padding: 20px; 
            background-color: #fff; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
        }
        select, input[type="submit"] { 
            width: 100%; 
            padding: 10px; 
            margin-bottom: 15px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            box-sizing: border-box; 
        }
        input[type="submit"] { 
            background-color: #4CAF50; 
            color: white; 
            border: none; 
            cursor: pointer; 
        }
        input[type="submit"]:hover { 
            background-color: #45a049; 
        }
        table {
            width: 100%; 
            margin: 20px 0; 
            border-collapse: collapse; 
            background-color: #fff; 
            border-radius: 8px; 
            overflow: hidden; 
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: center; 
        }
        th { 
            background-color: #4CAF50; 
            color: white; 
        }
        tr:nth-child(even) { 
            background-color: #f2f2f2; 
        }
        .container {
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .btn {
            display: inline-block; 
            padding: 10px 20px; 
            margin-top: 20px; 
            background-color: #4CAF50; 
            color: white; 
            text-align: center; 
            border-radius: 4px; 
            text-decoration: none; 
        }
        .btn:hover { 
            background-color: #45a049; 
        }
        .calculator {
            max-width: 600px; 
            margin: 20px auto; 
            padding: 20px; 
            background-color: #fff; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
            text-align: center; 
        }
        .calculator h2 { 
            margin-top: 0; 
        }
        .chart-container {
            max-width: 800px; 
            margin: 20px auto; 
            padding: 20px; 
            background-color: #fff; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
            text-align: center; 
        }
        canvas {
            width: 100% !important; 
            height: 400px !important; 
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <h1>Solar Inverter Data</h1>
    </header>
    <div class="container">
        <form method="GET" action="/">
            <label for="voltage">Voltage (V):</label>
            <select name="voltage" required>
                <option value="12">12V DC</option>
                <option value="24">24V DC</option>
                <option value="48">48V DC</option>
                <option value="96">96V DC</option>
                <option value="200">200V DC</option>
                <option value="400">400V DC</option>
                <option value="600">600V DC</option>
            </select>

            <label for="current">Current (A):</label>
            <select name="current" required>
                <option value="5">5A</option>
                <option value="10">10A</option>
                <option value="15">15A</option>
                <option value="20">20A</option>
                <option value="25">25A</option>
                <option value="30">30A</option>
                <option value="40">40A</option>
                <option value="50">50A</option>
            </select>

            <label for="power">Power (W):</label>
            <select name="power" required>
                <option value="1000">1 kW</option>
                <option value="2000">2 kW</option>
                <option value="3000">3 kW</option>
                <option value="5000">5 kW</option>
                <option value="10000">10 kW</option>
                <option value="15000">15 kW</option>
                <option value="20000">20 kW</option>
                <option value="30000">30 kW</option>
                <option value="50000">50 kW</option>
            </select>

            <label for="panel_area">Panel Area (m²):</label>
            <select name="panel_area" required>
                <option value="1">1 m²</option>
                <option value="2">2 m²</option>
                <option value="3">3 m²</option>
                <option value="5">5 m²</option>
                <option value="10">10 m²</option>
                <option value="20">20 m²</option>
                <option value="30">30 m²</option>
                <option value="50">50 m²</option>
                <option value="100">100 m²</option>
            </select>

            <label for="efficiency">Efficiency (%):</label>
            <select name="efficiency" required>
                <option value="15">15%</option>
                <option value="16">16%</option>
                <option value="17">17%</option>
                <option value="18">18%</option>
                <option value="19">19%</option>
                <option value="20">20%</option>
                <option value="21">21%</option>
                <option value="22">22%</option>
            </select>

            <input type="submit" value="Submit">
        </form>

        {% if data %}
        <div class="chart-container">
            <h2>Energy Output Chart</h2>
            <canvas id="energyChart"></canvas>
        </div>
        <script>
            const ctx = document.getElementById('energyChart').getContext('2d');
            const energyChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Total Energy Output'],
                    datasets: [{
                        label: 'Energy Output (kWh)',
                        data: [{{ data.total_energy_output_kwh }}],
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
        {% endif %}

        <h2>Battery Storage</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Voltage (V)</th>
                    <th>Current (A)</th>
                    <th>Power (W)</th>
                    <th>Temperature (°C)</th>
                    <th>Total Energy Output (kWh)</th>
                </tr>
            </thead>
            <tbody>
            {% for item in battery_storage %}
                <tr>
                    <td>{{ item.timestamp }}</td>
                    <td>{{ item.voltage }}</td>
                    <td>{{ item.current }}</td>
                    <td>{{ item.power }}</td>
                    <td>{{ item.temperature }}</td>
                    <td>{{ item.total_energy_output_kwh }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

        <form method="POST" action="/export">
            <input type="submit" value="Export Data" class="btn">
        </form>
    </div>
</body>
</html>

"""

@app.route('/', methods=['GET'])
def home():
    voltage = request.args.get('voltage')
    current = request.args.get('current')
    power = request.args.get('power')
    panel_area = request.args.get('panel_area')
    efficiency = request.args.get('efficiency')

    data = None
    if voltage and current and power and panel_area and efficiency:
        # Convert input to float
        voltage = float(voltage)
        current = float(current)
        power = float(power)
        panel_area = float(panel_area)
        efficiency = float(efficiency)
        
        # Generate data using input values and store in battery
        data = generate_data(voltage, current, power, panel_area, efficiency)
    
    return render_template_string(HTML_TEMPLATE, data=data, battery_storage=battery_storage)

@app.route('/show_energy', methods=['POST'])
def show_energy():
    stored_energy = calculate_stored_energy()
    return render_template_string(HTML_TEMPLATE, data=None, battery_storage=battery_storage, stored_energy=stored_energy)

@app.route('/api/data', methods=['GET'])
def get_data():
    voltage = request.args.get('voltage', default=350, type=float)
    current = request.args.get('current', default=10, type=float)
    power = request.args.get('power', default=4000, type=float)
    panel_area = request.args.get('panel_area', default=10, type=float)
    efficiency = request.args.get('efficiency', default=20, type=float)
    
    data = generate_data(voltage, current, power, panel_area, efficiency)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
