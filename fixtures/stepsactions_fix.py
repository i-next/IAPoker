
import models.stepactions as StepActionObj
from pony.orm import commit,db_session,TransactionIntegrityError

@db_session
def main():
    stepsactions = {"Preflop": 1, "Flop": 2, "Turn": 3, "River": 4}

    for key, value in stepsactions.items():
        try:
            with db_session:
                e = StepActionObj.StepActions(step = value,action = key)
        except TransactionIntegrityError as e:
            print("error")
    try:
        with db_session:
            commit()
    except TransactionIntegrityError as e:
        print("Fixture stepsactions integrity error")