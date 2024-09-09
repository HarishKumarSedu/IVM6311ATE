import pandas as pd 
from dft_syntaxparser import Parser
import re 
from time import sleep
# from Instruments.Keysight_34461 import A34461
# from Instruments.DigitalScope import dpo_2014B
import os 
import yaml
from pathlib import Path
from box import ConfigBox
from box.exceptions import BoxValueError
import os 
import yaml
from pathlib import Path

data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='AZ_COMP')
data.head()

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
typical_value_clean('1,2')

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
    Converte una stringa contenente un numero e un'unità di misura.
    - Riconosce i prefissi (kilo, milli, micro, nano, etc.).
    - Rimuove l'unità di misura (Volt, Ampere, etc.).
    """
    prefixes = {
        'k': 10**3,    # kilo
        'm': 10**-3,   # milli
        'u': 10**-6,   # micro
        'μ': 10**-6,   # micro
        'n': 10**-9,   # nano
        'p': 10**-12   # pico
    }

    # Usa regex per separare il numero dall'unità
    match = re.match(r"([-+]?\d*\.?\d+)([a-zA-Z]*)", value_str)
    if match:
        value, unit = match.groups()
        value = float(value)  # Converte il valore numerico in float

        # Controlla se l'unità inizia con un prefisso conosciuto
        if unit and unit[0].lower() in prefixes:
            prefix = unit[0].lower()
            multiplier = prefixes[prefix]
            # Aggiorna il valore usando il moltiplicatore
            value *= multiplier
        
        # Restituisce solo il valore numerico
        return value
    
    # Se non è un valore numerico con unità, ritorna la stringa originale
    return value_str

def convert_dict_values(data):
    """
    Converte i valori di un dizionario da stringhe con unità di misura a float,
    mantenendo le stringhe originali se non possono essere convertite.
    """
    converted_dict = {}
    for key, value in data.items():
        # Prova a convertire ogni valore
        converted_value = convert_value_unit(value)
        converted_dict[key] = converted_value  # Memorizza il valore, convertito o lasciato invariato

    return converted_dict

def extract_last_n_values(data, n):
    numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
    last_n_values = numeric_values[-n:]
    if len(last_n_values) < n:
        print(f"Non ci sono abbastanza valori numerici nel dizionario per estrarre {n} elementi.")
        return None
    
    return last_n_values


def AZcomp_DFT(data=pd.DataFrame({}),test_name=''):
    gen_value = -14.067
    AP_file_DC = "Char_6311_DC.approjx"
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
            #    execute_startup()
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