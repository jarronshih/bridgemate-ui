
class BaseScheduler(object):
    def __init__(self, meta_data):
        raise NotImplementedError

    def schedule_round(self, round_number):
        raise NotImplementedError

    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team) array
        raise NotImplementedError

    def get_metadata(self):
        raise NotImplementedError


    # def get_seat_by_round_table(self, round_number, table_id):
    #     # retrun (ns_team, ew_team)
    #     raise NotImplementedError

class CustomScheduler(BaseScheduler):
    def __init__(self, meta_data):
        self.match = meta_data

    def schedule_round(self, round_number):
        pass

    def get_match_by_round(self, round_number):
        return self.match[round_number-1]

    def get_metadata(self):
        return self.match

class RoundRobinScheduler(BaseScheduler):
    def __init__(self, meta_data):
        self.meta_data = meta_data
        self.team_count = meta_data['team_count']

    def schedule_round(self, round_number):
        pass

    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team) array
        raise NotImplementedError

    def get_metadata(self):
        return self.meta_data

#     def schedule_next_round(self):
#         self.current_round = self.current_round + 1

#         # Init
#         if self._round_robin_arry is None:
#             self._round_robin_arry = range(1, self.team_count + 1)
#         # Round robin rotate
#         else:
#             next_array = [ self._round_robin_arry[0] ] + [ self._round_robin_arry[-1] ] + self._round_robin_arry[1:-1]
#             self._round_robin_arry = next_array


# class SwissScheduler(BaseScheduler):
#     def __init__(self, team_count):
#         super(SwissSchedule, self).__init__(team_count)