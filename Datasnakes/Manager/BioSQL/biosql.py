import pkg_resources
from pathlib import Path
import os
import subprocess
import shutil
from Datasnakes.Tools.logit import LogIt
from Datasnakes.Manager.BioSQL.biosql_repo import sql
from Datasnakes.Manager.BioSQL.biosql_repo import scripts as sql_scripts


class BaseBioSQL(object):
    # TODO-ROB:  Organize the BioSQL files by driver/RDBMS
    # TODO-ROB:  Add functionality for database_type="biosqldb"
    def __init__(self, database_name, driver):

        self.database_name = database_name
        self.driver = driver
        self.biosqllog = LogIt().default(logname="BioSQL", logfile=None)

        self.scripts = pkg_resources.resource_filename(sql_scripts.__name__, "")
        self.ncbi_taxon_script = pkg_resources.resource_filename(sql_scripts.__name__, "load_taxonomy.pl")
        self.itis_taxon_script = pkg_resources.resource_filename(sql_scripts.__name__, "load_itis_taxonomy.pl")
        pass

    def load_biosql_schema(self, cmd, schema_file):
        schema_cmd = "%s < %s" % (cmd, schema_file)
        schema_load = subprocess.Popen([schema_cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                       encoding='utf-8')
        error = schema_load.stderr.readlines()
        out = schema_load.stdout.readlines()

        self.biosqllog.info("Schema-Error: " + str(error))
        self.biosqllog.info("Schema-Out: " + str(out))
        return error, out

    def load_taxonomy(self, cmd):
        # ./load_taxonomy.pl --dbname bioseqdb --driver mysql --dbuser root --download true
        taxon_cmd = cmd
        taxon_load = subprocess.Popen([taxon_cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                      encoding='utf-8')

        error = taxon_load.stderr.readlines()
        out = taxon_load.stdout.readlines()

        self.biosqllog.info("Taxon-Error: " + str(error))
        self.biosqllog.info("Taxon-Out: " + str(out))
        return error, out
        pass

    def create_executable_scripts(self):
        # Set up the permissions for the BioSQL Perl scripts
        biosql_scripts = self.scripts
        for file in os.listdir(biosql_scripts):
            print(file)
            if '.pl' in str(file):
                script_path = os.path.join(biosql_scripts, file)
                print(script_path)
                os.chmod(script_path, mode=0o755)


class SQLiteBioSQL(BaseBioSQL):
    def __init__(self, database_name, template="Template-BioSQL-SQLite.db"):
        super().__init__(database_name=database_name, driver="SQLite")
        self.schema_cmd = "sqlite3 %s -echo"
        self.schema_file = "biosqldb-sqlite.sql"
        self.taxon_cmd = "%s --dbname %s --driver %s --download true"

        self.template = template

    def load_sqlite_schema(self, database_name=None):
        schema_file = pkg_resources.resource_filename(sql.__name__, self.schema_file)
        if database_name:
            self.database_name = database_name
        schema_cmd = self.schema_cmd % self.database_name
        error, out = self.load_biosql_schema(schema_cmd, schema_file)
        # TODO-ROB: Parse output and error

    def load_sqlite_taxonomy(self, database_name=None):
        if database_name:
            self.database_name = database_name
        taxon_cmd = self.taxon_cmd % (self.ncbi_taxon_script, self.database_name, self.driver)
        error, out = self.load_taxonomy(taxon_cmd)
        # TODO-ROB: Parse output and error

    def create_template_database(self, db_path):
        db_path = Path(db_path) / Path(self.template)
        if not db_path.is_file():
            self.load_sqlite_schema(database_name=db_path)
            self.create_executable_scripts()
            self.load_sqlite_taxonomy(database_name=db_path)
        else:
            self.biosqllog.warning("The template, %s, already exists." % self.template)

    def copy_template_database(self, db_path, dest_path, dest_name=""):
        db_path = Path(db_path) / Path(self.template)
        if not db_path.is_file():
            self.create_template_database(db_path=db_path.parent)
        dest_path = Path(dest_path) / Path(dest_name)
        self.biosqllog.warn('Copying Template BioSQL Database...  This may take a few minutes...')
        shutil.copy2(str(db_path), str(dest_path))


class MySQLBioSQL(BaseBioSQL):

    def __init__(self):
        pass
