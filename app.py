from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

OPENWEATHER_KEY   = os.getenv("OPENWEATHER_KEY")
AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")
API_NINJAS_KEY    = os.getenv("API_NINJAS_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clima")
def clima():
    ciudad = request.args.get("ciudad", "Bogota")
    variables = {'q': ciudad, 'appid': OPENWEATHER_KEY, 'lang': 'es', 'units': 'metric'}
    r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=variables)
    return jsonify(r.json())

@app.route("/moneda")
def moneda():
    desde = request.args.get("desde", "COP")
    hasta = request.args.get("hasta", "EUR")
    r = requests.get(f'https://api.frankfurter.app/latest?from={desde}&to={hasta}')
    return jsonify(r.json())

@app.route("/vuelos")
def vuelos():
    origen  = request.args.get("origen", "BOG")
    destino = request.args.get("destino", "CDG")
    r = requests.get(f'https://api.aviationstack.com/v1/flights?dep_iata={origen}&arr_iata={destino}&access_key={AVIATIONSTACK_KEY}')
    return jsonify(r.json())

@app.route("/hoteles")
def hoteles():
    ciudad = request.args.get("ciudad", "Paris")
    r = requests.get('https://api.api-ninjas.com/v1/hotels', 
                     params={'city': ciudad},
                     headers={'X-Api-Key': API_NINJAS_KEY})
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(debug=True)