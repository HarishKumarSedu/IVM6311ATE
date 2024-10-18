import time 
import pyvisa as visa
from pyvisa.attributes import *
from pyvisa.constants import *

# ('USB0::0x2A8D::0x0F02::MY56002702::INSTR', 'USB0::0x0699::0x0401::C020132::INSTR', 'TCPIP0::172.16.10.29::inst0::INSTR', 'GPIB0::6::INSTR')
class N670x:

    def __init__(self,port='USB0::0x2A8D::0x0F02::MY56002702::INSTR') -> None:
        rm = visa.ResourceManager()
        rm.list_resources()
        self.my_instr = rm.open_resource(port)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_BAUD, 9600)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_DATA_BITS, 8)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_STOP_BITS, VI_ASRL_STOP_TWO)
        # self.my_instr.set_visa_attribute(visa.constants.VI_ATTR_ASRL_PARITY, visa.constants.VI_ASRL_PAR_NONE)
        self.my_instr.read_termination = '\n'
        self.my_instr.write_termination = '\n'

        self.channel = {
                            1:"OUT1",
                            2:"OUT2",
                            3:"OUT3",
                            4:"OUT4",
                        }

        self.erroMSG = {
            -100 :"Command error [generic command error]",
            -101 :"Invalid character",
            -102 :"Syntax error [unrecognized command or data type]",
            -103 :"Invalid separator [illegal character encountered in place of separator]",
            -104 :"Data type error [e.g., “numeric or string expected, got block date”]",
            -105 :"GET not allowed [ <GET> inside a program message]",
            -108 :"Parameter not allowed [too many parameters]",
            -109 :"Missing parameter [too few parameters]",
            -112 :"Program mnemonic too long [maximum 12 characters]",
            -113 :"Undefined header [syntactical correct but not defined for this device]",
            -121 :"Invalid character in number [e.g. alpha in decimal data, etc.]",
            -123 :"Exponent too large [ numeric overflow; exponent magnitude >32000]",
            -124 :"Too many digits [number too long; more than 255 digits received]",
            -128 :"Numeric data not allowed [numeric data not accepted where positioned]",
            -131 :"Invalid suffix [unrecognized suffix, or suffix not appropriate]",
            -138 :"Suffix not allowed [numeric element does not allow suffixes]"
        }
        
    # ! SYST:REM system remote connection 
    # * *IDN?' Instrument id Query 
    # ? provide the minimum sleep time(1 Sec) to configure for the remote connection time.sleep(1)
    def get_IDN(self):
        self.my_instr.write('SYST:REM') 
        time.sleep(1)
        return (self.my_instr.query('*IDN?'))
        
    
    # * Rest the instrument 
    def reset(self):
        self.my_instr.write('*RST')  

    # * switch off the Channle 
    def outp_OFF(self,channel:int):
        self.my_instr.write(f'OUTP OFF,(@{str(channel)})')  

    # * Switch on the channel 
    def outp_ON(self,channel:int):
        self.my_instr.write(f'OUTP ON,(@{str(channel)})')  

    # * Error Que Clear
    def clear_errors(self):
        self.my_instr.write('*CLS')  

    # * Installed Options in the Channl
    def modelNumber(self,channel:int):
        return self.my_instr.query(f'SYST:CHAN:MOD? (@{str(channel)})')
    
    # * Serial number of the channel
    def serialNumber(self,channel:int):
        return self.my_instr.query(f'SYST:CHAN:SER? (@{str(channel)})')
    
    # * installed Options in the channel
    def installedOptions(self,channel:int):
        return self.my_instr.query(f'SYST:CHAN:OPT? (@{str(channel)})')

    # Returns the error number and error string
    def errorLog(self):
        return (self.my_instr.query('SYST:ERR?'))

    # * Multi channel voltage set method 
    # ! first argument is the channel number shuold be in int  channel Number 1-4
    # ! voltage must be in the float ex: 1.4 
    # ? default it will provide the fist chanlle Voltage 
    # def setVoltage(self, channel:int, voltage:float):
    #     if channel in self.channel.keys() :
    #         ch = self.channel.get(channel)
    #     else:
    #         ch = self.channel.get(1)
    #     command = 'INST:SEL ' +  ch
    #     self.my_instr.write(command)   
    #     command = 'VOLT ' + str(voltage) 
    #     self.my_instr.write(command)  

    # * Multi channel voltage set method 
    # ! first argument is the channel number shuold be in int  channel Number 1-4
    # ! current must be in the float ex: 1.4 
    # ? default it will provide the fist chanlle current 
    # def setCurrent(self, channel:int, current:float):
    #     if channel in self.channel.keys() :
    #         ch = self.channel.get(channel)
    #     else:
    #         ch = self.channel.get(1)
    #     command = 'INST:SEL ' +  ch
    #     self.my_instr.write(command)   
    #     command = 'CURR ' + str(current) 
    #     self.my_instr.write(command)  

    def setCurrent(self, channel:int, current:float):
        self.my_instr.write(f'CURR {current},(@{channel})')

    def setVoltage(self, channel:int, voltage:float):
        self.my_instr.write(f'VOLT {voltage},(@{channel})')
    # ? get the output status 
    def getOutStatus(self):  
        # time.sleep(0.2)
        return self.my_instr.query('OUTP:STAT?')  
    
    # * set the Voltage Range of the channel 
    # * Channel Number must be int it is between 1-4 
    # * Voltage range must be float
    def setRange_Voltage(self,channel:int,voltageRange:float):
        self.my_instr.write(f'VOLT:RANG {str(voltageRange)},(@{str(channel)})')

    # * set the Current Range of the channel 
    # * Channel Number must be int it is between 1-4 
    # * Current range must be float
    def setRange_Current(self,channel:int,voltageRange:float):
        self.my_instr.write(f'CURR:RANG {str(voltageRange)},(@{str(channel)})')


    # * set the channel to the current mode =
    # * Channel Number must be int it is between 1-4 
    def setCurrentMode(self,channel:int):
        self.my_instr.write(f'OUTP:PMOD CURR,(@{str(channel)})')
        
    # * set the channel to the Voltage mode =
    # * Channel Number must be int it is between 1-4 
    def setVoltageMode(self,channel:int):
        self.my_instr.write(f'OUTP:PMOD VOLT,(@{str(channel)})')

    # * To reverse the relay polarity on units with Option 760
    # * Channel Number must be int it is between 1-4 
    def setReverseRelay_Polarity(self,channel:int):
        self.my_instr.write(f'OUTP:REL:POL REV,(@{str(channel)})')

    # * To return the relay polarity to normal
    # * Channel Number must be int it is between 1-4 
    def setNormalRelay_Polarity(self,channel:int):
        self.my_instr.write(f'OUTP:REL:POL NORM,(@{str(channel)})')

    # To set the positive current limit of output ex:1 to 1 A:
    def setCurrent_Positive_Limit(self,channel:int,current:float):
        self.my_instr.write(f'CURR:LIM {str(current)},(@{str(channel)})')

    # To set the negative current limit, you must first turn limit coupling
    # (tracking) off. Then set the negative current limit
    def setCurrent_Negative_Limit(self,channel:int,current:float):
        self.my_instr.write(f'CURR:LIM:COUP OFF,(@{str(channel)})')
        self.my_instr.write(f'CURR:LIM:NEG {str(current)},(@{str(channel)})')

    # To set the voltage priority mode:
    def setVoltage_Priority(self,channel:int):
        self.my_instr.write(f'FUNC VOLT,(@{str(channel)})')

    # To set the Current priority mode:
    def setCurrent_Priority(self,channel:int):
        self.my_instr.write(f'FUNC CURR,(@{str(channel)})')

    # TTo program turn-on delay 
    def setTurn_ON_Delay(self,channel:int,delay:float):
        self.my_instr.write(f'OUTP:DEL:RISE  {str(delay)},(@{str(channel)})')

    # TTo program turn-on delay 
    def setTurn_OFF_Delay(self,channel:int,delay:float):
        self.my_instr.write(f'OUTP:DEL:FALL  {str(delay)},(@{str(channel)})')


    # # ! Coupling of the channel is pending 
    # !!!
    # !!!



    # To program the OVP level for outputs
    def setOVP_Protection(self,channel:int,OVP:float):
        self.my_instr.write(f'VOLT:PROT  {str(OVP)},(@{str(channel)})')

    # To enable OCP for outputs 
    def setOCP_Protection(self,channel:int,OCP:float):
        self.my_instr.write(f'CURR:PROT:STAT  {str(OCP)},(@{str(channel)})')

    # To specify a 10 millisecond delay for the OCP
    def setOCP_Delay(self,channel:int,delay:float):
        self.my_instr.write(f'CURR:PROT:DEL  {str(delay)},(@{str(channel)})')
    
    # To enable output protection coupling
    def setOutput_Protection_Coupling_ON(self):
        self.my_instr.write('OUTP:PROT:COUP ON')


    def setOutput_Current_Protection_ON(self,channel:int):
        self.my_instr.write(f'CURR:PROT:STAT ON,(@{str(channel)})')


    def setOutput_Current_Protection_OFF(self,channel:int):
        self.my_instr.write(f'CURR:PROT:STAT OFF,(@{str(channel)})')


    def setOutput_Voltage_Protection_ON(self,channel:int):
        self.my_instr.write(f'VOLT:PROT:STAT ON,(@{str(channel)})')

    def setOutput_Voltage_Protection_OFF(self,channel:int):
        self.my_instr.write(f'VOLT:PROT:STAT OFF,(@{str(channel)})')

    # To clear an output protection fault
    def clearOutput_Protection_Clear(self,channel:int):
        self.my_instr.write(f'OUTP:PROT:CLE (@{str(channel)})')

    def protection_Status_Current(self):
        return self.my_instr.query('CURRent:PROTection:STATe?')

    def protection_Status_Voltage(self):
        return self.my_instr.query('VOLTage:PROTection:STATe?')


    
    def arbFunction_Priority__Voltage(self,channel:int):
        self.my_instr.write(f'ARB:FUNC:TYPE VOLT,(@{str(channel)})')

    def arbFunction_Sequence__Set(self,channel:int):
        self.my_instr.write(f'ARB:FUNC:SHAP SEQ,(@{str(channel)})')

    def arbFunction_Sequence__Reset(self,channel:int):
        self.my_instr.write(f'ARB:SEQ:RES(@{str(channel)})')
    
    def arbSet_Sequence_Waveform(self,channel:int):
        self.arbFunction_Priority__Voltage(channel)
        self.arbFunction_Sequence__Set(channel)

    def arb_Pulse__Voltage(self,channel:int,initial_Voltage:float,end_Voltage:float,initial_Time:float,top_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:VOLT:PULS:STAR  {str(initial_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:PULS:TOP  {str(end_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:PULS:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:PULS:TOP:TIM  {str(top_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:PULS:END:TIM   {str(end_Time)},(@{str(channel)})')
    def arb_Pulse__Current(self,channel:int,initial_Current:float,end_Current:float,initial_Time:float,top_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:CURR:PULS:STAR  {str(initial_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:PULS:TOP  {str(end_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:PULS:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:PULS:TOP:TIM  {str(top_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:PULS:END:TIM   {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:TERM:LAST OFF,(@{str(channel)})')
        self.my_instr.write(f'TRIG:ARB:SOUR BUS')
        self.my_instr.write(f'INIT:TRAN(@{str(channel)})')
    
    # The parameter setting remains at the last Arb value after the Arb completes.
    def arbLast_Value_ON(self,channel:int):
        self.my_instr.write(f'ARB:TERM:LAST ON,(@{str(channel)})')

    # The parameter setting returns to the DC value that was in effect prior to the Arb
    def arbLast_Value_OFF(self,channel:int):
        self.my_instr.write(f'ARB:TERM:LAST OFF,(@{str(channel)})')
    
    def arb_Trigger(self):
        self.my_instr.write('*TRG')

    def arb_Step__Current(self,channel:int,initial_Current:float,end_Current:float,initial_Time:float):
        self.my_instr.write(f'ARB:CURR:STEP:STAR  {str(initial_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STEP:END  {str(end_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STEP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')

    def arb_Step__Voltage(self,channel:int,initial_Voltage:float,end_Voltage:float,initial_Time:float):
        self.my_instr.write(f'ARB:VOLT:STEP:STAR  {str(initial_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STEP:END  {str(end_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STEP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
    
    def arb_Ramp__Voltage(self,channel:int,initial_Voltage:float,end_Voltage:float,initial_Time:float,raise_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:VOLT:RAMP:STAR  {str(initial_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:RAMP:END  {str(end_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:RAMP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:RAMP:END:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:RAMP:RTIM  {str(raise_Time)},(@{str(channel)})')
    
    def arb_Ramp__Current(self,channel:int,initial_Current:float,end_Current:float,initial_Time:float,raise_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:CURR:RAMP:STAR  {str(initial_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:RAMP:END  {str(end_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:RAMP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:RAMP:END:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:RAMP:RTIM  {str(raise_Time)},(@{str(channel)})')
    
    def arb_Staircase__Voltage(self,channel:int,steps:int,initial_Voltage:float,end_Voltage:float,initial_Time:float,raise_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:VOLT:STA:STAR  {str(initial_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STA:END  {str(end_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STA:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STA:END:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STA:TIM  {str(raise_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:STA:NST  {str(steps)},(@{str(channel)})')
    
    def arb_Staircase__Current(self,channel:int,steps:int,initial_Current:float,end_Current:float,initial_Time:float,raise_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:CURR:STA:STAR  {str(initial_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STA:END  {str(end_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STA:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STA:END:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STA:TIM  {str(raise_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:STA:NST  {str(steps)},(@{str(channel)})')
    
    def arb_Trapezoid__Voltage(self,channel:int,initial_Voltage:float,end_Voltage:float,initial_Time:float,raise_Time:float,top_Time:float,fall_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:volt:TRAP:STAR  {str(initial_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:volt:TRAP:END  {str(end_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:volt:TRAP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:volt:TRAP:END:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:volt:TRAP:TOP:TIM  {str(top_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:volt:TRAP:RTIM  {str(raise_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:volt:TRAP:FTIM  {str(fall_Time)},(@{str(channel)})')
    
    def arb_Trapezoid__Current(self,channel:int,initial_Current:float,end_Current:float,initial_Time:float,raise_Time:float,top_Time:float,fall_Time:float,end_Time:float,count=1,LastOFF=0):
        self.my_instr.write(f'CURR:MODE ARB,(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:STAR  {str(initial_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:TOP  {str(end_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:END:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:TOP:TIM  {str(top_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:RTIM  {str(raise_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:TRAP:FTIM  {str(fall_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:COUN  {str(count)},(@{str(channel)})')
        self.arbLast_Value_OFF(channel=1)
        if LastOFF !=0 :
            self.arbLast_Value_ON(channel=1)
    
    def arb_Exponential__Current(self,channel:int,initial_Current:float,end_Current:float,initial_Time:float,tcon_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:CURR:EXP:STAR  {str(initial_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:EXP:END  {str(end_Current)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:EXP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:EXP:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:CURR:EXP:TCON  {str(tcon_Time)},(@{str(channel)})')
   
    def arb_Exponential__Voltage(self,channel:int,initial_Voltage:float,end_Voltage:float,initial_Time:float,tcon_Time:float,end_Time:float):
        self.my_instr.write(f'ARB:VOLT:EXP:STAR  {str(initial_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:EXP:END  {str(end_Voltage)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:EXP:STAR:TIM  {str(initial_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:EXP:TIM  {str(end_Time)},(@{str(channel)})')
        self.my_instr.write(f'ARB:VOLT:EXP:TCON  {str(tcon_Time)},(@{str(channel)})')
     
    def arb_Immediate_Trigger(self):
        self.my_instr.write('TRIG:ARB:SOUR IMM')
    
    def arb_Mode__Voltage(self,channel:int):
        self.my_instr.write(f'VOLT:MODE ARB(@{str(channel)})')
    
    def arb_Mode__Current(self,channel:int):
        self.my_instr.write(f'CURR:MODE ARB(@{str(channel)})')
    

        
    def getVoltage(self, channel:int):
        if channel in self.channel.keys() :
            ch = self.channel.get(channel)
        else:
            ch = self.channel.get(1)
        command = 'INST:SEL ' +  ch
        self.my_instr.write(command)
        # ! sleep time to measure the voltage is optional but minimum sleep time needs to provided even atleast in the main program    
        # time.sleep(0.2)
        return float(self.my_instr.query(f'MEAS:VOLT? (@{str(channel)})'))
    
    def getCurrent(self, channel:int):
        if channel in self.channel.keys() :
            ch = self.channel.get(channel)
        else:
            ch = self.channel.get(1)
        command = 'INST:SEL ' +  ch
        self.my_instr.write(command)
        # ! sleep time to measure the voltage is optional but minimum sleep time needs to provided even atleast in the main program    
        # time.sleep(0.2)
        return float(self.my_instr.query(f'MEAS:CURR? (@{str(channel)})'))
    
    def setCurrRange(self, channel:int):
        if channel in self.channel.keys() :
            ch = self.channel.get(channel)
        else:
            ch = self.channel.get(1)
        command = 'INST:SEL ' +  ch
        self.my_instr.write(command)
        # ! sleep time to measure the voltage is optional but minimum sleep time needs to provided even atleast in the main program    
        # time.sleep(0.2)
        string = (f'SENS:CURR:RANG 10e-3,(@{str(channel)})')
        self.my_instr.write(string)
        print (string)
        print(ch)
        return
        
    def get_PeviousTriggered_Voltage(self, channel:int):
        if channel in self.channel.keys() :
            ch = self.channel.get(channel)
        else:
            ch = self.channel.get(1)
        command = 'INST:SEL ' +  ch
        self.my_instr.write(command)
        # ! sleep time to measure the voltage is optional but minimum sleep time needs to provided even atleast in the main program    
        # time.sleep(0.2)
        return float(self.my_instr.query('FETC:VOLT?'))
    
    def get_PeviousTriggered_Current(self, channel:int):
        if channel in self.channel.keys() :
            ch = self.channel.get(channel)
        else:
            ch = self.channel.get(1)
        command = 'INST:SEL ' +  ch
        self.my_instr.write(command)
        # ! sleep time to measure the voltage is optional but minimum sleep time needs to provided even atleast in the main program    
        # time.sleep(0.2)
        return float(self.my_instr.query('FETC:CURR?'))
        
    # o enable seamless voltage or current autoranging
    def setMeter_Range_Auto__Current(self,channel:int,Curr_range='10e-6'):
        self.my_instr.write(f'SENS:CURR:RANG {Curr_range},(@{str(channel)})')

    def setMeter_Range_Auto__Voltage(self,channel:int):
        self.my_instr.write(f'SENS:VOLT:RANG:AUTO ON,(@{str(channel)})')

        


#         Specifies the emulation mode on N678xA <type> = PS4Q, PS2Q,
# PS1Q, BATTery, CHARger, CCLoad, CVLoad, VMETer, AMETer
    def emulMode_Battery(self,channel:int):
        self.my_instr.write(f'EMUL BATTery,(@{str(channel)})')

    def emulMode_2Q(self,channel:int):
        self.my_instr.write(f'EMUL PS2Q,(@{str(channel)})')

    def emulMode_1Q(self,channel:int):
        self.my_instr.write(f'EMUL PS2Q,(@{str(channel)})')

    def emulMode_4Q(self,channel:int):
        self.my_instr.write(f'EMUL PS4Q,(@{str(channel)})')

    def emulMode_CC_Load(self,channel:int):
        self.my_instr.write(f'EMUL CCLoad,(@{str(channel)})')

    def emulMode_Ammeter(self,channel:int):
        self.my_instr.write(f'EMUL AMETer,(@{str(channel)})')

    def Set_4Q(self, channel:int, voltage):
        self.my_instr(f'VOLTage <value>, (@<channel>)')
        self.my_instr.write(f'SOURce:FUNCtion:MODE SOURce,(@{str(channel)})')
        

if __name__ == '__main__':
    supply = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
    # print(supply.get_IDN())
    # supply.emulMode_1Q(channel=1)
    # supply.setCurrent_Priority(channel=3)
    # # supply.my_instr.write('OUTP ON,(@1)') 
    # print(supply.errorLog())
    # supply.setCurrent(channel=3,current=-1)
    # supply.outp_ON(channel=3)
    # time.sleep(2)
    # supply.outp_OFF(channel=3)
    # supply.my_instr.write('CURR:MODE ARB,(@1)')
    # supply.arb_Trapezoid__Current(channel=1,initial_Current=0,end_Current=-5.2,initial_Time=0,raise_Time=0.001,top_Time=0,fall_Time=0.001,end_Time=0)
    # supply.my_instr.write('TRIG:ARB:SOUR BUS,(@1)')
    # time.sleep(0.1)
    # supply.my_instr.write('INIT:TRAN(@1)')
    # supply.my_instr.write('TRIG:TRAN(@1)')
    # supply.my_instr.write('*TRG')
    # supply.arb_Trigger()
    # supply.outp_ON(channel=3)
    # print(supply.getCurrent(channel=3))
    supply.emulMode_Ammeter(channel=1)