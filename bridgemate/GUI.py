import wx
import wx.grid
from bridgemate.Bridgemate2Manager import *
from bridgemate.ReportGenerate import *
from utils.config import PROJECT_FOLDER
from utils.Tools import str_to_num

MAINFRAME_HEIGHT=400
MAINFRAME_WIDTH=600

ID_MAINFRAME=100

PROJECT_STATUS_NONE=0
PROJECT_STATUS_CONFIG=1
PROJECT_STATUS_RUNNING=2

# Main UI
class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(
            parent=None, 
            id=ID_MAINFRAME, 
            style= wx.CAPTION | wx.SYSTEM_MENU  | wx.MINIMIZE_BOX | wx.CLOSE_BOX,
            )
        self.bm2_manager = None
        self.init_UI()
        self.SetSize((MAINFRAME_WIDTH, MAINFRAME_HEIGHT))
        self.Centre()
        self.reload_project()
        self.status=PROJECT_STATUS_NONE
        

    def init_UI(self):
        # Top Menu
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        file_menu = wx.Menu()
        menubar.Append(file_menu, '&File')

        new_item = file_menu.Append(wx.ID_NEW, '&New\tCtrl+N')
        open_item = file_menu.Append(wx.ID_OPEN, '&Open\tCtrl+O')
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')

        self.Bind(wx.EVT_MENU, self.on_new, new_item)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_quit, quit_item)


        # Statusbar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('')

        # Project Status Panel
        self.project_status_panel = ProjectStatusPanel(self)

        # Project Running Panel
        self.project_running_panel = ProjectRuningPanel(self)

        # Setup Panel
        self.project_status_panel.Hide()
        self.project_running_panel.Hide()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.project_status_panel, 1, wx.EXPAND)
        self.sizer.Add(self.project_running_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_BUTTON, self.on_generate_final_score, self.project_status_panel.btn_generate_final_result)
        self.Bind(wx.EVT_BUTTON, self.on_generate_schedule, self.project_status_panel.btn_schedule_next_round)
        self.Bind(wx.EVT_BUTTON, self.on_start_bcs, self.project_status_panel.btn_run_next_round)
        self.Bind(wx.EVT_BUTTON, self.on_stop_bcs, self.project_running_panel.btn_stop_bcs)
        self.bcs_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.bcs_timer_callback, self.bcs_timer)

    def on_quit(self, e):
        self.Close()

    def on_new(self, e):
        dlg = NewProjectDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            project_name = dlg.get_project_name()
            self.bm2_manager = open_project(project_name)
            self.status = PROJECT_STATUS_CONFIG

        self.reload_project()
        dlg.Destroy()
        
    def on_open(self, e):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
                           )
        dlg.SetPath(PROJECT_FOLDER)
        if dlg.ShowModal() == wx.ID_OK:
            project_name = dlg.GetPath()
            self.bm2_manager = open_project(project_name)
            self.status = PROJECT_STATUS_CONFIG
        self.reload_project()
        dlg.Destroy()

    def on_generate_schedule(self, e):
        self.bm2_manager.schedule_next_round()
        frame = MatchTableFrame(None, self.bm2_manager.config)
        frame.Show(True)
        self.project_status_panel.btn_run_next_round.Enable()
        self.project_status_panel.btn_score_detail.Disable()

    def on_generate_final_score(self, e):
        # update final score if the score of the last round is changed manually
        total_score = []
        for team in range(self.bm2_manager.config.team_count):
            score = [team+1, 0.0]
            for rnd_score in self.bm2_manager.config.scheduler_metadata["round_score"]:
                for t, s in rnd_score:
                    if t == score[0]:
                        score[1] = score[1] + s
            total_score.append(score)
        self.bm2_manager.scheduler.set_score(total_score)
        self.bm2_manager.scheduler.round_score = self.bm2_manager.config.scheduler_metadata["round_score"]

        # generate final score
        scheduler = self.bm2_manager.config.get_scheduler()
        generate_final_score(scheduler.get_match(), self.bm2_manager.config.team_count, scheduler.get_current_round(), scheduler.get_scores(), scheduler.get_round_scores(), self.bm2_manager.config.adjustment, get_project_folder(self.bm2_manager.project_name) + "/Final_Score.pdf")
        #self.project_status_panel.btn_score_detail.Disable()
        #self.project_status_panel.btn_generate_final_result.Disable()

    def on_start_bcs(self, e):
        # renew the output directiry
        output_folder = get_project_folder(self.bm2_manager.project_name) + "/output"
        if os.path.exists(output_folder):
            import shutil
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)

        self.status = PROJECT_STATUS_RUNNING
        self.bm2_manager.init_bws_file()
        scheduler = self.bm2_manager.config.get_scheduler()
        current_round = scheduler.get_current_round()
        match_table_process(scheduler.get_match(), self.bm2_manager.config.team_count, current_round, scheduler.get_scores(), scheduler.get_round_scores(), self.bm2_manager.config.adjustment, self.bm2_manager.config.start_board_number, self.bm2_manager.config.end_board_number, get_project_folder(self.bm2_manager.project_name))
        self.bm2_manager.start_bcs_collect_data()

        self.bcs_timer.Start(60*1000)
        self.reload_project()

    def bcs_timer_callback(self, e):
        data_ary = self.bm2_manager.get_bcs_data()
        filter_ary = [(int(x["PairNS"]), int(x["PairEW"]), int(x["Board"])) for x in data_ary]
        print filter_ary

        # generate report
        scheduler = self.bm2_manager.config.get_scheduler()
        current_round = scheduler.get_current_round()
        pdf_file_name = "Round " + str(current_round)
        result_data_process(data_ary, self.bm2_manager.config.team_count, self.bm2_manager.config.start_board_number, self.bm2_manager.config.end_board_number, self.bm2_manager.config.board_count, pdf_file_name, current_round, get_project_folder(self.bm2_manager.project_name), 0)

        pending_ary = []
        #scheduler = self.bm2_manager.config.get_scheduler()
        matches = scheduler.get_match_by_round(scheduler.get_current_round())
        for table, ns_team, ew_team in matches:
            start_board_number = self.bm2_manager.config.start_board_number
            end_board = self.bm2_manager.config.end_board_number+1
            board_array = []
            for board in range(start_board_number, end_board):
                if (ns_team, ew_team, board) in filter_ary:
                    filter_ary.remove((ns_team, ew_team, board))
                else:
                    board_array.append(board)

            if len(board_array) > 0:
                if table & 1:
                    table_str = "Open  %d" % int((table+1)/2)
                else:
                    table_str = "Close %d" % int(table/2)
                board_str = ', '.join(map(str, board_array))
                pending_ary.append("%s - NS %d - EW %d:\t\t%s" % (table_str, ns_team, ew_team, board_str))


        msg = "Waitng for %d table: \n%s" % (len(pending_ary), '\n'.join(pending_ary))
        self.project_running_panel.refresh_ui(msg)
        self.Layout()

        if len(pending_ary) == 0:
            self.bcs_timer.Stop()

    def on_stop_bcs(self, e):
        self.status = PROJECT_STATUS_CONFIG
        self.bcs_timer.Stop()
        
        # generate report
        data_ary = self.bm2_manager.get_bcs_data()
        scheduler = self.bm2_manager.config.get_scheduler()
        current_round = scheduler.get_current_round()
        pdf_file_name = "Round " + str(current_round)
        vps = result_data_process(data_ary, self.bm2_manager.config.team_count, self.bm2_manager.config.start_board_number, self.bm2_manager.config.end_board_number, self.bm2_manager.config.board_count, pdf_file_name, current_round, get_project_folder(self.bm2_manager.project_name), 1)
        
        # parse score
        total_vps = []
        for score in self.bm2_manager.scheduler.score:
            for t, s in vps:
                if t == score[0]:
                    new_score = s
            total_score = (score[0], score[1] + new_score)
            total_vps.append(total_score)
        self.bm2_manager.scheduler.score = total_vps
        self.bm2_manager.scheduler.append_score(vps)

        board_record_process(data_ary, current_round, self.bm2_manager.config.start_board_number, self.bm2_manager.config.end_board_number, self.bm2_manager.config.board_count, get_project_folder(self.bm2_manager.project_name))

#        total_score = []
#        for team in range(self.bm2_manager.config.team_count):
#            score = [team+1, 0.0]
#            for rnd_score in self.bm2_manager.config.scheduler_metadata["round_score"]:
#                for t, s in rnd_score:
#                    if t == score[0]:
#                        score[1] = score[1] + s
#            total_score.append(score)
#        self.bm2_manager.scheduler.set_score(total_score)
#        self.bm2_manager.scheduler.round_score = self.bm2_manager.config.scheduler_metadata["round_score"]

        # generate final score
        generate_final_score(self.bm2_manager.scheduler.match, self.bm2_manager.config.team_count, current_round, self.bm2_manager.scheduler.score, self.bm2_manager.scheduler.round_score, self.bm2_manager.config.adjustment, get_project_folder(self.bm2_manager.project_name) + "/Total_Score.pdf")
        
        self.bm2_manager.end_and_save_config()
        
        self.reload_project()

    def reload_project(self, status_string=''):
        if self.bm2_manager is None:
            self.statusbar.SetStatusText("Please Open / Create project")
            self.SetTitle("Main")
            self.status=PROJECT_STATUS_NONE

        else:
            self.statusbar.SetStatusText(status_string)
            self.SetTitle(self.bm2_manager.config.project_name)

        if self.status == PROJECT_STATUS_CONFIG:
            self.project_status_panel.Show()
            self.bm2_manager.config.read()
            self.project_status_panel.refresh_ui(self.bm2_manager.config)
            self.project_status_panel.btn_run_next_round.Disable()
            self.project_status_panel.btn_score_detail.Enable()
            self.project_running_panel.Hide()
        elif self.status == PROJECT_STATUS_RUNNING:
            self.project_status_panel.Hide()
            self.bm2_manager.config.read()
            self.project_running_panel.refresh_ui("Waiting result...")
            self.project_running_panel.Show()
        else:
            self.project_status_panel.Hide()
            self.project_running_panel.Hide()

        self.Layout()



# In MainFrame: Show project status
class ProjectStatusPanel(wx.Panel):
    def __init__(self, parent):
        super(ProjectStatusPanel, self).__init__(parent=parent)
        self.init_ui()

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.st_project_name = wx.StaticText(self, label='Proejct Name')
        vbox.Add(self.st_project_name, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.st_team_count = wx.StaticText(self, label='Team Count')
        vbox.Add(self.st_team_count, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.st_complete_round = wx.StaticText(self, label='Complete Round')
        vbox.Add(self.st_complete_round, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.st_starting_board_number = wx.StaticText(self, label='Starting Board')
        vbox.Add(self.st_starting_board_number, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.st_ending_board_number = wx.StaticText(self, label='Starting Board')
        vbox.Add(self.st_ending_board_number, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.btn_edit_starting_board_number = wx.Button(self, label='Edit Starting Board', size=(70, 30))
        vbox.Add(self.btn_edit_starting_board_number, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)
        self.Bind(wx.EVT_BUTTON, self.on_edit_starting_board_number, self.btn_edit_starting_board_number)

        self.btn_edit_ending_board_number = wx.Button(self, label='Edit Ending Board', size=(70, 30))
        vbox.Add(self.btn_edit_ending_board_number, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)
        self.Bind(wx.EVT_BUTTON, self.on_edit_ending_board_number, self.btn_edit_ending_board_number)

        self.btn_score_detail = wx.Button(self, label='Score', size=(70, 30))
        vbox.Add(self.btn_score_detail, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)
        self.Bind(wx.EVT_BUTTON, self.on_score_detail, self.btn_score_detail)

        self.btn_schedule_next_round = wx.Button(self, label='Schedule Next Round', size=(70, 30))
        vbox.Add(self.btn_schedule_next_round, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.btn_run_next_round = wx.Button(self, label='Run Next Round', size=(70, 30))
        vbox.Add(self.btn_run_next_round, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.btn_generate_final_result = wx.Button(self, label='Generate Final Result', size=(70, 30))
        vbox.Add(self.btn_generate_final_result, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.SetSizer(vbox)

    def refresh_ui(self, project_config=None):
        if project_config is None:
            project_config = self.config
        project_name = project_config.project_name
        team_count = project_config.team_count
        start_board_number = project_config.start_board_number
        end_board_number = project_config.end_board_number
        
        project_scheduler = project_config.get_scheduler()
        current_round = project_scheduler.get_current_round()
        is_next_round_available = project_scheduler.is_next_round_available()

        self.st_project_name.SetLabel('Proejct Name: %s' % project_name)
        self.st_team_count.SetLabel('Team Count: %d' % team_count)
        self.st_complete_round.SetLabel('Complete Round: %d' % current_round)
        self.st_starting_board_number.SetLabel('Starting Board: %d' % start_board_number)
        self.st_ending_board_number.SetLabel('Ending Board: %d' % end_board_number)
        
        if is_next_round_available:
            self.btn_schedule_next_round.Enable()
            self.btn_edit_starting_board_number.Enable()
            self.btn_generate_final_result.Hide()
        else:
            self.btn_schedule_next_round.Disable()
            self.btn_edit_starting_board_number.Disable()
            self.btn_generate_final_result.Show()        

        self.config = project_config

    def on_edit_starting_board_number(self, e):
        dialog = wx.NumberEntryDialog(parent=self, message='Enter starting board number', prompt='', caption='', value=self.config.start_board_number, min=1, max=1000)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            value = int(dialog.GetValue())
            self.config.start_board_number = value
            self.refresh_ui()
        dialog.Destroy()

    def on_edit_ending_board_number(self, e):
        dialog = wx.NumberEntryDialog(parent=self, message='Enter ending board number', prompt='', caption='', value=self.config.end_board_number, min=1, max=1000)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            value = int(dialog.GetValue())
            self.config.end_board_number = value
            self.refresh_ui()
        dialog.Destroy()
    

    def on_score_detail(self, e):
        #self.config.scheduler_metadata = self.scheduler.get_metadata()
        frame = ScoreTableFrame(None, self.config)
        frame.Show(True)


# In MainFrame: Show when project is running
class ProjectRuningPanel(wx.Panel):
    def __init__(self, parent):
        super(ProjectRuningPanel, self).__init__(parent=parent)
        self.init_ui()
        

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.btn_stop_bcs = wx.Button(self, label='Stop', size=(70, 30))
        vbox.Add(self.btn_stop_bcs, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.st_msg = wx.StaticText(self, label='Waiting result...')
        vbox.Add(self.st_msg, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)

        self.SetSizer(vbox)

    def refresh_ui(self, msg):
        self.st_msg.SetLabel(msg)

class MatchTableFrame(wx.Frame):
    def __init__(self, parent, config):
        wx.Frame.__init__(self, parent, -1, "Match Table: Round " + str(config.scheduler_metadata["current_round"]),
                size=(275, 275))
        grid = wx.grid.Grid(self)
        table = MatchTable(config)
        grid.SetTable(table)
        grid.SetColLabelValue(0, "NS")
        grid.SetColLabelValue(1, "EW")

class MatchTable(wx.grid.PyGridTableBase):
    def __init__(self, config):
        wx.grid.PyGridTableBase.__init__(self)
        self.config = config

    def GetColLabelValue(self, col):
        cols = ["NS", "EW"]
        return cols[col]

    def GetRowLabelValue(self, row):
        return "Table " + str(row+1)

    def GetNumberRows(self):
        """Return the number of rows in the grid"""
        return self.config.team_count

    def GetNumberCols(self):
        """Return the number of columns in the grid"""
        return 2

    def IsEmptyCell(self, row, col):
        """Return True if the cell is empty"""
        return False

    def GetTypeName(self, row, col):
        """Return the name of the data type of the value in the cell"""
        return None

    def GetValue(self, row, col):
        """Return the value of a cell"""
        current_matchup = self.config.scheduler_metadata["match"][self.config.scheduler_metadata["current_round"]-1]
        return current_matchup[row][col+1]

    def SetValue(self, row, col, value):
        """Set the value of a cell"""
        if value.isdigit():
            meta = self.config.scheduler_metadata
            matchup = []
            for table, ns, ew in self.config.scheduler_metadata["match"][self.config.scheduler_metadata["current_round"]-1]:
                if table == row + 1:
                    if col == 0:
                        matchup.append((table, int(value), ew))
                    elif col == 1:
                        matchup.append((table, ns, int(value)))
                else:
                    matchup.append((table, ns, ew))
            meta["match"][len(self.config.scheduler_metadata["match"])-1] = matchup
            self.config.scheduler_metadata = meta


class ScoreTableFrame(wx.Frame):
    def __init__(self, parent, config):
        wx.Frame.__init__(self, parent, -1, "Score",
                size=(275, 275))
        grid = wx.grid.Grid(self)
        table = ScoreTable(config)
        grid.SetTable(table)


class ScoreTable(wx.grid.PyGridTableBase):
    def __init__(self, config):
        wx.grid.PyGridTableBase.__init__(self)
        self.config = config

    def GetColLabelValue(self, col):
        cols = ["Round " + str(self.config.scheduler_metadata["current_round"]), "Adjustment"]
        return cols[col]

    def GetRowLabelValue(self, row):
        return "Team " + str(row+1)

    def GetNumberRows(self):
        """Return the number of rows in the grid"""
        return len(self.config.scheduler_metadata["score"])

    def GetNumberCols(self):
        """Return the number of columns in the grid"""
        return 2

    def IsEmptyCell(self, row, col):
        """Return True if the cell is empty"""
        return False

    def GetTypeName(self, row, col):
        """Return the name of the data type of the value in the cell"""
        return None

    def GetValue(self, row, col):
        """Return the value of a cell"""
        if col == 0:    #score in the previous round
            if len(self.config.scheduler_metadata["round_score"]) == 0:     #no rounds are played
                for team_number, score in self.config.scheduler_metadata["score"]:
                    if team_number == row + 1:
                        return score
            else:
                for team_number, score in self.config.scheduler_metadata["round_score"][len(self.config.scheduler_metadata["round_score"])-1]:
                    if team_number == row + 1:
                        return score
        else:           #adjustment
            for team_number, score in self.config.adjustment:
                if team_number == row + 1:
                    return score

    def SetValue(self, row, col, value):
        """Set the value of a cell"""
        if not str_to_num(value) is None:            
            if col == 0:
                meta = self.config.scheduler_metadata
                scores = []
                if len(self.config.scheduler_metadata["round_score"]) == 0:     #no rounds are played
                    for team_number, score in self.config.scheduler_metadata["score"]:
                        if team_number == row + 1:
                            scores.append([team_number, str_to_num(value)])
                        else:
                            scores.append([team_number, score])
                    meta["score"] = scores                    
                else:
                    for team_number, score in self.config.scheduler_metadata["round_score"][len(self.config.scheduler_metadata["round_score"])-1]:
                        if team_number == row + 1:
                            scores.append([team_number, str_to_num(value)])
                        else:
                            scores.append([team_number, score])
                    meta["round_score"][len(self.config.scheduler_metadata["round_score"])-1] = scores
                self.config.scheduler_metadata = meta    
            else:
                adjs = self.config.adjustment
                adj = []
                for team_number, score in self.config.adjustment:
                    if team_number == row + 1:
                        adj.append([team_number, str_to_num(value)])
                    else:
                        adj.append([team_number, score])
                adjs = adj
                self.config.adjustment = adjs


class NewProjectDialog(wx.Dialog):
    def __init__(self, parent):
        super(NewProjectDialog, self).__init__(parent=parent)

        self.on_init()

        self.SetTitle("New Project")
        self.Centre()
        self.Show(True)

    def on_init(self):
        self.SetSize((400,300))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        btn_swiss = wx.Button(panel, label='SWISS')
        vbox.Add(btn_swiss)

        btn_roundrobin = wx.Button(panel, label='RoundRobin')
        vbox.Add(btn_roundrobin)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_swiss, btn_swiss)
        self.Bind(wx.EVT_BUTTON, self.on_roundrobin, btn_roundrobin)

    def on_swiss(self, e):
        self.Show(False)
        dlg = NewProjectSWISSDialog(self)

        if dlg.ShowModal() == wx.ID_OK:
            self.project_name = dlg.get_project_name()
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    def on_roundrobin(self, e):
        self.Show(False)
        dlg = NewProjectRoundRobinDialog(self)


        if dlg.ShowModal() == wx.ID_OK:
            self.project_name = dlg.get_project_name()
            self.EndModal(wx.ID_OK)
        else:
            self.Close()

    def get_project_name(self):
        return self.project_name

class NewProjectRoundRobinDialog(wx.Dialog):
    def __init__(self, parent):
        super(NewProjectRoundRobinDialog, self).__init__(parent=parent)
        
        self.on_init()

        self.SetTitle("New RoundRobin Project")
        self.Centre()
        self.Show(True)

    def on_init(self):
        self.SetSize((400,300))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Proejct Name: ')
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.project_name_textctrl = wx.TextCtrl(panel)
        import datetime
        today_str = datetime.datetime.today().strftime("%Y_%m_%d")
        self.project_name_textctrl.AppendText('%s_tm' % today_str)
        hbox1.Add(self.project_name_textctrl, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Scheduler: RoundRobin')
        hbox2.Add(st2)
        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))


        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='Team Count: ')
        hbox3.Add(st3, flag=wx.RIGHT, border=8)
        self.team_count_textctrl = wx.TextCtrl(panel)
        hbox3.Add(self.team_count_textctrl, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))


        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='Board Count: ')
        hbox6.Add(st6, flag=wx.RIGHT, border=8)
        self.board_count_textctrl = wx.TextCtrl(panel)
        hbox6.Add(self.board_count_textctrl, proportion=1)
        vbox.Add(hbox6, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 25))

        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        btn7_1 = wx.Button(panel, label='OK', size=(70, 30))
        hbox7.Add(btn7_1)
        btn7_2 = wx.Button(panel, label='Close', size=(70, 30))
        hbox7.Add(btn7_2)
        vbox.Add(hbox7, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_save, btn7_1)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn7_2)

    def on_save(self, e):
        ret, v = self.validate_input()
        if ret:
            # create project
            project = create_project(v["project_name"])
            project.setup_config(
                tm_name="TM", 
                team_count=v["team_count"], 
                board_count=v["board_count"], 
                scheduler_type="RoundRobinScheduler", 
                scheduler_metadata={
                    "match":[],
                    "score": [ [x+1,0] for x in range(v["team_count"]) ],
                    "team_count": v["team_count"],
                    "round_score": [],
                    "current_round": 0
                }, 
                adjustment =[ [x+1, 0.0] for x in range(v["team_count"]) ],
                start_board_number=1,
                end_board_number=start_board_number+board_count-1, 
                section_id=1, 
                section_letter='A'
            )
            self.EndModal(wx.ID_OK)
        else:
            err_dial = wx.MessageDialog(None, v, 'Error', wx.OK | wx.ICON_ERROR)
            err_dial.ShowModal()
            err_dial.Destroy()

    def on_close(self, e):
        self.Close()

    def validate_input(self):
        project_name = self.project_name_textctrl.GetValue()
        team_count = self.team_count_textctrl.GetValue()
        board_count = self.board_count_textctrl.GetValue()

        values = { 
            "project_name":project_name, 
            "team_count": team_count,
            "board_count":board_count, 
        }

        if os.path.exists(get_project_folder(values["project_name"])):
            return False, "Project exist!"

        if not values["team_count"].isdigit():
            return False, "Team count error"
        else:
            values["team_count"] = int(values["team_count"])

        if not values["board_count"].isdigit():
            return False, "Board count error"
        else:
            values["board_count"] = int(values["board_count"])

        return True, values

    def get_project_name(self):
        return self.project_name_textctrl.GetValue()

class NewProjectSWISSDialog(wx.Dialog):
    def __init__(self, parent):
        super(NewProjectSWISSDialog, self).__init__(parent=parent)
        
        self.on_init()

        self.SetTitle("New SWISS Project")
        self.Centre()
        self.Show(True)

    def on_init(self):
        self.SetSize((400,300))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Proejct Name: ')
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.project_name_textctrl = wx.TextCtrl(panel)
        import datetime
        today_str = datetime.datetime.today().strftime("%Y_%m_%d")
        self.project_name_textctrl.AppendText('%s_tm' % today_str)
        hbox1.Add(self.project_name_textctrl, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Scheduler: Swiss')
        hbox2.Add(st2)
        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))


        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='Team Count: ')
        hbox3.Add(st3, flag=wx.RIGHT, border=8)
        self.team_count_textctrl = wx.TextCtrl(panel)
        hbox3.Add(self.team_count_textctrl, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))
        

        # line4 = wx.StaticLine(panel)
        # vbox.Add(line4, border=10)

        # vbox.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(panel, label='Round Count: ')
        hbox5.Add(st5, flag=wx.RIGHT, border=8)
        self.round_count_textctrl = wx.TextCtrl(panel)
        hbox5.Add(self.round_count_textctrl, proportion=1)
        vbox.Add(hbox5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='Board Count: ')
        hbox6.Add(st6, flag=wx.RIGHT, border=8)
        self.board_count_textctrl = wx.TextCtrl(panel)
        hbox6.Add(self.board_count_textctrl, proportion=1)
        vbox.Add(hbox6, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 25))

        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        btn7_1 = wx.Button(panel, label='OK', size=(70, 30))
        hbox7.Add(btn7_1)
        btn7_2 = wx.Button(panel, label='Close', size=(70, 30))
        hbox7.Add(btn7_2)
        vbox.Add(hbox7, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_save, btn7_1)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn7_2)

    def on_save(self, e):
        ret, v = self.validate_input()
        if ret:
            # create project
            project = create_project(v["project_name"])
            project.setup_config(
                tm_name="TM", 
                team_count=v["team_count"], 
                board_count=v["board_count"], 
                scheduler_type="SwissScheduler", 
                scheduler_metadata={
                    "match":[],
                    "round_count": v["round_count"],
                    # TODO: init !!
                    "matchup_table": [ [0 for i in range(v["team_count"]+1)] for j in range(v["team_count"]+1) ],
                    "score": [ [x+1,0] for x in range(v["team_count"]) ],
                    "round_score": [],
                    "current_round": 0
                }, 
                adjustment =[ [x+1, 0.0] for x in range(v["team_count"]) ],
                start_board_number=1,
                end_board_number=v["board_count"], 
                section_id=1, 
                section_letter='A'
            )
            self.EndModal(wx.ID_OK)
        else:
            err_dial = wx.MessageDialog(None, v, 'Error', wx.OK | wx.ICON_ERROR)
            err_dial.ShowModal()
            err_dial.Destroy()

    def on_close(self, e):
        self.Close()

    def validate_input(self):
        project_name = self.project_name_textctrl.GetValue()
        team_count = self.team_count_textctrl.GetValue()
        round_count = self.round_count_textctrl.GetValue()
        board_count = self.board_count_textctrl.GetValue()

        values = { 
            "project_name":project_name, 
            "team_count": team_count,
            "board_count":board_count, 
            "round_count": round_count, 
        }

        if os.path.exists(get_project_folder(values["project_name"])):
            return False, "Project exist!"

        if not values["team_count"].isdigit():
            return False, "Team count error"
        else:
            values["team_count"] = int(values["team_count"])

        if not values["board_count"].isdigit():
            return False, "Board count error"
        else:
            values["board_count"] = int(values["board_count"])

        if not values["round_count"].isdigit():
            return False, "round_count error"
        else:
            values["round_count"] = int(values["round_count"])

        return True, values

    def get_project_name(self):
        return self.project_name_textctrl.GetValue()



class MainApp(wx.App):
    def OnInit(self):
        main_frame = MainFrame()
        main_frame.Show()

        self.SetTopWindow(main_frame)
        return True

