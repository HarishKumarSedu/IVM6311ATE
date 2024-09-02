import time 
import pyvisa as visa
from pyvisa.attributes import *
from pyvisa.constants import *


class E362X:

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


    def get__IDN(self):
        return self.supply.query('*IDN?')
    
    def set_supply__On(self,channel:int):
        self.supply.write(f'OUTP ON,(@{str(channel)})')

    def set_supply__Off(self,channel:int):
        self.supply.write(f'OUTP OFF,(@{str(channel)})')

    def set_supply__On__Status(self):
        return self.supply.query(f'OUTP?')
    

    #? @@@@@@@@@@@@@@@@@ Measurements @@@@@@@@@@@@@@@@@@@

    def meas_supply__Voltage(self,channel:int):
        return float(self.supply.query(f'MEAS:VOLT? (@{str(channel)})'))
    
    def meas_supply__Current(self,channel:int):
        return float(self.supply.query(f'MEAS:CURR? (@{str(channel)})'))
    
    
    #? @@@@@@@@@@@@@@@@@ Protections @@@@@@@@@@@@@@@@@@@

    # To set the over-voltage protection for output 1 to the maximum limit:
    def set_supply__Voltage___protection___Max(self,channel:int):
        self.supply.write(f'VOLT:PROT MAX(@{str(channel)})')
    
    # To enable the over-current protection for output 1
    def set_supply__Current___protection__On(self,channel:int):
        self.supply.write(f'CURR:PROT:STAT ON (@{str(channel)})')

    # To clear protection for output
    def set_supply__OutpProtection___Clear(self,channel:int):
        self.supply.write(f'OUTP:PROT:CLE (@{str(channel)})')

    # To set the remote sense relay to 4-wire sense at output
    def set_supply__4Wire___Sense(self,channel:int):
        self.supply.write(f'VOLT:SENS EXT (@{str(channel)})')


    #? @@@@@@@@@@@@@@@@@@@@ Delay @@@@@@@@@@@@@@@@@@@@@@@
    # To program turn-on and turn-off delays for outputs
    def set_supply__Raise___Delay(self,channel:int,delay:float):
        self.supply.write(f'UTP:DEL:RISE {str(delay)},(@{str(channel)})')

    # To program turn-on and turn-off delays for outputs
    def set_supply__Fall___Delay(self,channel:int,delay:float):
        self.supply.write(f'UTP:DEL:FALL {str(delay)},(@{str(channel)})')

    # To only include outputs 1 and 2 in a sequence:
    def set_supply__Channels___Couple(self):
        self.supply.write(f'OUTP:COUP:CHAN CH1,CH2')

    # To enable Auto-Series mode:
    def set_supply__Channels___Series(self):
        self.supply.write(f'OUT:PAIR SER')

    # To enable Auto-Series mode:
    def set_supply__Channels___Parallel(self):
        self.supply.write(f'OUT:PAIR PAR')