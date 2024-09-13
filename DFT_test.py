import pandas as pd 
from dft_syntaxparser import Parser
import re 
from time import sleep
from Instruments.Keysight_34461 import A34461
from Instruments.DigitalScope import dpo_2014B
from SwitchMatrix.mcp2221 import MCP2221
from SwitchMatrix.mcp2317 import MCP2317
import os 
import yaml
from pathlib import Path
from box import ConfigBox
from box.exceptions import BoxValueError
import os 
import yaml
from pathlib import Path

############################ initialization
data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='AZ_COMP')
data.head()
mcp = MCP2221()
mcp2317 = MCP2317(mcp=mcp)
slave_address = 0x6c
procedures = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Procedure')

def typical_value_clean(value:str):
    value = (lambda value : value.replace(',','.') if re.findall(',',value) else value)(value=value)
    value = (lambda value : float(value.replace('m',''))*10**-3  if isinstance(value,str)    and re.findall('m',value) else value)(value=value)
    value = (lambda value : float(value.replace('n',''))*10**-9  if isinstance(value,str)    and re.findall('n',value)  else value)(value=value)
    value = (lambda value : float(value.replace('u',''))*10**-6  if isinstance(value,str)    and re.findall('u',value)  else value)(value=value)
    value = (lambda value : float(value.replace('k',''))*10**3   if isinstance(value,str)    and re.findall('k',value)  else value)(value=value)
    value = (lambda value : float(value.replace('M',''))*10**6   if isinstance(value,str)    and re.findall('M',value)  else value)(value=value)
    value = (lambda value : float(value.replace('G',''))*10**9   if isinstance(value,str)    and re.findall('G',value)  else value)(value=value)
    if not isinstance(value,float) :
        value = float(value)
    return value
# typical_value_clean('1,2')

def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: ConfigBox type
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e

def DFT_Tests(path='Tests.yaml'):
    return read_yaml(path_to_yaml=path)

def convert_value_unit(value_str):

    """
    Converts a string containing a number and a unit of measurement.
    - Recognizes prefixes (kilo, milli, micro, nano, etc.).
    - Removes the unit of measurement (Volt, Ampere, etc.).
    """

    prefixes = {
        'k': 10**3,    # kilo
        'm': 10**-3,   # milli
        'u': 10**-6,   # micro
        'μ': 10**-6,   # micro
        'n': 10**-9,   # nano
        'p': 10**-12   # pico
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

def convert_dict_values(data):
    """
    Converts the values of a dictionary from strings with units of measurement to floats,
    keeping the original strings if they cannot be converted.
    """

    converted_dict = {}
    for key, value in data.items():
        
        converted_value = convert_value_unit(value)
        converted_dict[key] = converted_value 

    return converted_dict

def extract_last_n_values(data, n):
    numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
    last_n_values = numeric_values[-n:]
    if len(last_n_values) < n:
        print(f"Non ci sono abbastanza valori numerici nel dizionario per estrarre {n} elementi.")
        return None
    
    return last_n_values

def execute_startup():
    startup_procedure = procedures['Startup'].loc[0].split('\n')
    for instruction in startup_procedure:
        instruction = instruction.lower()
        if re.match('0x',instruction):
            reg_data = parser.extract_RegisterAddress__Instruction(instruction) 
            # print(reg_data)
            write_device(reg_data)
        if re.match('Force__SDWN__1.8V'.lower(), instruction):
            print('Force 1.8V on SDWN')
            mcp2317.Switch(device_addr=0x23,row=8, col=4, Enable=True)

def write_device(data:{}):
    device_data = mcp.mcpRead(SlaveAddress=slave_address,data=[int(data.get('RegAddr'),16)])[0]
    # print(f'Read data {hex(device_data)} ')
    bit_width = 2**(data.get('MSB') - data.get('LSB')+1)
    # print(bit_width)
    if int(data.get('Data'),16) < bit_width :
        mask = ~((bit_width-1) << data.get('LSB'))
        # print(f'mask {hex(256+mask)}')
        device_data = (device_data & mask) | ((int(data.get('Data'),16)) << data.get('LSB'))
        # print(f'Data write {hex(device_data)}')
        mcp.mcpWrite(SlaveAddress=slave_address, data=[int(data.get('RegAddr'),16),device_data])
        # written_data = mcp.mcpRead(SlaveAddress=slave_address,data=[int(data.get('RegAddr'),16)])[0]
        # print(f' data written {hex(written_data)}')
    else:
        print(f'Data is outof width ')

def execute_Enable_Ana_Testpoint():
    startup_procedure = procedures['Enable_Ana_Testpoint'].loc[0].split('\n')
    for instruction in startup_procedure:
        instruction = instruction.lower()
        if re.match('0x',instruction):
            print(parser.extract_RegisterAddress__Instruction(instruction)) 
            reg_data = parser.extract_RegisterAddress__Instruction(instruction) 
            write_device(reg_data)
        if re.match('FORCE__SDWN__OPEN'.lower(), instruction):
            print('Force SDWN OPEN')
            mcp2317.Switch(device_addr=0x23,row=8, col=4, Enable=False)

def AZcomp_DFT(data=pd.DataFrame({}),test_name=''):
    test_name = test_name
    instructions = data[test_name].loc[3].split('\n')
    typical = typical_value_clean(data[test_name].loc[6]) 
    for instruction in instructions:
        instruction = instruction.lower()
        print(instruction)
        # parse the instructions
        if re.match('run',instruction):
            if re.findall('startup', instruction):
               print('Startup Procedure')
               execute_startup()
            if re.findall('enable_ana_testpoint', instruction):
                print('execute_Enable_Ana_Testpoint Procedure')
                # execute_Enable_Ana_Testpoint()
        if re.match('0x',instruction):
            reg_data = parser.extract_RegisterAddress__Instruction(instruction)
            print(reg_data)
            # write_device(reg_data)

        if re.match('forceap', instruction):
            force_signal = parser.extract_Force_Instruction_AP(instruction)
            print(f'force_signal  > {force_signal}')
            lim = extract_last_n_values(force_signal, len(force_signal)-4)
            force_ap(force_signal, lim[0])


        if re.match('compsweepap', instruction):
            sweep_signal = parser.extract_Sweep_Instruction_AP(instruction)
            print(f'sweeep_signal  > {sweep_signal}')
            converted_dict = convert_dict_values(sweep_signal)
            print('#############################################', converted_dict)
            lim = extract_last_n_values(converted_dict, len(converted_dict)-1)
            sweep_ap(lim[0], lim[1], lim[2])

        if re.match('measure',instruction):
            print(instruction)
            measure_signal = parser.extract_Measure__Instruction(instruction)
            print(f'measure_signal  > {measure_signal}')
            # measure_value_check(measure_signal=measure_signal,typical=typical)


def force_ap(force_signal:{}, start_value):
        dc_mode = force_signal.get('AP_mode')
        if re.search('dc', dc_mode):
            print('DC_mode')
            # mcp2317.Switch(device_addr=0x23,row=8, col=5, Enable=True)
            # path = os.path.join(os.getcwd() + "PA_template" + AP_file_DC)
            # ap = Audio_precision.AP555(mode = 'BenchMode', fullpath=path)
            # ap.Configure_Generator(True, gen_value , Freq=1000, Waveform = 'Sine, Var Phase')
            # ap.FilterSel(HP_Mode='Elliptic', LP_Mode='Elliptic', Weighting="None")
            # ap.Enable_Generator(True)

def sweep_ap(start_value, end_value, step):
    print("Sei dentro")
            

if __name__ == '__main__':
    parser = Parser()
    AZ_COMP_data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='AZ_COMP')
    tests = DFT_Tests()
    print(tests)
    for test in tests.AZ_COMP:
        print(f'............ {test}')
        AZcomp_DFT(AZ_COMP_data, test)