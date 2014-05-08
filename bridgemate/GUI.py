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
        self.edit_config_btn = wx.Button(self, label='Edit Config', pos=(10,20) )
        self.run_one_round_btn = wx.Button(self, label='Run one round', pos=(10,50) )

        self.Bind(wx.wx.EVT_BUTTON, self.on_edit_config, self.edit_config_btn)
        self.Bind(wx.wx.EVT_BUTTON, self.on_run_one_round, self.run_one_round_btn)

        # Statusbar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('')

        #Other        
        

    def on_quit(self, e):
        self.Close()

    def on_new(self, e):
        import datetime
        today_str = datetime.datetime.today().strftime("%Y_%m_%d")
        dlg = wx.TextEntryDialog(None,'Enter project name:','New Project', '%s_touronment' % today_str)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            project_name = dlg.GetValue()
            self.bm2_manager = create_project(project_name)

            if self.bm2_manager is None:
                err_dial = wx.MessageDialog(None, 'Project exist !', 'Error', wx.OK | wx.ICON_ERROR)
                err_dial.ShowModal()
                err_dial.Destroy()
            else:
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

    def on_edit_config(self, e):
        if self.bm2_manager is None:
            return

        dlg = ProjectConfigFrame(parent=self,config=self.bm2_manager.config)
        if dlg.ShowModal() == wx.ID_OK:
            self.reload_project()
        dlg.Destroy()

    def on_run_one_round(self, e):
        self.bm2_manager.run_one_round()

    def reload_project(self, status_string=''):
        if self.bm2_manager is None:
            self.statusbar.SetStatusText("Please Open / Create project")
            self.SetTitle("Main")
            self.edit_config_btn.Disable()
            self.run_one_round_btn.Disable()

        else:
            self.statusbar.SetStatusText(status_string)
            self.SetTitle(self.bm2_manager.config.project_name)
            self.edit_config_btn.Enable()
            self.run_one_round_btn.Enable()


class ProjectConfigFrame(wx.Dialog):
    def __init__(self, config, parent):
        super(ProjectConfigFrame, self).__init__(parent=parent)
        self.config = config
        
        self.Centre()
        self.Show(True)

    def on_init(self):
        wx.StaticText(self, -1, 'Width:', (20, 20))
        wx.StaticText(self, -1, 'Height:', (20, 70))
        self.sc1 = wx.SpinCtrl(self, -1, str(w), (80, 15), (60, -1), min=200, max=500)
        self.sc2 = wx.SpinCtrl(self, -1, str(h), (80, 65), (60, -1), min=200, max=500)


        save_btn = wx.Button(self, 1, 'Save', (20, 120))
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)


class MainApp(wx.App):
    def OnInit(self):
        main_frame = MainFrame()
        main_frame.Show()

        self.SetTopWindow(main_frame)
        return True

