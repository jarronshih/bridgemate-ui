from bridgemate.Bridgemate2Manager import open_project, create_project

def test_run_custom():
    # Run Project in
    project = create_project('test_custom')
    project.setup_config(
        tm_name="TM", 
        team_count=2, 
        board_count=2, 
        scheduler_type="CustomScheduler", 
        scheduler_metadata{
            "match":
            [
                [ (1, 1, 2), (2, 2, 1) ]  # Round 1 (table_id, ns_team, ew_team)
            ],
            "round_count": 1,
            "current_round": 0
        }, 
        start_board_number=1, 
        section_id=1, 
        section_letter='A'
    )
    project.run_one_round()

test_run_custom()