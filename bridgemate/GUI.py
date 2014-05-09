import wx
from bridgemate.Bridgemate2Manager import *
from utils.config import PROJECT_FOLDER

MAINFRAME_HEIGHT=400
MAINFRAME_WIDTH=600

ID_MAINFRAME=100


class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(
            parent=None, 
            id=ID_MAINFRAME, 
            style= wx.CAPTION | wx.SYSTEM_MENU  | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.STAY_ON_TOP,
            )
        self.bm2_manager = None
        self.init_UI()
        self.SetSize((MAINFRAME_WIDTH, MAINFRAME_HEIGHT))
        self.Centre()
        self.reload_project()
        

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

        # Button
        self.run_one_round_btn = wx.Button(self, label='Run one round', pos=(10,50) )
        self.Bind(wx.EVT_BUTTON, self.on_run_one_round, self.run_one_round_btn)

        # Statusbar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('')

        #Other     
        # Team count, round count, current round
        # btn: run, start board
        

    def on_quit(self, e):
        self.Close()

    def on_new(self, e):
        dlg = NewProjectFrame(self)
        if dlg.ShowModal() == wx.ID_OK:
            project_name = dlg.get_project_name()
            self.bm2_manager = open_project(project_name)
            self.reload_project()
        dlg.Destroy()

        
    def on_open(self, e):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           )
        dlg.SetPath(PROJECT_FOLDER)
        if dlg.ShowModal() == wx.ID_OK:
            project_name = dlg.GetPath()
            self.bm2_manager = open_project(project_name)
            self.reload_project()
        dlg.Destroy()


    def on_run_one_round(self, e):
        self.bm2_manager.run_one_round()

    def reload_project(self, status_string=''):
        if self.bm2_manager is None:
            self.statusbar.SetStatusText("Please Open / Create project")
            self.SetTitle("Main")
            self.run_one_round_btn.Disable()

        else:
            self.statusbar.SetStatusText(status_string)
            self.SetTitle(self.bm2_manager.config.project_name)
            self.run_one_round_btn.Enable()

class NewProjectFrame(wx.Dialog):
    def __init__(self, parent):
        super(NewProjectFrame, self).__init__(parent=parent)
        
        self.on_init()

        self.SetTitle("New Project")
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
            project.setup_config( tm_name='TM', 
                            team_count=v["team_count"], 
                            scheduler_type="CustomScheduler",
                            scheduler_metadata=
                            {
                                "match":
                                [
                                    [ (1, 1, 2), (2, 2, 1) ]  # Round 1 (table_id, ns_team, ew_team)
                                ]
                            },
                            round_count=v["round_count"],
                            board_count=v["board_count"]
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


class RunFrame(wx.Dialog):
    def __init__(self, parent):
        pass

    def init_ui(self):
        pass


class MainApp(wx.App):
    def OnInit(self):
        main_frame = MainFrame()
        main_frame.Show()

        self.SetTopWindow(main_frame)
        return True

