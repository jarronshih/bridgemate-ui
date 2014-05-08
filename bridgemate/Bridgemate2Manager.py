import os
import time

from utils.Logger import get_logger, init_logger
from utils.Tools import get_project_folder, get_project_file_path
from utils.config import *
from bridgemate.Scheduler import *
from bridgemate.BWS import BWS
from bridgemate.BCSManager import BCSManager
from bridgemate.ProjectConfig import ProjectConfig

logger = get_logger()


# Project Handler
class BM2Manager(object):
    def __init__(self, project_name):
        global logger 
        logger = get_logger()
        logger.info("Init BM2Manager")
        self.config = ProjectConfig(project_name)
        self.project_name = project_name
        scheduler_class = globals()[self.config.scheduler_type]
        self.scheduler = scheduler_class(self.config.scheduler_metadata)

    def run(self):
        logger.info("Start full run")
        for r in xrange(self.config.current_round, self.config.total_round+1):
            self.run_one_round()

    def setup_config(self, tm_name, team_count, scheduler_type, scheduler_metadata, total_round, board_count, start_board_number=1, current_round=1, section_id=DEFAULT_SECTION_ID, section_letter=DEFAULT_SECTION_LETTER):
        self.config.setup(tm_name, team_count, scheduler_type, scheduler_metadata, total_round, current_round, board_count, start_board_number, section_id, section_letter)
        scheduler_class = globals()[self.config.scheduler_type]
        self.scheduler = scheduler_class(self.config.scheduler_metadata)

    def run_one_round(self):
        logger.info("== %d Round == " % self.config.current_round)
        self.init_bws_file()
        self.sync_with_bcs()
        self.end_and_save_config()

    def init_bws_file(self):
        logger.info("Init .bws file")
        current_round = self.config.current_round
        bws_path = get_project_file_path(self.project_name, str(current_round) + '.bws')
        bws = BWS(bws_path)
        bws.fill_section(current_round=current_round,
                        board_start=self.config.start_board_number,
                        board_end=self.config.start_board_number+self.config.board_count - 1,
                        section_id=self.config.section_id,
                        section_letter=self.config.section_letter,
                        matches=self.scheduler.get_match_by_round(current_round))

    def sync_with_bcs(self):
        logger.info("Sync with Bridgemate Control Software")
        current_round = self.config.current_round
        bws_path = get_project_file_path(self.project_name, str(current_round) + '.bws')
        
        bcs = BCSManager(bws_path)
        bcs.open()

        # Sync data
        while bcs.is_alive():
            bws = BWS(bws_path)
            data_ary = bws.get_recevied_date()

            # TODO: data process
            logger.info("Get Data")
            for data in data_ary:
                logger.info("Data: %s" % str(data))

            # collect all data
            if data_ary and len(data_ary) >= self.config.team_count * self.config.board_count:
                break

            time.sleep(5)
        
        bcs.close()
        logger.info("Done sync")

    def end_and_save_config(self):
        logger.info("Write config back to json format")
        self.config.start_board_number = self.config.start_board_number + self.config.board_count
        self.config.current_round = self.config.current_round + 1
        self.config.scheduler_metadata = self.scheduler.get_metadata()
        self.config.write()


# Use these function to open project
def create_project(project_name):
    project_folder = get_project_folder(project_name)

    if os.path.exists(project_folder):
        return None
        #import shutil
        #shutil.rmtree(project_folder)
    os.makedirs(project_folder)

    global logger
    logger = init_logger(project_name)
    
    # create project
    logger.info('Create Project: ' + project_name)
    return BM2Manager(project_name)

    

def open_project(project_name):
    project_folder = get_project_folder(project_name)

    if not os.path.exists(project_folder):
        raise ValueError

    global logger
    logger = init_logger(project_name)

    # open project
    logger.info('Open Project: ' + project_name)
    return BM2Manager(project_name)
    

