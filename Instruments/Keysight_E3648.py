import time 
import pyvisa as visa
from pyvisa.attributes import *
from pyvisa.constants import *
from time import sleep
import numpy as np


class E3648:

    def __init__(self,port='GPIB0::7::INSTR') -> None:
        rm = visa.ResourceManager()
        rm.list_resources()
        self.supply = rm.open_resource(port)
        # self.supply.set_visa_attribute(visa.constants.VI_ATTR_ASRL_BAUD, 9600)
        # self.supply.set_visa_attribute(visa.constants.VI_ATTR_ASRL_DATA_BITS, 8)
        # self.supply.set_visa_attribute(visa.constants.VI_ATTR_ASRL_STOP_BITS, VI_ASRL_STOP_TWO)
        # self.supply.set_visa_attribute(visa.constants.VI_ATTR_ASRL_PARITY, visa.constants.VI_ASRL_PAR_NONE)
        self.supply.read_termination = '\n'
        self.supply.write_termination = '\n'
    @property
    def get__IDN(self):
        return self.supply.query('*IDN?')
    @property
    def reset(self):
        return self.supply.query('*RST')
    @property
    def clear(self):
        return self.supply.query('*CLS')

    def setVoltage(self,channel=1, voltage=0.0):
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        self.supply.write(f'VOLT {str(voltage)}')

    def setCurrent(self,channel=1, current=0.0):
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        self.supply.write(f'CURR {str(current)}')

    def setRange(self,channel=1, range=0):
        ''' Set 1 for High range and set 0 for low range'''
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        range = 'HIGH' if range == 1 else 'LOW' 
        self.supply.write(f'VOLTage:RANGe HIGH')

    
    def meas_Voltage(self,channel=1):
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        return float(self.supply.query('MEASure:VOLT?'))
    
    def meas_Voltage(self,channel=1):
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        return float(self.supply.query('MEASure:CURRent?'))
    
    def outp_ON(self,channel=1):
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        return self.supply.write('OUTPut:STATe ON')
    def outp_OFF(self,channel=1):
        self.supply.write(f'INSTrument:NSELect {str(channel)}')
        return self.supply.write('OUTPut:STATe OFF')
    
    def decresing_Ramp(self,channel=1, start_voltage = 4.5, end_voltage = 1 ):
        self.setVoltage(channel=channel, voltage = start_voltage)
        self.outp_ON(channel=1)
        voltage = start_voltage
        step = 0.250
        while voltage >= end_voltage:
            print(voltage)
            voltage = voltage - step
            sleep(0.5)
            self.setVoltage(channel=channel, voltage = voltage)

    def get_voltage(self, channel):
        if channel == 1:
            ch = 'OUT1'
        elif channel == 2:
            ch = 'OUT2'
        else:
            ch = 'OUT1'
        
        command = 'INST:SEL ' +  ch
        self.supply.write(command)   
        time.sleep(0.2)
        return self.supply.query('MEAS:VOLT?')

    def get_current(self, channel):
        if channel == 1:
            ch = 'OUT1'
        elif channel == 2:
            ch = 'OUT2'
        else:
            ch = 'OUT1'
        
        command = 'INST:SEL ' +  ch
        self.supply.write(command)   
        time.sleep(0.2)
        return self.supply.query('MEAS:CURR?')   
 

    class OutputControl:
        def __init__(self, port='GPIB0::7::INSTR') -> None:
            self.supply = E3648(port).supply  
        
        def output_on(self, channel1=1, channel2=2, voltage1=0.0, voltage2=0.0, current1=0.0, current2=0.0):
            self.supply.write(f'INSTrument:NSELect {channel1}')
            self.supply.write(f'VOLT {voltage1}')
            sleep(1)
            self.supply.write(f'INSTrument:NSELect {str(channel1)}')
            self.supply.write(f'CURR {str(current1)}')
            sleep(1)
            self.supply.write(f'INSTrument:NSELect {channel2}')
            self.supply.write(f'VOLT {voltage2}')
            sleep(1)
            self.supply.write(f'INSTrument:NSELect {str(channel2)}')
            self.supply.write(f'CURR {str(current2)}')
            sleep(1)
            self.supply.write(f'INSTrument:NSELect {channel1}')
            self.supply.write('OUTPut:STATe ON')
            sleep(0.5)
            self.supply.write(f'INSTrument:NSELect {channel2}')
            self.supply.write('OUTPut:STATe ON')
            

if __name__ == '__main__':
    supply = E3648(port='GPIB0::8::INSTR')
    supply.setVoltage(channel=1, voltage=3.6)
    supply.outp_ON(channel=1)
    voltage = supply.get_voltage(channel=1)
    print(voltage)
    # print(supply.get__IDN)
    # supply.setRange(channel=2, range=1)
    # supply.setVoltage(channel=2,voltage=14) 
    # supply.setCurrent(channel=2,current=0.5) 
    # supply.outp_OFF(channel=1)
    # supply.outp_ON(channel=1)
    # supply.setCurrent(current=0.5) 
    # print(supply.meas_Voltage())