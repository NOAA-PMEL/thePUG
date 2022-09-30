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
import numpy as np

# other PUG packages
import backend
import cft
import serial_io

class PUG():
    def __init__(self):
        self.sp = serial.Serial()
        self.current_com = None
        self.cancelFlag = False
        self.serial_buff = []
        self.templates = cft.TemplateGen
        self.new_config = self.templates.c_info
        self.calibrations = None
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

    def deact_after_edit(self, sender, user_data, app_data):

        def switch_case(case):
            return {'header':    backend.chk_header_format,
                    'phone_no':  backend.chk_phone_format,
                    'release':   backend.chk_date_format
                    }.get(user_data, '')

        updated_str = switch_case(user_data)(dpg.get_value(user_data))

        dpg.set_value(user_data, updated_str)

    def truncate_text_input(self, sender, user_data, app_data):

        def switch_case(case):
            return {'header':    4,
                    'phone_no':  10,
                    'release':   8
                    }.get(case, 1024)

        print(f'Input len: {len(dpg.get_value(user_data))} ' \
              f'Limit: {switch_case(user_data)}, ' \
              f'Sender: {sender}, ' \
              f'User data: {user_data}, '
              f'Returned value: {dpg.get_value(user_data)[:switch_case(user_data)]}')

        if len(dpg.get_value(user_data)) > switch_case(user_data):
            dpg.set_value(user_data, dpg.get_value(user_data)[:switch_case(user_data)])

        #print(user_data, len(dpg.get_value(user_data)), switch_case(user_data))

        # if dpg.get switch_plot(user_data)(dpg.get_value(user_data))

    def string_pusher(self, message):
        '''
        this function handles strings
        strings need to be written one character at a time
        other wise the PuF will only recieve the last character
        '''

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
    Config handlers
    '''
    def check_config(self):


        fail_log = []
        fields = ['header', 'phone', 'release', 'gps_start', 'bottom_start', 'ice_start', 'iridium_start', 'sst_start',
                  'gps_dt', 'bottom_dt', 'ice_dt', 'iridium_dt', 'sst_dt']

        def switch_chk(case):
            return {'header':     backend.chk_header_format,
                    'phone':      backend.chk_phone_format,
                    'release':    backend.chk_date_format
                    }.get(case, backend.chk_time_format)

        for field in fields:

            field_content = dpg.get_value(field)

            print(field, f'x{field_content}x Type: {type(field_content)}')
            try:
                is_good = switch_chk(field)(field_content)
            except TypeError:
                fail_log.append(field)
                print(switch_chk(field)(field_content))
                continue

            if is_good:
                continue

            fail_log.append(field)

        if len(fail_log) > 0:

            fail_statement = f''

            for f in fail_log:

                dpg.set_value(f, '')
                fail_statement += f'{self.templates.human_readable[f]} incorrectly formatted!'

            self.pop_window('format_fail', 'Check formatting!', fail_statement)
            print(fail_statement)

        else:

            return True

    '''
    Sensor Interval Template
    '''

    def gen_interval_input(self, instr):

        with dpg.group(horizontal=True, xoffset=150) as interval_input:
            dpg.add_text(f"{self.templates.human_readable[f'{instr}_start']}:")
            dpg.add_input_text(tag=f'{instr}start', hint='HH:MM:SS', width=75)
            dpg.add_text(f"{self.templates.human_readable[f'{instr}_dt']}:")
            dpg.add_input_text(tag=f'{instr}interval', hint='HH:MM:SS', width=75)

        return interval_input

    '''
    Import Calibrations
    
    TODO:
        Add selection
            Exclude selected thermometer calibration from other list
        Read
    
    '''

    def init_temp_cal_table(self, id):

        with dpg.table(tag=id, header_row=True, borders_outerH=True, borders_outerV=True, parent='cal_tab', height=125,
                       scrollY=True, freeze_rows=1) as tc:
            dpg.add_table_column(parent=id, tag=f'{id}_SN', label='SN', width=50)
            dpg.add_table_column(parent=id, tag=f'{id}_date', label='Date Calibrated', width=100)
            dpg.add_table_column(parent=id, tag=f'{id}_ac1', label='Factor 1', width=100)
            dpg.add_table_column(parent=id, tag=f'{id}_bc2', label='Factor 2', width=100)
            dpg.add_table_column(parent=id, tag=f'{id}_cc3', label='Factor 3', width=100)

        return tc

    def init_pres_cal_table(self):

        with dpg.table(tag='prescal', header_row=True, borders_outerH=True, borders_outerV=True, parent='cal_tab',
                       height=125, scrollY=True, freeze_rows=1) as pc:
            dpg.add_table_column(parent='prescals', tag='pc_SN', label='SN', width=50)
            dpg.add_table_column(parent='prescals', tag='pc_date', label='Date Calibrated', width=100)
            dpg.add_table_column(parent='prescals', tag='pc_sbe', label='Ref SBE Meters', width=100)
            dpg.add_table_column(parent='prescals', tag='pc_bar', label='Keller Bar', width=100)

        return pc

    def clear_tables(self):
        '''
        Clears table entries, needed when a new calibration file is read in.
        A little big awkward, it is necessary to delete cells before deleting rows.
        :return:
        '''

        dpg.set_value(item='cal_file', value=f'No Calibrations Loaded')

        cells_to_delete = []
        rows_to_delete = []

        for alias in dpg.get_aliases():

            if 'cell_t' in alias or 'cell_p' in alias:
                cells_to_delete.append(alias)
            elif 'row_t' in alias or 'row_p' in alias:
                rows_to_delete.append(alias)

        for alias in cells_to_delete:
            dpg.delete_item(alias)

        for alias in rows_to_delete:
            dpg.delete_item(alias)

    def update_cal_tables(self, usr, path):

        self.calibrations = backend.import_cal_data(path['file_path_name'])

        temp_cals = self.calibrations['temp'].to_numpy()
        pres_cals = self.calibrations['pressure'].to_numpy()

        self.clear_tables()

        dpg.set_value(item='cal_file', value=f'Cal. File: {path["file_name"]}')

        dpg.configure_item(item='therm1_select', items=self.calibrations['temp'].index.tolist())
        dpg.configure_item(item='therm2_select', items=self.calibrations['temp'].index.tolist())
        dpg.configure_item(item='pres_select', items=self.calibrations['pressure'].index.tolist())
        dpg.enable_item('therm1_select')
        dpg.enable_item('therm2_select')
        dpg.enable_item('pres_select')

        for n, row in enumerate(temp_cals):

            dpg.add_table_row(tag=f'row_t1-{n}', parent='thermcals1')
            # dpg.add_table_row(tag=f'row_t2-{n}', parent='thermcals2')

            # with dpg.item_handler_registry(tag=f'row_handler_1-{n}'):
            #     dpg.add_item_clicked_handler(callback=self.select_instr)
            # with dpg.item_handler_registry(tag=f'row_handler_2-{n}'):
            #     dpg.add_item_clicked_handler(callback=self.select_instr)

            for m, cell in enumerate(row):

                try:
                    if m == 0:
                        dpg.add_text(f'{cell:.4g}', parent=f'row_t1-{n}', tag=f'tcell_1-{n}-{m}')
                    #     dpg.add_text(f'{cell:.4g}', parent=f'row_t2-{n}', tag=f'tcell_2-{n}-{m}')
                    elif m == 1:
                        dpg.add_text(f'{cell:%Y-%m-%d}', parent=f'row_t1-{n}', tag=f'tcell_1-{n}-{m}')
                    #     dpg.add_text(f'{cell:%Y-%m-%d}', parent=f'row_t2-{n}', tag=f'tcell_2-{n}-{m}')
                    elif m == 2 or m == 3 or m == 4:
                        dpg.add_text(f'{cell:.10f}', parent=f'row_t1-{n}', tag=f'tcell_1-{n}-{m}')
                    #     dpg.add_text(f'{cell:.10f}', parent=f'row_t2-{n}', tag=f'tcell_2-{n}-{m}')
                except ValueError:
                    dpg.add_text(f'{cell}', parent=f'row_t1-{n}', tag=f'tcell_1-{n}-{m}')
                #     dpg.add_text(f'{cell}', parent=f'row_t2-{n}', tag=f'tcell_2-{n}-{m}')

        for n, row in enumerate(pres_cals):

            dpg.add_table_row(tag=f'row_p-{n}', parent='prescal')

            for m, cell in enumerate(row):

                try:
                    if m == 0:
                        dpg.add_text(f'{cell:.4g}', parent=f'row_p-{n}', tag=f'cell_p-{n}-{m}')
                    elif m == 1:
                        dpg.add_text(f'{cell:%Y-%m-%d}', parent=f'row_p-{n}', tag=f'cell_p-{n}-{m}')
                    elif m == 2 or m == 3:
                        dpg.add_text(f'{cell:.10f}', parent=f'row_p-{n}', tag=f'cell_p-{n}-{m}')

                except ValueError:
                    dpg.add_text(f'{cell}', parent=f'row_p-{n}', tag=f'cell_p-{n}-{m}')

    def open_cal_file(self, sender, app_data, user_data):
        fd_uid = dpg.generate_uuid()

        with dpg.file_dialog(label='Select Calibration Spreadsheet', width=400, height=400, show=False,
                             callback=lambda s, a, u: self.update_cal_tables(user_data, a), tag=fd_uid,
                             default_path="D:\Data\PopUps\Calibrations\\"):
            dpg.add_file_extension('.xlsx')
            dpg.add_file_extension('.csv')
            dpg.add_file_extension('.xls')
            dpg.add_file_extension('.*')

        dpg.show_item(fd_uid)

    def select_instr(self, sender, app_data):

        if sender == 'therm1_select':

            cal_data = self.calibrations['temp'].loc[int(app_data)]
            cals = self.calibrations['temp'].index.tolist()
            cals.remove(int(app_data))

            self.new_config["probe1_sn"] = app_data
            self.new_config['p1c1'] = cal_data['AC1']
            self.new_config['p1c2'] = cal_data['BC2']
            self.new_config['p1c3'] = cal_data['CC3']

            dpg.configure_item('therm2_select', items=cals)

        if sender == 'therm2_select':

            cal_data = self.calibrations['temp'].loc[int(app_data)]
            cals = self.calibrations['temp'].index.tolist()
            cals.remove(int(app_data))

            self.new_config["probe2_sn"] = app_data
            self.new_config['p2c1'] = cal_data['AC1']
            self.new_config['p2c2'] = cal_data['BC2']
            self.new_config['p2c3'] = cal_data['CC3']

            dpg.configure_item('therm1_select', items=cals)

        if sender == 'pres_select':

            cal_data = self.calibrations['pressure'].loc[app_data]

            self.new_config["p_sn"] = app_data
            self.new_config["cal_pres"] = cal_data['REF SBE METERS']
            self.new_config[ "cal_depth"] = cal_data['KELLER BAR']


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

        with dpg.item_handler_registry(tag='widget_handler') as handler:
            dpg.add_item_clicked_handler()
            dpg.add_item_deactivated_after_edit_handler(callback=self.deact_after_edit)
            #dpg.add_item_focus_handler(callback=self.truncate_text_input)
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
                    dpg.add_menu_item(label='Load Calibration Spreadsheet', callback=self.open_cal_file)
                    dpg.add_menu_item(label='Clear Calibrations', callback=self.clear_tables)

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

                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Check Config', callback=self.check_config)
                        dpg.add_button(label='Enter', tag='go_button', callback=self.init_write)

                with dpg.tab(label='Sampling'):
                    '''
                    [gpsstart, gpsinterval, bottomstart, bottominterval, icestart, iceinterval, irstart, irinterval,
                     sststart, sstinterval]
                     '''

                    self.gen_interval_input('gps')
                    self.gen_interval_input('bottom')
                    self.gen_interval_input('ice')
                    self.gen_interval_input('iridium')
                    self.gen_interval_input('sst')

                with dpg.tab(label='Calibrations', tag='cal_tab'):

                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Import Calibration File', callback=self.open_cal_file)
                        dpg.add_button(label='Clear Calibration Tables', callback=self.clear_tables)

                    dpg.add_text('No calibration file', tag='cal_file')

                    with dpg.group(horizontal=True):
                        dpg.add_text('Thermometer #1')
                        dpg.add_combo(tag='therm1_select', callback=self.select_instr, enabled=False, width=75)
                        dpg.add_text('Thermometer #2')
                        dpg.add_combo(tag='therm2_select', callback=self.select_instr, enabled=False, width=75)
                    self.init_temp_cal_table('thermcals1')

                    # with dpg.group(horizontal=True):

                    # self.init_temp_cal_table('thermcals2')

                    with dpg.group(horizontal=True):
                        dpg.add_text('Pressure Sensor')
                        dpg.add_combo(tag='pres_select', callback=self.select_instr, enabled=False, width=75)
                    self.init_pres_cal_table()

                with dpg.tab(label='Serial I/O', tag='serialio'):

                    with dpg.group(horizontal=True, xoffset=150):
                        dpg.add_text('Select COM port')
                        dpg.add_button(label='Refresh COM list', callback=self.list_coms)
                    dpg.add_combo(tag='tab_com_list', user_data='tab', callback=self.set_com)

                    dpg.add_listbox(tag='serial_monitor', label='Serial Monitor', width=450, num_items=20)

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

    file_name = 'dpg_test.txt'

    PUG()