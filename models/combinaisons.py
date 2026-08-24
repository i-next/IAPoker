from .database import db
from pony import orm as database


class Combinaison(db.Entity):
    first_card = database.Required('Card')
    second_card = database.Required('Card')
    count = database.Required(int)
