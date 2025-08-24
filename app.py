from flask import Flask, render_template, request, redirect, url_for
import requests, os

app = Flask(__name__)
API_KEY = API_KEY = os.environ.get('API_KEY', '')  # Replace with your MARTA API key

def get_marta_arrivals(station):
    url = f'https://developerservices.itsmarta.com:18096/itsmarta/railrealtimearrivals/developerservices/traindata?apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    arrivals = [train for train in data if train['STATION'].upper() == station.upper()]
    arrivals.sort(key=lambda x: int(x.get('WAITING_SECONDS', '99999')))
    return arrivals

@app.route("/")
def home():
    return render_template('home.html')

def interpret_delay(delay_code):
    if not delay_code or delay_code.upper() == "NONE" or delay_code == "0":
        return "On Time"
    else:
        # Optionally: parse delay_code if you want delay duration in seconds
        return "Delayed"

@app.route('/arrivals')
def arrivals():
    
    station_name = request.args.get('station').replace('_', ' ').replace('-', ' ').upper()
    if not station_name:
        # If no station given, redirect back to home
        return redirect(url_for('home'))
    
    # fetch arrivals and render your arrivals page (reusing your previous code)
    
    try:
        data = get_marta_arrivals(station_name)
    except Exception as e:
        # Handle API call failure or similar errors.
        error_message = f"Failed to retrieve data: {str(e)}."
        return render_template('arrivals.html', station = station_name, trains=[], error=error_message)

    if not data:
        error_message = f"No upcoming trains found for {station_name}."
        return render_template('arrivals.html', station=station_name, trains=[], error=error_message)

    trains = []
    direction_map = {'N': 'Northbound', 'S': 'Southbound', 'E': 'Eastbound', 'W': 'Westbound'}
    
    for train in data[:6]: # limit to next 4
        delay_status = interpret_delay(train.get('DELAY', 'None'))
        trains.append({
            "destination": train.get('DESTINATION', 'Unknown'),
            "arrival_in": train.get('WAITING_TIME', 'N/A'),
            "line": train.get('LINE', 'Unknown'),
            "direction": direction_map.get(train.get('DIRECTION', ''), 'Unknown'),
            "delay": delay_status
        })
    
    return render_template("arrivals.html", station=station_name, trains=trains)

if __name__ == "__main__":
    app.run(debug=True)
    
