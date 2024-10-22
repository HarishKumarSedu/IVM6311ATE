import pandas as pd
from dft_syntaxparser import Parser
import re
from time import sleep
from Instruments.Keysight_34461 import A34461
from Instruments.DigitalScope import dpo_2014B
from Instruments.KeySight_N670x import N670x
from Instruments.Keysight_E3648 import E3648
from SwitchMatrix.mcp2221 import MCP2221
from SwitchMatrix.mcp2317 import MCP2317
import traceback
import os
import yaml
from pathlib import Path
from box import ConfigBox
from box.exceptions import BoxValueError

class Boost:

    ############################ initialization
    def __init__(self):
        self.data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Boost')
        self.procedures = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Procedure')
        self.mcp = MCP2221()
        self.mcp2317 = MCP2317(mcp=self.mcp)
        self.pa = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
        self.ps_gpib = E3648('GPIB0::6::INSTR')
        self.supplies = E3648('GPIB0::7::INSTR')
        self.supplies_8 = E3648('GPIB0::8::INSTR')
        self.parser = Parser()
        self.voltmeter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.ammeter = A34461('USB0::0x2A8D::0x1401::MY57216238::INSTR')
        self.slave_address = 0x6c
        self.sdwn_measurements = []
        self.vbso_measurements = []
        self.vbat_measurements = []

    def value_clean(self,value:str):
        value = (lambda value : value.replace(',','.') if re.findall(',',value) else value)(value=value)
        # value = re.sub(r'[a-zA-Z]+$', '', value) # use it when you want to replace the any string in the number 
        value = re.sub(r'[v|V]|[a|A]|[hZ|HZ]+$', '', value) # use it when you want to replace the any string in the number 
        value = (lambda value : float(value.replace('m',''))*10**-3  if isinstance(value,str)    and re.findall('m',value) else value)(value=value)
        value = (lambda value : float(value.replace('n',''))*10**-9  if isinstance(value,str)    and re.findall('n',value)  else value)(value=value)
        value = (lambda value : float(value.replace('u',''))*10**-6  if isinstance(value,str)    and re.findall('u',value)  else value)(value=value)
        value = (lambda value : float(value.replace('k',''))*10**3   if isinstance(value,str)    and re.findall('k',value)  else value)(value=value)
        value = (lambda value : float(value.replace('M',''))*10**6   if isinstance(value,str)    and re.findall('M',value)  else value)(value=value)
        value = (lambda value : float(value.replace('G',''))*10**9   if isinstance(value,str)    and re.findall('G',value)  else value)(value=value)
        if not isinstance(value,float) :
            value = float(value)
        return value

    def read_yaml(self,path_to_yaml: Path) -> ConfigBox:
        try:
            with open(path_to_yaml) as yaml_file:
                content = yaml.safe_load(yaml_file)
                return ConfigBox(content)
        except BoxValueError:
            raise ValueError("yaml file is empty")
        except Exception as e:
            raise e

    def DFT_Tests(self,path='Tests.yaml'):
        return self.read_yaml(path_to_yaml=path)

    def convert_value_unit(self,value_str):
        prefixes = {
            'k': 10 ** 3,    # kilo
            'm': 10 ** -3,   # milli
            'u': 10 ** -6,   # micro
            'μ': 10 ** -6,   # micro
            'n': 10 ** -9,   # nano
            'p': 10 ** -12   # pico
        }

        match = re.match(r"([-+]?\d*\.?\d+)([a-zA-Z]*)", value_str)
        if match:
            value, unit = match.groups()
            value = float(value)

            if unit and unit[0].lower() in prefixes:
                prefix = unit[0].lower()
                multiplier = prefixes[prefix]
                value *= multiplier

            return value

        return value_str

    def convert_dict_values(self,data):
        converted_dict = {}
        for key, value in data.items():
            converted_value = self.convert_value_unit(value)
            converted_dict[key] = converted_value

        return converted_dict

    def extract_last_n_values(self,data, n):
        numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
        last_n_values = numeric_values[-n:]
        if len(last_n_values) < n:
            return None
        return last_n_values

    def execute_startup(self):
        startup_procedure = self.procedures['Startup'].loc[0].split('\n')
        for instruction in startup_procedure:
            instruction = instruction.lower()
            if re.match('0x', instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction) 
                print(reg_data)
                self.write_device(reg_data) 
            if re.match('Force__SDWN__1.8V'.lower(), instruction):
                print('Force 1.8V on SDWN')
                self.pa.arb_Ramp__Voltage(channel=4,initial_Voltage=1.8,end_Voltage= 0, initial_Time=0.2, raise_Time= 1, end_Time = 0.2)
                sleep(0.5)
                self.mcp2317.Switch(device_addr=0x20, row=1, col=4, Enable=True)
                sleep(0.5)

    def write_device(self, data: {}):
        # Function to convert hexadecimal or numeric values to integers
        def convert_to_int(value):
            if isinstance(value, str):
                return int(value, 16)  # Convert from hexadecimal string to integer
            elif isinstance(value, (int, float)):  # Also handle floats by converting them to integers
                return int(value)
            else:
                raise TypeError(f"Unsupported type for conversion: {type(value)}")
        # Convert MSB, LSB, RegAddr, and Data to integers
        msb = convert_to_int(data.get('MSB'))
        lsb = convert_to_int(data.get('LSB'))
        reg_addr = convert_to_int(data.get('RegAddr'))
        data_value = convert_to_int(data.get('Data'))
        # Read the register from the device
        device_data = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg_addr])[0]
        # print(hex(device_data))
        # Calculate the bit width and ensure it's an integer
        bit_width = int(2 ** (msb - lsb + 1))
        # Check if the value is valid
        if data_value < bit_width:
            # Create the mask for the bit width, ensuring that mask and lsb are integers
            mask = ~((bit_width - 1) << int(lsb))
            # Ensure `device_data` and `mask` are integers
            device_data = int(device_data)
            mask = int(mask)
            # Perform bitwise operations
            device_data = (device_data & mask) | (data_value << int(lsb))
            print(hex(device_data))
            # Write the new value to the device
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg_addr, device_data])
        else:
            print(f'Data is out of width')


    def execute_Enable_Ana_Testpoint(self):
        startup_procedure = self.procedures['Enable_Ana_Testpoint'].loc[0].split('\n')
        for instruction in startup_procedure:
            instruction = instruction.lower()
            if re.match('0x', instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                print(reg_data)
                self.write_device(reg_data)
            if re.match('FORCE__SDWN__OPEN'.lower(), instruction):
                self.pa.arb_Ramp__Voltage(channel=4,initial_Voltage=1.8,end_Voltage= 0, initial_Time=0.2, raise_Time= 1, end_Time = 0.2)
                self.pa.setVoltage(channel=4,voltage=0)
                sleep(0.5)
                self.mcp2317.Switch(device_addr=0x20, row=1, col=4, Enable=False)
                sleep(0.5)

    def execute_Boost_test_default(self):
        startup_procedure = self.procedures['Boost_Test_Default'].loc[0].split('\n')
        for instruction in startup_procedure:
            instruction = instruction.lower()
            if re.match('0x', instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                print(reg_data)
                self.write_device(reg_data)
            if re.match('Force__VBIAS__5V'.lower(), instruction):
                print('Force__VBIAS__5V')
                self.supplies_8.setVoltage(channel=2,voltage=5.0)
                self.supplies_8.outp_ON(channel=2)
            if re.match('Force__VBSO__3.6V'.lower(), instruction):
                print('Force__VBSO__3.6V')
                self.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= True)
                sleep(0.2)
                self.supplies_8.setVoltage(channel=1,voltage=3.6)
                self.supplies_8.outp_ON(channel=1)
            if re.match('Force__SW__3.6V'.lower(), instruction):
                print('Force__SW__3.6V')
                SW_target = 3.6
                tollerance = 0.1
                self.mcp2317.Switch(device_addr=0x27,row=7,col=1,Enable=True)
                sleep(1)
                SW_pin= self.voltmeter.meas_V()
                if(SW_pin - SW_target) <= tollerance:
                    print("SW is shorted on VBAT")
                    sleep(0.5)
                    self.mcp2317.Switch(device_addr=0x27,row=7,col=1,Enable=False)
                else:
                    input("Shorted SW with the jumper on the board, or connected SW to a supply")

    def measure_value_check(self,measure_signal: {}, typical: float):
        if measure_signal:
            signal_Unit = measure_signal.get('Unit')
            print(signal_Unit)
            if re.search('voltage', signal_Unit):
                signal_pin = measure_signal.get('Signal')
                if re.search('sdwn',signal_pin):
                    self.mcp2317.Switch(device_addr=0x20, row=1, col=1, Enable=True)
                    sleep(0.2)
                    sdwn = self.voltmeter.meas_V()
                    self.sdwn_measurements.append(sdwn)
                    print(self.sdwn_measurements)
                    self.mcp2317.Switch(device_addr=0x20, row=1, col=1, Enable=False)

                if re.search('vbso',signal_pin):
                    self.mcp2317.Switch(device_addr=0x23, row=7, col=1, Enable=True)
                    sleep(0.2)
                    vbso = self.voltmeter.meas_V()
                    self.vbso_measurements.append(vbso)
                    print(self.vbso_measurements)
                    self.mcp2317.Switch(device_addr=0x23, row=7, col=1, Enable=False)

                if re.search('vbat', signal_pin):
                    self.mcp2317.Switch(device_addr=0x21, row=3, col=1, Enable=True)
                    sleep(0.2)
                    vbat = self.voltmeter.meas_V()
                    self.vbat_measurements.append(vbat)
                    print(self.vbat_measurements)
                    self.mcp2317.Switch(device_addr=0x21, row=3, col=1, Enable=False)

            if re.search('current', signal_Unit):
                signal_pin = measure_signal.get('Signal')
                if re.search('sdwn',signal_pin):
                    self.mcp2317.Switch(device_addr=0x20, row=1, col=7, Enable=True)
                    sleep(0.5)
                    self.pa.setMeter_Range_Auto__Current(channel=1,Curr_range='1e-6')
                    bst_mirr = self.pa.getCurrent(channel=1)
                    print("bst_mirr = ", bst_mirr)
                    self.mcp2317.Switch(device_addr=0x20, row=1, col=7, Enable=False)
        return 

    def force_signal(self,force_signal_instruction: {}):
        if force_signal_instruction:
            signal_Unit = force_signal_instruction.get('Unit')
            signal_name = force_signal_instruction.get('Signal')
            print(signal_Unit)
            if re.search('V', signal_Unit):
                signal_force = force_signal_instruction.get('Value')
                if re.search('sdwn', signal_name):
                    self.mcp2317.Switch(device_addr=0x20, row=1, col=7, Enable=True)
                    sleep(0.5)
                    self.pa.emulMode_2Q(channel=1)
                    self.pa.setVoltage(channel=1, voltage=signal_force)
                    self.pa.outp_ON(channel=1)
                    sleep(0.2)
                if re.search('vbat',signal_name):
                    self.supplies.setVoltage(channel=1, voltage=signal_force)
                    sleep(0.1)
                    self.supplies.outp_ON(channel=1)
                if re.search('vddio',signal_name):
                    self.supplies.setVoltage(channel=2, voltage=signal_force)
                    sleep(0.1)
                    self.supplies.outp_ON(channel=2)
                if re.search('vbso',signal_name):
                    self.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= True)
                    self.supplies_8.setVoltage(channel=1, voltage=signal_force)
                    sleep(0.1)
                    self.supplies_8.outp_ON(channel=1)
                if re.search('vbias',signal_name):
                    self.supplies_8.setVoltage(channel=2, voltage=signal_force)
                    sleep(0.1)
                    self.supplies_8.outp_ON(channel=2)

            if re.search('A', signal_Unit):
                signal_force = force_signal_instruction.get('Value')
                if re.search('sw',signal_name):
                    self.mcp2317.Switch(device_addr=0x23, row=8, col=7, Enable=True)
                    sleep(0.5)
                    self.pa.emulMode_2Q(channel=1)
                    self.pa.setCurrent_Priority(channel=1)
                    self.pa.setCurrent(channel=1,current=signal_force)
                    self.pa.outp_ON(channel=1)
                    sleep(0.2)
                if re.search('vbso',signal_name):
                    self.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= False)
                    sleep(0.2)
                    self.mcp2317.Switch(device_addr=0x23, row=7, col=7, Enable=True)
                    sleep(0.5)
                    self.pa.emulMode_2Q(channel=1)
                    self.pa.setCurrent_Priority(channel=1)
                    self.pa.setCurrent(channel=1,current=signal_force)
                    self.pa.outp_ON(channel=1)
                    sleep(0.2)
                    
            force_signal_instruction = None

    def calculate_signal(self, calculate_signal_instruction:{}):
            if calculate_signal_instruction:
                signal_name = calculate_signal_instruction.get('Parameter')
                print(signal_name)
                if re.search('ronls', signal_name):
                    TSwitch_SW = self.sdwn_measurements[0]
                    print(TSwitch_SW)
                    TSwitch_GND = self.sdwn_measurements[1]
                    print(TSwitch_GND)
                    ron_ls = ((TSwitch_SW - TSwitch_GND)/ (400e-3) )
                    print("RON_LS value: " , ron_ls)
                if re.search('ronhs', signal_name):
                    TSwitch_SW2 = self.sdwn_measurements[2]
                    print(TSwitch_SW2)
                    TSwitch_vbso = self.vbso_measurements[0]
                    print(TSwitch_vbso)
                    ron_hs = ((TSwitch_vbso - TSwitch_SW2)/ (100e-3) )
                    print("RON_HS value: " , ron_hs)
                if re.search('ronbyp', signal_name):
                    vbat = self.vbat_measurements[0]
                    vbso_byp = self.vbso_measurements[0]
                    print(vbso_byp)
                    ron_byp = ((vbat - vbso_byp)/ (100e-3) )
                    print("RON_BYP value: " , ron_byp)

    def boost_DFT(self,data=pd.DataFrame({}), test_name=''):
        instructions = data[test_name].loc[3].split('\n')
        print(data[test_name].loc[6])
        typical = self.value_clean(data[test_name].loc[6])
        print(typical)
        for instruction in instructions:
            instruction = instruction.lower()
            # print(instruction)
            
            if re.match('run', instruction):
                if re.findall('startup', instruction):
                    print('Startup Procedure')
                    self.execute_startup()
                if re.findall('Enable_Ana_Testpoint'.lower(), instruction):
                    print('Enable Ana TestPoint Procedure')
                    self.execute_Enable_Ana_Testpoint()
                if re.findall('Boost_test_default'.lower(), instruction):
                    print('Enable Boost Test Default Procedure')
                    self.execute_Boost_test_default()
                   

            if re.match('0x',instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                print(reg_data)
                self.write_device(reg_data)
            if re.match('force', instruction):
                force_signal_instruction = self.parser.extract_Force__Instruction(instruction)
                print(f'Force Signal : {force_signal_instruction}')
                self.force_signal(force_signal_instruction)
            if re.match('measure', instruction):
                measure_signal = self.parser.extract_Measure__Instruction(instruction)
                print(f'Measure Signal : {measure_signal}')
                self.measure_value_check(measure_signal=measure_signal, typical=typical)
            if re.match('calculate',instruction):
                calculate_signal_instruction = self.parser.extract_calculation_instruction(instruction)
                print(f'Calculate Signal : {calculate_signal_instruction}')
                self.calculate_signal(calculate_signal_instruction)
                


if __name__ == '__main__':
    boost = Boost()
    output_control = E3648.OutputControl(port='GPIB0::7::INSTR')
    boost.supplies_8.setVoltage(channel=1, voltage=5)
    boost.supplies_8.setCurrent(channel=1, current=0.2)
    boost.supplies_8.outp_ON(channel=1)
    sleep(0.5)
    boost.supplies_8.setVoltage(channel=2, voltage=3.6)
    boost.supplies_8.setCurrent(channel=2, current=0.2)
    boost.supplies_8.outp_ON(channel=2)
    sleep(0.5)
    output_control.output_on(channel1=1, channel2=2 , voltage1=3.6, voltage2=1.8, current1=0.2, current2=0.2)
    boost.pa.setVoltage(channel=4,voltage=1.8)
    boost.pa.outp_ON(channel=4)
    boost_data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Boost')
    tests = boost.read_yaml(path_to_yaml=Path('Tests.yaml'))
    print(tests)
    try:
        for test in tests.Boost:
            for i in range (0x20,0x27):
                sleep(0.5)
                boost.mcp2317.Switch_reset(device_addr=i)
            sleep(0.1)
            print(f'............ {test}')
            boost.boost_DFT(boost_data, test)
    except  TypeError as e:
        print(f'Entered in Exception loop :> {e}')
        traceback.print_exc()
        pass 
    except  TypeError as e:
        print(f'CANE Entered in Exception loop :> {e}')
        traceback.print_exc()
        for i in range (0x20,0x27):
            sleep(0.5)
            boost.mcp2317.Switch_reset(device_addr=i)
        boost.pa.outp_OFF(channel=4)
        boost.supplies.outp_OFF(channel=1)
        sleep(0.5)
        boost.supplies.outp_OFF(channel=2)
        sleep(0.1)
        boost.supplies_8.outp_OFF(channel=1)
        sleep(0.5)
        boost.supplies_8.outp_OFF(channel=2)
        pass 

    except KeyboardInterrupt:
        try:
            for i in range(0x20, 0x27):
                sleep(0.5)
                boost.mcp2317.Switch_reset(device_addr=i)
            boost.pa.outp_OFF(channel=4)
            boost.supplies.outp_OFF(channel=1)
            sleep(0.5)
            boost.supplies.outp_OFF(channel=2)
            sleep(0.1)
            boost.supplies_8.outp_OFF(channel=1)
            sleep(0.5)
            boost.supplies_8.outp_OFF(channel=2)
        except KeyboardInterrupt:
            print("Interruzione forzata durante il blocco di cleanup")
            raise  

    except  Exception as e:
        print(f'PORCO Entered in Exception loop :> {e}')
        traceback.print_exc()
        for i in range (0x20,0x27):
            sleep(0.5)
            boost.mcp2317.Switch_reset(device_addr=i)
        boost.pa.outp_OFF(channel=4)
        boost.supplies.outp_OFF(channel=1)
        sleep(0.5)
        boost.supplies.outp_OFF(channel=2)
        sleep(0.1)
        boost.supplies_8.outp_OFF(channel=1)
        sleep(0.5)
        boost.supplies_8.outp_OFF(channel=2)
for i in range (0x20,0x27):
    sleep(0.5)
    boost.mcp2317.Switch_reset(device_addr=i)
boost.pa.outp_OFF(channel=1)
boost.pa.outp_OFF(channel=4)
sleep(0.1)
boost.supplies.outp_OFF(channel=1)
boost.supplies.outp_OFF(channel=2)
sleep(0.1)
boost.supplies_8.outp_OFF(channel=1)
boost.supplies_8.outp_OFF(channel=2)

