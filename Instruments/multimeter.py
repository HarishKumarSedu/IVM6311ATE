import time

import pyvisa as visa
from pyvisa.attributes import *
from pyvisa.constants import *

class mul_34401A:

    def __init__(self, usb_id):
        rm = visa.ResourceManager()
        # rm.list_resources()
        self.my_instr = rm.open_resource(usb_id)
        self.my_instr.read_termination = '\n'
        self.my_instr.write_termination = '\n'

        # self.reset()
        self.set_Input__Impedence___auto()

    def get_IDN(self):
        return (self.my_instr.query('*IDN?'))

    def reset(self):
        self.my_instr.write('*RST')     

    def get_error(self):
        return self.my_instr.query('SYST:ERR?')  


    def read_value(self, cnt):
        self.my_instr.write(':SAMP:COUN ' + str(cnt) +';:TRIG:SOUR IMM')      
        data_str= self.my_instr.query(':READ?')
        data_split = data_str.split(sep =',')
        value = list(map(float, data_split))
        return(sum(value) / len(value))

    def meas_V(self, range = -1, count = 4):
        # self.my_instr.write(':FUNC "VOLT:DC"') 
        # #Range: Autorange (-1), 100 mV, 1 V, 10 V, 100 V, or 750 V
        # range_list = [-1, 0.1, 1, 10, 100, 750]
        # if range in range_list:
        #     range_auto = ':VOLT:DC:RANG:AUTO '
        #     range_val = ';:VOLT:DC:RANG '
        #     res_com = ';:VOLT:DC:RES '

        #     if range == -1:
        #         range_auto_cmd = 'ON'
        #         range_val = ''
        #         range_val_str = ''
        #         res_com = ''
        #         res_val_str = ''
        #     else:
        #         range_auto_cmd = 'OFF'
        #         range_val_str = str(range)
        #         if range == 0.1 or range == 1:
        #             res = 1e-6
        #         elif range == 10:
        #             res = 1e-5
        #         elif range == 100:
        #             res = 1e-4    
        #         else:   
        #             res = 1e-3
        #         res_val_str = str(res)

        #     com = range_auto + range_auto_cmd +  range_val + range_val_str + res_com + res_val_str
        #     self.my_instr.write(com) 
        #     self.my_instr.write('VOLT:IMP:AUTO ON')
        #     array = []
        #     while count>0:
        #         if count > 4:
        #             cnt = 4
        #         else:
        #             cnt = count 
        #         array.append(self.read_value(cnt))
        #         count -= 4 
        #     return(sum(array)/len(array))   
        # else:
        #     return('ERR: Wrong range')   

        # enable function type to the DC voltage 
        self.my_instr.write('INPut:IMPedance:AUTO ON')
        self.my_instr.write('FUNCtion "VOLTage:DC"')
        # enable the voltage measure range to AUTO
        self.my_instr.write('VOLTage:DC:RANGe:AUTO ON')
        # measure the voltage 
        return float(self.my_instr.query('MEASure:VOLTage:DC?'))

    def set_Input__Impedence___auto(self):
        self.my_instr.write('INPut:IMPedance:AUTO ON')


    

    def meas_I(self, range = -1, count = 4):
        # self.my_instr.write(':FUNC "CURR:DC"') 
        # #Range: : Autorange (-1), 100 µA, 1 mA, 10 mA, 100 mA, 1 A, 3 A, or 10 A
        # range_list = [-1, 100e-6, 1e-3, 0.01, 0.1, 1, 3]
        # if range in range_list:
        #     range_auto = ':CURR:DC:RANG:AUTO '
        #     range_val = ';:CURR:DC:RANG '
        #     res_com = ';:CURR:DC:RES '

        #     if range == -1:
        #         range_auto_cmd = 'ON'
        #         range_val = ''
        #         range_val_str = ''
        #         res_com = ''
        #         res_val_str = ''
        #     else:
        #         range_auto_cmd = 'OFF'
        #         range_val_str = str(range)
        #         if range in list([100e-6, 1e-3]):
        #             res = 1e-9
        #         elif range == 10e-3:
        #             res = 1e-8
        #         elif range == 100e-3:
        #             res = 1e-7   
        #         elif range == 1:
        #             res = 1e-6
        #         else:   
        #             res = 1e-5
        #         res_val_str = str(res)

        #     com = range_auto + range_auto_cmd +  range_val + range_val_str + res_com + res_val_str
        #     self.my_instr.write(com) 
        #     #self.my_instr.write('VOLT:IMP:AUTO ON')
        #     array = []
        #     while count>0:
        #         if count > 4:
        #             cnt = 4
        #         else:
        #             cnt = count 
        #         array.append(self.read_value(cnt))
        #         count -= 4 
        #     return(sum(array)/len(array))   
        # else:
        #     return('ERR: Wrong range')     

        # Set input impedence to AUTO
        self.my_instr.write('INPut:IMPedance:AUTO ON')
        # DC Current Measurment 
        self.my_instr.write('FUNCtion "CURRent:DC"')
        self.my_instr.write('CURRent:DC:RANGe:AUTO ON')
        return float(self.my_instr.query('MEASure:CURRent:DC?'))

if __name__ == '__main__':
    vmeter = mul_34401A('USB0::0x2A8D::0x1301::MY57229855::INSTR')
    print(vmeter.meas_V())
    print(vmeter.get_error())