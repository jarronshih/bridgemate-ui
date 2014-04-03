from bridgemate.Bridgemate2Manager import open_project, create_project, start_project

def test_run_custom():
    # Run Project in
    project = create_project('test_custom')
    project.setup_config(   tm_name='TM', 
                            team_count=2, 
                            scheduler_type="CustomScheduler",
                            scheduler_metadata=
                            [
                                [ (1, 1, 2), (2, 2, 1) ]  # Round 1 (table_id, ns_team, ew_team)
                            ],
                            total_round=1, 
                            board_count=2
                            )
    project.run()


def test_run_roundrobin():
    project = create_project('test_roundrobin')
    project.setup_config(   tm_name='Round', 
                            team_count=4, 
                            scheduler_type="RoundRobinScheduler", 
                            scheduler_metadata=
                            {
                                team_count = 4
                            }
                            total_round=4, 
                            board_count=3
                            )
    project.run()

test_run_custom()