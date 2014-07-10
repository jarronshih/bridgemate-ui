import config

def get_computer_name():
    import os
    return os.getenv('COMPUTERNAME')

def get_project_folder(project_name):
    import os
    return os.path.join(config.PROJECT_FOLDER, project_name)

def get_project_file_path(project_name, file_name):
    import os
    return os.path.join( get_project_folder(project_name) , file_name)

def ask_user_input(question, default=None):
    ret = raw_input(question) or default
    return ret

def str_to_num(s):
    try:
        return float(int(s))
    except Exception, e:
        pass

    return None