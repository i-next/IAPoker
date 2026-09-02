from .database import db
from pony import orm as database


class Players(db.Entity):
    pseudo = database.Required(str)
    countrycity = database.Required('CountryCity')
    nb_tour = database.Required(int, default=0)
    tournaments = database.Set('Tournament', reverse='players')