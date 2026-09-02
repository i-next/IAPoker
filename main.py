import models.settings as settings_db
import fixtures.fixtures as fixtures
import functions.transfertfiles as transfertfile
from functions.tournaments.sync_new_files import main as sync_new_files_main

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


