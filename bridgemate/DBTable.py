# -*- coding: utf-8 -*-
from utils.Logger import get_logger
logger = get_logger()

class DBTable(object):
    def __init__(self, table_name, colume_types):
        global logger 
        logger = get_logger()
        self.table_name = table_name
        self.colume_types = colume_types

    def get_init_sql(self):
        '''
        Return SQL code for create table in access
        '''
        fields = []
        for field_type in self.colume_types:
            fields.append("[%s] %s" % field_type)
        return "CREATE TABLE %s( %s )" % (self.table_name, ", ".join(fields))

    def get_insert_sql(self, field_tuples):
        keys = []
        values = []
        condition = []
        for key, value in field_tuples:
            keys.append("[%s]" % key)
            values.append(value)
            # condition.append(" [%s] = %s " % (key, value))
        return  '''
                    INSERT INTO [%s] ( %s ) 
                    SELECT %s 
                ''' % ( self.table_name, ", ".join(keys), ", ".join(values))
    def get_select_sql(self, fields=None):
        field_ary = '*'
        if fields:
            field_ary = ', '.join(fields)

        return  '''
                    SELECT %s FROM %s
                ''' % (field_ary, self.table_name)

    def get_array_from_recordset(self, rs):
        array = []
        while not rs.EOF:
            dic = {}
            for f_name, _ in self.colume_types:
                dic[f_name] = rs.Fields(f_name).value
                # logger.debug("[%s]: %s" % (f_name, dic[f_name]))
            
            array.append(dic)
            rs.MoveNext()

        return array

    def get_first_from_recordset(self, rs, condition):
        while not rs.EOF:
            match = True
            for f_name, value in condition:
                if rs.Fields(f_name).value != value:
                    match = False
                    break
                
            if match:
                dic = {}
                for f_name, _ in self.colume_types:
                    dic[f_name] = rs.Fields(f_name).value
                return dic
            
            rs.MoveNext()
        return None



# Clients
DBTABLE_CLIENTS = 'Clients'
CLIENTS_ID = 'ID'
CLIENTS_COMPUTER = 'Computer'
CLIENTS_COLS = [
    (CLIENTS_ID , 'AUTOINCREMENT'), 
    (CLIENTS_COMPUTER, 'Text(255)'),
]

# Section
DBTABLE_SECTION = 'Section'
SECTION_ID = 'ID'
SECTION_LETTER = 'Letter'
SECTION_TABLES = 'Tables'
SECTION_MISSINGPAIR = 'MissingPair'
SECTION_COLS = [
    (SECTION_ID, 'Integer'),
    (SECTION_LETTER, 'Text(2)'),
    (SECTION_TABLES, 'Integer'),
    (SECTION_MISSINGPAIR, 'Integer'),
]


# Tables
DBTABLE_TABLES = 'Tables'
TABLES_SECTION = "Section"
TABLES_TABLE = "Table"
TABLES_COMPUTERID = "ComputerID"
TABLES_STATUS = "Status"
TABLES_LOGONOFF = "LogOnOff"
TABLES_CURRENTROUND = "CurrentRound"
TABLES_CURRENTBOARD = "CurrentBoard"
TABLES_UPDATEFROMROUND = "UpdateFromRound"
TABLES_COLS = [
    (TABLES_SECTION, 'Integer'),
    (TABLES_TABLE, 'Integer'),
    (TABLES_COMPUTERID, 'Integer'),
    (TABLES_STATUS, 'Integer'),
    (TABLES_LOGONOFF, 'Integer'),
    (TABLES_CURRENTROUND, 'Integer'),
    (TABLES_CURRENTBOARD, 'Integer'),
    (TABLES_UPDATEFROMROUND, 'Integer'),
]


# RoundData
DBTABLE_ROUNDDATA = "RoundData"
ROUNDDATA_SECTION = "Section"
ROUNDDATA_TABLE = "Table"
ROUNDDATA_ROUND = "Round"
ROUNDDATA_NSPAIR = "NSPair"
ROUNDDATA_EWPAIR = "EWPair"
ROUNDDATA_LOWBOARD = "LowBoard"
ROUNDDATA_HIGHBOARD = "HighBoard"
ROUNDDATA_CUSTOMBOARDS = "CustomBoards"
ROUNDDATA_COLS = [
    (ROUNDDATA_SECTION, 'Integer'),
    (ROUNDDATA_TABLE, 'Integer'),
    (ROUNDDATA_ROUND, 'Integer'),
    (ROUNDDATA_NSPAIR, 'Integer'),
    (ROUNDDATA_EWPAIR, 'Integer'),
    (ROUNDDATA_LOWBOARD, 'Integer'),
    (ROUNDDATA_HIGHBOARD, 'Integer'),
    (ROUNDDATA_CUSTOMBOARDS, 'Text(255)'),
]


# ReceivedData / IntermediateData
DBTABLE_RECEIVEDDATA = "ReceivedData"
DBTABLE_INTERMEDIATEDATA = "IntermediateData"
DATA_ID = "ID"
DATA_SECTION = "Section"
DATA_TABLE = "Table"
DATA_ROUND = "Round"
DATA_BOARD = "Board"
DATA_PAIRNS = "PairNS"
DATA_PAIREW = "PairEW"
DATA_DECLARER = "Declarer"
DATA_DIRECTION = "NS/EW"
DATA_CONTRACT = "Contract"
DATA_RESULT = "Result"
DATA_LEADCARD = "LeadCard"
DATA_REMARKS = "Remarks"
DATA_DATE = "DateLog"
DATA_TIME = "TimeLog"
DATA_PROCESSED0 = "Processed0"
DATA_PROCESSED1 = "Processed1"
DATA_PROCESSED2 = "Processed2"
DATA_PROCESSED3 = "Processed3"
DATA_ERASED = "Erased"
RECEIVEDDATA_COLS = INTERMEDIATEDATA_COLS = [
    (DATA_ID, 'AUTOINCREMENT'), 
    (DATA_SECTION, 'Integer'), 
    (DATA_TABLE, 'Integer'), 
    (DATA_ROUND, 'Integer'), 
    (DATA_BOARD, 'Integer'), 
    (DATA_PAIRNS, 'Integer'), 
    (DATA_PAIREW, 'Integer'), 
    (DATA_DECLARER, 'Integer'), 
    (DATA_DIRECTION, 'Text(2)'), 
    (DATA_CONTRACT, 'Text(10)'), 
    (DATA_RESULT, 'Text(10)'), 
    (DATA_LEADCARD, 'Text(10)'), 
    (DATA_REMARKS, 'Text(255)'), 
    (DATA_DATE, 'Date'), 
    #(DATA_TIME, 'Date'),       # Python can't parse Time exception
    #(DATA_PROCESSED0, 'BIT'), 
    #(DATA_PROCESSED1, 'BIT'), 
    #(DATA_PROCESSED2, 'BIT'), 
    #(DATA_PROCESSED3, 'BIT'), 
    (DATA_ERASED, 'BIT'), 
]


# Player Numbers
DBTABLE_PLAYERNUMBERS = "PlayerNumbers"
PLAYERNUMBERS_SECTION = "Section"
PLAYERNUMBERS_TABLE = "Table"
PLAYERNUMBERS_DIRECTION = "Direction"
PLAYERNUMBERS_NUMBER = "Number"
PLAYERNUMBERS_COLS = [
    (PLAYERNUMBERS_SECTION, 'Integer'),
    (PLAYERNUMBERS_TABLE, 'Integer'),
    (PLAYERNUMBERS_DIRECTION, 'Text(2)'),
    (PLAYERNUMBERS_NUMBER, 'Text(16)'),
]


# Bidding Data
DBTABLE_BIDDINGDATA = "BiddingData"
BIDDINGDATA_ID = "ID"
BIDDINGDATA_SECTION = "Section"
BIDDINGDATA_TABLE = "Table"
BIDDINGDATA_ROUND = "Round"
BIDDINGDATA_BOARD = "Board"
BIDDINGDATA_COUNTER = "Counter"
BIDDINGDATA_DIRECTION = "Direction"
BIDDINGDATA_BID = "Bid"
BIDDINGDATA_DATE = "DateLog"
BIDDINGDATA_TIME = "TimeLog"
BIDDINGDATA_ERASED = "Erased"
BIDDINGDATA_COLS = [
    (BIDDINGDATA_ID, 'AUTOINCREMENT'),
    (BIDDINGDATA_SECTION, 'Integer'),
    (BIDDINGDATA_TABLE, 'Integer'),
    (BIDDINGDATA_ROUND, 'Integer'),
    (BIDDINGDATA_BOARD, 'Integer'),
    (BIDDINGDATA_COUNTER, 'Integer'),
    (BIDDINGDATA_DIRECTION, 'Text(2)'),
    (BIDDINGDATA_BID, 'Text(10)'),
    (BIDDINGDATA_DATE, 'Date'),
    (BIDDINGDATA_TIME, 'Date'),
    (BIDDINGDATA_ERASED, 'BIT'),
]


# Player Data
DBTABLE_PLAYDATA = "PlayData"
PLAYDATA_ID = "ID"
PLAYDATA_SECTION = "Section"
PLAYDATA_TABLE = "Table"
PLAYDATA_ROUND = "Round"
PLAYDATA_BOARD = "Board"
PLAYDATA_COUNTER = "Counter"
PLAYDATA_DIRECTION = "Direction"
PLAYDATA_CARD = "Card"
PLAYDATA_DATE = "DateLog"
PLAYDATA_TIME = "TimeLog"
PLAYDATA_ERASED = "Erased"
PLAYDATA_COLS = [
    (PLAYDATA_ID, 'Integer'),
    (PLAYDATA_SECTION, 'Integer'),
    (PLAYDATA_TABLE, 'Integer'),
    (PLAYDATA_ROUND, 'Integer'),
    (PLAYDATA_BOARD, 'Integer'),
    (PLAYDATA_COUNTER, 'Integer'),
    (PLAYDATA_DIRECTION, 'Text(2)'),
    (PLAYDATA_CARD, 'Text(10)'),
    (PLAYDATA_DATE, 'Date'),
    (PLAYDATA_TIME, 'Date'),
    (PLAYDATA_ERASED, 'BIT'),
]


# Setting
DBTABLE_SETTINGS = "Settings"
SETTINGS_SHOWRESULTS = "ShowResults"
SETTINGS_SHOWOWNRESULT = "ShowOwnResult"
SETTINGS_REPEATRESULTS = "RepeatResults"
SETTINGS_MAXIMUMRESULTS = "MaximumResults"
SETTINGS_SHOWPERCENTAGE = "ShowPercentage"
SETTINGS_GROUPSECTIONS = "GroupSections"
SETTINGS_SCOREPOINTS = "ScorePoints"
SETTINGS_ENTERRESULTSMETHOD = "EnterResultsMethod"
SETTINGS_SHOWPAIRNUMBERS = "ShowPairNumbers"
SETTINGS_INTERMEDIATERESULTS = "IntermediateResults"
SETTINGS_AUTOPOWEROFFTIME = "AutopoweroffTime"
SETTINGS_VERIFICATIONTIME = "VerificationTime"
SETTINGS_SHOWCONTRACT = "ShowContract"
SETTINGS_LEADCARD = "LeadCard"
SETTINGS_MEMBERNUMBERS = "MemberNumbers"
SETTINGS_MEMBERNUMBERSNOBLANKENTRY = "MemberNumbersNoBlankEntry"
SETTINGS_BOARDORDERVERIFICATION = "BoardOrderVerification"
SETTINGS_HANDRECORDVALIDATION = "HandRecordValidation"
SETTINGS_AUTOSHUTDOWNBPC="AutoShutDownBPC"
SETTINGS_COLS = [
    (SETTINGS_SHOWRESULTS, 'BIT'),
    (SETTINGS_SHOWOWNRESULT, 'BIT'),
    (SETTINGS_REPEATRESULTS, 'BIT'),
    (SETTINGS_MAXIMUMRESULTS, 'Integer'),
    (SETTINGS_SHOWPERCENTAGE, 'BIT'),
    (SETTINGS_GROUPSECTIONS, 'BIT'),
    (SETTINGS_SCOREPOINTS, 'Integer'),
    (SETTINGS_ENTERRESULTSMETHOD, 'Integer'),
    (SETTINGS_SHOWPAIRNUMBERS, 'BIT'),
    (SETTINGS_INTERMEDIATERESULTS, 'BIT'),
    (SETTINGS_AUTOPOWEROFFTIME, 'Integer'),
    (SETTINGS_VERIFICATIONTIME, 'Integer'),
    (SETTINGS_SHOWCONTRACT, 'Integer'),
    (SETTINGS_LEADCARD, 'BIT'),
    (SETTINGS_MEMBERNUMBERS, 'BIT'),
    (SETTINGS_MEMBERNUMBERSNOBLANKENTRY, 'BIT'),
    (SETTINGS_BOARDORDERVERIFICATION, 'BIT'),
    (SETTINGS_HANDRECORDVALIDATION, 'BIT'),
    (SETTINGS_AUTOSHUTDOWNBPC, 'BIT'),
]


# Property define
PROPERTY_MOVEMENT = "MovementProperty"
PROPERTY_DBVERSION = "DBVersionProperty"
PROPERTY_CREATEDBY = "CreatedByProgramProperty"


class ClientsTable(DBTable):
    def __init__(self):
        super(ClientsTable, self).__init__(DBTABLE_CLIENTS, CLIENTS_COLS)
class SectionTable(DBTable):
    def __init__(self):
        super(SectionTable, self).__init__(DBTABLE_SECTION, SECTION_COLS)
class TablesTable(DBTable):
    def __init__(self):
        super(TablesTable, self).__init__(DBTABLE_TABLES, TABLES_COLS)
class RoundDataTable(DBTable):
    def __init__(self):
        super(RoundDataTable, self).__init__(DBTABLE_ROUNDDATA, ROUNDDATA_COLS)
class ReceivedDataTable(DBTable):
    def __init__(self):
        super(ReceivedDataTable, self).__init__(DBTABLE_RECEIVEDDATA, RECEIVEDDATA_COLS)
class IntermediateDataTable(DBTable):
    def __init__(self):
        super(IntermediateDataTable, self).__init__(DBTABLE_INTERMEDIATEDATA, INTERMEDIATEDATA_COLS)
class PlayerNumbersTable(DBTable):
    def __init__(self):
        super(PlayerNumbersTable, self).__init__(DBTABLE_PLAYERNUMBERS, PLAYERNUMBERS_COLS)
class BiddingDataTable(DBTable):
    def __init__(self):
        super(BiddingDataTable, self).__init__(DBTABLE_BIDDINGDATA, BIDDINGDATA_COLS)
class PlayerDataTable(DBTable):
    def __init__(self):
        super(PlayerDataTable, self).__init__(DBTABLE_PLAYDATA, PLAYERNUMBERS_COLS)
class SettingsTable(DBTable):
    def __init__(self):
        super(SettingsTable, self).__init__(DBTABLE_SETTINGS, SETTINGS_COLS)

BWS_DBTABLES = [
    ClientsTable(),
    SectionTable(),
    TablesTable(),
    RoundDataTable(),
    ReceivedDataTable(),
    IntermediateDataTable(),
    PlayerNumbersTable(),
    BiddingDataTable(),
    PlayerDataTable(),
    SettingsTable()
]