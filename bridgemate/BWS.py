import os
import shutil
import time
import win32com.client

from utils.config import BWS_TEMPLATE_PATH
from utils.Tools import get_computer_name
from bridgemate.DBTable import *

dbLangGeneral = ';LANGID=0x0409;CP=1252;COUNTRY=0'
dbVersion = 64
class MDB97(object):
    def __init__(self):
        self.access_object = win32com.client.Dispatch('Access.Application')
        self.access_object.Visible = False
        self.db = None

    def create(self, file_path):
        self.db = self.access_object.DBEngine.CreateDatabase(file_path, dbLangGeneral, dbVersion)

    def load(self, file_path):
        self.db = self.access_object.DBEngine.OpenDatabase(file_path)

    def execute(self, sql):
        self.db.Execute(sql)

    def get_recordset(self, sql):
        return self.db.OpenRecordset(sql)

    def close(self):
        self.db.Close()
        self.access_object.Quit()
        del self.db
        time.sleep(1)
        

class BWS(object):
    def __init__(self, file_path):
        self.file_path = file_path

        if os.path.exists(file_path):
            pass
        else:
            self.init_file()

        # add current computer to DB
        self.computer_id = self.add_client_to_db()


    def init_file(self):
        shutil.copy(BWS_TEMPLATE_PATH, self.file_path)

        mdb = MDB97()
        mdb.load(self.file_path)
        mdb.execute("ALTER TABLE Settings ADD BM2AutoShowScoreRecap BIT")
        mdb.execute("ALTER TABLE Settings ADD BM2ScoreRecap BIT")
        mdb.close()

    def add_client_to_db(self, computer_name=None):
        if computer_name is None:
            computer_name = get_computer_name()

        mdb = MDB97()
        mdb.load(self.file_path)

        rs = mdb.get_recordset( ClientsTable().get_select_sql() )
        res = ClientsTable().get_first_from_recordset(rs, [(CLIENTS_COMPUTER, computer_name)])
        if not res:
            fields = [ (CLIENTS_COMPUTER, '"%s"' % computer_name) ]
            sql = ClientsTable().get_insert_sql(fields)
            mdb.execute(sql)
            rs = mdb.get_recordset( ClientsTable().get_select_sql() )
            res = ClientsTable().get_first_from_recordset(rs, [(CLIENTS_COMPUTER, computer_name)])

        mdb.close()

        return res[CLIENTS_ID]


    def fill_section(self, current_round, board_start, board_end, section_id, section_letter, matches):
        team_count =  len(matches)

        mdb = MDB97()
        mdb.load(self.file_path)

        # Section fill
        fields = [ 
            (SECTION_ID, str(section_id)),
            (SECTION_LETTER, '"%s"' % section_letter),
            (SECTION_TABLES, str(team_count)),
            (SECTION_MISSINGPAIR, '0')
        ]
        sql = SectionTable().get_insert_sql(fields)
        mdb.execute(sql)

        # Table fill
        for table, ns_team, ew_team in matches:
            fields = [
                (TABLES_SECTION, str(section_id)),
                (TABLES_TABLE, str(table)),
                (TABLES_COMPUTERID, str(self.computer_id)),
            ]
            sql = TablesTable().get_insert_sql(fields)
            mdb.execute(sql)

        # RoundData fill
        for table, ns_team, ew_team in matches:
            fields = [
                (ROUNDDATA_SECTION, str(section_id)),
                (ROUNDDATA_TABLE, str(table)),
                (ROUNDDATA_ROUND, str(current_round)),
                (ROUNDDATA_NSPAIR, str(ns_team)),
                (ROUNDDATA_EWPAIR, str(ew_team)),
                (ROUNDDATA_LOWBOARD, str(board_start)),
                (ROUNDDATA_HIGHBOARD, str(board_end)),
                (ROUNDDATA_CUSTOMBOARDS, '""'),
            ]
            sql = RoundDataTable().get_insert_sql(fields)
            mdb.execute(sql)

        # Setting fill
        fields = [
            (SETTINGS_SHOWRESULTS, "0"),
            (SETTINGS_SHOWOWNRESULT, "1"),
            (SETTINGS_SHOWPERCENTAGE, "0"),
            (SETTINGS_BM2SCORERECAP, "1"),
            (SETTINGS_BM2AUTOSHOWSCORERECAP, "1")
        ]
        sql = SettingsTable().get_insert_sql(fields)
        mdb.execute(sql)

        mdb.close()


    def get_recevied_date(self):
        mdb = MDB97()
        mdb.load(self.file_path)
        sql = ReceivedDataTable().get_select_sql()
        rs = mdb.get_recordset(sql)

        return ReceivedDataTable().get_array_from_recordset(rs)
