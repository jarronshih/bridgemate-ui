import os
import json
from utils.Tools import get_project_folder, get_project_file_path

class ProjectConfig(object):
    def __init__(self, project_name):
        self.project_name = project_name
        self.config_path = get_project_file_path(self.project_name, 'config.json')

        if os.path.exists(self.config_path):
            self.load()
        else:
            self.init()
        
    def init(self):
        # config content
        self.tm_name = 'TM'
        self.team_count = 2
        self.scheduler_type = "CustomScheduler"
        self.total_round = 1
        self.current_round = 1

        self.write()

        
    def write(self):
        json_content = json.dumps(self.__dict__, indent=4)

        f = open(self.config_path, 'w')
        f.write(json_content)
        f.close()

    def load(self):
        # load config.json to config
        f = open(self.config_path)
        json_content = f.read()
        f.close()

        self.__dict__ = json.loads(json_content)


        