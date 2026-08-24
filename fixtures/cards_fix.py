import sys

# sys.path.append('D:\\IA\\Softwares\\IA Poker\\models')
import models.cards as Cards_obj
from pony.orm import commit, db_session, TransactionIntegrityError

@db_session
def main():
    colors = ["s","h","d","c"]
    for val in range(2,11):
        for color in colors:
            try:
                with db_session:
                    e = Cards_obj.Card(card_value = str(val), card_color = color, card_indice = 1)
            except TransactionIntegrityError as e:
                print("duplicate")

    values_high = ["J","Q"]
    for val in values_high:
        for color in colors:
            try:
                with db_session:
                    e = Cards_obj.Card(card_value = val, card_color = color, card_indice = 2)
            except TransactionIntegrityError as e:
                print("duplicate")        

    values_premium = ["K","A"]
    for val in values_premium:
        for color in colors:
            try:
                with db_session:
                    e = Cards_obj.Card(card_value = val, card_color = color, card_indice = 3)
            except TransactionIntegrityError as e:
                print("duplicate")        

    try:
        with db_session:
                commit()
    except TransactionIntegrityError as e:
                    print("duplicate")        
                    
# if __name__ == "__main__":
#     main()