import requests
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from threading import Thread
import os

from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import dateparser

app = Flask('')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
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


  query = str(s + " prayer time site:muslimpro.com")
  data = {}

  # Run the asynchronous function in the event loop
urls = get_results(query)

  try:
    url = urls[0]['href']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    city = soup.find("p", attrs={"class": "location"})
    dates = soup.find("div", attrs={"class": "prayer-daily-title-location"})
    data["city"] = city.get_text()
    data["date"] = dates.get_text()
    data["today"] = {}
    data["tomorrow"] = {}
    waktu = soup.find_all("span", attrs={"class": "waktu-solat"})
    jam = soup.find_all("span", attrs={"class": "jam-solat"})

    for x, y in zip(waktu, jam):
      data["today"][x.get_text()] = y.get_text()

    names = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Ishaa"]

    try:
      tomorrow = soup.find("tr", attrs={
        "class": "active"
      }).find_next("tr").find_all("td", attrs={"class": "prayertime"})
      for x, y in zip(names, tomorrow):
        data["tomorrow"][x] = y.get_text()
    except:
      month = str(dateparser.parse(data["date"]))[5:7]
      url = url + '?date=2021-' + str(int(month) + 1)
      response = requests.get(url)
      soup = BeautifulSoup(response.content, "html.parser")
      tomorrow = soup.find_all("tr")[1].find_all("td",
                                                 attrs={"class": "prayertime"})
      for x, y in zip(names, tomorrow):
        data["tomorrow"][x] = y.get_text()
  except Exception as e:
    print(e)
    data["Error"] = "Result Not Found"

  return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

