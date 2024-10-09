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

class AZ_comp:

    ############################ initialization
    def __init__(self):
        self.data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='AZ_COMP')
        self.procedures = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Procedure')
        self.mcp = MCP2221()
        self.mcp2317 = MCP2317(mcp=self.mcp)
        self.meter = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
        self.ps_gpib = E3648('GPIB0::6::INSTR')
        self.supplies = E3648('GPIB0::7::INSTR')
        self.parser = Parser()
        self.voltmeter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.slave_address = 0x6c

    def typical_value_clean(self,value: str):
        value = (lambda value: value.replace(',', '.') if re.findall(',', value) else value)(value=value)
        value = re.sub(r'[a-zA-Z]+$', '', value)
        value = (lambda value: float(value.replace('m', '')) * 10 ** -3 if isinstance(value, str) and re.findall('m', value) else value)(value=value)
        value = (lambda value: float(value.replace('n', '')) * 10 ** -9 if isinstance(value, str) and re.findall('n', value) else value)(value=value)
        value = (lambda value: float(value.replace('u', '')) * 10 ** -6 if isinstance(value, str) and re.findall('u', value) else value)(value=value)
        value = (lambda value: float(value.replace('k', '')) * 10 ** 3 if isinstance(value, str) and re.findall('k', value) else value)(value=value)
        value = (lambda value: float(value.replace('M', '')) * 10 ** 6 if isinstance(value, str) and re.findall('M', value) else value)(value=value)
        value = (lambda value: float(value.replace('G', '')) * 10 ** 9 if isinstance(value, str) and re.findall('G', value) else value)(value=value)
        if not isinstance(value, float):
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
                self.write_device(reg_data) 
            if re.match('Force__SDWN__1.8V'.lower(), instruction):
                print('Force 1.8V on SDWN')
                self.mcp2317.Switch(device_addr=0x20, row=1, col=4, Enable=True) 

    def write_device(self,data: {}):
        device_data = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[int(data.get('RegAddr'), 16)])[0]
        bit_width = 2 ** (data.get('MSB') - data.get('LSB') + 1)
        if int(data.get('Data'), 16) < bit_width:
            mask = ~((bit_width - 1) << data.get('LSB'))
            device_data = (device_data & mask) | ((int(data.get('Data'), 16)) << data.get('LSB'))
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[int(data.get('RegAddr'), 16), device_data])
        else:
            print(f'Data is out of width')

    def execute_Enable_Ana_Testpoint(self):
        startup_procedure = self.procedures['Enable_Ana_Testpoint_AZ_comp'].loc[0].split('\n')
        for instruction in startup_procedure:
            instruction = instruction.lower()
            if re.match('0x', instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                self.write_device(reg_data)
            if re.match('FORCE__SDWN__OPEN'.lower(), instruction):
                print('Force SDWN OPEN')
                self.mcp2317.Switch(device_addr=0x20, row=1, col=4, Enable=False)

    def measure_value_check(self,measure_signal: {}, typical: float):
        if measure_signal:
            signal_Unit = measure_signal.get('Unit')
            measure_values = None
            print(signal_Unit)
            if re.search('voltage', signal_Unit):
                self.mcp2317.Switch(device_addr=0x20, row=1, col=1, Enable=True)
                sleep(0.1)
                measure_values = self.voltmeter.meas_V()
                print(f' value : {measure_values}')

            if re.search('current', signal_Unit):
                meter = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
                self.mcp2317.Switch(device_addr=0x20, row=1, col=2, Enable=True)
                sleep(1)
                self.mcp2317.Switch(device_addr=0x21, row=3, col=3, Enable=True)
                sleep(0.1)
                meter.outp_ON(channel=3)
                meter.setMeter_Range_Auto__Current(channel=3)
                sleep(1)
                measure_values = meter.getCurrent(channel=3)
                print(f' value : {measure_values}')
                sleep(1)
                meter.outp_OFF(channel=3)

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
            force_signal_instruction = None

    def AZcomp_DFT(self,data=pd.DataFrame({}), test_name=''):
        instructions = data[test_name].loc[3].split('\n')
        print(data[test_name].loc[6])
        typical = self.typical_value_clean(data[test_name].loc[6])
        print(typical)
        for instruction in instructions:
            instruction = instruction.lower()
            # print(instruction)
            
            if re.match('run', instruction):
                if re.findall('startup', instruction):
                    print('Startup Procedure')
                    self.execute_startup()
                if re.findall('Enable_Ana_Testpoint_AZ_comp'.lower(), instruction):
                    print('Enable Ana TestPoint Procedure')
                    self.execute_Enable_Ana_Testpoint()

            if re.match('0x',instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                # print(reg_data)
                self.write_device(reg_data)
            if re.match('force', instruction):
                force_signal_instruction = self.parser.extract_Force__Instruction(instruction)
                print(f'Force Signal : {force_signal_instruction}')
                self.force_signal(force_signal_instruction)
            if re.match('measure', instruction):
                measure_signal = self.parser.extract_Measure__Instruction(instruction)
                print(f'Measure Signal : {measure_signal}')
                self.measure_value_check(measure_signal=measure_signal, typical=typical)


if __name__ == '__main__':
    az_comp = AZ_comp()
    output_control = E3648.OutputControl(port='GPIB0::7::INSTR')
    output_control.output_on(channel1=1, channel2=2 , voltage1=4.0, voltage2=1.8, current1=0.2, current2=0.2)
    az_comp.meter.outp_ON(channel=4)
    AZ_COMP_data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='AZ_COMP')
    tests = az_comp.read_yaml(path_to_yaml=Path('Tests.yaml'))
    print(tests)
    try:
        for test in tests.AZ_COMP:
            print(f'............ {test}')
            az_comp.AZcomp_DFT(AZ_COMP_data, test)
    except  TypeError as e:
        print(f'Entered in Exception loop :> {e}')
        traceback.print_exc()
        pass 
    except  KeyboardInterrupt:
        for i in range (0x20,0x28):
            az_comp.mcp2317.Switch_reset(device_addr=i)
            az_comp.supplies.outp_OFF(channel=1)
            sleep(0.5)
            az_comp.supplies.outp_OFF(channel=2)
    except  Exception as e:
        print(f'Entered in Exception loop :> {e}')
        traceback.print_exc()
        for i in range (0x20,0x28):
            az_comp.mcp2317.Switch_reset(device_addr=i)
            az_comp.supplies.outp_OFF(channel=1)
            sleep(0.5)
            az_comp.supplies.outp_OFF(channel=2)

    az_comp.supplies.outp_OFF(channel=1)
    az_comp.supplies.outp_OFF(channel=2)
    az_comp.meter.outp_OFF(channel=1)
    az_comp.meter.outp_OFF(channel=4)
    # finally:

