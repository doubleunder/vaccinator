from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import datetime
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
    db.connect()
    db.create_tables([Clinic])

    clinics = []
    for url in helper.get_doctors():
        clinics.append(helper.get_clinic_details(url))

    Clinic.replace_many(clinics).execute()
    db.close()

else:
    print(f"db is imported into another module")
