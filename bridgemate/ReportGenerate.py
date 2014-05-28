import unittest
from jinja2 import Template
import pdfkit
import os
from bridgemate.Score import *
from utils.config import SWISS_SCORE_TEMPLATE_PATH


def result_to_dict(result_array, team_count, board_count):
    match_count = int(team_count / 2)
    vp_table = [ [i+1, 0] for i in range(team_count)]

    overall_result = [{
        "match_no": k+1,
        "boards" : [ {
            "board_num" : i + 1, 
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
        "vp_b" : 0.0
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
                            board["open_contract"] = contract + result
                            board["open_score"] = ns_score
                        else :
                            if match["team_a"] == 0 :
                                match["team_a"] = ew_team
                            elif match["team_a"] != ew_team :
                                raise TeamNumberConflictException
                            if match["team_b"] == 0 :
                                match["team_b"] = ns_team
                            elif match["team_b"] != ns_team :
                                raise TeamNumberConflictException
                            board["close_contract"] = contract + result
                            board["close_score"] = ns_score

    for match in overall_result:
        #print ("match %d: team %d vs team %d" % (match["match_no"], match["team_a"], match["team_b"]) )
        for board in match["boards"]:
            ns_imp = score_to_imp(board["open_score"], board["close_score"])
            score_diff = board["open_score"] - board["close_score"]
            board["team_a_score_diff"] = score_diff if score_diff > 0 else 0
            board["team_b_score_diff"] = score_diff if score_diff < 0 else 0
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



def result_data_process(result_array, team_count, board_count, pdf_file):
    output_folder = "output"
    if os.path.exists(output_folder):
        import shutil
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    result_dict_array, vps = result_to_dict(result_array, team_count, board_count)
    # gen html
    html_files = []

    for result_dict in result_dict_array:
        file_name = output_folder + "/" + str(len(html_files)+1) + ".html"
        html_files.append(file_name)
        result_dict_to_html(result_dict, file_name)

    # gen pdf
    html_files_to_pdf(html_files, pdf_file)
    return vps


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