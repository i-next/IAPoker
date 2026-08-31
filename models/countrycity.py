from .database import db
from pony import orm as database


class CountryCity(db.Entity):
    name = database.Required(str, unique = True)
    players = database.Set('Players', reverse='countrycity')