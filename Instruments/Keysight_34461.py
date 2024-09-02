import time 
import pyvisa as visa
# from pyvisa.attributes import *
# from pyvisa.constants import *


class A34461:

    def __init__(self,port:str) -> None:
        rm = visa.ResourceManager()
        rm.list_resources()
        self.meter = rm.open_resource(port)
        # self.meter.set_visa_attribute(visa.constants.VI_ATTR_ASRL_BAUD, 9600)
        # self.meter.set_visa_attribute(visa.constants.VI_ATTR_ASRL_DATA_BITS, 8)
        # self.meter.set_visa_attribute(visa.constants.VI_ATTR_ASRL_STOP_BITS, VI_ASRL_STOP_TWO)
        # self.meter.set_visa_attribute(visa.constants.VI_ATTR_ASRL_PARITY, visa.constants.VI_ASRL_PAR_NONE)
        # self.meter.read_termination = '\n'
        # self.meter.write_termination = '\n'

    
    def get_IDN(self):
        return (self.meter.query('*IDN?'))
    
    def reset(self):
        self.meter.write('*RST')     

    def get_error(self):
        return self.meter.query('SYST:ERR?')  
    
    def reset(self):
        self.meter.write('*RST')     

    def get_error(self):
        return self.meter.query('SYST:ERR?')  


    def read_value(self, cnt):
        self.meter.write(':SAMP:COUN ' + str(cnt) +';:TRIG:SOUR IMM')      
        data_str= self.meter.query(':READ?')
        data_split = data_str.split(sep =',')
        value = list(map(float, data_split))
        return(sum(value) / len(value))

    def meas_V(self, range = -1, count = 4):
        self.meter.write(':FUNC "VOLT:DC"') 
        #Range: Autorange (-1), 100 mV, 1 V, 10 V, 100 V, or 750 V
        range_list = [-1, 0.1, 1, 10, 100, 750]
        if range in range_list:
            range_auto = ':VOLT:DC:RANG:AUTO '
            range_val = ';:VOLT:DC:RANG '
            res_com = ';:VOLT:DC:RES '

            if range == -1:
                range_auto_cmd = 'ON'
                range_val = ''
                range_val_str = ''
                res_com = ''
                res_val_str = ''
            else:
                range_auto_cmd = 'OFF'
                range_val_str = str(range)
                if range == 0.1 or range == 1:
                    res = 1e-6
                elif range == 10:
                    res = 1e-5
                elif range == 100:
                    res = 1e-4    
                else:   
                    res = 1e-3
                res_val_str = str(res)

            com = range_auto + range_auto_cmd +  range_val + range_val_str + res_com + res_val_str
            self.meter.write(com) 
            self.meter.write('VOLT:IMP:AUTO ON')
            array = []
            while count>0:
                if count > 4:
                    cnt = 4
                else:
                    cnt = count 
                array.append(self.read_value(cnt))
                count -= 4 
            return(sum(array)/len(array))   
        else:
            return('ERR: Wrong range')   

    

    def meas_I(self, range = -1, count = 4):
        self.meter.write(':FUNC "CURR:DC"') 
        #Range: : Autorange (-1), 100 µA, 1 mA, 10 mA, 100 mA, 1 A, 3 A, or 10 A
        range_list = [-1, 100e-6, 1e-3, 0.01, 0.1, 1, 3]
        if range in range_list:
            range_auto = ':CURR:DC:RANG:AUTO '
            range_val = ';:CURR:DC:RANG '
            res_com = ';:CURR:DC:RES '

            if range == -1:
                range_auto_cmd = 'ON'
                range_val = ''
                range_val_str = ''
                res_com = ''
                res_val_str = ''
            else:
                range_auto_cmd = 'OFF'
                range_val_str = str(range)
                if range in list([100e-6, 1e-3]):
                    res = 1e-9
                elif range == 10e-3:
                    res = 1e-8
                elif range == 100e-3:
                    res = 1e-7   
                elif range == 1:
                    res = 1e-6
                else:   
                    res = 1e-5
                res_val_str = str(res)

            com = range_auto + range_auto_cmd +  range_val + range_val_str + res_com + res_val_str
            self.meter.write(com) 
            #self.meter.write('VOLT:IMP:AUTO ON')
            array = []
            while count>0:
                if count > 4:
                    cnt = 4
                else:
                    cnt = count 
                array.append(self.read_value(cnt))
                count -= 4 
            return(sum(array)/len(array))   
        else:
            return('ERR: Wrong range')  

    # ? VOLTage:DC:RANGe {<range>|MIN|MAX|DEF}
    def set_Meter_DC__Voltage___Range(self,range:int):
        self.meter.write(f'VOLT:DC:RANG {str(range)}')  

    # ? VOLTage:DC:RANGe {<range>|MIN|MAX|DEF}
    def get_Meter_DC__Voltage___Range(self,range:int):
        return self.meter.write(f'VOLT:DC:RANG {str(range)}')   
    

    #* SET the trigger edge 
    #? OUTPut:TRIGger:SLOPe {POSitive|NEGative}
    #? OUTPut:TRIGger:SLOPe?

    def set_meter_TriggerSlope__Positve(self):
        self.meter.write('OUTP:TRIG:SLOP POS') 

    def set_meter_TriggerSlope__Negative(self):
        self.meter.write('OUTP:TRIG:SLOP NEG')

    def get_meter_TriggerSlope(self):
        return self.meter.query('OUTP:TRIG:SLOP?')
     
    #? The following method is uses INITiate, The INITiate command places the instrument in the "wait-for-trigger" state, 
    #? triggers a measurement when the rearpanel Ext Trig input is pulsed (low by default), and 
    #? sends the measurement to reading memory. 
    #? The FETCh? query  must use to transfers the measurement from reading memory to the instrument's output buffer
    def set_meter_External__Positivetrigger___Voltage(self):
        self.meter.write('CONF:VOLT:DC')
        self.meter.write('TRIG:SOUR EXT')
        self.meter.write('INIT')

    def fetch_meter__Reading(self):
        return float(self.meter.query('FETCh?'))    


    #* Meter Configureations 

    def get_meter__Configuration(self):
        return self.meter.query('CONF?')
        
    #?  <range>: {100 µA|1 mA|10 mA|100 mA|1 A|3 A|10 A}. Default: AUTO (autorange). 
    def configure_meter__Mode__DcCurrent(self,Range:int,resolution:float):
        self.meter.write(f'CONF:CURR:DC {str(Range)},{str(resolution)}')

    #?  <range>: {100 µA|1 mA|10 mA|100 mA|1 A|3 A|10 A}. Default: AUTO (autorange). 
    def configure_meter__Mode__AcCurrent(self,Range:int,resolution:float):
        self.meter.write(f'CONF:CURR:AC {str(Range)},{str(resolution)}')

    #? The FETCh?, READ?, and MEASure:DIODe? queries return the measured voltage, regardless of its value.
    def configure_meter__Mode__Diode(self):
        self.meter.write('CONF:DIOD')

    #?  <range>: 100 Ω, 1 kΩ, 10 kΩ, 100 kΩ, 1 MΩ, 10 MΩ, 100 MΩ, 1GΩ, AUTO,or DEFault 
    def configure_meter__Mode__Resistance(self,Range:int,resolution:float):
        self.meter.write(f'CONF:RES {str(Range)},{str(resolution)}')

    #?  <range>: {100 mV|1 V|10 V|100 V|1000 V}. Default: AUTO (autorange). 
    def configure_meter__Mode__DcVoltage(self,Range:int,resolution:float):
        self.meter.write(f'CONF:CURR:DC {str(Range)},{str(resolution)}')

    #?  <range>: {100 mV|1 V|10 V|100 V|1000 V}. Default: AUTO (autorange). 
    def configure_meter__Mode__AcVoltage(self,Range:int,resolution:float):
        self.meter.write(f'CONF:CURR:AC {str(Range)},{str(resolution)}')

    #* Measure functions 
    # ? With the MEASure? queries, you can select the function, range and resolution in one command. All other
    # ? parameters are set to their default values (below).

    # ? Measurement Parameter                       Default Setting
    # ?     AC Input Filter (bandwidth)                     20 Hz (medium filter)
    # ?     Autozero                                        OFF if resolution setting results in NPLC < 1
    # ?                                                     ON if resolution setting results in NPLC ≥ 1
    # ? 
    # ?     Range                                           AUTO (including voltage range for frequency and period measurements)
    # ?     Samples per Trigger                             1 sample
    # ?     Trigger Count                                   1 trigger
    # ?     Trigger Delay                                   Automatic delay
    # ?     Trigger Source                                  Immediate
    # ?     Trigger Slope                                   NEGative
    # ?     Math Functions                                  Disabled. Other parameters are unchanged.
    # ?     Per-function Null State                         Disabled

    # <range>: {1 nF|10 nF|100 nF|1 µF|10 µF|100 µF}. Default:AUTO.
    # <resolution>: optional and ignored; fixed at 4½ digits.
    def meas_meter__Capacitance(self):
        return float(self.meter.query('MEAS:CAP?'))
    
    # <range>: {100 µA|1 mA|10 mA|100 mA|1 A|3 A|10 A}. Default: AUTO(autorange).
    # <resolution> (AC): optional and ignored; fixed at 6½ digits.
    def meas_meter__AcCurrent(self):
        return float(self.meter.query('MEAS:CURR:AC?'))
    
    # <range>: {100 µA|1 mA|10 mA|100 mA|1 A|3 A|10 A}. Default: AUTO(autorange).
    # <resolution> (DC): optional and ignored; fixed at 6½ digits.
    def meas_meter__DcCurrent(self):
        return float(self.meter.query('MEAS:CURR:DC?'))
    

    # Resolution 0.001 PLC 0.002 PLC 0.006 PLC 0.02 PLC 0.06 PLC  0.2 PLC  1 PLC  10 PLC 100 PLC
    def meas_meter__Diod(self):
        return float(self.meter.query('MEAS:DIOD?'))
    
    # <range>: 100 mV, 1 V, 10 V, 100 V, 1000 V, AUTO (default) or DEFault
    # <resolution> (DC): optional and ignored; fixed at 6½ digits.  
    # # Resolution 0.001 PLC 0.002 PLC 0.006 PLC 0.02 PLC 0.06 PLC  0.2 PLC  1 PLC  10 PLC 100 PLC
    def meas_meter__DcVoltage(self):
        return float(self.meter.query('MEAS:VOLT:DC?'))
    
    # <range>: 100 mV, 1 V, 10 V, 100 V, 1000 V, AUTO (default) or DEFault
    # <resolution> (DC): optional and ignored; fixed at 6½ digits.  
    # # Resolution 0.001 PLC 0.002 PLC 0.006 PLC 0.02 PLC 0.06 PLC  0.2 PLC  1 PLC  10 PLC 100 PLC
    def meas_meter__AcCurrent(self):
        return float(self.meter.query('MEAS:VOLT:AC?'))
    

    #? @@@@@@@@@@@@@@@@@@@@@@@@@@@@@        Trigger Function @@@@@@@@@@@@@@@@@@@

    # 0 to ~3600 seconds (~1 µs steps). Default: 1 s.
    def set_meter__Trigger___Delay(self,delay:float):
        self.meter.write(f'SAMP:COUN 1')
        self.meter.write(f'TRIGger:DELay:AUTO OFF')
        self.meter.write(f'TRIG:DEL {str(delay)}')
        self.meter.write('CONF:VOLT:DC 1,0.0001') 
        self.meter.write('TRIG:SOUR INT')                   
        self.meter.write('TRIG:LEV 0.75')
        self.meter.write('TRIG:SLOP POS')
        self.meter.write('INIT')

    # 0 to ~3600 seconds (~1 µs steps). Default: 1 s.
    def get_meter__Trigger___Delay(self):
        return float(self.meter.query(f'TRIG:DEL?'))
    
    # <level> (see bullet points below). Default: 0. 
    def get_meter__Trigger___Level(self):
        return float(self.meter.query(f'TRIG:LEV?'))
    
    # <level> (see bullet points below). Default: 0. 
    def set_meter__Trigger___Level(self,levle:float):
        self.meter.write(f'TRIG:LEV {str(levle)}')


    # {ON|1|OFF|0}. Default: OFF. 0 (OFF) or 1 (ON)
    # ?  OFF: the input impedance for DC voltage measurements is fixed at 10 MΩ for all ranges to minimize noise pickup.
    def set_meter__OutputVoltage___ImdpedenceAuto____On(self):
        self.meter.write(f'VOLT:IMP:AUTO ON')
    def set_meter__OutputCurrent___ImdpedenceAuto____On(self):
        self.meter.write(f'CURR:IMP:AUTO ON')

    # ?  ON: the input impedance for DC voltage measurements varies by range. It is set to "HI-Z" (>10 GΩ) for
    #?        the 100 mV, 1 V, and 10 V ranges to reduce the effects of measurement loading errors on these lower
    #?        ranges. The 100 V and 1000 V ranges remain at a 10 MΩ input impedance.
    # {ON|1|OFF|0}. Default: OFF. 0 (OFF) or 1 (ON)
    def set_meter__OutputVoltage___ImdpedenceAuto____Off(self):
        self.meter.write(f'VOLT:IMP:AUTO ON')

    def get_meter__OutputVoltage___ImdpedenceAuto____Status(self):
        return float(self.meter.write(f'VOLT:IMP:AUTO?'))

    def set_Voltage__NPLC(self,NPLC):
        self.meter.write(f'VOLT:DC:NPLC {str(NPLC)}')

if __name__ == '__main__':
    meter = A34461('USB0::0x2A8D::0x1401::MY57216238::INSTR')
    # print(meter.meas_V())
    # print(meter.meas_I())
    print(meter.fetch_meter__Reading() )