from datetime import datetime
import re


class extract_tournament_info:
    NICKNAME = "psychoman59"
    def __init__(self, tournament_data: list[str]):
        self.tournament_data = tournament_data
        self.NICKNAME = self.NICKNAME
        
    def extract_info(self) -> dict:
        """Extrait les informations du tournoi à partir de la liste de lignes."""
        info = {}
        
        for line in self.tournament_data:
            print("read line",line)
            if line.startswith("PokerStars Tournoi"):
                id_match = re.search(r"#(\d+)", line)
                if not id_match:
                    return None
                info["tournament_id"] = id_match.group(1)
                # print(info)
            elif "Tournoi commencé" in line:
                date_match = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})", line)
                raw = date_match.group(1)
                dt = datetime.strptime(raw, "%d/%m/%Y %H:%M:%S")
                info["date"] = dt.isoformat()
            elif line.startswith("Buy-in"):
                buy_match = re.findall(r"€([0-9]+[.,]?[0-9]*)", line)
                info["buy_in_total"] = sum(
                    float(m.replace(",", ".")) for m in buy_match
                )
            elif line.startswith("Dotation totale"):
                dot_match = re.search(r"€([0-9]+[.,]?[0-9]*)", line)
                info["dotation"] = float(dot_match.group(1).replace(",", "."))
            elif "joueurs" in line:
                players_match = re.search(r"(\d+)\s+joueurs?", line, re.IGNORECASE)
                info["nbjoueurs"] = int(players_match.group(1))
            elif "Vous avez terminé" in line:
                pos_match = re.search(
                    r"Vous avez terminé à la (\d+)(?:er|e|ème|eme)? place", line, re.IGNORECASE
                )
                if pos_match:
                    info["position"] = int(pos_match.group(1))
            else:
                gain_pattern = re.compile(
                    rf"^\s*\d+:\s*{re.escape(self.NICKNAME)}\s+\([^)]*\),\s*€([0-9]+[.,]?[0-9]*)",
                    re.MULTILINE | re.IGNORECASE,
                )
                gain_match = gain_pattern.search(line)
                if gain_match:
                    info["gain"] = float(gain_match.group(1).replace(",", "."))
                    info["profit"] = info['gain'] - info["buy_in_total"]
        print("return info",info)
        return info

        