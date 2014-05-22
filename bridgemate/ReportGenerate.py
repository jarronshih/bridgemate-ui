from jinja2 import Template
import pdfkit

def result_to_html(config):
    # results = array of (board_num, open_contract, close_contract, openscore, close_score)
    tmpl = Template(HTML_TEMPLATE)
    return tmpl.render(config)

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