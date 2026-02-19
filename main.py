from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from adhan import PrayerTimes, Coordinates, CalculationParameters
from adhan.calculation import Madhab
import pytz

app = Flask(__name__)
CORS(app)

# قاعدة بيانات بسيطة للمدن الجزائرية
CITIES = {
    "algiers": (36.7538, 3.0588),
    "oran": (35.6981, -0.6348),
    "constantine": (36.3650, 6.6147),
    "setif": (36.1911, 5.4137),
    "annaba": (36.9000, 7.7667),
    "blida": (36.4700, 2.8289)
}

def algeria_calculation():
    params = CalculationParameters(
        fajr_angle=18,
        isha_angle=17
    )
    params.madhab = Madhab.SHAFI
    return params

@app.route("/")
def home():
    return "Algeria Prayer API is running"

@app.route("/api/<city>")
def prayer(city):
    city = city.lower()

    if city not in CITIES:
        return jsonify({"error": "City not supported"}), 404

    lat, lng = CITIES[city]

    coordinates = Coordinates(lat, lng)
    params = algeria_calculation()

    tz = pytz.timezone("Africa/Algiers")
    today = datetime.now(tz)

    prayer_times = PrayerTimes(coordinates, today, params)

    return jsonify({
        "city": city,
        "Fajr": prayer_times.fajr.astimezone(tz).strftime("%H:%M"),
        "Sunrise": prayer_times.sunrise.astimezone(tz).strftime("%H:%M"),
        "Dhuhr": prayer_times.dhuhr.astimezone(tz).strftime("%H:%M"),
        "Asr": prayer_times.asr.astimezone(tz).strftime("%H:%M"),
        "Maghrib": prayer_times.maghrib.astimezone(tz).strftime("%H:%M"),
        "Isha": prayer_times.isha.astimezone(tz).strftime("%H:%M")
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
