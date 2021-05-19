import requests
from bs4 import BeautifulSoup
from urllib import parse
import db
import helper


class Person:
    def __init__(self, gender, surname, lastname, birth_day, birth_month,
                 birth_year, email, mobile, street, zip, city, egk,
                 max_distance):
        self.gender = gender  # "d", "m" or "w"
        self.surname = surname
        self.lastname = lastname
        self.birth_day = birth_day  # needs 0 padding if <10
        self.birth_month = birth_month  # needs 0 padding if <10
        self.birth_year = birth_year  # eg. 1969
        self.email = email
        self.mobile = mobile  # phone number
        self.street = street
        self.zip = zip
        self.city = city
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


def post_registration(id: str, token: str, person: Person, vacc, text=""):
    url = f"https://impfterminmanagement.de/praxis/{id}/registrieren"

    payload = {
        "patient[geschlecht]": person.gender,
        "patient[vorname]": person.surname,
        "patient[name]": person.lastname,
        "patient[geburtsdatum_tag]": person.birth_day,
        "patient[geburtsdatum_monat]": person.birth_month,
        "patient[geburtsdatum_jahr]": person.birth_year,
        "patient[email]": person.email,
        "patient[emailRepeat]": person.email,
        "patient[mobile]": person.mobile,
        "patient[fax]": "",
        "patient[strasse]": person.street,
        "patient[plz]": person.zip,
        "patient[ort]": person.city,
        "patient[versichertenArt]": "gesetzlich",
        "patient[egk]": person.egk,
        "patient[bemerkung]": text,
        "patient[datenschutz]": "1",
        "patient[verarbeitung]": "1",
        "patient[save]": "",
        "patient[_token]": token
    }

    payload_list = [(k, v) for k, v in payload.items()]

    if not vacc:
        payload_list.append(("patient[keinVakzinBevorzugt]", "1"))
    else:
        for vaccine, value in vacc.items():
            if vaccine == "astrafever" and value:
                payload_list.append(("patient[bevorzugteVakzine][]", "1"))
            elif vaccine == "biontech" and value:
                payload_list.append(("patient[bevorzugteVakzine][]", "0"))
            elif vaccine == "j&j" and value:
                payload_list.append(("patient[bevorzugteVakzine][]", "2"))
            elif vaccine == "moderna" and value:
                payload_list.append(("patient[bevorzugteVakzine][]", "3"))

    headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Origin": "https://impfterminmanagement.de",
        "Referer": f"https://impfterminmanagement.de/praxis/{id}/registrieren",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = session.post(url, headers=headers, data=payload_list)

    # print(response.text)


def encode_text(s):
    encoded_string = map(parse.quote, s.split(" "))

    return "+".join(list(encoded_string))


def register(id, p1, vacc, text=""):
    registered, clinic = db.is_registered(id)

    if registered:
        print(f"already registered at {clinic.name} ({clinic.id})")
    else:
        print(f"try to register at: {clinic.name} ({clinic.id})")
        post_registration(id, get_token(id), p1, vacc, text)
        db.register_at(clinic)


if __name__ == "__main__":
    # create person to register
    p1 = Person(
        "d",  # gender: "d", "m" or "w" 
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

    # comment/delete if you care which vaccine you get
    prefer_vaccine = False

    # uncomment and edit to choose vaccine. example only mRNA
    # prefer_vaccine = {
    #     "astrafever": False,
    #     "biontech": True,
    #     "j&j": False,
    #     "moderna": True
    # }

    for c in db.get_info():
        dist = helper.get_distance(p1.location,
                                   (c['latitude'], c['longitude']))
        if dist <= p1.max_distance:
            register(c.get("id"), p1, prefer_vaccine, additional_text)