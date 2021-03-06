import unittest
from jinja2 import Template
from operator import itemgetter
import pdfkit
import os
from bridgemate.Score import *
from utils.config import SWISS_SCORE_TEMPLATE_PATH, SEAT_MATCH_TEMPLATE_PATH, BOARD_RECORD_TEMPLATE_PATH, FINAL_SCORE_TEMPLATE_PATH, PER_TABLE_RESULT_EMPTY_PATH
def result_to_record(result_array, start_board, board_count):
    board_record_ary = []

    for board_num in range(start_board, start_board+board_count):
        board_rec = {
            "board_no": board_num,
            "board": []
        }
        for array_elt in result_array:
            if int(array_elt["Board"]) == board_num:
                ns_team = int(array_elt["PairNS"])
                ew_team = int(array_elt["PairEW"])
                table_no = int(array_elt["Table"])
                contract = array_elt["Contract"]
                declarer = array_elt["NS/EW"]
                result = array_elt["Result"]
                ns_score = compute_score(board_num, contract, declarer, result)
                board_record={
                    "table_no": table_no,
                    "ns_team": ns_team,
                    "ew_team": ew_team,
                    "contract": contract,
                    "declarer": declarer,
                    "result": result,
                    "ns_score": ns_score
                }
                board_rec["board"].append(board_record)
        sorted_board = sorted(board_rec["board"], key=itemgetter('table_no'))
        board_rec["board"] = sorted_board
        board_record_ary.append(board_rec)
    sorted_board_record_ary = sorted(board_record_ary, key=itemgetter('board_no'))
    return sorted_board_record_ary

def board_record_process(result_array, round_number, start_board, end_board, board_count, project_path):
    output_folder = project_path + "/record_output"
    if not os.path.exists(output_folder):
        #import shutil
        #shutil.rmtree(output_folder)
        os.makedirs(output_folder)    

    board_record_array = result_to_record(result_array, start_board, board_count)
    
    # gen html
    html_files = []   
    for board_record in board_record_array:        
        file_name = output_folder + "/" + str(board_record["board_no"]) + ".html"
        print file_name        
        html_files.append(file_name)
        f = open(BOARD_RECORD_TEMPLATE_PATH, "r")
        tmp_html = f.read()
        f.close()
        tmpl = Template(tmp_html)
        html = tmpl.render({"boards":board_record["board"], "round": round_number, "board_no": board_record["board_no"]})
        f = open(file_name, "w")
        f.write(html)
        f.close()        
    
    pdf_file_name = project_path + "/" + "Round " + str(round_number) + " Board Record.pdf"
    print pdf_file_name    
    html_files_to_pdf(html_files, pdf_file_name)


    # gen html
#    f = open(BOARD_RECORD_TEMPLATE_PATH, "r")
#    tmp_html = f.read()
#    f.close()
#    tmpl = Template(tmp_html)
#    html = tmpl.render({"boards":board_record_array, "round":round_number})

    # gen pdf
#    options = {
#        'page-size': 'A4',
#        'margin-top': '20mm',
#        'margin-right': '20mm',
#        'margin-bottom': '20mm',
#        'margin-left': '20mm',
#        'encoding': "UTF-8",
#        'grayscale': None,
#        'outline-depth':3,
#        # 'footer-center':'[page]',
#        'footer-line': None,
#    }
#    pdf_file_name = project_path + "/" + "Round " + str(round_number) + " Board Record.pdf"
#    print pdf_file_name
#    pdfkit.from_string(html, pdf_file_name, options=options)


def result_to_dict(result_array, team_count, start_board, board_count, round_number):
    match_count = int(team_count / 2)
    vp_table = [ [i+1, 0] for i in range(team_count)]

    overall_result = [{
        "match_no": k+1,
        "match_finished" : 0,
        "boards" : [ {
            "board_num" : i + start_board, 
            "board_played" : 0,
            "open_contract" : "",
            "close_contract" : "", 
            "open_score" : 0, 
            "close_score" : 0, 
            "team_a_score_diff" : 0, 
            "team_b_score_diff" : 0, 
            "team_a_imp" : 0, 
            "team_b_imp" : 0
        } for i in range(board_count) ],
        "team_a" : 0,
        "team_b" : 0,
        "imp_a" : 0,
        "imp_b" : 0,
        "vp_a" : 0.0,
        "vp_b" : 0.0,
        "round_number": round_number
    } for k in range(match_count)]

    for array_elt in result_array:    
        ns_team = int(array_elt["PairNS"])
        ew_team = int(array_elt["PairEW"])
        table_no = int(array_elt["Table"])
        board_no = int(array_elt["Board"])
        contract = array_elt["Contract"]
        declarer = array_elt["NS/EW"]
        result = array_elt["Result"]
        ns_score = compute_score(board_no, contract, declarer, result)
        #print ("table %d board %d: %d vs. %d, %s %s %s, NS score %d" % (table_no, board_no, ns_team, ew_team, contract, declarer, result, ns_score) )
        for match in overall_result:
            if match["match_no"] == int((table_no+1) / 2) :
                match["match_finished"] = 1
                for board in match["boards"]:
                    if board["board_num"] == board_no :# found the corresponding match and board
                        if table_no % 2 == 1 : #open room: ns_team = team_a, ew_team = team_b
                            if match["team_a"] == 0 :
                                match["team_a"] = ns_team
                            elif match["team_a"] != ns_team :
                                raise TeamNumberConflictException
                            if match["team_b"] == 0 :
                                match["team_b"] = ew_team
                            elif match["team_b"] != ew_team :
                                raise TeamNumberConflictException
                            board["open_contract"] = contract + " " + declarer + " " + result
                            board["open_score"] = ns_score
                            board["board_played"] = board["board_played"] + 1   # 1 table has played this board
                        else :
                            if match["team_a"] == 0 :
                                match["team_a"] = ew_team
                            elif match["team_a"] != ew_team :
                                raise TeamNumberConflictException
                            if match["team_b"] == 0 :
                                match["team_b"] = ns_team
                            elif match["team_b"] != ns_team :
                                raise TeamNumberConflictException
                            board["close_contract"] = contract + " " + declarer + " " + result
                            board["close_score"] = ns_score
                            board["board_played"] = board["board_played"] + 1   # 1 table has played this board
                    if board["board_played"] != 2:
                        match["match_finished"] = 0

    for match in overall_result:
        #print ("match %d: team %d vs team %d" % (match["match_no"], match["team_a"], match["team_b"]) )
        for board in match["boards"]:
            ns_imp = score_to_imp(board["open_score"], board["close_score"])
            score_diff = board["open_score"] - board["close_score"]
            board["team_a_score_diff"] = score_diff if score_diff > 0 else 0
            board["team_b_score_diff"] = 0 if score_diff > 0 else -score_diff
            board["team_a_imp"] = ns_imp if ns_imp > 0 else 0
            board["team_b_imp"] = 0 if ns_imp > 0 else -ns_imp
            match["imp_a"] = match["imp_a"] + board["team_a_imp"]
            match["imp_b"] = match["imp_b"] + board["team_b_imp"]
            #print ("\tboard %d: open %d closed %d diff %d imp_a %d imp_b %d" % (board["board_num"], board["open_score"], board["close_score"], score_diff, board["team_a_imp"], board["team_b_imp"]) )
        match["vp_a"] = imp_to_vp(match["imp_a"]-match["imp_b"], board_count)
        match["vp_b"] = imp_to_vp(match["imp_b"]-match["imp_a"], board_count)
        vp_table[match["team_a"]-1][1] = match["vp_a"]
        vp_table[match["team_b"]-1][1] = match["vp_b"]
        #print ("\ttotal_imp_a %d total_imp_b %d vp_a %f vp_b %f" % (match["imp_a"], match["imp_b"], match["vp_a"], match["vp_b"]) )

    return overall_result, vp_table

def result_dict_to_html(result_dict, output_file):
    f = open(SWISS_SCORE_TEMPLATE_PATH, "r")
    tmp_html = f.read()
    f.close()
    tmpl = Template(tmp_html)
    html = tmpl.render(result_dict)
    f = open(output_file, "w")
    f.write(html)
    f.close()
    return 


def html_files_to_pdf(html_files, output_file):
    options = {
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'grayscale': None,
        'outline-depth':3,
        # 'footer-center':'[page]',
        'footer-line': None,
    }
    pdfkit.from_file(html_files, output_file, options=options, )



def result_data_process(result_array, team_count, start_board, end_board, board_count, pdf_file, round_number, project_path, match_finished):
    output_folder = project_path + "/output"
    if not os.path.exists(output_folder):
        #import shutil
        #shutil.rmtree(output_folder)
        os.makedirs(output_folder)    

    result_dict_array, vps = result_to_dict(result_array, team_count, start_board, board_count, round_number)
    
    # gen html   
    for result_dict in result_dict_array:
        html_files = []
        file_name = output_folder + "/" + str(result_dict["match_no"]) + ".html"
        print file_name
        pdf_file_name = project_path + "/" + pdf_file + " Table " + str(result_dict["match_no"]) + "- " + str(result_dict["team_a"]) + " vs " + str(result_dict["team_b"]) + ".pdf"
        print pdf_file_name
        html_files.append(file_name)
        result_dict_to_html(result_dict, file_name)
        if match_finished == 1:
            html_files_to_pdf(html_files, pdf_file_name)
        else :
            if (result_dict["match_finished"] == 1):
                print "Round %d Table %d has finished" % (round_number, result_dict["match_no"])
                if not os.path.exists(pdf_file_name):    # match is finished && pdf has not yet generated            
                    print "Round %d Table %d finished but pdf has not yet generated" % (round_number, result_dict["match_no"])
                    html_files_to_pdf(html_files, pdf_file_name)

    # gen pdf
    #html_files_to_pdf(html_files, pdf_file)
    return vps

def generate_final_score(matches, team_count, round_number, scores, round_scores, adjustment, pdf_file):
    team_dict_ary = []
    for i in range(team_count):
        team_number = i + 1
        total_score = [ x[1] for x in scores if x[0] == team_number ][0]
        team_adjustment = [ x[1] for x in adjustment if x[0] == team_number ][0]
        adjusted_score = total_score + team_adjustment
        team_dict = {
            "team_number": team_number,
            "rounds": [],
            "score": total_score,
            "adjustment": team_adjustment,
            "adjusted_score": adjusted_score,
            "rank": -1
        }
        for j in range(round_number):
            print j
            print round_scores
            round_match = matches[j]            
            match = [ x for x in round_match if x[1] == team_number ][0]
            opp_team = match[2]
            table = int((match[0]+1)/2)
            current_round_score = round_scores[j]
            score = [ x[1] for x in current_round_score if x[0] == team_number ][0]
            rnd_score_entry = {
                "opp_team": opp_team,
                "table": table,
                "score": score
            }
            team_dict["rounds"].append(rnd_score_entry)
        team_dict_ary.append(team_dict)

    final_score_sorted_by_rank = sorted(team_dict_ary, reverse=True, key=itemgetter('adjusted_score'))
    i = 1;
    for team in final_score_sorted_by_rank:
        team["rank"] = i
        i = i + 1
    final_score_sorted_by_team = sorted(final_score_sorted_by_rank, key=itemgetter('team_number'))    

    f = open(FINAL_SCORE_TEMPLATE_PATH, "r")
    tmp_html = f.read()
    f.close()
    tmpl = Template(tmp_html)
    round_number_counts = [ x+1 for x in range(round_number)]
    html = tmpl.render({"teams":final_score_sorted_by_team, "round_numbers":round_number_counts })

    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'grayscale': None,
        'outline-depth':3,
        # 'footer-center':'[page]',
        'footer-line': None,
    }
    pdfkit.from_string(html, pdf_file, options=options)


def match_table_process(matches, team_count, round_number, scores, round_scores, adjustment, start_board, end_board, pdf_file):
    team_dict_ary = []
    for i in range(team_count):
        team_number = i + 1
        total_score = [ x[1] for x in scores if x[0] == team_number ][0]
        team_adjustment = [ x[1] for x in adjustment if x[0] == team_number ][0]
        adjusted_score = total_score + team_adjustment
        team_dict = {
            "team_number": team_number,
            "rounds": [],
            "score": total_score,
            "opp_team": 0,
            "table": 0,
            "adjustment": team_adjustment,
            "adjusted_score": adjusted_score,
            "rank": ""
        }
        for j in range(round_number):
            round_match = matches[j]            
            match = [ x for x in round_match if x[1] == team_number ][0]
            opp_team = match[2]
            table = int((match[0]+1)/2)
            if j == round_number - 1:
                team_dict["opp_team"] = opp_team
                team_dict["table"] = table
            else:
                current_round_score = round_scores[j]
                score = [ x[1] for x in current_round_score if x[0] == team_number ][0]
                rnd_score_entry = {
                    "opp_team": opp_team,
                    "table": table,
                    "score": score
                }
                team_dict["rounds"].append(rnd_score_entry)
        team_dict_ary.append(team_dict)

    if round_number == 1:
        team_dict_sorted_by_team = team_dict_ary
    else:
        team_dict_sorted_by_rank = sorted(team_dict_ary, reverse=True, key=itemgetter('adjusted_score'))
        i = 1;
        for team in team_dict_sorted_by_rank:
            team["rank"] = i
            i = i + 1
        team_dict_sorted_by_team = sorted(team_dict_sorted_by_rank, key=itemgetter('team_number'))    

    f = open(SEAT_MATCH_TEMPLATE_PATH, "r")
    tmp_html = f.read()
    f.close()
    tmpl = Template(tmp_html)
    if round_number == 1:
        round_number_counts = []
    else:
        round_number_counts = [ x+1 for x in range(round_number-1)]
    html = tmpl.render({"teams":team_dict_sorted_by_team, "round":round_number, "round_numbers":round_number_counts })

    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'grayscale': None,
        'outline-depth':3,
        # 'footer-center':'[page]',
        'footer-line': None,
    }
    pdfkit.from_string(html, pdf_file + "/Match%d.pdf" % round_number, options=options)

    options = {
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'grayscale': None,
        'outline-depth':3,
        # 'footer-center':'[page]',
        'footer-line': None,
    }
    
    f = open(PER_TABLE_RESULT_EMPTY_PATH, "r")
    tmp_html = f.read()
    f.close()
    tmpl = Template(tmp_html)
    for match in matches[round_number-1]:
        table_no = int(match[0] + 1) / 2
        if match[0] % 2 == 1:
            open_close = "OPEN"
        else:
            open_close = "CLOSED"
        html = tmpl.render({"round":round_number, "open_close":open_close, "table_no":table_no, "team_a":match[1], "team_b":match[2], "start_board":start_board, "end_board":end_board+1 })
        pdfkit.from_string(html, pdf_file + "/Match%d_%s%d.pdf" % (round_number, open_close, table_no) , options=options)



class IMPVPGenerationTest(unittest.TestCase):
    def test_from_sample_input(self):
        self.data_array = [{
        "Erased": "False", 
        "PairEW": "1", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "N", 
        "Section": "1", 
        "Contract": "2 D", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "1", 
        "Remarks": "", 
        "Table": "1", 
        "PairNS": "2", 
        "ID": "1", 
        "Result": "="
        }, {
        "Erased": "False", 
        "PairEW": "1", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "W", 
        "Section": "1", 
        "Contract": "2 NT x", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "2", 
        "Remarks": "", 
        "Table": "1", 
        "PairNS": "2", 
        "ID": "1", 
        "Result": "+2"
        }, {
        "Erased": "False", 
        "PairEW": "1", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "E", 
        "Section": "1", 
        "Contract": "4 S xx", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "3", 
        "Remarks": "", 
        "Table": "1", 
        "PairNS": "2", 
        "ID": "1", 
        "Result": "-2"
        }, {
        "Erased": "False", 
        "PairEW": "1", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "S", 
        "Section": "1", 
        "Contract": "6 C", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "4", 
        "Remarks": "", 
        "Table": "1", 
        "PairNS": "2", 
        "ID": "1", 
        "Result": "-1"
        }, {
        "Erased": "False", 
        "PairEW": "2", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "N", 
        "Section": "1", 
        "Contract": "3 D x", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "1", 
        "Remarks": "", 
        "Table": "2", 
        "PairNS": "1", 
        "ID": "1", 
        "Result": "-1"
        }, {
        "Erased": "False", 
        "PairEW": "2", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "E", 
        "Section": "1", 
        "Contract": "3 NT", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "2", 
        "Remarks": "", 
        "Table": "2", 
        "PairNS": "1", 
        "ID": "1", 
        "Result": "="
        }, {
        "Erased": "False", 
        "PairEW": "2", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "S", 
        "Section": "1", 
        "Contract": "4 H x", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "3", 
        "Remarks": "", 
        "Table": "2", 
        "PairNS": "1", 
        "ID": "1", 
        "Result": "-2"
        }, {
        "Erased": "False", 
        "PairEW": "2", 
        "LeadCard": "", 
        "DateLog": "05/24/14 00:00:00", 
        "NS/EW": "N", 
        "Section": "1", 
        "Contract": "6 NT", 
        "Round": "1", 
        "Declarer": "2", 
        "Board": "4", 
        "Remarks": "", 
        "Table": "2", 
        "PairNS": "1", 
        "ID": "1", 
        "Result": "="
        }] 
        result_data_process(self.data_array, 2, 4, "matches.pdf")


if __name__ == "__main__":
    unittest.main()