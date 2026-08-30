from .database import db
from pony import orm as database


class StepActions(db.Entity):
    step = database.Required(int,unique = True)
    action = database.Required(str,unique = True)
    hands = database.Set('Hands', reverse='step_id')