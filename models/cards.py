from .database import db
from pony import orm as database


class Card(db.Entity):
    card_value = database.Required(str)
    card_color = database.Required(str)
    card_indice = database.Required(int)
    card_count_all = database.Optional(int)
    card_count_me = database.Optional(int)
    combinaisons_first = database.Set('Combinaison', reverse='first_card')
    combinaisons_second = database.Set('Combinaison', reverse='second_card')
    database.composite_key(card_value,card_color)