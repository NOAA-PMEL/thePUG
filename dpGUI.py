'''
v2 of the GUI portion

dearpygui runs off the GPU, making it parallel to the rest of the process
This hopefully will help performance over the wx GUI
TODO:
    Sampling Tab
        Read in config
    Calibration tab
        Read in calibration
    Serial_IO
        Get reading working
        Write config

'''

# external packages
import dearpygui.dearpygui as dpg
import os
import time
import serial
import serial.tools.list_ports as list_ports
import threading
import datetime

# other PUG packages
import backend
import cft
import serial_io


def chk_date_format(input_str):

    new_str = input_str.replace('/', '')

    if len(new_str) >= 6:
        return f'{new_str[:2]}/{new_str[2:4]}/{new_str[4:6]}'

    return new_str


def chk_header_format(input_str):
    pass


def chk_phone_format(input_str):
    pass

class PUG():
    def __init__(self):
        self.sp = serial.Serial()
        self.current_com = None
        self.cancelFlag = False
        self.serial_buff = []
        self.GUI()

    def write_config(self):

        header_id = dpg.get_value('header')

        with open(file_name, 'w+') as writer:
            writer.write(header_id)
            writer.write('\n')

    # def store_config(sender, user_data, app_data):
    #
    #     print(sender, user_data, app_data)
    #     print(dpg.get_item_info(sender))
    #     dpg.item_
    #     #our_config[]

    def list_coms(self):
        '''
        Calls com list generator in backend.py,
        Updates combo boxes in menu bar and Serial I/O tab

        Should have a popup error for no detected COMs, but that doesn't seem to work. Might need a parent object.
        :return:
        '''
        self.current_com = None
        dpg.set_value('tab_com_list', '')
        dpg.set_value('menu_com_list', '')

        dpg.configure_item('io_read', show=False)
        dpg.configure_item('io_write', show=False)

        coms = serial_io.gen_coms_list()

        # I don't think this works
        if len(coms) < 0:
            # with dpg.window(parent='primary', tag='empty_coms', modal=True, show=False):
            #     dpg.add_text('No COMS detected!')
            #     dpg.add_text('Check connection or drivers')
            #     dpg.add_button('Close', close=lambda: dpg.close_popup('empty_coms'))
            self.pop_window('empty_coms', 'No COMS detected!', f'Check connection or drivers')

        else:
            dpg.configure_item('menu_com_list', items=coms)
            dpg.configure_item('tab_com_list', items=coms)

    def set_com(self, sender, user_data, app_data):

        if user_data != '':
            dpg.configure_item('io_read', show=True)
            dpg.configure_item('io_write', show=True)

        if user_data == 'tab':
            self.current_com = dpg.get_value('tab_com_list')
            dpg.set_value('menu_com_list', self.current_com)
        elif user_data == 'menu':
            self.current_com = dpg.get_value('menu_com_list')
            dpg.set_value('tab_com_list', self.current_com)

        sr = serial_io.init_coms(self.current_com)

        #if sr:


    def deact_after_edit(self, sender, user_data, app_data):

        def switch_case(case):
            return {'header':    chk_header_format,
                    'phone_no':  chk_phone_format,
                    'release':   chk_date_format
                    }.get(user_data, '')

        updated_str = switch_case(user_data)(dpg.get_value(user_data))

        dpg.set_value(user_data, updated_str)

    def truncate_text_input(self, sender, user_data, app_data):

        def switch_case(case):
            return {'header':    4,
                    'phone_no':  10,
                    'release':   8
                    }.get(case, 1024)

        if len(dpg.get_value(user_data)) > switch_case(user_data):
            dpg.set_value(user_data, dpg.get_value(user_data)[:switch_case(user_data)])

        #print(user_data, len(dpg.get_value(user_data)), switch_case(user_data))

        # if dpg.get switch_plot(user_data)(dpg.get_value(user_data))

    def string_pusher(self, message):
        # this function handles strings
        # strings need to be written one character at a time
        # other wise the PuF will only recieve the last character

        #logger.info(['Writing ', message, ' to serial'])

        for letter in message:
            self.sp.flush()
            self.sp.write(bytearray(letter, 'ascii'))
            time.sleep(0.01)

    def y_press(self):
        # simulates pressing the 'y' key
        #logger.info('Pressing y key')
        self.sp.flush()
        self.sp.write(bytearray('y', 'ascii'))

    def set_com(self, sender):

        self.current_com = dpg.get_value(sender)

        dpg.set_value('menu_com_list', self.current_com)
        dpg.set_value('tab_com_list', self.current_com)

        if serial_io.init_coms(self.current_com):
            self.update_log(f'Connected to {self.current_com}')
        else:
            self.update_log(f'Failed to connect to {self.current_com}')

        if not self.current_com:
            self.pop_window('no_com_selected', 'No COM Selected!', f'Select a COM port!')

        if not self.sp:
            self.pop_window('bad_com', 'Bad COM!', f'Failed to connect to {self.current_com}!')

        dpg.configure_item('io_read', show=True)
        dpg.configure_item('io_write', show=True)
        dpg.configure_item('abort', show=True)
        dpg.enable_item('io_read')
        dpg.enable_item('io_write')

    def read_serial(self):
        # logger.info('Reading from serial')

        self.update_log(f'Connecting...')
        log = []
        logger = False
        self.y_press()

        while True:
            if self.cancelFlag:
                self.update_log(f'Cancelled')
                dpg.disable_item('abort')
                dpg.enable_item('io_read')
                dpg.enable_item('menu_pop_read')
                return

            a = self.sp.readline()
            # print(str(a))dae
            # logger.info(['Received from serial: ', a])

            if not a.isascii():
                self.update_log(f'Aborting. . .')
                self.update_log(f'Bad character returned; update your firmware!')
                dpg.disable_item('cancel')
                dpg.enable_item('start_read')

                break

            dpg.configure_item('log', items=[f'{self.readableCfg(str(a))}'] + [{dpg.get_value("log")}])
            self.update_log(f'{self.readableCfg(str(a))}')
            # POP-UP gets sent back through serial.readline after a bad command has been sent, annoyingly, so we
            # simulate 'y' key presses until it appears
            if 'POP-UP' in str(a):
                self.update_log(f'Reading Config')
                self.string_pusher(' status\n')
                continue
            # '~' is the EOF character for configs
            elif "~" in str(a):
                self.update_log(f'Completed')
                dpg.disable_item('cancel')
                dpg.enable_item('start_read')
                return log
            # pound the 'y' key until it reacts
            else:
                time.sleep(.5)
                self.y_press()

            # 'header' is the first line of a config, so start logging once it appears
            if "Header" in str(a):
                logger = True
            # log stuff
            if logger:
                log = log + [str(a)]

    def init_read(self):
        self.cancelFlag = False
        dpg.enable_item('abort')
        dpg.disable_item('start_read')
        threading.Thread(target=self.read_serial).start()

    def init_write(self):
        pass

    def cancel_read(self):

        self.cancelFlag = True
        dpg.enable_item('cancel')
        dpg.endable_item('menu_pop_read')
        dpg.disable_item('io_read')

    def update_log(self, new_lines):

        if new_lines == '':
            pass

        self.serial_buff = [f'{datetime.datetime.now().strftime("%H:%M:%S")}: {new_lines}'] + self.serial_buff
        dpg.configure_item('serial_monitor', items=self.serial_buff)



    '''
    ========================================================================================================================
    Begin GUI
    '''

    def close_window(self, sender, app_data, user_data):

        dpg.configure_item(user_data, modal=False)
        dpg.configure_item(user_data, show=False)

    def pop_window(self, tag, title, text):

        with dpg.window(label=title, tag=tag, modal=True):
            dpg.add_text(text)
            dpg.add_button(label='Close', user_data=tag, callback=self.close_window)

    def GUI(self):

        dpg.create_context()

        with dpg.item_handler_registry(tag='widget handler') as handler:
            dpg.add_item_deactivated_after_edit_handler(callback=self.deact_after_edit)
            dpg.add_item_focus_handler(callback=self.truncate_text_input)
            # dpg.add_item_visible_handler(callback=truncate_text_input)
            # dpg.add_item_active_handler(callback=truncate_text_input)

        with dpg.window(tag='primary'):

            with dpg.menu_bar():
                with dpg.menu(label='File'):
                    dpg.add_menu_item(label='Load Config')
                    dpg.add_menu_item(label='Verify Config')
                    dpg.add_menu_item(label='Save Config', callback=self.init_write)
                    dpg.add_menu_item(label='Clear Config')
                    dpg.add_menu_item(label='Exit')

                with dpg.menu(label='Calibration'):
                    dpg.add_menu_item(label='Load Calibration Spreadsheet')

                with dpg.menu(label='PopUp I/O'):
                    dpg.add_menu_item(label='Refresh Serial List', callback=self.list_coms)
                    dpg.add_combo(tag='menu_com_list', label='Select COM', user_data='menu', callback=self.set_com)
                    dpg.add_menu_item(tag='menu_pop_check', label='Check Config', enabled=False)
                    dpg.add_menu_item(tag='menu_pop_read', label='Import Config', enabled=False)
                    dpg.add_menu_item(tag='menu_pop_reboot', label='Reboot PopUp', enabled=False)

            with dpg.tab_bar():

                with dpg.tab(label='Basic Info'):

                    dpg.add_text('Header ID:')
                    dpg.add_input_text(tag='header', user_data='hid', no_spaces=True, uppercase=True, hint='NNNN')

                    dpg.add_text('Satellite Phone #:')
                    dpg.add_input_text(tag='phone', user_data='phone_no', decimal=True, hint='NNNNNNNNNN', no_spaces=True)

                    dpg.add_text('Release Date')
                    dpg.add_input_text(tag='release', user_data='release', hint='DD/MM/YY', decimal=True, no_spaces=True)

                    dpg.add_button(label='Enter', tag='go_button', callback=self.init_write)

                with dpg.tab(label='Sampling'):
                    '''
                    [gpsstart, gpsinterval, bottomstart, bottominterval, icestart, iceinterval, irstart, irinterval,
                     sststart, sstinterval]
                     '''

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('GPS Start:')
                        dpg.add_input_text(tag='gpsstart', hint='HH:MM:SS', width=75)
                        dpg.add_text('GPS Interval:')
                        dpg.add_input_text(tag='gpsinterval', hint='HH:MM:SS', width=75)

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('Bottom Start:')
                        dpg.add_input_text(tag='bottomstart', hint='HH:MM:SS', width=75)
                        dpg.add_text('Bottom Interval:')
                        dpg.add_input_text(tag='bottominterval', hint='HH:MM:SS', width=75)

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('Ice Start:')
                        dpg.add_input_text(tag='icestart', hint='HH:MM:SS', width=75)
                        dpg.add_text('Ice Interval:')
                        dpg.add_input_text(tag='iceinterval', hint='HH:MM:SS', width=75)

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('Iridium Start:')
                        dpg.add_input_text(tag='irstart', hint='HH:MM:SS', width=75)
                        dpg.add_text('Iridium Interval:')
                        dpg.add_input_text(tag='irinterval', hint='HH:MM:SS', width=75)

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('SST Start:')
                        dpg.add_input_text(tag='sststart', hint='HH:MM:SS', width=75)
                        dpg.add_text('SST Interval:')
                        dpg.add_input_text(tag='sstinterval', hint='HH:MM:SS', width=75)

                with dpg.tab(label='Calibrations'):

                    with dpg.group(horizontal=True):
                        dpg.add_text('No calibration file', tag='cal_file')
                        dpg.add_button(label='Import Calibration File')

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('Thermometer #1')
                        dpg.add_combo(tag='therm1', width=75)
                        dpg.add_text('Thermometer #2')
                        dpg.add_combo(tag='therm2', width=75)

                    with dpg.group(horizontal=True, xoffset=250):
                        dpg.add_listbox(tag='thermcals1', width=200)
                        dpg.add_listbox(tag='thermcals2', width=200)

                    with dpg.group(horizontal=True, xoffset=125):
                        dpg.add_text('Pressure Sensor')
                        dpg.add_combo(tag='pres', width=75)

                    dpg.add_listbox(tag='prescals', width=200)

                with dpg.tab(label='Serial I/O', tag='serialio'):

                    with dpg.group(horizontal=True, xoffset=150):
                        dpg.add_text('Select COM port')
                        dpg.add_button(label='Refresh COM list', callback=self.list_coms)
                    dpg.add_combo(tag='tab_com_list', user_data='tab', callback=self.set_com)

                    dpg.add_listbox(tag='serial_monitor', label='Serial Monitor', width=450)

                    with dpg.group(horizontal=True,):
                        dpg.add_button(tag='io_read', label='Read From PopUp', enabled=False, show=False)
                        dpg.add_button(tag='io_write', label='Write To PopUp', enabled=False, show=False)
                        dpg.add_button(tag='abort', label='Cancel', enabled=False, show=False)



        dpg.bind_item_handler_registry('phone', 'widget handler')
        dpg.bind_item_handler_registry('header', 'widget handler')
        dpg.bind_item_handler_registry('release', 'widget handler')

        dpg.create_viewport(title='The PopUp GUI', width=600, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary', True)
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == '__main__':

    our_config = cft.TemplateGen.c_info
    file_name = 'dpg_test.txt'

    PUG()