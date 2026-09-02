from .database import db
from pony import orm as database

class Tournament(db.Entity):
    tournament_id = database.Required(int, unique = True, size = 64)
    date = database.Required(str)
    nb_players = database.Required(int)
    buy_in_total = database.Required(float)
    dotation = database.Required(float)
    position = database.Required(int)
    gain = database.Required(float, default=0)
    profit = database.Required(float)
    newone = database.Required(bool, default=True)
    players = database.Set('Players', reverse='tournaments')
    hands = database.Set('Hands', reverse='tournament_id')
