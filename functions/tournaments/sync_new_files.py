from pathlib import Path

from pony.orm import db_session

from functions.tournaments.convert_data_to_tournament import main as convert_data_main
from models import db
from models import settings as settings_db
from models.tournaments import Tournament


# def get_content_file(file_path: str):
#     path = Path(file_path)
#     if not path.exists():
#         print(f"Le fichier n'existe pas : {file_path}")
#         return None

#     with path.open("r", encoding="utf-8", errors="replace") as file:
#         print(file.read())


def main():
    if not db.provider:
        db.bind(settings_db.db_params)
        db.generate_mapping(create_tables=True)

    with db_session():
        new_tournaments = list(Tournament.select(lambda t: t.newone == True))
        for tournament in new_tournaments:
            file_name = f"TS_T{tournament.tournament_id}.txt"
            file_path = Path("dataps") / file_name
            print(file_path.name)
            if file_path.exists():
                with file_path.open("r", encoding="utf-8", errors="replace") as file:
                    convert_data_main(file.read())
            tournament.newone = False
    return new_tournaments


if __name__ == "__main__":
    main()
