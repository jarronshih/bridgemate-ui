
class BaseScheduler(object):
    def __init__(self, team_count):
        raise NotImplementedError

    def schedule_round(self, round_number):
        raise NotImplementedError

    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team)
        raise NotImplementedError

    def get_seat_by_round_table(self, round_number, table_id):
        # retrun (ns_team, ew_team)
        raise NotImplementedError

class CustomScheduler(BaseScheduler):
    def __init__(self):
        self.match = [
            None,
            [ (1, 1, 2), (2, 2, 1) ]  # Round 1
        ]

    def schedule_round(self, round_number):
        pass

    def get_match_by_round(self, round_number):
        return self.match[round_number]

    def get_seat_by_round_table(self, round_number, table_id):
        return self.match[round_number][table_id-1]

# class RoundRobinScheduler(BaseScheduler):
#     def __init__(self, team_count):
#         super(RoundRobinSchedule, self).__init__(team_count)
#         self._round_robin_arry = None

#     def schedule_next_round(self):
#         self.current_round = self.current_round + 1

#         # Init
#         if self._round_robin_arry is None:
#             self._round_robin_arry = range(1, self.team_count + 1)
#         # Round robin rotate
#         else:
#             next_array = [ self._round_robin_arry[0] ] + [ self._round_robin_arry[-1] ] + self._round_robin_arry[1:-1]
#             self._round_robin_arry = next_array

#     def get_current_round_pair_by_table(self, table_id):
#         '''
#         @Returns: visit_team, home_team
#         '''
#         team1_id = table_id - 1
#         team1 = self._round_robin_arry[team1_id]
#         team2_id = self.team_count - table_id
#         team2 = self._round_robin_arry[team2_id]
#         if team1 >  team2:
#             return team2, team1
#         else:
#             return team1, team2

# class SwissScheduler(BaseScheduler):
#     def __init__(self, team_count):
#         super(SwissSchedule, self).__init__(team_count)