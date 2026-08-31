# import historic_file_parser.historic_file_parser as hfp
# import historic_file_parser.sync_files as sync_files
# import files_saved_parser.new_files_parser as new_files_parser
import models.settings as settings_db
import fixtures.fixtures as fixtures
import functions.transfertfiles as transfertfile

import models.countrycity  # noqa: F401
import models.players  # noqa: F401
from models.migrations import migrate_database
from models import db

def run_parser():
    # Migrations BDD
    migrate_database(settings_db.db_params['filename'])
    db.bind(settings_db.db_params)
    db.generate_mapping(create_tables=True)

    # Transfert des fichiers issus de PS vers dataps
    transfertfile.main()

    # Fixtures
    fixtures.main()

    # Traitement des tournois
    #     
    # sync_files_Data = sync_files.sync_files()
    # print(sync_files_Data)
    # new_files = sync_files_Data.sync_new_tournaments()

    # new_files_parser_data = new_files_parser.new_files_parser()
    # new_tournament = new_files_parser_data.add_new_files(new_files)
    # print(new_tournament)
    

if __name__ == "__main__":
    run_parser()


