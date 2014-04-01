from bridgemate.Bridgemate2Manager import open_project, create_project, start_project
from utils.Logger import init_logger, get_logger


def help():
    ret = 'Help menu:\n'
    ret += '\tcreate <PROJECT_NAME>\n'
    ret += '\topen <PROJECT_NAME>\n'
    ret += '\t# deploy <PROJECT_NAME>\n'
    return ret


if __name__ == '__main__':
    import sys

    # open project
    if len(sys.argv) == 3 and sys.argv[1] == 'open':
        open_project(sys.argv[2])
    # create project
    elif len(sys.argv) == 3 and sys.argv[1] == 'create' :
        create_project(sys.argv[2])
    # help menu
    else:
        print help()

        # Test Code
        #start_project('test').run()
        project = create_project('test')
        project.setup_config(   tm_name='TM', 
                                team_count=2, 
                                scheduler_type="CustomScheduler", 
                                total_round=1, 
                                board_count=2
                                )
        project.run()
        # open_project('test')

