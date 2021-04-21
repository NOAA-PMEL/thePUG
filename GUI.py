'''
GUI is the gui elemens for the PUG

TODO:
generalize format
generalize textbox information
    This is so that if a configuration is read in, it will populate the textboxes with pre-existing information
    Should hookup with a info template from cft.py
error popup for badly formatted inputs
Maybe a file bar?
'''


import wx
#from wx.lib.pubsub import Publisher
import pandas
import pickle
import os
import cft
import backend
import copy

# BaseTab is for entry of basic configuration information: ID, date, phone number
# also is the location of the write path and import calibration path

class BaseTab(wx.Panel):
    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)
        super(BaseTab, self).__init__(parent, size=(350, 400))
        panel = wx.Panel(self, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        #sizer.Add(self.btn, 0, wx.ALIGN_CENTER)

        self.InitUI()

    def InitUI(self):

        wx.StaticText(self, label="Header ID:", pos=(5, 10))
        self.id = wx.TextCtrl(self, -1, "", pos=(5, 30))

        wx.StaticText(self, label="Phone #:", pos=(5,80))
        self.phone = wx.TextCtrl(self, -1, "", pos=(5, 100))

        wx.StaticText(self, label="Release Date:", pos=(5, 150))
        self.rel_date = wx.TextCtrl(self, -1, "", pos=(5, 170))

        wx.StaticText(self, label="Configuration Write Location", pos=(200, 10))
        path = "\\".join(os.path.abspath(__file__).split("\\")) + "\\config.txt"
        self.write_path = wx.FilePickerCtrl(self, wx.FLP_SAVE, path=path, pos=(200, 30),)


        self.btn = wx.Button(self, -1, "Write Configuration", pos=(200, 100))
        self.btn.Bind(wx.EVT_BUTTON, self.WriteConfig)

    def WriteConfig(self, event):
        #global our_config
        self.our_config = Backend.our_config

        self.our_config['hid'] = self.id.GetValue()
        self.our_config['phone_no'] = self.phone.GetValue()
        self.our_config['release'] = self.rel_date.GetValue()

        missing = []
        k_list = list(self.our_config.keys())
        #It would be nice to have a error popup here
        for n in range(len(k_list)):
            if self.our_config[k_list[n]] == '':
                missing.append(k_list[n])

        # if len(missing) >= 1:
        #     miss_str = ""
        #     for n in missing:
        #         miss_str += n + ", "
        #
        #     wx.MessageBox(miss_str, 'Missing Info',
        #                   wx.OK | wx.ICON_INFORMATION)
        #else:
        cft.Output.WriteConfig(cft.Output, self.our_config, self.write_path.GetPath())


class SamplingTab(wx.Panel):
    global data_pack

    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)
        super(SamplingTab, self).__init__(parent, size=(350, 400))   # size doesn't seem to do anything
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.InitUI()

    def InitUI(self):
        #global data_pack
        self.data_pack = Backend.data_pack

        #GPS sampling
        wx.StaticText(self, label="GPS:", pos=(5, 10))
        self.gpsstart = wx.TextCtrl(self, -1, "", pos=(5, 30))
        self.gpsstart.SetHint("Start HH:MM:DD")
        self.gpsstart.Bind(wx.EVT_TEXT, self.GPSSample)
        self.gpsinterval = wx.TextCtrl(self, -1, "", pos=(5, 55))
        self.gpsinterval.SetHint("Interval HH:MM:DD")
        self.gpsinterval.Bind(wx.EVT_TEXT, self.GPSSample)

        # Under Ice Sampling
        wx.StaticText(self, label="Under Ice:", pos=(150, 10))
        self.icestart = wx.TextCtrl(self, -1, "", pos=(150, 30))
        self.icestart.SetHint("Start HH:MM:DD")
        self.icestart.Bind(wx.EVT_TEXT, self.IceSample)
        self.iceinterval = wx.TextCtrl(self, -1, "", pos=(150, 55))
        self.iceinterval.SetHint("Interval HH:MM:DD")
        self.iceinterval.Bind(wx.EVT_TEXT, self.IceSample)

        # Bottom Sampling
        wx.StaticText(self, label="Bottom:", pos=(5, 90))
        self.bottomstart = wx.TextCtrl(self, -1, "", pos=(5, 110))
        self.bottomstart.SetHint("Start HH:MM:DD")
        self.bottomstart.Bind(wx.EVT_TEXT, self.BottomSample)
        self.bottominterval = wx.TextCtrl(self, -1, "", pos=(5, 135))
        self.bottominterval.SetHint("Interval HH:MM:DD")
        self.bottominterval.Bind(wx.EVT_TEXT, self.BottomSample)

        # Iridium Sampling
        wx.StaticText(self, label="Iridium:", pos=(150, 90))
        self.irstart = wx.TextCtrl(self, -1, "", pos=(150, 110))
        self.irstart.SetHint("Start HH:MM:DD")
        self.irstart.Bind(wx.EVT_TEXT, self.IrSample)
        self.irinterval = wx.TextCtrl(self, -1, "", pos=(150, 135))
        self.irinterval.SetHint("Interval HH:MM:DD")
        self.irinterval.Bind(wx.EVT_TEXT, self.IrSample)

        # SST Sampling
        wx.StaticText(self, label="SST:", pos=(5, 180))
        self.sststart = wx.TextCtrl(self, -1, "", pos=(5, 200))
        self.sststart.SetHint("Start HH:MM:DD")
        self.sststart.Bind(wx.EVT_TEXT, self.SSTSample)
        self.sstinterval = wx.TextCtrl(self, -1, "", pos=(5, 225))
        self.sstinterval.SetHint("Interval HH:MM:DD")
        self.sstinterval.Bind(wx.EVT_TEXT, self.SSTSample)

    def GPSSample(self, event):
        #global our_config
        self.our_config = Backend.our_config

        if self.gpsstart.GetValue() != "":
            self.our_config['gps_start'] = self.gpsstart.GetValue()
        if self.gpsinterval.GetValue() != "":
            self.our_config['gps_dt'] = self.gpsinterval.GetValue()

    def IceSample(self, event):
        #global our_config
        self.our_config = Backend.our_config

        if self.icestart.GetValue() != "":
            self.our_config['ice_start'] = self.icestart.GetValue()
        if self.iceinterval.GetValue() != "":
            self.our_config['ice_dt'] = self.iceinterval.GetValue()

    def BottomSample(self, event):
        #global our_config
        self.our_config = Backend.our_config

        if self.bottomstart.GetValue() != "":
            self.our_config['bottom_start'] = self.bottomstart.GetValue()
        if self.bottominterval.GetValue() != "":
            self.our_config['bottom_dt'] = self.bottominterval.GetValue()

    def IrSample(self, event):
        #global our_config
        self.our_config = Backend.our_config

        if self.irstart.GetValue() != "":
            self.our_config['iridium_start'] = self.irstart.GetValue()
        if self.irinterval.GetValue() != "":
            self.our_config['iridium_dt'] = self.irinterval.GetValue()

    def SSTSample(self, event):
        #global our_config
        self.our_config = Backend.our_config

        if self.sststart.GetValue() != "":
            self.our_config['sst_start'] = self.sststart.GetValue()
        if self.sstinterval.GetValue() != "":
            self.our_config['sst_dt'] = self.sstinterval.GetValue()


class CalTab(wx.Panel):
    def __init__(self, parent):
        #wx.Panel.__init__(self, parent)
        super(CalTab, self).__init__(parent, size=(350, 400))   # size doesn't seem to do anything
        panel = wx.Panel(self, -1)

        self.InitUI()

    def InitUI(self):
        #global data_pack
        self.data_pack = Backend.data_pack

        #dropbox for thermometers
        self.label = wx.StaticText(self, label="Thermometer #1", pos=(50, 30))
        self.label = wx.StaticText(self, label="Thermometer #2", pos=(250, 30))

        # generate a list of calibrated thermometers
        t_sns = {"": ""}
        for sn in list(self.data_pack['temp'].index):
            t_sns[(str(int(sn)).rjust(4,'0'))] = sn

        # generate a list of calibrated barometers
        p_sns = list(self.data_pack['pressure'].index)
        p_sns.insert(0, "")

        # dropboxes for selecting thermometer calibration
        self.combobox1 = wx.ComboBox(self, choices=list(t_sns.keys()), pos=(50, 50))
        self.thermlabel1 = wx.StaticText(self, label='', pos=(50, 80))
        self.Bind(wx.EVT_COMBOBOX, lambda evt1: self.TempCombo(evt1, t_sns, self.data_pack))

        self.combobox2 = wx.ComboBox(self, choices=list(t_sns.keys()), pos=(250, 50))
        self.thermlabel2 = wx.StaticText(self, label='', pos=(250, 80))
        self.Bind(wx.EVT_COMBOBOX, lambda evt2: self.TempCombo(evt2, t_sns, self.data_pack))

        self.label = wx.StaticText(self, label="Barometer", pos=(50, 170))
        self.presbox = wx.ComboBox(self, choices=p_sns, pos=(50, 200))
        self.preslabel = wx.StaticText(self, label='', pos=(50, 230))
        self.Bind(wx.EVT_COMBOBOX, lambda evp: self.TempCombo(evp, t_sns, self.data_pack))

    # for whatever reason, it wouldn't update the output cal date if I made individual functions
    # so one giant one. Fun!
    def TempCombo(self, event, sns, data):
        #global our_config
        self.our_config = Backend.our_config

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
        nb.AddPage(tab2, "Sampling Info")
        nb.AddPage(tab3, "Calibrations")

        # Set sizer
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

# PUG (PopUpGui) main application.
# Basically just starts

class PUGApp(wx.App):

    def OnInit(self):
        self.frame = PUGFrame(parent=None, title="The PUG")
        self.frame.Show()
        return True

class Backend():
    def __init__(self):
        self.our_config = cft.TemplateGen.c_info
        self.data_pack = backend.startup()

    our_config = cft.TemplateGen.c_info
    data_pack = backend.startup()

#path = "C:\\Users\\jewell\\PycharmProjects\\PopUpGUI\\dat files\\pt_calibration_20210413.dat"
#data_pack = pickle.load(open(path, 'rb'))
