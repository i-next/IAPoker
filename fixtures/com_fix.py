from pony.orm import db_session

from models.cards import Card
from models.combinaisons import Combinaison


@db_session
def main():
    cards = list(Card.select().order_by(lambda card: (card.card_indice, card.id)))

    for first_index, first_card in enumerate(cards):
        for second_card in cards[first_index + 1:]:
            Combinaison.get(first_card=first_card, second_card=second_card) or Combinaison(
                first_card=first_card,
                second_card=second_card,
                count=0,
            )