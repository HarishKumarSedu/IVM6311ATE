import pyvisa as visa
from time import sleep


class su_241:

    def __init__(self, usb_id = "GPIB0::1::INSTR"):
        rm = visa.ResourceManager()
        # rm.list_resources()
        self.my_instr = rm.open_resource(usb_id)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_BAUD, 9600)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_DATA_BITS, 8)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_STOP_BITS, VI_ASRL_STOP_TWO)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_PARITY, visa.constants.VI_ASRL_PAR_NONE)
        self.my_instr.read_termination = '\n'
        self.my_instr.write_termination = '\n'
        self.my_instr.clear()

    def read_temp(self):
        self.my_instr.clear()
        temp = self.my_instr.query('TEMP?')
        temp_list = temp.split(",")
        return float(temp_list[0])



    def set_temp(self, temp):
        self.my_instr.query('POWER, ON')
        temp_Str = "TEMP, S" + str(temp)
        self.my_instr.query(temp_Str)

    def powerOff(self):
        self.my_instr.query("POWER, OFF")

if __name__ == '__main__':
    chamber = su_241()
    chamber.set_temp(temp=25)
    print(chamber.read_temp())
    # for temp in [-20]:
    #     chamber.set_temp(temp=temp)
    #     # sleep(2000)
    #     while ( float(temp) !=    (temperature := chamber.read_temp())):
    #         print(f'Reading temperature from chamber:> {temperature}')
    #         sleep(30)
    #         ...
    #     sleep(300)
    #     print(chamber.read_temp())
        # input('Note down the Values :>')
    # chamber.powerOff()