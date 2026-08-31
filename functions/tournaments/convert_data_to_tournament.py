import re
from datetime import datetime

from pony.orm import db_session

from models.tournaments import Tournament


@db_session
def convert_data(file_content: str):
    lines = file_content.splitlines()
    parsed_tournament_id = None

    for line in lines:
        if line.startswith("PokerStars Tournoi"):
            id_match = re.search(r"#(\d+)", line)
            if id_match:
                parsed_tournament_id = int(id_match.group(1))

    if parsed_tournament_id is not None:
        data = Tournament.get(tournament_id=parsed_tournament_id)
        if data is None:
            data = Tournament(
                tournament_id=parsed_tournament_id,
                date="1970-01-01T00:00:00",
                nb_players=0,
                buy_in_total=0.0,
                dotation=0.0,
                position=0,
                gain=0.0,
                profit=0.0,
                newone=True,
            )
    else:
        data = Tournament(
            tournament_id=0,
            date="1970-01-01T00:00:00",
            nb_players=0,
            buy_in_total=0.0,
            dotation=0.0,
            position=0,
            gain=0.0,
            profit=0.0,
            newone=True,
        )

    for line in lines:
        if line.startswith("PokerStars Tournoi"):
            id_match = re.search(r"#(\d+)", line)
            if id_match:
                data.tournament_id = int(id_match.group(1))
        elif "Tournoi commencé" in line:
            date_match = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})", line)
            if date_match:
                raw = date_match.group(1)
                dt = datetime.strptime(raw, "%d/%m/%Y %H:%M:%S")
                data.date = dt.isoformat()
        elif line.startswith("Buy-in"):
            buy_match = re.findall(r"€([0-9]+[.,]?[0-9]*)", line)
            if buy_match:
                data.buy_in_total = sum(float(m.replace(",", ".")) for m in buy_match)
        elif line.startswith("Dotation totale"):
            dot_match = re.search(r"€([0-9]+[.,]?[0-9]*)", line)
            if dot_match:
                data.dotation = float(dot_match.group(1).replace(",", "."))
        elif "joueurs" in line:
            players_match = re.search(r"(\d+)\s+joueurs?", line, re.IGNORECASE)
            if players_match:
                data.nb_players = int(players_match.group(1))
        elif "Vous avez terminé" in line:
            pos_match = re.search(
                r"Vous avez terminé à la (\d+)(?:er|e|ème|eme)? place", line, re.IGNORECASE
            )
            if pos_match:
                data.position = int(pos_match.group(1))

    if not data.gain:
        data.gain = 0.0
    if not data.profit:
        data.profit = 0.0
    data.newone = True
    return data


def main(file_content):
    main.data = convert_data(file_content)
    print(main.data)


if __name__ == "__main__":
    main("")