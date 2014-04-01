import os
import time

from utils.Logger import get_logger, init_logger
from utils.Tools import get_project_folder, get_project_file_path
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
        self.scheduler = scheduler_class()

    def run(self):
        logger.info("Start run")
        self.run_one_round()

    def run_one_round(self):
        for r in xrange(self.config.current_round, self.config.total_round+1):
            logger.info("== %d Round == " % r)
            self.init_bws_file()
            self.sync_with_bcs()
            self.save_config()

    def init_bws_file(self):
        logger.info("Init .bws file")
        current_round = self.config.current_round
        bws_path = get_project_file_path(self.project_name, str(current_round) + '.bws')
        bws = BWS(bws_path)
        bws.fill_section(current_round=current_round,
                        board_start=1,
                        board_end=8,
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

            logger.info("Get Data")
            for data in data_ary:

                logger.info("Data: %s" % str(data))
            time.sleep(5)
        
        bcs.close()
        logger.info("Done sync")

    def save_config(self):
        logger.info("Write config back to json format")
        self.config.write()


# Use these function to open project
def start_project(project_name):
    project_folder = get_project_folder(project_name)
    if os.path.exists(project_folder):
        return open_project(project_name)
    else:
        return create_project(project_name)

def create_project(project_name):
    project_folder = get_project_folder(project_name)

    # remove exist project
    if os.path.exists(project_folder):
        import shutil
        shutil.rmtree(project_folder)
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
    

