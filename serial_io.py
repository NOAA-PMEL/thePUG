import serial
import serial.tools.list_ports as list_ports

def gen_coms_list():
    # generates a list of active com ports for the dropbox

    clist = [str(x) for x in list_ports.comports()]

    return clist

def init_coms(comport):
    if comport != None:

        sp = serial.Serial()

        sp.baudrate = 9600
        sp.timeout = 5
        sp.port = comport[:4]

        if sp.is_open:
            sp.close()

        sp.open()

        return sp

    else:
        return False