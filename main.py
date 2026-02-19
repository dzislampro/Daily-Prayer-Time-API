import requests
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import os
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import dateparser

app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False


def get_results(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=2))
    return results


@app.route('/')
def home():
    return "I'm alive"


@app.route('/api/<string:s>', methods=['GET'])
@cross_origin(origin='*')
def prayer(s):
    query = f"{s} prayer time site:muslimpro.com"
    data = {}

    try:
        urls = get_results(query)
        url = urls[0]['href']

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        city = soup.find("p", attrs={"class": "location"})
        dates = soup.find("div", attrs={"class": "prayer-daily-title-location"})

        data["city"] = city.get_text() if city else "Unknown"
        data["date"] = dates.get_text() if dates else "Unknown"
        data["today"] = {}
        data["tomorrow"] = {}

        waktu = soup.find_all("span", attrs={"class": "waktu-solat"})
        jam = soup.find_all("span", attrs={"class": "jam-solat"})

        for x, y in zip(waktu, jam):
            data["today"][x.get_text()] = y.get_text()

    except Exception as e:
        data["Error"] = "Result Not Found"

    return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
