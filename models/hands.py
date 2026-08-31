from .database import db
from pony import orm as database


class Hands(db.Entity):
    tournament_id = database.Required('Tournament', reverse='hands')
    step_id = database.Required('StepActions', reverse='hands')