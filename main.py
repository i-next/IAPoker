import historic_file_parser.historic_file_parser as hfp
import historic_file_parser.sync_files as sync_files
import files_saved_parser.new_files_parser as new_files_parser
import models.settings as settings_db
import fixtures.cards_fix as card_fix
import fixtures.com_fix as combinaison_fix
from models import db
def run_parser():
    db.bind(settings_db.db_params)
    db.generate_mapping(create_tables=True)
    card_fix.main()
    combinaison_fix.main()
    sync_files_Data = sync_files.sync_files()
    new_files = sync_files_Data.sync_new_tournaments()

    new_files_parser_data = new_files_parser.new_files_parser()
    new_tournament = new_files_parser_data.add_new_files(new_files)
    
    # print("New tournament created:", new_tournament.id)

if __name__ == "__main__":
    run_parser()


