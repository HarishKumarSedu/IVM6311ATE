

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
from Trimming import Trim
import traceback
import os
import yaml
from pathlib import Path
from box import ConfigBox
from box.exceptions import BoxValueError

class Reference:

    ############################ initialization
    def __init__(self):
        self.data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Trimming')
        self.procedures = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Procedure')
        self.mcp = MCP2221()
        self.mcp2317 = MCP2317(mcp=self.mcp)
        self.oscilloscope = dpo_2014B('USB0::0x0699::0x0456::C014545::INSTR')
        self.pa = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
        self.ps_gpib = E3648('GPIB0::6::INSTR')
        self.supplies = E3648('GPIB0::7::INSTR')
        self.supplies_8 = E3648('GPIB0::8::INSTR')
        self.output_control = E3648.OutputControl(port='GPIB0::7::INSTR')
        self.parser = Parser()
        self.voltmeter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.slave_address = 0x6c
        self.trim = Trim(mcp=self.mcp, mcp2317=self.mcp2317)
        self.reg_trim = None
        self.LSB_trim = None
        self.MSB_trim = None
        self.trim_values = None
        self.reg_value = None
        self.reg_trim2 = None
        self.LSB_trim2 = None
        self.MSB_trim2 = None
        self.current_priority_set = False

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
                sleep(0.5)
                print(reg_data)
                self.write_device(reg_data) 
            if re.match('Force__SDWN__1.8V'.lower(), instruction):
                print('Force 1.8V on SDWN')
                self.pa.arb_Ramp__Voltage(channel=4,initial_Voltage=1.8,end_Voltage= 0, initial_Time=0.2, raise_Time= 1, end_Time = 0.2)
                sleep(0.5)
                self.pa.setCurrent(channel=4, current= 0.2)
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
                self.write_device(reg_data)
            if re.match('FORCE__SDWN__OPEN'.lower(), instruction):
                print('Force SDWN OPEN')
                self.pa.arb_Ramp__Voltage(channel=4,initial_Voltage=1.8,end_Voltage= 0, initial_Time=0.2, raise_Time= 1, end_Time = 0.2)
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
                self.supplies_8.setCurrent(channel=2, current= 0.2)
                self.supplies_8.outp_ON(channel=2)
            if re.match('Force__VBSO__3.6V'.lower(), instruction):
                print('Force__VBSO__3.6V')
                self.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= True)
                sleep(0.5)
                self.supplies_8.setVoltage(channel=1,voltage=3.6)
                self.supplies_8.setCurrent(channel=1, current=0.2)
                self.supplies_8.outp_ON(channel=1)

    def measure_value_check(self,measure_signal: {}, typical: float):
        if measure_signal:
            signal_Unit = measure_signal.get('Unit')
            signal_Name = measure_signal.get('Signal')
            measure_values = None
            print(signal_Unit)
            print(signal_Name)
            if re.search('voltage', signal_Unit):
                if re.search('fsyn', signal_Name):
                    self.trim_OCP(self.reg_trim,self.LSB_trim,self.MSB_trim,self.reg_trim2,self.LSB_trim2,self.MSB_trim2)
                else: 
                    self.trim_values,self.reg_value = self.trim_sweep_voltage(self.reg_trim,self.LSB_trim,self.MSB_trim)
            if re.search('current', signal_Unit):
                pa = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
                self.mcp2317.Switch(device_addr=0x20, row=1, col=2, Enable=True)
                sleep(1)
                self.mcp2317.Switch(device_addr=0x21, row=3, col=3, Enable=True)
                sleep(0.1)
                pa.outp_ON(channel=3)
                pa.setMeter_Range_Auto__Current(channel=3)
                sleep(1)
                measure_values = pa.getCurrent(channel=3)
                print(f' value : {measure_values}')
                sleep(1)
                pa.outp_OFF(channel=3)
            if re.search('frequency', signal_Unit):
                self.trim_values,self.reg_value = self.trim_sweep_freq(self.reg_trim,self.LSB_trim,self.MSB_trim)


    def force_signal(self,force_signal_instruction: {}):
        if force_signal_instruction:
            signal_Unit = force_signal_instruction.get('Unit')
            signal_name = force_signal_instruction.get('Signal')
            print(signal_Unit)
            if re.search('V', signal_Unit):
                signal_force = force_signal_instruction.get('Value')
                if re.search('outn', signal_name):
                    self.ps_gpib.setCurrent(channel=1, current=0.2)
                    self.ps_gpib.setVoltage(channel=1, voltage=signal_force)
                    sleep(0.5)
                    self.ps_gpib.outp_ON(channel=1)
                if re.search('outp', signal_name):
                    self.ps_gpib.setCurrent(channel=2, current=0.2)
                    self.ps_gpib.setVoltage(channel=2, voltage=signal_force)
                    sleep(0.5)
                    self.ps_gpib.outp_ON(channel=2)
            
            if re.search('A', signal_Unit):
                signal_force = force_signal_instruction.get('Value')
                if re.search('sw',signal_name):
                    self.mcp2317.Switch(device_addr=0x23, row=8, col=7, Enable=True)
                    sleep(0.5)
                    self.pa.emulMode_2Q(channel=1)
                    if not self.current_priority_set:
                        self.pa.setCurrent_Priority(channel=1)
                        self.current_priority_set = True
                    # self.pa.setCurrent_Priority(channel=1)
                    self.pa.setCurrent(channel=1,current=signal_force)
                    self.pa.set_Limit_Voltage(channel=1, voltage=1)
                    self.pa.outp_ON(channel=1)
                    sleep(0.5)

            force_signal_instruction = None

    def trim_OCP(self,reg_trim, lsb, msb, reg_trim2,lsb2,msb2):
        self.reg_value,self.reg_trim, self.reg_trim2 = self.trim.sweep_trim_bit_freq_two_registers(self.reg_trim,self.LSB_trim,self.MSB_trim,self.reg_trim2,self.LSB_trim2,self.MSB_trim2)
        return self.reg_trim,self.LSB_trim,self.MSB_trim,self.reg_trim2,self.LSB_trim2,self.MSB_trim2
    
    def trim_sweep_voltage(self,reg_trim,lsb,msb):
        self.mcp2317.Switch(device_addr=0x20, row=1, col=1, Enable=True)
        self.trim_values,self.reg_value = self.trim.sweep_trim_bit_voltage(self.reg_trim,self.LSB_trim,self.MSB_trim)
        return self.trim_values,self.reg_value
    
    def trim_sweep_freq(self,reg_trim,lsb,msb):
        # input("Remove the wire that connects motherboars with the matrix number 2")
        self.trim_values,self.reg_value = self.trim.sweep_trim_bit_freq(self.reg_trim,self.LSB_trim,self.MSB_trim)
        return self.trim_values,self.reg_value

    def find_best_code(self, trim_values, reg_value, typical):
        closest_value = self.trim.find_closest_value(trim_values,typical)
        best_code = self.trim.find_best_code(trim_values, reg_value, typical)
        print(closest_value)
        print(hex(best_code))
        return closest_value,best_code
    
    def waiting_function(self,waiting_instruction:{}):
        if waiting_instruction:
            waiting_time = waiting_instruction.get('Delay')
            print(waiting_time)
            sleep(float(waiting_time))
        
    def ref_DFT(self,data=pd.DataFrame({}), test_name=''):
        instructions = data[test_name].loc[3].split('\n')
        print(data[test_name].loc[6])
        typical = self.value_clean(data[test_name].loc[6])
        print(typical)
        for instruction in instructions:
            instruction = instruction.lower()
            print(instruction)
            
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
            if re.match('trim', instruction):
                reg_instr = self.parser.extract_TrimSweep_Instruction(instruction)
                print(f'Trim instruction : {reg_instr}')
                print(type(reg_instr))
                if len(reg_instr) == 4:
                    self.reg_trim = int(reg_instr.get('regaddr1'), 16)
                    self.LSB_trim = int(reg_instr.get('lsb1'))
                    self.MSB_trim = int(reg_instr.get('msb1'))
                elif len(reg_instr) == 8:
                    self.reg_trim = int(reg_instr.get('regaddr1'), 16)
                    self.LSB_trim = int(reg_instr.get('lsb1'))
                    self.MSB_trim = int(reg_instr.get('msb1'))
                    self.reg_trim2 = int(reg_instr.get('regaddr2'), 16)
                    self.LSB_trim2 = int(reg_instr.get('lsb2'))
                    self.MSB_trim2 = int(reg_instr.get('msb2'))
                    print(hex(self.reg_trim),hex(self.LSB_trim),hex(self.MSB_trim),hex(self.reg_trim2),hex(self.LSB_trim2),hex(self.MSB_trim2 ))
            if re.match('calculate', instruction):
                closest_value,best_code =self.find_best_code(self.trim_values,self.reg_value,typical)
                best_codes.append(best_code)
                closest_values.append(closest_value)
                print(best_codes)
                print(closest_values)
            if re.match('wait', instruction):
                waiting_instruction = self.parser.extract_wait_instruction(instruction)
                print(f'Wait : {waiting_instruction}')
                self.waiting_function(waiting_instruction)

    def power_on(self):
        self.output_control = E3648.OutputControl(port='GPIB0::7::INSTR')
        self.supplies_8.setVoltage(channel=1, voltage=5)
        self.supplies_8.setCurrent(channel=1, current=0.2)
        self.supplies_8.outp_ON(channel=1)
        self.output_control.output_on(channel1=1, channel2=2 , voltage1=3.6, voltage2=1.8, current1=0.2, current2=0.2)
        sleep(0.5)
        self.supplies_8.setVoltage(channel=2, voltage=3.6)
        self.supplies_8.setCurrent(channel=2, current=0.2)
        sleep(0.5)
        self.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= True)
        sleep(0.5)
        self.supplies_8.outp_ON(channel=2)
        sleep(0.5)
        self.pa.setVoltage(channel=4,voltage=1.8)
        self.pa.setCurrent(channel=4, current=0.2)
        self.pa.outp_ON(channel=4)

    def power_off(self):
        self.pa.outp_OFF(channel=4)
        self.pa.outp_OFF(channel=3)
        self.pa.outp_OFF(channel=1)
        self.supplies.outp_OFF(channel=1)
        sleep(0.5)
        self.supplies.outp_OFF(channel=2)
        sleep(0.1)
        self.supplies_8.outp_OFF(channel=1)
        sleep(0.5)
        self.supplies_8.outp_OFF(channel=2)

if __name__ == '__main__':
    ref = Reference()
    ref.power_on()
    ref_data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Trimming')
    tests = ref.read_yaml(path_to_yaml=Path('Trimming.yaml'))
    print(tests)
    best_codes = []
    closest_values = []

    try:
        for test in tests.Trim:
            for i in range (0x20,0x27):
                sleep(0.5)
                ref.mcp2317.Switch_reset(device_addr=i)
            print(f'............ {test}')
            ref.ref_DFT(ref_data, test)

    except  TypeError as e:
        print(f'ZIO Entered in Exception loop :> {e}')
        traceback.print_exc()
        pass 

    except  TypeError as e:
        print(f'CANE Entered in Exception loop :> {e}')
        traceback.print_exc()
        for i in range (0x20,0x27):
            sleep(0.5)
            ref.mcp2317.Switch_reset(device_addr=i)
        ref.power_off()
        pass 

    except  KeyboardInterrupt:
        for i in range (0x20,0x27):
            sleep(0.5)
            ref.mcp2317.Switch_reset(device_addr=i)
        ref.power_off()

    except  Exception as e:
        print(f'PORCO Entered in Exception loop :> {e}')
        traceback.print_exc()
        for i in range (0x20,0x27):
            sleep(0.5)
            ref.mcp2317.Switch_reset(device_addr=i)
        ref.power_off(

        )
for i in range (0x20,0x27):
    sleep(0.5)
    ref.mcp2317.Switch_reset(device_addr=i)
ref.power_off()


