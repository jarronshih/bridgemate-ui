import os
import json
from utils.config import *
from utils.Tools import get_project_folder, get_project_file_path
from bridgemate.Scheduler import *

class ProjectConfig(object):
    def __init__(self, project_name):
        self.project_name = project_name
        self.config_path = get_project_file_path(self.project_name, 'config.json')

        if os.path.exists(self.config_path):
            self.read()
        else:
            self.setup('TM', 0, 8, "CustomScheduler", {"match":[], "round_count":0, "current_round":0}, 1, 1, 'A')
        

    def setup(self, tm_name, team_count, board_count, scheduler_type, scheduler_metadata, start_board_number, section_id, section_letter):
        self.tm_name = tm_name
        self.team_count = team_count
        self.board_count = board_count

        self.scheduler_type = scheduler_type
        self.scheduler_metadata = scheduler_metadata

        self.start_board_number = start_board_number

        self.section_id = section_id
        self.section_letter = section_letter

        self.write()
        
    def dump(self):
        return json.dumps(self.__dict__, indent=4)

    def load(self, json_content):
        self.__dict__ = json.loads(json_content)
        
    def write(self):
        json_content = self.dump()

        f = open(self.config_path, 'w')
        f.write(json_content)
        f.close()

    def read(self):
        # load config.json to config
        f = open(self.config_path)
        json_content = f.read()
        f.close()

        self.load(json_content)

    def get_scheduler(self):
        scheduler_class = globals()[self.scheduler_type]
        scheduler = scheduler_class(self.scheduler_metadata)
        return scheduler





        