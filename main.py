# import historic_file_parser.historic_file_parser as hfp
# import historic_file_parser.sync_files as sync_files
# import files_saved_parser.new_files_parser as new_files_parser
import models.settings as settings_db
import fixtures.fixtures as fixtures
import functions.transfertfiles as transfertfile
from functions.tournaments.sync_new_files import main as sync_new_files_main

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
    print(sync_new_files_main())


if __name__ == "__main__":
    run_parser()


