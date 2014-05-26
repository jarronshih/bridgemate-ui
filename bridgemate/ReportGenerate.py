from jinja2 import Template
import pdfkit
from bridgemate.Score import compute_score, score_to_imp, imp_to_vp

def result_to_html(config, team_count, board_count):
    # results = array of (board_num, open_contract, close_contract, openscore, close_score)
    match_count = team_count / 2

    vp_table = [ [i+1, 0] for i in range(team_count)]

    overall_result = [{
        "match_no": k+1,
        "boards" : [ {
          "board_num" = i + 1, 
          "open_contract" = "",
          "close_contract" = "", 
          "open_score" = 0, 
          "close_score" = 0, 
          "team_a_score_diff" = 0, 
          "team_b_score_diff" = 0, 
          "team_a_imp" = 0, 
          "team_b_imp" = 0
          } for i in range(board_count) ],
        "team_a" : 0,
        "team_b" : 0,
        "imp_a" : 0,
        "imp_b" : 0,
        "vp_a" : 0,
        "vp_b" : 0
      } for k in range(match_count)]
            
    bcs_array = config.get_result_array()
    for array_elt in bcs_array    #calculate per-board score and fill it into corresnponding position in overall result
      ns_team = array_elt["PairNS"]
      ew_team = array_elt["PairEW"]
      table_no = array_elt["Table"]
      board_no = array_elt["Board"]
      contract = array_elt["Contract"]
      declarer = array_elt["NS/EW"]
      result = array_elt["Result"]
      ns_score = compute_score(board_no, contract, declarer, result)
      for match in overall_result
        if match["match_no"] == (table_no / 2 + 1) 
          for board in match["boards"]
            if board["board_num"] == board_no # found the corresponding match and board
              if table_no % 2 == 0  #open room: ns_team = team_a, ew_team = team_b
                if match["team_a"] == 0
                  match["team_a"] = ns_team
                elif match["team_a"] != ns_team
                  raise TeamNumberConflictException
                if match["team_b"] == 0
                  match["team_b"] = ew_team
                elif match["team_a"] != ew_team
                  raise TeamNumberConflictException
                board["open_contract"] = contract + result
                board["open_score"] = ns_score
              else
                if match["team_a"] == 0
                  match["team_a"] = ew_team
                elif match["team_a"] != ew_team
                  raise TeamNumberConflictException
                if match["team_b"] == 0
                  match["team_b"] = ns_team
                elif match["team_a"] != ns_team
                  raise TeamNumberConflictException
                board["close_contract"] = contract + result
                board["close_score"] = ns_score

    for match in overall_result
      for board in match["boards"]
        ns_imp = score_to_imp(board["open_score"], board["close_score"])
        score_diff = board["open_score"] - board["close_score"]
        board["team_a_score_diff"] = score_diff if score_diff > 0 else 0
        board["team_b_score_diff"] = score_diff if score_diff < 0 else 0
        board["team_a_imp"] = ns_imp if ns_imp > 0 else 0
        board["team_b_imp"] = -ns_imp if ns_imp > 0 else 0
        match["imp_a"] = match["imp_a"] + board["team_a_imp"]
        match["imp_b"] = match["imp_b"] + board["team_b_imp"]
      match["vp_a"] = imp_to_vp(match["imp_a"]-match["imp_b"], board_count)
      match["vp_b"] = imp_to_vp(match["imp_b"]-match["imp_a"], board_count)
      vp_table[match["team_a"]-1][1] = match["vp_a"]
      vp_table[match["team_b"]-1][1] = match["vp_b"]

    return overall_result, vp_table

    #tmpl = Template(HTML_TEMPLATE)
    #return tmpl.render(config)

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



HTML_TEMPLATE="""
<table>
  <tr>
    <th></th>
    <th colspan="2">Results</th>
    <th colspan="2">NS Score</th>
    <th colspan="2">Score diff</th>
    <th colspan="2">IMP</th>
  </tr>
  <tr>
    <th>#</th>
    <th>Open</th>
    <th>Close</th>
    <th>Open</th>
    <th>Close</th>
    <th>{{ team_a }}</th>
    <th>{{ team_b }}</th>
    <th>{{ team_a }}</th>
    <th>{{ team_b }}</th>
  </tr>

  {%- for board_num, open_contract, close_contract, open_score, close_score, team_a_score_diff, team_b_score_diff, team_a_imp, team_b_imp in results %}
      <tr>
        <td>{{ board_num }}</td>
        <td>{{ open_contract }}</td>
        <td>{{ close_contract }}</td>
        <td>{{ open_score }}</td>
        <td>{{ close_score }}</td>
        <td>{{ team_a_score_diff }}</td>
        <td>{{ team_b_score_diff }}</td>
        <td>{{ team_a_imp }}</td>
        <td>{{ team_b_imp }}</td>
      </tr>
  {%- endfor %}

  <tr>
    <th colspan="7">Sum</th>
    <th></th>
    <th></th>
  </tr>
  <tr>
    <th colspan="7">Carry</th>
    <th></th>
    <th></th>
  </tr>
  <tr>
    <th colspan="7">Total</th>
    <th></th>
    <th></th>
  </tr>
</table>

"""