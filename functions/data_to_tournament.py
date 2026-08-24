import re
from datetime import datetime
import models.tournaments as tournaments
from pony.orm import commit, db_session
class data_to_tournament():
    NICKNAME = "psychoman59"
    GAIN_PATTERN = re.compile(
                    rf"^\s*\d+:\s*{re.escape(NICKNAME)}\s+\([^)]*\),\s*€([0-9]+[.,]?[0-9]*)",
                    re.MULTILINE | re.IGNORECASE,
                )
    @db_session
    def set_entity_tournament(self,data:list):
        data_info = {}
        for info in data:
            if info.startswith("PokerStars Tournoi"):
                id_match = re.search(r"#(\d+)", info)
                if not id_match:
                    return None
                tournament_id = id_match.group(1)
                data_info["tournament_id"] = tournament_id
            elif "Tournoi commencé" in info:
                date_match = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})", info)
                raw = date_match.group(1)
                dt = datetime.strptime(raw, "%d/%m/%Y %H:%M:%S")
                data_info["date"] = dt.isoformat()
            elif info.startswith("Buy-in"):
                buy_match = re.findall(r"€([0-9]+[.,]?[0-9]*)", info)
                data_info["buy_in_total"] = sum(
                    float(m.replace(",", ".")) for m in buy_match
                )
            elif info.startswith("Dotation totale"):
                dot_match = re.search(r"€([0-9]+[.,]?[0-9]*)", info)
                if dot_match is None:
                    dot_match= re.search(r"([0-9]+[.,]?[0-9]*) €", info)
                data_info["dotation"] = float(dot_match.group(1).replace(",", "."))
            elif "joueurs" in info:
                players_match = re.search(r"(\d+)\s+joueurs?", info, re.IGNORECASE)
                data_info["nbjoueurs"] = int(players_match.group(1))
            elif "Vous avez terminé" in info:
                pos_match = re.search(
                    r"Vous avez terminé à la (\d+)(?:er|e|ème|eme)? place", info, re.IGNORECASE
                )
                if pos_match:
                    data_info["position"] = int(pos_match.group(1))
            else:
                # TODO Change gain calculate see files to detect  
                gain_pattern = re.compile(
                    rf"^\s*\d+:\s*{re.escape(self.NICKNAME)}\s+\([^)]*\),\s*€([0-9]+[.,]?[0-9]*)",
                    re.MULTILINE | re.IGNORECASE,
                )
                gain_match = gain_pattern.search(info)
                if gain_match is not None:
                    data_info["gain"] = float(gain_match.group(1).replace(",", "."))
        data_info["gain"] = data_info.get('gain',0)        
        data_info["profit"] = data_info['gain'] - data_info["buy_in_total"]        
        new_tournament = tournaments.Tournament(tournament_id = data_info["tournament_id"], date = data_info["date"], nb_players = data_info["nbjoueurs"], buy_in_total = data_info["buy_in_total"], dotation = data_info["dotation"], position = data_info["position"], gain = data_info["gain"], profit = data_info["profit"])
        commit()
        return new_tournament
        