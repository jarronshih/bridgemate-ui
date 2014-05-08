import wx
from bridgemate.Bridgemate2Manager import *
from utils.config import PROJECT_FOLDER

MAINFRAME_HEIGHT=400
MAINFRAME_WIDTH=600


class MainFrame(wx.Frame):
    def __init__(self, parent=None, id=-1, title="Main"):
        super(MainFrame, self).__init__(
            parent=parent, 
            id=id, 
            title=title,
            style= wx.CAPTION | wx.SYSTEM_MENU  | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.STAY_ON_TOP,
            )

        self.InitUI()
        self.SetSize((MAINFRAME_WIDTH, MAINFRAME_HEIGHT))
        self.Centre()
        

    def InitUI(self):
        # Top Menu
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        file_menu = wx.Menu()
        menubar.Append(file_menu, '&File')

        new_item = file_menu.Append(wx.ID_NEW, '&New\tCtrl+N')
        open_item = file_menu.Append(wx.ID_OPEN, '&Open\tCtrl+O')
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')

        self.Bind(wx.EVT_MENU, self.OnNew, new_item)
        self.Bind(wx.EVT_MENU, self.OnOpen, open_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)

        #Other        
        

    def OnQuit(self, e):
        self.Close()

    def OnNew(self, e):
        import datetime
        today_str = datetime.datetime.today().strftime("%Y_%m_%d")
        dlg = wx.TextEntryDialog(None,'Enter project name:','New Project', '%s_touronment' % today_str)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            project_name = dlg.GetValue()
            print "You chose %s" % project_name
        dlg.Destroy()
        
    def OnOpen(self, e):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           )
        dlg.SetPath(PROJECT_FOLDER)
        if dlg.ShowModal() == wx.ID_OK:
            project_name = dlg.GetPath()
            print "You chose %s" % project_name
        dlg.Destroy()



class MainApp(wx.App):
    def OnInit(self):
        main_frame = MainFrame()
        main_frame.Show()

        self.SetTopWindow(main_frame)
        return True

