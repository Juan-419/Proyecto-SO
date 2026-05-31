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
        # Paso 1: coordenadas de la ciudad
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": ciudad, "format": "json", "limit": 1},
            headers={"User-Agent": "GlobePlanner/1.0"},
            timeout=10
        ).json()

        if not geo:
            return jsonify({"error": f"Ciudad '{ciudad}' no encontrada"})

        lat = geo[0]["lat"]
        lon = geo[0]["lon"]

        # Paso 2: hoteles cercanos con Overpass API (OpenStreetMap)
        query = f"""
        [out:json][timeout:10];
        node["tourism"="hotel"](around:5000,{lat},{lon});
        out 10;
        """
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            timeout=15
        ).json()

        hoteles = []
        for el in r.get("elements", []):
            tags = el.get("tags", {})
            nombre = tags.get("name")
            if nombre:
                hoteles.append({
                    "name": nombre,
                    "star_rating": int(tags.get("stars", 0)) if tags.get("stars", "").isdigit() else None,
                    "address": tags.get("addr:street", "") + " " + tags.get("addr:housenumber", "")
                })

        return jsonify(hoteles)

    except requests.Timeout:
        return jsonify({"error": "Hoteles no respondió a tiempo"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)