import re
from datetime import datetime

from pony.orm import db_session

from models.countrycity import CountryCity
from models.players import Players
from models.tournaments import Tournament


def _parse_players_from_text(file_content: str):
    players = []
    player_pattern = re.compile(
        r"^\s*(?:Place\s+)?(\d+)\s*:\s*([^\s(]+)\s*\(([^)]+)\),\s*(?:€([0-9]+(?:[.,][0-9]*)?)|ticket\s+([0-9]+(?:[.,][0-9]*)?) €)?",
        re.IGNORECASE,
    )
    
    for line in file_content.splitlines():
        match = player_pattern.match(line.strip())
       
        if not match:
            continue
        pseudo = match.group(2).strip()
        country_name = match.group(3).strip()
        gain = None
       
        # Extract gain: either "€x,xx" or "ticket x €" format
        if match.group(4):  # €x,xx format
            gain = float(match.group(4).replace(",", "."))
        elif match.group(5):  # ticket x € format
            gain = float(match.group(5).replace(",", "."))
        
        players.append({"pseudo": pseudo, "countrycity": country_name, "gain": gain})

    return players


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
        if "Tournoi commencé" in line:
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

    for player_data in _parse_players_from_text(file_content):
        country = CountryCity.get(name=player_data["countrycity"])
        if country is None:
            country = CountryCity(name=player_data["countrycity"])

        player = Players.get(pseudo=player_data["pseudo"])
        if player is None:
            player = Players(pseudo=player_data["pseudo"], countrycity=country)

        # Add player to tournament
        data.players.add(player)
        player.nb_tour += 1
        
        # If this is psychoman59 (the user player), update gain from player data
        if player_data["pseudo"] == "psychoman59" and player_data.get("gain") is not None:
            data.gain = player_data["gain"]
    
    # Calculate profit = gain - buy_in_total
    data.profit = data.gain - data.buy_in_total

    data.newone = True
    return data


def main(file_content):
    main.data = convert_data(file_content)
    print(main.data)


if __name__ == "__main__":
    main("")