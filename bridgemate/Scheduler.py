import unittest


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
        self.match = meta_data["match"]

    def schedule_round(self, round_number):
        pass

    def get_match_by_round(self, round_number):
        return self.match[round_number-1]

    def get_metadata(self):
        return {"match":self.match}

# class RoundRobinScheduler(BaseScheduler):
#     def __init__(self, meta_data):
#         self.meta_data = meta_data
#         self.team_count = meta_data['team_count']

#     def schedule_round(self, round_number):
#         pass

#     def get_match_by_round(self, current_round):
#         # return (tableid, ns_team, ew_team) array
#         raise NotImplementedError

#     def get_metadata(self):
#         return self.meta_data

#     def schedule_next_round(self):
#         self.current_round = self.current_round + 1

#         # Init
#         if self._round_robin_arry is None:
#             self._round_robin_arry = range(1, self.team_count + 1)
#         # Round robin rotate
#         else:
#             next_array = [ self._round_robin_arry[0] ] + [ self._round_robin_arry[-1] ] + self._round_robin_arry[1:-1]
#             self._round_robin_arry = next_array


class SwissScheduler(BaseScheduler):
    def __init__(self, meta_data):
        self.match = meta_data["match"]
        self.score = meta_data["score"]

    def schedule_round(self, round_number):
        raise NotImplementedError

    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team) array
        return self.match[current_round-1]

    def get_metadata(self):
        return {
            "match": self.match,
            "score": self.score,
        }


# Unittest


class CustomSchedulerTest(unittest.TestCase):
    def test_custom_format(self):
        print "test_custom_format"

        meta_data = {
            "team_count"
        }

class SwissSchedulerTest(unittest.TestCase):
    def test_16team_swiss_5round(self):
        print "test_16team_swiss_5round"
        team_count = 16
        round_count = 5
        meta_data = {
            "match": [],
            "score": [ (x+1,0) for x in xrange(team_count) ]
        }
        swiss = SwissScheduler(meta_data)

        for r in xrange(round_count):
            current_round = r+1
            print "Schedule round: %d" % current_round 
            swiss.schedule_round(current_round)
            match = swiss.get_match_by_round(current_round)

            for table, ns_team, ew_team in match:
                print "Table %d: NS=%d EW=%d" % (table, ns_team, ew_team)


if __name__ == "__main__":
    unittest.main()


