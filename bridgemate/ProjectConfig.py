import os
import json
from utils.config import *
from utils.Tools import get_project_folder, get_project_file_path
from bridgemate.Scheduler import *

class ConfigFile(dict):
    def __init__(self, config_path):
        if os.path.exists(config_path):
            self.read(config_path)
        else:
            self["config_path"] = config_path
            self.write()

    def dump(self):
        return json.dumps(self, indent=4)

    def load(self, json_content):
        dic = json.loads(json_content)
        for key in dic.keys():
            self[key] = dic[key]

    def write(self, config_path=None):
        json_content = self.dump()

        if config_path is None:
            config_path = self["config_path"]

        f = open(config_path, 'w')
        f.write(json_content)
        f.close()


    def read(self, config_path=None):
        if config_path is None:
            config_path = self["config_path"]
        # load config.json to config
        f = open(config_path)
        json_content = f.read()
        f.close()
        self.load(json_content)

    def __getattr__(self, attr):
        self.read()
        return self[attr]

    def __setattr__(self, attr, value):
        self.read()
        self[attr] = value
        self.write()


class ProjectConfig(ConfigFile):
    def __init__(self, project_name):
        config_path = get_project_file_path(project_name, 'config.json')
        super(ProjectConfig, self).__init__(config_path)

        # first init
        if not "project_name" in self.keys():
            self.project_name = project_name
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


    def get_scheduler(self):
        scheduler_class = globals()[self.scheduler_type]
        scheduler = scheduler_class(self.scheduler_metadata)
        return scheduler


class BCSConfig(object):
    def __init__(self, file_path):
        super(BCSConfig, self).__init__(file_path)
        if not "result_array" in self.keys():
            self.result_array = []

    def load_from_bcsdata_array(self, data_ary):
        self.result_array = data_ary

    def get_data_array(self):
        return self.result_array
        