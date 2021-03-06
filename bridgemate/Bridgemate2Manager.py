import os
import time

from utils.Logger import get_logger, init_logger
from utils.Tools import get_project_folder, get_project_file_path
from utils.config import *
from bridgemate.Scheduler import *
from bridgemate.BWS import BWS
from bridgemate.BCSManager import BCSManager
from bridgemate.ProjectConfig import ProjectConfig, BCSConfig

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

    def setup_config(self, tm_name, team_count, board_count, scheduler_type, scheduler_metadata, adjustment, start_board_number, end_board_number, section_id, section_letter):
        self.config.setup(tm_name, team_count, board_count, scheduler_type, scheduler_metadata, adjustment, start_board_number, end_board_number, section_id, section_letter)
        self.scheduler = self.config.get_scheduler()

    def schedule_next_round(self):
        complete_round = self.scheduler.get_current_round()
        if complete_round > 0:
            total_score = []
            for team in range(self.config.team_count):
                score = [team+1, 0.0]
                for rnd_score in self.config.scheduler_metadata["round_score"]:
                    for t, s in rnd_score:
                        if t == score[0]:
                            score[1] = score[1] + s
                total_score.append(score)
            self.scheduler.set_score(total_score)
            self.scheduler.round_score = self.config.scheduler_metadata["round_score"]
        else:
            self.scheduler.set_score(self.config.scheduler_metadata["score"])
        self.scheduler.schedule_next_round()
        print self.scheduler.get_match_by_round(self.scheduler.get_current_round())
        self.config.scheduler_metadata = self.scheduler.get_metadata()

    def init_bws_file(self):
        logger.info("Init .bws file")
        self.scheduler.set_match(self.config.scheduler_metadata["match"])
        self.config.write()
        current_round = self.scheduler.get_current_round()
        print self.scheduler.get_match_by_round(current_round)
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
            current_round = self.scheduler.get_current_round()
            bws_path = get_project_file_path(self.project_name, str(current_round) + '.bws')
            bws = BWS(bws_path)
            data_ary = bws.get_recevied_date()
            logger.info("Get Data")
            for data in data_ary:
                logger.info("Data: %s" % str(data))
            bcs_config_path = get_project_file_path(self.project_name, "round"+str(current_round) + '.json')
            bcs_config = BCSConfig(bcs_config_path)
            bcs_config.load_from_bcsdata_array(data_ary)
            bcs_config.write()
            return data_ary
        else:
            return None


    def is_bcs_alive(self):
        return self.bcs.is_alive()

    def end_and_save_config(self):
        logger.info("end and save")
        self.bcs.close()
        self.config.start_board_number = self.config.start_board_number + self.config.board_count
        self.config.scheduler_metadata = self.scheduler.get_metadata()
        self.config.write()
        logger.info("Write config back to json format")


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
    

