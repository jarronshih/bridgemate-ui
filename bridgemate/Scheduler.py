import unittest
from operator import itemgetter, attrgetter  
import random

class BaseScheduler(object):
    def __init__(self, meta_data):
        raise NotImplementedError

    def schedule_next_round(self):
        raise NotImplementedError

    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team) array
        raise NotImplementedError

    def get_metadata(self):
        raise NotImplementedError

    def is_next_round_available(self):
        raise NotImplementedError

    def get_current_round(self):
        raise NotImplementedError


    # def get_seat_by_round_table(self, round_number, table_id):
    #     # retrun (ns_team, ew_team)
    #     raise NotImplementedError

class CustomScheduler(BaseScheduler):
    def __init__(self, meta_data):
        self.match = meta_data["match"]
        self.round_count = meta_data["round_count"]
        self.current_round = meta_data["current_round"]

    def schedule_next_round(self):
        if not self.is_next_round_available():
            raise
        else:
            self.current_round = self.current_round + 1

    def get_match_by_round(self, round_number=None):
        if round_number is None:
            round_number = self.current_round
        return self.match[round_number-1]

    def get_metadata(self):
        return {
            "match": self.match,
            "round_count": self.round_count,
            "current_round": self.current_round
        }

    def is_next_round_available(self):
        return self.round_count > self.current_round 

    def get_current_round(self):
        return self.current_round


class RoundRobinScheduler(BaseScheduler):
    def __init__(self, meta_data):
        self.match = meta_data["match"]
        self.score = meta_data["score"]
        self.team_count = meta_data['team_count']
        if "round_score" in meta_data.keys()    :
            self.round_score = meta_data["round_score"]
        else:
            self.round_score = []
        self.current_round = meta_data["current_round"]
        #self.matchup_table = meta_data["matchup_table"]

        if self.team_count == 10:
            match1 = [[1, 2, 1], [2, 1, 2], [3, 4, 3], [4, 3, 4], [5, 6, 5], [6, 5, 6], [7, 8, 7], [8, 7, 8], [9, 10, 9], [10, 9, 10]]
            match2 = [[1, 3, 1], [2, 1, 3], [3, 5, 2], [4, 2, 5], [5, 6, 4], [6, 4, 6], [7, 9, 7], [8, 7, 9], [9, 10, 8], [10, 8, 10]]
            match3 = [[1, 4, 1], [2, 1, 4], [3, 6, 2], [4, 2, 6], [5, 8, 3], [6, 3, 8], [7, 9, 5], [8, 5, 9], [9, 10, 7], [10, 7, 10]]
            match4 = [[1, 5, 1], [2, 1, 5], [3, 7, 2], [4, 2, 7], [5, 9, 3], [6, 3, 9], [7, 8, 4], [8, 4, 8], [9, 10, 6], [10, 6, 10]]
            match5 = [[1, 6, 1], [2, 1, 6], [3, 8, 2], [4, 2, 8], [5, 7, 3], [6, 3, 7], [7, 9, 4], [8, 4, 9], [9, 10, 5], [10, 5, 10]]
            match6 = [[1, 7, 1], [2, 1, 7], [3, 9, 2], [4, 2, 9], [5, 6, 3], [6, 3, 6], [7, 8, 5], [8, 5, 8], [9, 10, 4], [10, 4, 10]]
            match7 = [[1, 8, 1], [2, 1, 8], [3, 4, 2], [4, 2, 4], [5, 7, 5], [6, 5, 7], [7, 9, 6], [8, 6, 9], [9, 10, 3], [10, 3, 10]]
            match8 = [[1, 9, 1], [2, 1, 9], [3, 5, 3], [4, 3, 5], [5, 7, 4], [6, 4, 7], [7, 8, 6], [8, 6, 8], [9, 10, 2], [10, 2, 10]]
            match9 = [[1, 10, 1], [2, 1, 10], [3, 3, 2], [4, 2, 3], [5, 5, 4], [6, 4, 5], [7, 7, 6], [8, 6, 7], [9, 9, 8], [10, 8, 9]]
            self.match.append(match1)
            self.match.append(match2)
            self.match.append(match3)
            self.match.append(match4)
            self.match.append(match5)
            self.match.append(match6)
            self.match.append(match7)
            self.match.append(match8)
            self.match.append(match9)
        elif self.team_count == 12:
            match1  = [[1, 2, 1], [2, 1, 2], [3, 4, 3], [4, 3, 4], [5, 6, 5], [6, 5, 6], [7, 8, 7], [8, 7, 8], [9, 10, 9], [10, 9, 10], [11, 12, 11], [12, 11, 12]]
            match2  = [[1, 3, 1], [2, 1, 3], [3, 11, 2], [4, 2, 11], [5, 7, 4], [6, 4, 7], [7, 9, 5], [8, 5, 9], [9, 8, 6], [10, 6, 8], [11, 12, 10], [12, 10, 12]]
            match3  = [[1, 4, 1], [2, 1, 4], [3, 6, 2], [4, 2, 6], [5, 5, 3], [6, 3, 5], [7, 11, 7], [8, 7, 11], [9, 10, 8], [10, 8, 10], [11, 12, 9], [12, 9, 12]]
            match4  = [[1, 5, 1], [2, 1, 5], [3, 9, 2], [4, 2, 9], [5, 6, 3], [6, 3, 6], [7, 11, 4], [8, 4, 11], [9, 10, 7], [10, 7, 10], [11, 12, 8], [12, 8, 12]]
            match5  = [[1, 6, 1], [2, 1, 6], [3, 8, 2], [4, 2, 8], [5, 9, 3], [6, 3, 9], [7, 10, 4], [8, 4, 10], [9, 11, 5], [10, 5, 11], [11, 12, 7], [12, 7, 12]]
            match6  = [[1, 7, 1], [2, 1, 7], [3, 4, 2], [4, 2, 4], [5, 8, 3], [6, 3, 8], [7, 10, 5], [8, 5, 10], [9, 11, 9], [10, 9, 11], [11, 12, 6], [12, 6, 12]]
            match7  = [[1, 8, 1], [2, 1, 8], [3, 7, 2], [4, 2, 7], [5, 11, 3], [6, 3, 11], [7, 9, 4], [8, 4, 9], [9, 10, 6], [10, 6, 10], [11, 12, 5], [12, 5, 12]]
            match8  = [[1, 9, 1], [2, 1, 9], [3, 10, 2], [4, 2, 10], [5, 7, 3], [6, 3, 7], [7, 8, 5], [8, 5, 8], [9, 11, 6], [10, 6, 11], [11, 12, 4], [12, 4, 12]]
            match9  = [[1, 10, 1], [2, 1, 10], [3, 5, 2], [4, 2, 5], [5, 6, 4], [6, 4, 6], [7, 9, 7], [8, 7, 9], [9, 11, 8], [10, 8, 11], [11, 12, 3], [12, 3, 12]]
            match10 = [[1, 11, 1], [2, 1, 11], [3, 10, 3], [4, 3, 10], [5, 8, 4], [6, 4, 8], [7, 7, 5], [8, 5, 7], [9, 9, 6], [10, 6, 9], [11, 12, 2], [12, 2, 12]]
            match11 = [[1, 12, 1], [2, 1, 12], [3, 3, 2], [4, 2, 3], [5, 5, 4], [6, 4, 5], [7, 7, 6], [8, 6, 7], [9, 9, 8], [10, 8, 9], [11, 11, 10], [12, 10, 11]]
            self.match.append(match1)
            self.match.append(match2)
            self.match.append(match3)
            self.match.append(match4)
            self.match.append(match5)
            self.match.append(match6)
            self.match.append(match7)
            self.match.append(match8)
            self.match.append(match9)
            self.match.append(match10)
            self.match.append(match11)
        else:
            raise NotImplementedError

    def schedule_round(self, round_number):
        pass

    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team) array
        return self.match[current_round-1]

    def schedule_next_round(self):
        self.current_round = self.current_round + 1

        # Init
        #if self._round_robin_arry is None:
        #    self._round_robin_arry = range(1, self.team_count + 1)
        # Round robin rotate
        #else:
        #    next_array = [ self._round_robin_arry[0] ] + [ self._round_robin_arry[-1] ] + self._round_robin_arry[1:-1]
        #    self._round_robin_arry = next_array
    
    def get_metadata(self):
        return {
            "match": self.match,
            "score": self.score,
            "round_score": self.round_score,
            #"matchup_table": self.matchup_table,
            "team_count": self.team_count,
            "current_round": self.current_round
        }

    def is_next_round_available(self):
        return self.current_round < self.team_count-1

    def get_current_round(self):
        return self.current_round

    def set_score(self, new_score):
        self.score = new_score

    def set_match(self, new_match):
        self.match = new_match

    def append_score(self, score_by_round):
        self.round_score.append(score_by_round)

    def get_scores(self):
        return self.score

    def get_round_scores(self):
        return self.round_score

class SwissScheduler(BaseScheduler):
    def __init__(self, meta_data):
        self.match = meta_data["match"]
        self.score = meta_data["score"]
        if "round_score" in meta_data.keys():
            self.round_score = meta_data["round_score"]
        else:
            self.round_score = []
        self.matchup_table = meta_data["matchup_table"]
        self.round_count = meta_data["round_count"]
        self.current_round = meta_data["current_round"]

    def generate_match(self, team_rank, total_team, round_number):
        #print (self.matchup_table)
        t1 = self.sorted_score[team_rank-1][0]
        print ("generating matchup for team %d, which is at rank %d" % (t1, team_rank))

        if self.matched[t1-1] == False:
            found = False
            for tmp_t in range(team_rank, total_team):
                if self.matched[self.sorted_score[tmp_t][0]-1] == False:
                    print ("find team %d does not have a matchup" % (tmp_t))
                    found = True
                    break

            if found == False:  #all to other teams have a matchup => must be a bye or a wrong matchup result
                if self.matchup_table[t1-1][total_team] == 0:
                    print ("bye for team %d" % (t1))
                    self.matchup_table[t1-1][total_team] = self.matchup_table[total_team][t1-1] = round_number
                    #self.matched[t1] = True
                    return 1
                else:
                    print ("team %d already has a bye, conflict!!" % (t1))
                    return 0
            else:
                if team_rank < total_team:
                    resolved = 0
                    for tmp_t in range(team_rank, total_team):
                        t2 = self.sorted_score[tmp_t][0]
                        if self.matched[t2-1] == False and self.matchup_table[t1-1][t2-1] == 0:   
                            # found a candidate matchup between t1 and t2, set matched flag and matchup_table
                            self.matched[t1-1] = self.matched[t2-1] = True
                            self.matchup_table[t1-1][t2-1] = self.matchup_table[t2-1][t1-1] = round_number
                            resolved = self.generate_match(team_rank+1, total_team, round_number)
                            if resolved == 0:
                                print ("select %d vs. %d as a candidate matchup but resulted in conflict" % (t1, t2))
                                self.matched[t1-1] = self.matched[t2-1] = False
                                self.matchup_table[t1-1][t2-1] = self.matchup_table[t2-1][t1-1] = 0
                            else:
                                print ("select %d vs. %d as a candidate matchup and passed" % (t1, t2))
                                break
                    return resolved            
                elif team_rank == total_team:
                    if self.matchup_table[t1-1][total_team] == 0:
                        print ("bye for team %d" % (t1))
                        self.matchup_table[t1-1][total_team] = self.matchup_table[total_team][t1-1] = round_number
                        #self.matched[t1] = True
                        return 1
                    else:
                        print ("team %d already has a bye, conflict!!" % (t1))
                        return 0
        else:   # already have a matchup => finish schedule or test the next team
            print ("team %d already has a matchup" % (t1))
            if team_rank == total_team:
                return 1
            else:
                return self.generate_match(team_rank+1, total_team, round_number)

    def schedule_round(self, round_number):
        self.sorted_score = sorted(self.score, reverse=True, key=itemgetter(1))
        print(self.sorted_score)
        
        self.matched = [False for i in range(len(self.sorted_score))]
        self.printed = [False for i in range(len(self.sorted_score))]

        result = self.generate_match(1, len(self.sorted_score), round_number)
        if result == 0:
            print ("cannot find a viable swiss matchup!!")
            raise SwissFailError

        current_swiss_matchup = []
        table_no = 1
        for i in range(len(self.sorted_score)):
            t1 = self.sorted_score[i][0]
            if self.printed[t1-1] == True:
                continue
            for j in range(len(self.sorted_score)):
                if self.matchup_table[t1-1][j] == round_number:
                    print ("team %d and %d at table %d" % (t1, j+1, table_no))
                    t_open = (table_no * 2 - 1, max(t1, j+1), min(t1, j+1))
                    t_close = (table_no * 2, min(t1, j+1), max(t1, j+1))
                    current_swiss_matchup.append(t_open)
                    current_swiss_matchup.append(t_close)
                    self.printed[t1-1] = self.printed[j] = True;
                    table_no = table_no + 1
                    break;
        self.match.append(current_swiss_matchup)

        # raise NotImplementedError

    def schedule_next_round(self):
        if not self.is_next_round_available():
            raise
        else:
            self.current_round = self.current_round + 1
        self.schedule_round(self.current_round)
        
    def get_match_by_round(self, current_round):
        # return (tableid, ns_team, ew_team) array
        return self.match[current_round-1]

    def get_match(self):
        return self.match

    def get_metadata(self):
        return {
            "match": self.match,
            "score": self.score,
            "round_score": self.round_score,
            "matchup_table": self.matchup_table,
            "round_count": self.round_count,
            "current_round": self.current_round
        }

    def is_next_round_available(self):
        return self.current_round < self.round_count

    def get_current_round(self):
        return self.current_round

    def set_score(self, new_score):
        self.score = new_score

    def set_match(self, new_match):
        self.match = new_match

    def append_score(self, score_by_round):
        self.round_score.append(score_by_round)

    def get_scores(self):
        return self.score

    def get_round_scores(self):
        return self.round_score
                    




# Unittest


class CustomSchedulerTest(unittest.TestCase):
    def test_custom_format(self):
        print ("test_custom_format")

        meta_data = {
            "team_count"
        }

class SwissSchedulerTest(unittest.TestCase):
    def test_16team_swiss_5round(self):
        print ("test_16team_swiss_5round")
        team_count = 17
        round_count = 5
        meta_data = {
            "match": [],
            "score": [ [x+1,0] for x in range(team_count) ],
            "matchup_table": [ [0 for i in range(team_count+1)] for j in range(team_count+1) ] 
        }
        swiss = SwissScheduler(meta_data)

        vp = [i for i in range(team_count)]

        for r in range(round_count):
            current_round = r+1
            print ("Schedule round: %d" % current_round )
            swiss.schedule_round(current_round)
            match = swiss.get_match_by_round(current_round)

            for table, ns_team, ew_team in match:
                print ("Table %d: NS=%d EW=%d" % (table, ns_team, ew_team))

            meta_data = swiss.get_metadata()
            score = meta_data["score"]
            random.shuffle(vp)
            for i in range(team_count):
                score[i][1] = score[i][1] + vp[i]
            swiss.set_score(score)


if __name__ == "__main__":
    unittest.main()


