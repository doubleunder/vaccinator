from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
from bs4 import BeautifulSoup
from urllib import parse
import datetime
import requests
import helper

db = SqliteDatabase('clinics.db')


class BaseModel(Model):
    class Meta:
        database = db


class Clinic(BaseModel):
    name = TextField()
    id = CharField(unique=True)
    date_added = DateTimeField(default=datetime.datetime.now)
    address = TextField()
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    @classmethod
    def get_as_dict(cls, expr):
        query = cls.select().where(expr).dicts()
        return query.get()


db.connect()
db.create_tables([Clinic])


def get_clinic_details(url) -> dict:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    infotext = soup.select(".alert-info")[0].text.splitlines()

    id = res.url.split("/")[4]
    name = infotext[6].strip()
    address = infotext[8].strip() + ", " + infotext[10].strip(
    ) + " " + infotext[11].strip()
    location = get_location(address)

    details = {
        "name": name,
        "id": id,
        "address": address,
        "latitude": location[0],
        "longitude": location[1]
    }

    return details


def get_info(id="all"):
    if id == "all":
        data = Clinic.select()
        result = []
        for i in data:
            result.append(model_to_dict(i))
        return result
    else:
        return model_to_dict(Clinic.get_by_id(id))


if __name__ == '__main__':
    for url in helper.get_doctors():
        clinic = get_clinic_details(url)
        Clinic.get_or_create(**clinic)
else:
    print(f"db is imported into another module")
