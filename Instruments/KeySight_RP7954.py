import time 
import pyvisa as visa
from pyvisa.attributes import *
from pyvisa.constants import *

# ('USB0::0x2A8D::0x0F02::MY56002702::INSTR', 'USB0::0x0699::0x0401::C020132::INSTR', 'TCPIP0::172.16.10.29::inst0::INSTR', 'GPIB0::6::INSTR')
class RP790x:

    def __init__(self,port='USB0::0x2A8D::0x2802::MY59003109::INSTR') -> None:
        rm = visa.ResourceManager()
        rm.list_resources()
        self.my_instr = rm.open_resource(port)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_BAUD, 9600)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_DATA_BITS, 8)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_STOP_BITS, VI_ASRL_STOP_TWO)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_PARITY, visa.constants.VI_ASRL_PAR_NONE)
        self.my_instr.read_termination = '\n'
        self.my_instr.write_termination = '\n'

        # * switch off the Channle 
    def outp_OFF(self):
        self.my_instr.write(f'OUTP OFF')  

    # * Switch on the channel 
    def outp_ON(self):
        self.my_instr.write(f'OUTP ON')

    def setCurrent_Priority(self):
        self.my_instr.write(f'FUNC CURR')  

    def setVoltage_Priority(self):
        self.my_instr.write(f'FUNC VOLT')  
    # * Switch on the channel 
    def setCurrent_Limit(self,current):
        if current >= 0:
            self.my_instr.write(f'CURR:LIM {str(current)}')
        else:
            self.my_instr.write(f'CURR:LIM:NEG {str(current)}')

    def setVoltage(self,voltage):
        self.my_instr.write(f'VOLT {str(voltage)}')
    
    def setCurrent(self,current):
        self.my_instr.write(f'CURR {str(current)}')
        
    def setVoltage_Limit(self,voltage):
        self.my_instr.write(f'VOLT:LIM {str(voltage)}')
      
    def setVoltage_Limit__LOW(self,voltage):
        self.my_instr.write(f'VOLT:LIM:LOW {str(voltage)}')
    
    def rest(self):
        self.my_instr.write(f'*RST')

    def getVotlage(self):
        return float(self.my_instr.query(f'MEASure:VOLTage?'))
    
    def getCurrent(self):
        return float(self.my_instr.query(f'MEASure:CURR?'))
    def getPower(self):
        return float(self.my_instr.query(f'MEASure:POW?'))
    
    def getError(self):
        self.my_instr.query(f'SYST:ERR?')


if __name__ == '__main__':
    supply = RP790x()
    # supply.outp_OFF()
    # time.sleep(0.1)
    # supply.rest()
    # supply.setCurrent_Priority()
    # supply.setCurrent_Limit(current=-1)
    # supply.setVoltage_Limit(voltage=4.3)
    # supply.setVoltage(voltage=4)
    # supply.setCurrent(current=-1)
    # print(supply.getError())
    # supply.outp_ON()
    print(supply.getCurrent())
