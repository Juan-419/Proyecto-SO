from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")

HEADERS = {
    "User-Agent": "GlobePlanner/1.0 (contact@example.com)"
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/clima")
def clima():
    ciudad = request.args.get("ciudad", "Bogota")

    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": ciudad,
                "appid": OPENWEATHER_KEY,
                "lang": "es",
                "units": "metric"
            },
            timeout=10
        )

        r.raise_for_status()
        return jsonify(r.json())

    except requests.Timeout:
        return jsonify({"error": "Clima no respondió a tiempo"}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/moneda")
def moneda():
    desde = request.args.get("desde", "COP")
    hasta = request.args.get("hasta", "EUR")

    try:
        r = requests.get(
            f"https://open.er-api.com/v6/latest/{desde}",
            timeout=10
        )

        r.raise_for_status()
        data = r.json()

        if data.get("result") != "success":
            return jsonify({"error": "No se pudo obtener la tasa"})

        tasa = data["rates"].get(hasta)

        if tasa is None:
            return jsonify({"error": f"Moneda {hasta} no encontrada"})

        return jsonify({
            "rates": {hasta: tasa},
            "date": data.get("time_last_update_utc", "")
        })

    except requests.Timeout:
        return jsonify({"error": "Moneda no respondió a tiempo"}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/vuelos")
def vuelos():
    origen = request.args.get("origen", "BOG")
    destino = request.args.get("destino", "CDG")

    try:
        r = requests.get(
            "https://api.aviationstack.com/v1/flights",
            params={
                "dep_iata": origen,
                "arr_iata": destino,
                "access_key": AVIATIONSTACK_KEY
            },
            timeout=10
        )

        r.raise_for_status()
        return jsonify(r.json())

    except requests.Timeout:
        return jsonify({"error": "Vuelos no respondió a tiempo"}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/hoteles")
def hoteles():
    ciudad = request.args.get("ciudad", "Paris")

    try:
        # Buscar la ciudad
        geo_resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": ciudad,
                "format": "json",
                "limit": 1
            },
            headers=HEADERS,
            timeout=10
        )

        geo_resp.raise_for_status()

        try:
            geo = geo_resp.json()
        except Exception:
            return jsonify({
                "error": "Nominatim devolvió una respuesta inválida",
                "respuesta": geo_resp.text[:500]
            }), 500

        if not geo:
            return jsonify({
                "error": f"Ciudad '{ciudad}' no encontrada"
            }), 404

        bbox = geo[0]["boundingbox"]

        sur = bbox[0]
        norte = bbox[1]
        oeste = bbox[2]
        este = bbox[3]

        # Buscar hoteles
        hotel_resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": "hotel",
                "format": "json",
                "limit": 10,
                "addressdetails": 1,
                "viewbox": f"{oeste},{norte},{este},{sur}",
                "bounded": 1
            },
            headers=HEADERS,
            timeout=10
        )

        hotel_resp.raise_for_status()

        try:
            lugares = hotel_resp.json()
        except Exception:
            return jsonify({
                "error": "La búsqueda de hoteles devolvió una respuesta inválida",
                "respuesta": hotel_resp.text[:500]
            }), 500

        hoteles = []

        for lugar in lugares:
            nombre = lugar.get("display_name", "").split(",")[0]

            direccion = ", ".join(
                lugar.get("display_name", "").split(",")[1:3]
            ).strip()

            hoteles.append({
                "name": nombre,
                "address": direccion,
                "star_rating": None,
                "lat": lugar.get("lat"),
                "lon": lugar.get("lon")
            })

        return jsonify(hoteles)

    except requests.Timeout:
        return jsonify({"error": "Hoteles no respondió a tiempo"}), 504

    except requests.HTTPError as e:
        return jsonify({
            "error": f"Error HTTP: {e}"
        }), 500

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
