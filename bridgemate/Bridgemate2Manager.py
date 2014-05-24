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


# 1. init_bws_file
# 2. start_bcs_collect_data
# 3. get_bcs_data, check get all or stop
# 4. end_and_save_config

# Project Handler
class BM2Manager(object):
    def __init__(self, project_name):
        global logger 
        logger = get_logger()
        logger.info("Init BM2Manager")
        self.config = ProjectConfig(project_name)
        self.project_name = project_name
        self.scheduler = self.config.get_scheduler()
        self.bcs = None

    def setup_config(self, tm_name, team_count, board_count, scheduler_type, scheduler_metadata, start_board_number, section_id, section_letter):
        self.config.setup(tm_name, team_count, board_count, scheduler_type, scheduler_metadata, start_board_number, section_id, section_letter)
        self.scheduler = self.config.get_scheduler()

    def init_bws_file(self):
        logger.info("Init .bws file")
        self.scheduler.schedule_next_round()

        current_round = self.scheduler.get_current_round()
        bws_path = get_project_file_path(self.project_name, str(current_round) + '.bws')
        bws = BWS(bws_path)
        bws.fill_section(current_round=current_round,
                        board_start=self.config.start_board_number,
                        board_end=self.config.start_board_number+self.config.board_count - 1,
                        section_id=self.config.section_id,
                        section_letter=self.config.section_letter,
                        matches=self.scheduler.get_match_by_round(current_round))

    def start_bcs_collect_data(self):
        logger.info("Sync with Bridgemate Control Software")
        current_round = self.scheduler.get_current_round()
        bws_path = get_project_file_path(self.project_name, str(current_round) + '.bws')
        
        self.bcs = BCSManager(bws_path)
        self.bcs.open()

    def get_bcs_data(self):
        # Sync data
        if self.is_bcs_alive():
            bws = BWS(bws_path)
            data_ary = bws.get_recevied_date()
            logger.info("Get Data")
            for data in data_ary:
                logger.info("Data: %s" % str(data))

            return data_ary
        else:
            return None


    def is_bcs_alive(self):
        return self.bcs.is_alive()

    def end_and_save_config(self):
        bcs.close()
        logger.info("Write config back to json format")
        self.config.start_board_number = self.config.start_board_number + self.config.board_count
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
    

