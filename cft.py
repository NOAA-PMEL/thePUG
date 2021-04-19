'''
dict and list data templates for PopUpGui
also has a test write function

TODO:
Generalize the sensors so that if new sensors are added it is easy to expand this program
'''

class TemplateGen():


    master = [
        ["MASTER\n"],
        ["headerid=", "hid", "\n"],
        ["phone=", "phone_no", "\n"],
        ["release=", "release", "\n"],
        ["gps\n"],
        ["samplestart=", "gps_start", "\n"],
        ["sampleinterval=", "gps_dt", "\n"],
        ["under_ice\n"],
        ["samplestart=", "ice_start", "\n"],
        ["sampleinterval=", "ice_dt", "\n"],
        ["iridium_tx\n"],
        ["samplestart=", "iridium_start", "\n"],
        ["sampleinterval=", "iridium_dt", "\n"],
        ["bottom_sample\n"],
        ["samplestart=", "bottom_start", "\n"],
        ["sampleinterval=", 'bottom_dt', "\n"],
        ["sst_sample\n"],
        ["samplestart=", 'sst_start', "\n"],
        ["sampleinterval=", 'sst_dt', "\n"],
        ["pressure S/N: ", 'p_sn', "\n"],
        ["cal=", "cal_pres"],
        [",", "cal_depth", "\n"],
        ["probe1 S/N: ", "probe1_sn", "\n"],
        ["c1=", "p1c1"],
        [",c2=", "p1c2"],
        [",c3=", "p1c3", "\n"],
        ["probe2 S/N: ", "probe2_sn", "\n"],
        ["c1=", "p2c1"],
        [",c2=", "p2c2"],
        [",c3=", "p2c3", "\n"],
        ["~"]
    ]


    c_info = {
        "hid": "",
        "phone_no": "",
        "release": "",
        "gps_start": "",
        "gps_dt": "",
        "ice_start": "",
        "ice_dt": "",
        "iridium_start": "",
        "iridium_dt": "",
        "bottom_start": "",
        "bottom_dt": "",
        "sst_start": "",
        "sst_dt": "",
        "p_sn": "",
        "cal_pres": "",
        "cal_depth": "",
        "probe1_sn": "",
        "p1c1": "",
        "p1c2": "",
        "p1c3": "",
        "probe2_sn": "",
        "p2c1": "",
        "p2c2": "",
        "p2c3": ""
    }


    dummy = [
        "0001",
        "88160000519",
        "09/15/21",
        "00:02:00",
        "24:00:00",
        "00:10:00",
        "01:00:00",
        "00:15:00",
        "24:00:00",
        "00:10:00",
        "01:00:00",
        "00:10:00",
        "01:00:00",
        "0003",
        "-0.35085681",
        "9.997099147",
        "0001",
        "0.0009014985345945230",
        "0.0002585549554150320",
        "0.000000090371139168705",
        "0002",
        "0.0010487040596532700",
        "0.0002366273872330380",
        "0.000000162236356555533"
        ]


class SelfTests():

    @classmethod
    def dummy_filled(self):

        filled_dummy = []
        c_info = TemplateGen.c_info(self)
        c_items = list(c_info.keys())

        for n in range(len(c_items)):
            c_info[c_items[n]] = TemplateGen.dummy(self)[n]

        for line in TemplateGen.master(self):

            if len(line) == 1:

                filled_dummy.append(line[0])

            elif len(line) == 2:

                temp = line[0] + str(c_info[line[1]])
                filled_dummy.append(temp)

            elif len(line) == 3:

                temp = line[0] + str(c_info[line[1]]) + line[2]
                filled_dummy.append(temp)

        return filled_dummy