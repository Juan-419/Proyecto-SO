from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

OPENWEATHER_KEY   = os.getenv("OPENWEATHER_KEY")
AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")

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
            f"https://open.er-api.com/v6/latest/{desde}",
            timeout=10
        )
        data = r.json()
        if data.get("result") != "success":
            return jsonify({"error": "No se pudo obtener la tasa"})

        tasa = data["rates"].get(hasta)
        if not tasa:
            return jsonify({"error": f"Moneda {hasta} no encontrada"})

        return jsonify({
            "rates": {hasta: tasa},
            "date": data["time_last_update_utc"][:16]
        })
    except requests.Timeout:
        return jsonify({"error": "Moneda no respondió a tiempo"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        # Primero obtenemos las coordenadas de la ciudad
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": ciudad, "format": "json", "limit": 1},
            headers={"User-Agent": "GlobePlanner/1.0"},
            timeout=10
        ).json()

        if not geo:
            return jsonify({"error": f"Ciudad '{ciudad}' no encontrada"})

        # Usamos el boundingbox de la ciudad para buscar hoteles dentro de ella
        bbox = geo[0]["boundingbox"]  # [sur, norte, oeste, este]
        sur, norte, oeste, este = bbox[0], bbox[1], bbox[2], bbox[3]

        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": "hotel",
                "format": "json",
                "limit": 10,
                "addressdetails": 1,
                "viewbox": f"{oeste},{norte},{este},{sur}",
                "bounded": 1
            },
            headers={"User-Agent": "GlobePlanner/1.0"},
            timeout=10
        ).json()

        hoteles = []
        for lugar in r:
            nombre = lugar.get("display_name", "").split(",")[0]
            direccion = ", ".join(lugar.get("display_name", "").split(",")[1:3]).strip()
            hoteles.append({
                "name": nombre,
                "star_rating": None,
                "address": direccion
            })

        return jsonify(hoteles)

    except requests.Timeout:
        return jsonify({"error": "Hoteles no respondió a tiempo"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)