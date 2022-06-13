
'''
The PUG: PopUpGUI
04/09/21
SJewell, scott.jewell@noaa.gov, https://github.com/shjewellEDD
This provides a GUI interface for generating PopUp calibration files
Reads in fresh calibration data from spreadsheets
Sends data to PopUp embedded electronics
It uses Pickle to store previous calibration data
    If this framework is expanded, a different binary format should be used, as Pickle .dat files are not safe

TODO:
Write cal file
GUI:

Import pre-existing Configs and populate text boxes
    Imports pre-existing configs, but doesn't consider them correct for export
    Need to touch all textboxes that get filled so that they can be written

'''

import GUI

# #the dict which will contain our data is copied from a template in cft.py -> TemplateGen class
def main():
    # # some basic start up stuff, check if there is a .dat file repository

    #app = GUI.PUGApp(redirect=True, filename='GUI_logfile.txt')
    app = GUI.PUGApp()
    app.MainLoop()

if __name__ == '__main__':

    main()

