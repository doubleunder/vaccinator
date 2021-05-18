from bs4 import BeautifulSoup
from urllib import parse
import datetime
from geopy.geocoders import Nominatim
from geopy import distance
import requests


def get_location(query):
    geolocator = Nominatim(user_agent="vaccinator")
    location = geolocator.geocode(query)
    return location.latitude, location.longitude


def get_distance(source, destination):
    return distance.distance(source, destination).km


def get_google_results(pos=0):
    cookies = {"CONSENT": "YES+DE.de+20160410-02-0"}
    url = f"https://www.google.com/search?q=site:impfterminmanagement.de&start={pos}"
    response = requests.get(url, cookies=cookies).text
    body = BeautifulSoup(response, 'html.parser')
    entries = body.find_all("a")
    urls = [
        parse.parse_qs(entry["href"])["/url?q"][0] for entry in entries
        if entry["href"].startswith("/url")
    ]
    return urls


def get_doctors():
    doctors = []
    pos = 0
    while True:
        results = get_google_results(pos)
        results = [result for result in results if "praxis" in result]
        if not results:
            break
        pos += 10
        doctors.extend(results)
    return doctors
