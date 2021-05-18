import requests
from bs4 import BeautifulSoup
from urllib import parse
import db
import helper


class Person:
    def __init__(self, gender, surname, lastname, birth_day, birth_month,
                 birth_year, email, mobile, street, zip, city, egk,
                 max_distance):
        self.gender = gender  # "m" or "f"
        self.surname = parse.quote(surname)
        self.lastname = parse.quote(lastname)
        self.birth_day = birth_day  # needs 0 padding if <10
        self.birth_month = birth_month  # needs 0 padding if <10
        self.birth_year = birth_year  # eg. 1969
        self.email = parse.quote(email)
        self.mobile = mobile  # phone number
        self.street = parse.quote(street)
        self.zip = zip
        self.city = parse.quote(city)
        self.egk = egk  # client number on your medical insurance card
        self.max_distance = max_distance  # max distance in KM
        self.location = helper.get_location(street + ", " + zip + " " + city)


session = requests.Session()


def get_token(id, headers=""):
    page = session.get(
        f"https://impfterminmanagement.de/praxis/{id}/registrieren",
        headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    token = soup.find(id="patient__token")["value"]

    return token


def post_registration(id: str, token: str, person: Person, text=""):
    url = f"https://impfterminmanagement.de/praxis/{id}/registrieren"
    payload = f"patient%5Bgeschlecht%5D={person.gender}&patient%5Bvorname%5D={person.surname}&patient%5Bname%5D={person.lastname}&patient%5Bgeburtsdatum_tag%5D={person.birth_day}&patient%5Bgeburtsdatum_monat%5D={person.birth_month}&patient%5Bgeburtsdatum_jahr%5D={person.birth_year}&patient%5Bemail%5D={person.email}&patient%5BemailRepeat%5D={person.email}&patient%5Bmobile%5D={person.mobile}&patient%5Bfax%5D=&patient%5Bstrasse%5D={person.street}&patient%5Bplz%5D={person.zip}&patient%5Bort%5D={person.city}&patient%5BversichertenArt%5D=gesetzlich&patient%5Begk%5D={person.egk}&patient%5BbevorzugteVakzine%5D%5B%5D=0&patient%5BbevorzugteVakzine%5D%5B%5D=2&patient%5BbevorzugteVakzine%5D%5B%5D=3&patient%5Bbemerkung%5D={text}&patient%5Bdatenschutz%5D=1&patient%5Bverarbeitung%5D=1&patient%5Bsave%5D=&patient%5B_token%5D={token}"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Origin": "https://impfterminmanagement.de",
        "Referer": f"https://impfterminmanagement.de/praxis/{id}/registrieren",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = session.post(url, headers=headers, data=payload)

    print(response.text)


def encode_text(s):
    encoded_string = map(parse.quote, s.split(" "))

    return "+".join(list(encoded_string))


def register(id, p1, text):
    registered, clinic = db.is_registered(id)

    if registered:
        print(f"already registered at {id}")
    else:
        post_registration(id, get_token(id), p1, encode_text(text))
        db.register_at(clinic)


if __name__ == "__main__":
    # create person to register
    p1 = Person(
        "d",  # gender: "d", "f" or "m" 
        "Max",  #surname
        "Muster",  # lastname
        "01",  # birt_hday (needs 0 padding if <10)
        "03",  # birth_month (needs 0 padding if <10)
        "1969",  # birth_year
        "mail@example.com",  # e-mail
        "01724169420",  # phone number
        "Friedrichstraße 6",  # street
        "70174",  # zip
        "Stuttgart",  # city
        "Z129838971",  # egk number
        50)  # max distance in km

    additional_text = "additional info like prio or diseases"

    for c in db.get_info():
        dist = helper.get_distance(p1.location,
                                   (c['latitude'], c['longitude']))
        if dist <= p1.max_distance:
            print(f"try to register at: {c.get('name')} ({c.get('id')})")
            register(c.get("id"), p1, additional_text)