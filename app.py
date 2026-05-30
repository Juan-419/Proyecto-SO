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
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": ciudad, "appid": OPENWEATHER_KEY, "lang": "es", "units": "metric"},
            timeout=10
        )
        return jsonify(r.json())
    except requests.Timeout:
        return jsonify({"error": "Clima no respondió a tiempo"}), 504

@app.route("/moneda")
def moneda():
    desde = request.args.get("desde", "COP")
    hasta = request.args.get("hasta", "EUR")
    try:
        r = requests.get(
            f"https://api.frankfurter.app/latest?from={desde}&to={hasta}",
            timeout=10
        )
        return jsonify(r.json())
    except requests.Timeout:
        return jsonify({"error": "Moneda no respondió a tiempo"}), 504

@app.route("/vuelos")
def vuelos():
    origen  = request.args.get("origen", "BOG")
    destino = request.args.get("destino", "CDG")
    try:
        r = requests.get(
            f"https://api.aviationstack.com/v1/flights?dep_iata={origen}&arr_iata={destino}&access_key={AVIATIONSTACK_KEY}",
            timeout=10
        )
        return jsonify(r.json())
    except requests.Timeout:
        return jsonify({"error": "Vuelos no respondió a tiempo"}), 504

@app.route("/hoteles")
def hoteles():
    ciudad = request.args.get("ciudad", "Paris")
    try:
        r = requests.get(
            "https://api.api-ninjas.com/v1/hotels",
            params={"city": ciudad},
            headers={"X-Api-Key": API_NINJAS_KEY},
            timeout=10
        )
        return jsonify(r.json())
    except requests.Timeout:
        return jsonify({"error": "Hoteles no respondió a tiempo"}), 504

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)