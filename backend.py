
'''
TODO:
Move startup to main?

'''

import os
import pickle
import pandas as pd
import wx
from datetime import date
from dateutil.parser import parse
import cft
import re

# class StartDialog(wx.App):
#
#     app = wx.App()
#
#     def OpenFile(self):
#         openFileDialog = wx.FileDialog(self, "Select calibration file",
#                                        wildcard="Excel files (*.xlsx;*.xls)|*.xlsx;*.xls",
#                                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
#
#         openFileDialog.ShowModal()
#         path = openFileDialog.GetPath()
#         openFileDialog.Destroy()
#
#         return path

def chk_date_format(input_str):

    new_str = input_str.replace('/', '')

    try:
        dt = parse(new_str)
    except ValueError:
        return False

    return dt.strftime('%m/%d/%y')

def chk_time_format(input_str):

    new_str = input_str.replace(':', '')

    if len(new_str) > 6:
        return False

    if 0 > int(new_str[:2]) > 24:
        return False
    if 0 > int(new_str[2:4]) > 59:
        return False
    if 0 > int(new_str[4:]) > 59:
        return False

def chk_header_format(input_str):
    if len(input_str) > 4:
        return False

    return True


def chk_phone_format(input_str):
    if len(input_str != 10):
        return False

    return True

def import_cal_data(path):
    # import cal data
    # imports an excel sheet containing the calibration data
    # exports a pickle dat file for convienence
    # returns a dictionary containting calibration data and errors

    # this is all going to be very finicky if the excel formatting gets changed around
    # in the future, it will be desirable to make this more robust

    tabs = ["Temp CAL DATA", "Pres CAL DATA"]

    # read in our master calibration file from excel
    data = pd.read_excel(path, sheet_name=tabs, skiprows=[0])

    # extract temperature calibration data
    # we also want to clean it up and warn the user if there are any issues

    temp = data[tabs[0]]
    temp = temp[temp['SN'].notna()]
    tindex = temp.loc[:, 'SN'].astype(int)
    t_cal = temp[['SN', 'Date', "A/C1", "B/C2", "C/C3"]].copy()
    t_cal.index = tindex

    # Slashes(/) play merry hell with our indexing; PURGE THEM
    t_cal.rename(columns={"A/C1": 'AC1', "B/C2": 'BC2', "C/C3": 'CC3'}, inplace=True)
    # t_cal.apply(pd.to_numeric, errors='coerce')
    # t_cal.set_index(t_cal['SN'], drop=True, inplace=True)

    # collect all the rows of data which have bad/incorrectly formatted data
    bad_tdates = list(t_cal[t_cal['Date'].isna()].index)
    bad_tsn = list(t_cal[t_cal['SN'].isna()].index)

    t_cal.drop(labels=bad_tsn, inplace=True)

    t_cal.drop(bad_tsn)
    bad_tcal = set()

    for col in ['AC1', 'BC2', 'CC3']:
        bad_tcal.update(t_cal[t_cal[col].isna()].index)

    t_cal.drop(labels=bad_tcal, inplace=True)

    # Extract Pressure sensor data:
    p_cal = data[tabs[1]]
    p_cal.set_index(p_cal['Sensor'], drop=True, inplace=True)
    p_cal[['Date', 'REF SBE METERS', 'KELLER BAR']].apply(pd.to_numeric, errors='coerce')

    # collect the bad data for warnings
    bad_pdate = list(p_cal[p_cal['Date'].isna()].index)
    bad_pcal = set()

    for col in ['REF SBE METERS', 'KELLER BAR']:
        bad_pcal.update(p_cal[p_cal[col].isna()].index)

    p_cal.drop(labels=bad_pcal, inplace=True)

    # write our calibration data to a .dat, so that this process only needs to be performed for new calibration files
    td = date.today()

    # dat_name = os.path.dirname(os.path.abspath(__file__)) + "\\dat files\\" + "pt_calibration_" + str(td.year) + str(
    #     td.month).rjust(2, '0') + str(td.day).rjust(2, '0') + ".dat"

    package = {'temp': t_cal,
               'pressure': p_cal,
               't serial errors': bad_tsn,
               't date errors': bad_tdates,
               't cal errors': bad_tcal,
               'p date errors': bad_pdate,
               'p cal errors': bad_pcal
               }

    # pickle.dump(package, open(dat_name, 'wb'))

    return package


class ImportData:

    def import_cal_data(self, path):

    # import cal data
    # imports an excel sheet containing the calibration data
    # exports a pickle dat file for convienence
    # returns a dictionary containting calibration data and errors

    # this is all going to be very finicky if the excel formatting gets changed around
    # in the future, it will be desirable to make this more robust

        tabs = ["Temp CAL DATA", "Pres CAL DATA"]

        # read in our master calibration file from excel
        data = pd.read_excel(path, sheet_name=tabs, skiprows=[0])

        # extract temperature calibration data
        # we also want to clean it up and warn the user if there are any issues

        temp = data[tabs[0]]
        temp = temp[temp['SN'].notna()]
        tindex= temp.loc[:, 'SN'].astype(int)
        t_cal = temp[['SN', 'Date', "A/C1", "B/C2", "C/C3"]].copy()
        t_cal.index = tindex

        # Slashes(/) play merry hell with our indexing; PURGE THEM
        t_cal.rename(columns={"A/C1": 'AC1', "B/C2": 'BC2', "C/C3": 'CC3'}, inplace=True)
        #t_cal.apply(pd.to_numeric, errors='coerce')
        #t_cal.set_index(t_cal['SN'], drop=True, inplace=True)

        # collect all the rows of data which have bad/incorrectly formatted data
        bad_tdates = list(t_cal[t_cal['Date'].isna()].index)
        bad_tsn = list(t_cal[t_cal['SN'].isna()].index)

        t_cal.drop(labels=bad_tsn, inplace=True)

        t_cal.drop(bad_tsn)
        bad_tcal = set()

        for col in ['AC1', 'BC2', 'CC3']:
            bad_tcal.update(t_cal[t_cal[col].isna()].index)

        t_cal.drop(labels=bad_tcal, inplace=True)

        # Extract Pressure sensor data:
        p_cal = data[tabs[1]]
        p_cal.set_index(p_cal['Sensor'], drop=True, inplace=True)
        p_cal[['Date', 'REF SBE METERS', 'KELLER BAR']].apply(pd.to_numeric, errors='coerce')

        #collect the bad data for warnings
        bad_pdate = list(p_cal[p_cal['Date'].isna()].index)
        bad_pcal = set()

        for col in ['REF SBE METERS', 'KELLER BAR']:
            bad_pcal.update(p_cal[p_cal[col].isna()].index)

        p_cal.drop(labels=bad_pcal, inplace=True)

        # write our calibration data to a .dat, so that this process only needs to be performed for new calibration files
        td = date.today()

        dat_name = os.path.dirname(os.path.abspath(__file__)) + "\\dat files\\" + "pt_calibration_" + str(td.year) + str(td.month).rjust(2, '0') + str(td.day).rjust(2, '0') + ".dat"

        package = {'temp':              t_cal,
                   'pressure':          p_cal,
                   't serial errors':   bad_tsn,
                   't date errors':     bad_tdates,
                   't cal errors':      bad_tcal,
                   'p date errors':     bad_pdate,
                   'p cal errors':      bad_pcal
                   }

        pickle.dump(package, open(dat_name, 'wb'))

        return package


    def p_sensor_format(sn):

        return "P" + str(sn).rjust(4, '0')


    def importConfig(self, path):

        config = {}
        master = cft.TemplateGen.master
        cinfo = cft.TemplateGen.c_info

        # this monstrosity is a map,
        # first element in the inner list is the internal key
        # second element in the inner list is number of rows down outer keys the actual info is
        # third element in the inner list is where in the split line the desired element will come from
        c_groups = {'MASTER': [['h_id', 1], ['phone_no', 2], ['release', 3]],
                    'gps': [['gps_start', 1], ['gps_dt', 2]],
                    'under_ice': [['ice_start', 1], ['ice_dt', 2]],
                    'iridium_tx': [['iridium_start', 1], ['iridium_dt', 2]],
                    'bottom_sample': [['bottom_start', 1], ['bottom_dt', 2]],
                    'sst_sample': [['sst_start', 1], ['sst_dt', 2]],
                    'pressure S/N': [['p_sn', 0, 1], ['cal_pres', 1, 1], ['cal_depth', 1, 2]],
                    'probe1 S/N': [['probe1_sn', 0, 1], ['p1c1', 1, 1], ['p1c2', 1, 3], ['p1c3', 1, 5]],
                    'probe2 S/N': [['probe2_sn', 0, 1], ['p2c1', 1, 2], ['p2c2', 1, 3], ['p2c3', 1, 5]]
                    }

        raw = []

        # it's not terribly efficient, but it's easier to read the config into list
        # and and then break it down into the desired chunks
        with open(path, "r") as f:

            for line in f.readlines():
                line = line.replace("\n", "")
                raw.append(line)

        headings = list(c_groups.keys())

        for n in range(len(raw)):

            # this searchers for the group headings in the config
            if raw[n] in headings:

                for sect in c_groups[raw[n]]:
                    config[sect[0]] = raw[n + sect[1]].split("=")[1]

            # this breaks down the calibration portion of the config, which is more complex and difficult to deal with
            elif raw[n].split(":")[0] in headings:

                for sect in c_groups[raw[n].split(":")[0]]:
                    delims = re.split("[=:,P]+", raw[n + sect[1]].replace(' ', ''))

                    config[sect[0]] = delims[sect[2]]

        return config


    def startup(self):

        # some basic start up stuff, check if there is a .dat file repository
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        dats_dir = cur_dir + '\\dat files'

        # if there isn't, create one
        if not os.path.exists(dats_dir):
            os.mkdir(dats_dir, mode=0o777)

        dats = []

        # list the dat files
        for dat in os.listdir(dats_dir):

            if ".dat" in dat:
                dats.append(dat)

        # TEMPORARY, remove this things have been converted to strings
        # ImportData.import_cal_data(dats_dir)

        # if there aren't any dat files, create one from a spreadsheet
        if len(dats) == 0:

            #cal_pack = ImportData.import_cal_data(StartDialog.OpenFile(self))
            fpath = 'C:\\Users\jewell\\Documents\\PopUps\\GUI\\steinhart_hart_calculator_2019 REFORMAT.xlsx'
            if os.path.exists(fpath):
                cal_pack = ImportData.import_cal_data(self, fpath)
            else:
                cal_pack = None

        # find the most recent dat file, they should have their creation date in the filename
        else:
            most_recent = "00000000.dat"

            for file in dats:

                if int(file[-12:-4]) > int(most_recent[-12:-4]):
                    most_recent == file

            cal_pack = pickle.load(open(dats_dir + '\\' + file, 'rb'))

        return cal_pack

# class ImportConfig:
#     def __init__(self):
#
#         self.template = cft.TemplateGen.master
#         self.inputs = cft.TemplateGen.c_info
#
#     def readConfig(self, config_path):


