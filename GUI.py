'''
GUI is the gui elements for the PUG

TODO:
Maybe a file bar?

Importing a config file causes
'''


import wx
from pubsub import pub
import os
import cft
import backend

# BaseTab is for entry of basic configuration information: ID, date, phone number
# also is the location of the write path and import calibration path

class BaseTab(wx.Panel):
    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)
        super(BaseTab, self).__init__(parent, size=(350, 400))
        panel = wx.Panel(self, -1)
        self.our_config = Backend.our_config
        #self.data_pack = Backend.data_pack

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        #sizer.Add(self.btn, 0, wx.ALIGN_CENTER)

        self.InitUI()

    def InitUI(self):

        wx.StaticText(self, label="Header ID:", pos=(5, 10))
        self.id = wx.TextCtrl(self, -1, "", pos=(5, 30))
        self.id.SetMaxLength(4)
        self.id.Bind(wx.EVT_KILL_FOCUS, self.CheckIDFormat)

        wx.StaticText(self, label="Phone #:", pos=(5,80))
        self.phone = wx.TextCtrl(self, -1, "", pos=(5, 100))
        self.phone.SetMaxLength(12)
        self.phone.Bind(wx.EVT_KILL_FOCUS, self.CheckPhnFormat)

        wx.StaticText(self, label="Release Date:", pos=(5, 150))
        self.rel_date = wx.TextCtrl(self, -1, "", pos=(5, 170))
        self.rel_date.SetHint("DD/MM/YY")
        self.rel_date.SetMaxLength(8)
        self.rel_date.Bind(wx.EVT_KILL_FOCUS, self.CheckDateFormat)

        wx.StaticText(self, label="Configuration Write Location", pos=(200, 10))
        self.path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])
        self.out_disp = wx.TextCtrl(self, -1, str(self.path), pos=(200,30))

        self.get_path = wx.Button(self, -1, "...", pos=(320, 30))
        self.get_path.Bind(wx.EVT_BUTTON, self.getWritePath)
        self.btn = wx.Button(self, -1, "Write Configuration", pos=(200, 60))
        self.btn.Bind(wx.EVT_BUTTON, self.WriteConfig)

        wx.StaticText(self, label="Import Existing Configuration File", pos=(200, 150))
        self.import_config = wx.Button(self, -1, "Import", pos=(200, 170))
        self.import_config.Bind(wx.EVT_BUTTON, self.ImportConfig)

    def getWritePath(self, event):

        with wx.FileDialog(self, message="Configuration Save",
                            wildcard=".txt files (*.txt)|*.txt",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                            defaultDir=self.path, defaultFile="config.txt") as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            new_path = fileDialog.GetPath()
            self.out_disp.Clear()
            self.out_disp.SetLabel(new_path)
            return

    def WriteConfig(self, event):
        # what it says on the tin,
        # calls to backend.py for writing code

        missing = []
        k_list = list(self.our_config.keys())
        # Error checking is done in the GUI as data is input
        for n in range(len(k_list)):
            if self.our_config[k_list[n]] == '':
                missing.append(k_list[n])

        if len(missing) >= 1:
            miss_str = ""
            for n in missing:
                if cft.TemplateGen.human_readable[n] != "":
                    miss_str += cft.TemplateGen.human_readable[n] + ", "

            wx.MessageBox(miss_str, 'Missing Info',
                          wx.OK | wx.ICON_INFORMATION)
        else:
            cft.Output.WriteConfig(cft.Output, self.our_config, self.out_disp.GetValue())

    def ImportConfig(self, event):

        with wx.FileDialog(self, message="Open Config",
                            wildcard=".txt files (*.txt)|*.txt",
                            style=wx.FD_OPEN,
                            defaultDir=self.path) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            new_path = fileDialog.GetPath()

        config = backend.ImportData.importConfig(self, new_path)

        self.id.SetValue(config['h_id'])
        self.id.SetFocus()
        self.phone.SetValue(config['phone_no'])
        self.phone.SetFocus()
        self.rel_date.SetValue(config['release'])
        self.rel_date.SetFocus()
        self.id.SetFocus()

        #wx.PostEvent(self.CheckIDFormat)

        pub.sendMessage('load_config', message=config)


    def CheckIDFormat(self, event):

        id_inf = self.id.GetValue()
        if id_inf == "":
            event.Skip()
            return

        self.id.Clear()

        if id_inf.isdigit() and self.id.IsEmpty():
            self.id.write(id_inf.rjust(4, "0"))
            self.our_config['hid'] = id_inf
        else:
            self.ErrorMsg("ID incorrectly formatted!")
        event.Skip()

    def CheckPhnFormat(self, event):
        pnum = self.phone.GetValue()
        if pnum == "":
            event.Skip()
            return

        pnum.replace("-", "")

        if pnum.isdigit() and len(pnum) >= 10:
            self.our_config['phone_no'] = pnum
        else:
            self.ErrorMsg("Phone number incorrectly formatted!")
        event.Skip()

    def CheckDateFormat(self, event):

        rdate = self.rel_date.GetValue()
        if rdate == "":
            event.Skip()
            return

        rdate = rdate.replace("/", '')

        # actually check date
        if len(rdate) != 6:
            self.ErrorMsg("Release date incorrectly formatted!")
            event.Skip()

        if 0 > int(rdate[:2]) > 12:
            self.ErrorMsg("Release date incorrectly formatted!")
            event.Skip()
        if 0 > int(rdate[2:4]) > 32:
            self.ErrorMsg("Release date incorrectly formatted!")
            event.Skip()

        rdate = rdate[:2] + "/" + rdate[2:4] + "/" + rdate[4:]
        self.rel_date.Clear()
        self.rel_date.write(rdate)
        self.our_config['release'] = self.rel_date.GetValue()

        event.Skip()


    def ErrorMsg(self, msg):

        wx.MessageBox(msg, 'Formatting Error',
                      wx.OK | wx.ICON_INFORMATION)


class SamplingTab(wx.Panel):
    #global data_pack

    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)
        super(SamplingTab, self).__init__(parent, size=(350, 400))   # size doesn't seem to do anything
        pub.subscribe(self.updateSampling, "load_config")
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.our_config = Backend.our_config

        self.InitUI()

    def InitUI(self):

        #GPS sampling
        wx.StaticText(self, label="GPS:",  pos=(5, 10))
        gpsstart = wx.TextCtrl(self, -1, "", name='gps_start', pos=(5, 30))
        gpsinterval = wx.TextCtrl(self, -1, "", name='gps_dt', pos=(5, 55))

        # Under Ice Sampling
        wx.StaticText(self, label="Under Ice:", pos=(150, 10))
        icestart = wx.TextCtrl(self, -1, "", name='ice_start', pos=(150, 30))
        iceinterval = wx.TextCtrl(self, -1, "", name='ice_dt', pos=(150, 55))

        # Bottom Sampling
        wx.StaticText(self, label="Bottom:", pos=(5, 90))
        bottomstart = wx.TextCtrl(self, -1, "", name='bottom_start', pos=(5, 110))
        bottominterval = wx.TextCtrl(self, -1, "", name='bottom_dt', pos=(5, 135))

        # Iridium Sampling
        wx.StaticText(self, label="Iridium:", pos=(150, 90))
        irstart = wx.TextCtrl(self, -1, "", name='iridium_start', pos=(150, 110))
        irinterval = wx.TextCtrl(self, -1, "", name='iridium_dt', pos=(150, 135))

        # SST Sampling
        wx.StaticText(self, label="SST:", pos=(5, 180))
        sststart = wx.TextCtrl(self, -1, "", name='sst_start', pos=(5, 200))
        sstinterval = wx.TextCtrl(self, -1, "", name='sst_dt', pos=(5, 225))

        self.boxes = [gpsstart, gpsinterval, bottomstart, bottominterval, icestart, iceinterval, irstart, irinterval, sststart, sstinterval]
        for box in self.boxes:
            self.buildTxtBox(box)

    def buildTxtBox(self, txt):
        #builds our text boxes
        txt.Bind(wx.EVT_KILL_FOCUS, self.enterText)
        txt.SetMaxLength(8)
        if "dt" in txt.GetName():
            txt.SetHint("Interval: HH:MM:SS")
        else:
            txt.SetHint("Start: HH:MM:SS")

    def updateSampling(self, message):

        labels = ['gps_start', 'gps_dt',
                  'ice_start', 'ice_dt',
                  'iridium_start', 'iridium_dt',
                  'bottom_start', 'bottom_dt',
                  'sst_start', 'sst_dt'
                  ]

        for n in range(len(self.boxes)):

            self.boxes[n].SetValue(message[labels[n]])
            self.boxes[n].SetFocus()

        self.boxes[0].SetFocus()

    def enterText(self, event):

        box = event.GetEventObject()
        tstr = (box.GetValue()).replace(":", "")

        if tstr == "":
            event.Skip()
            return
        if self.TimeCheck(tstr):
            self.our_config[box.GetName()] = tstr[:2] + ":" + tstr[2:4] + ":" + tstr[4:]
            box.Clear()
            box.write(tstr[:2] + ":" + tstr[2:4] + ":" + tstr[4:])
        event.Skip()


    def TimeCheck(self, tstr):

        tstr.replace(':', '')

        # hours
        if not (25 > int(tstr[:2]) >= 0):
            self.ErrorMsg("Hours incorrectly formatted!")
            return False
        # minutes
        if not (60 > int(tstr[2:4]) >= 0):
            self.ErrorMsg("Minutes incorrectly formatted!")
            return False
        # seconds
        if not (60 > int(tstr[4:]) >= 0):
            self.ErrorMsg("Seconds incorrectly formatted!")
            return False

        return True

    def ErrorMsg(self, msg):
        wx.MessageBox(msg, 'Formatting Error',
                      wx.OK | wx.ICON_INFORMATION)

class CalTab(wx.Panel):
    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)
        super(CalTab, self).__init__(parent, size=(350, 400))   # size doesn't seem to do anything
        pub.subscribe(self.updateCals, "load_config")
        panel = wx.Panel(self, -1)
        self.data_pack = Backend.data_pack
        self.our_config = Backend.our_config

        self.InitUI()


    def InitUI(self):

        #dropbox for thermometers
        self.label = wx.StaticText(self, label="Thermometer #1", pos=(50, 30))
        self.label = wx.StaticText(self, label="Thermometer #2", pos=(250, 30))

        if not self.data_pack:
            path = PUGFrame.OpenFile(self)
            self.data_pack = backend.ImportData.import_cal_data(self, path)

        [t_sns, p_sns] = self.instrList(self.data_pack)

        # dropboxes for selecting thermometer calibration
        self.combobox1 = wx.ComboBox(self, choices=list(t_sns.keys()), pos=(50, 50))
        self.thermlabel1 = wx.StaticText(self, label='', pos=(50, 80))
        self.Bind(wx.EVT_COMBOBOX, lambda evt1: self.TempCombo(evt1, t_sns, self.data_pack))

        self.combobox2 = wx.ComboBox(self, choices=list(t_sns.keys()), pos=(250, 50))
        self.thermlabel2 = wx.StaticText(self, label='', pos=(250, 80))
        self.Bind(wx.EVT_COMBOBOX, lambda evt2: self.TempCombo(evt2, t_sns, self.data_pack))

        self.label = wx.StaticText(self, label="Depth Sensor", pos=(50, 170))
        self.presbox = wx.ComboBox(self, choices=p_sns, pos=(50, 200))
        self.preslabel = wx.StaticText(self, label='', pos=(50, 230))
        self.Bind(wx.EVT_COMBOBOX, lambda evp: self.TempCombo(evp, t_sns, self.data_pack))

        path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])
        wx.StaticText(self, label="Import New Calibration File", pos=(200, 170))
        self.read_path = wx.FilePickerCtrl(self, wx.FLP_OPEN, path=path, pos=(200, 200))

        self.btn = wx.Button(self, -1, "Import Calibration", pos=(200, 230))
        self.btn.Bind(wx.EVT_BUTTON, self.ReadCal)

    def instrList(self, data_pack):

        # generate a list of calibrated thermometers
        t_sns = {"": ""}
        for sn in list(self.data_pack['temp'].index):
            t_sns[(str(int(sn)).rjust(4, '0'))] = sn

        # generate a list of calibrated barometers
        p_sns = list(self.data_pack['pressure'].index)
        p_sns.insert(0, "")

        return [t_sns, p_sns]

    def updateCals(self, message):

        # this uses the new serial number to gather calibration data from the cal file
        # so if the calibration data in the config is out of date, it will be updated

        t_sns, p_sns = self.instrList(self.data_pack)

        tp1 = str(int(message['probe1_sn'])).zfill(4)
        if tp1 not in t_sns:
            self.ErrorMsg("Calibaration data for " + tp1 + " not on file!")
        else:
            self.combobox1.SetValue(tp1)
            self.our_config['probe1_sn'] = tp1
            self.our_config["p1c1"] = self.data_pack['temp'].loc[int(tp1), 'AC1']
            self.our_config["p1c2"] = self.data_pack['temp'].loc[int(tp1), 'BC2']
            self.our_config["p1c3"] = self.data_pack['temp'].loc[int(tp1), 'CC3']

        tp2 = str(int(message['probe2_sn'])).zfill(4)
        if tp2 not in t_sns:
            self.ErrorMsg("Calibaration data for " + tp2 + " not on file!")
        else:
            self.combobox2.SetValue(tp2)
            self.our_config['probe2_sn'] = tp2
            self.our_config['p2c1'] = self.data_pack['temp'].loc[int(tp2), 'AC1']
            self.our_config['p2c2'] = self.data_pack['temp'].loc[int(tp2), 'BC2']
            self.our_config['p2c3'] = self.data_pack['temp'].loc[int(tp2), 'CC3']


        pp = 'P' + message['p_sn']
        if pp not in p_sns:
            self.ErrorMsg("Calibaration data for " + pp + " not on file!")
        else:
            self.presbox.SetValue(pp)
            self.our_config['p_sn'] = pp
            self.our_config['cal_pres'] = self.data_pack['pressure'].loc[pp, 'KELLER BAR']
            self.our_config['cal_depth'] = self.data_pack['pressure'].loc[pp, 'REF SBE METERS']


    def ErrorMsg(self, msg):
        wx.MessageBox(msg, '',
                      wx.OK | wx.ICON_INFORMATION)

    # for whatever reason, it wouldn't update the output cal date if I made individual functions
    # so one giant one. Fun!
    def TempCombo(self, event, sns, data):


        # collect our inputs
        tmeter1, tmeter2, pmeter = "", "", ""
        tmeter1 = sns[self.combobox1.GetValue()]
        tmeter2 = sns[self.combobox2.GetValue()]
        pmeter = self.presbox.GetValue()

        # check the first thermometer
        if tmeter1 != "":
            cals1 = "\nA/C1: " + str(data['temp'].loc[tmeter1, 'AC1']) + " \nB/C2: " + str(
                data['temp'].loc[tmeter1, 'BC2']) + " \nC/C3: " + str(data['temp'].loc[tmeter1, 'CC3'])
            self.thermlabel1.SetLabel("Calibration: " + cals1)

            # write calibration data to our bucket
            self.our_config["probe1_sn"] = tmeter1
            self.our_config["p1c1"] = data['temp'].loc[tmeter1, 'AC1']
            self.our_config["p1c2"] = data['temp'].loc[tmeter1, 'BC2']
            self.our_config["p1c3"] = data['temp'].loc[tmeter1, 'CC3']
        else:
            self.thermlabel1.SetLabel("")

        # check the second thermometer
        if tmeter2 != "":
            cals2 = "\nA/C1: " + str(data['temp'].loc[tmeter2, 'AC1']) + " \nB/C2: " + str(
                data['temp'].loc[tmeter2, 'BC2']) + " \nC/C3: " + str(data['temp'].loc[tmeter2, 'CC3'])
            self.thermlabel2.SetLabel("Calibration:" + cals2)

            # write calibration data to our bucket
            self.our_config["probe2_sn"] = tmeter2
            self.our_config["p2c1"] = data['temp'].loc[tmeter2, 'AC1']
            self.our_config["p2c2"] = data['temp'].loc[tmeter2, 'BC2']
            self.our_config["p2c3"] = data['temp'].loc[tmeter2, 'CC3']
        else:
            self.thermlabel2.SetLabel("")

        # check the barometer
        if pmeter != "":
            cals = "\nMeters: " + str(data['pressure'].loc[pmeter, 'REF SBE METERS']) + " \nBar: " + str(
                data['pressure'].loc[pmeter, 'KELLER BAR'])
            self.preslabel.SetLabel("Calibration: " + cals)

            # write calibrationdata to our bucket
            self.our_config["p_sn"] = pmeter
            self.our_config["cal_pres"] = data['pressure'].loc[pmeter, 'REF SBE METERS']
            self.our_config['cal_depth'] = data['pressure'].loc[pmeter, 'KELLER BAR']
        else:
            self.preslabel.SetLabel("")

    def ReadCal(self, event):

        self.data_pack = backend.ImportData.import_cal_data(self, self.read_path.GetPath())

        [t_sns, p_sns] = self.instrList(self.data_pack)

        self.combobox1.Clear()
        self.combobox2.Clear()
        self.presbox.Clear()

        self.combobox1.Append(list(t_sns.keys()))
        self.combobox2.Append(list(t_sns.keys()))
        self.presbox.Append(p_sns)



class PUGFrame(wx.Frame):
    def __init__(self, parent, title):
        super(PUGFrame, self).__init__(parent, title=title, size=(450, 450))

        # Panel and notebook (notebook holds tabs)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # Create tabs
        tab1 = BaseTab(nb)
        tab2 = SamplingTab(nb)
        tab3 = CalTab(nb)

        # Add the windows and name them
        nb.AddPage(tab1, "Basic Info")
        nb.AddPage(tab2, "Sampling")
        nb.AddPage(tab3, "Calibrations")

        # menubar = wx.MenuBar()
        #
        # fileMenu = wx.Menu()
        # fileMenu.Append(wx.ID_OPEN, '&Import Calibration File')
        # fileMenu.Append(wx.ID_SAVE, '&Export Configuration')
        # fileMenu.AppendSeparator()
        # qmi = fileMenu.Append(wx.ID_EXIT, '&Quit\tCtrl+W')
        #
        # self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        #
        # menubar.Append(fileMenu, '&File')
        # self.SetMenuBar(menubar)

        # Set sizer
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

    def OpenFile(self):
        openFileDialog = wx.FileDialog(self, "Select calibration file",
                                       wildcard="Excel files (*.xlsx;*.xls)|*.xlsx;*.xls",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        openFileDialog.ShowModal()
        path = openFileDialog.GetPath()
        openFileDialog.Destroy()

        return path

    def OnQuit(self, e):
        self.Close()

# PUG (PopUpGui) main application.
# Basically just starts

class PUGApp(wx.App):

    def OnInit(self):
        self.frame = PUGFrame(parent=None, title="PopUp Configuration Loader")
        self.frame.Show()
        return True

# lazy gateway to our backend.py datastructures
# grabs data from backend.py method and makes is available more convienently here
class Backend():
    def __init__(self):
        self.our_config = cft.TemplateGen.c_info
        self.data_pack = backend.ImportData.startup()

    our_config = cft.TemplateGen.c_info
    data_pack = backend.ImportData.startup(backend.ImportData)

#path = "C:\\Users\\jewell\\PycharmProjects\\PopUpGUI\\dat files\\pt_calibration_20210413.dat"
#data_pack = pickle.load(open(path, 'rb'))


