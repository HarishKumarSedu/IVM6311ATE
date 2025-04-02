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
from openpyxl import load_workbook 

class Reference:

    ############################ initialization
    def __init__(self):
        self.data = pd.read_excel('IVM6021_ATE_TM_web.xlsx', sheet_name='Trimming')
        self.procedures = pd.read_excel('IVM6021_ATE_TM_web.xlsx', sheet_name='Procedure')
        self.mcp = MCP2221()
        self.mcp2317 = MCP2317(mcp=self.mcp)
        self.oscilloscope = dpo_2014B('USB0::0x0699::0x0401::C020132::INSTR')
        self.pa = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
        self.ps_gpib = E3648('GPIB0::6::INSTR')
        self.supplies = E3648('GPIB0::7::INSTR')
        self.supplies_8 = E3648('GPIB0::8::INSTR')
        self.output_control = E3648.OutputControl(port='GPIB0::7::INSTR')
        self.parser = Parser()
        self.voltmeter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.ammeter = A34461('USB0::0x2A8D::0x1401::MY57216238::INSTR')
        self.slave_address = 0x68
        self.trim = Trim(mcp=self.mcp, mcp2317=self.mcp2317)
        self.reg_trim = None
        self.LSB_trim = None
        self.MSB_trim = None
        self.trim_values = None
        self.reg_value = None
        self.reg_trim2 = None
        self.LSB_trim2 = None
        self.MSB_trim2 = None
        self.best_codes = []
        self.closest_values = []
        self.valore_multimetro = None
        self.new_register_val1=None
        self.new_register_val2 = None
        self.current_priority_set = False
        self.row_names = []
        self.burn_var = False
        self.chip_counter = 0

    def value_clean(self, value):
        # Se il valore è già un numero, restituiscilo direttamente con unità vuota
        if isinstance(value, (int, float)):
            return float(value), ""

        # Converte in stringa e normalizza la virgola in punto
        value = str(value).replace(',', '.')

        # Identifica l'unità di misura (Volt, Ampere, Hertz)
        match = re.search(r'([munkMG]?[VAHz])$', value, re.IGNORECASE)
        unit = match.group(1).upper() if match else ""

        # Rimuove l'unità dalla stringa numerica
        if match:
            value = value[:match.start()]

        # Gestione dei prefissi metrici (milli, micro, nano, kilo, mega, giga)
        multipliers = {
            'm': 1e-3,  # milli
            'u': 1e-6,  # micro
            'n': 1e-9,  # nano
            'k': 1e3,   # kilo
            'M': 1e6,   # mega
            'G': 1e9    # giga
        }

        # Trova e applica il prefisso se presente
        match = re.search(r'([munkMG])', value)
        multiplier = multipliers.get(match.group(1), 1) if match else 1
        value = value.replace(match.group(1), '') if match else value

        # Converte in float
        try:
            value = float(value) * multiplier
        except ValueError:
            raise ValueError(f"Valore non valido: {value}")

        return value, unit

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
        print(startup_procedure)
        for instruction in startup_procedure:
            instruction = instruction.strip().lower()
            print(instruction)
            if re.match('Force__VDDIO__3.3V'.lower(), instruction):
                print('Force__VDDIO__3.3V')
                self.supplies.setVoltage(channel=2, voltage=3.3)
                self.supplies.setCurrent(channel=2, current=0.2)
                self.supplies.outp_ON(channel=2)
            if re.match('Force__VCC__7V'.lower(), instruction):
                print('Force__VCC__7V')
                self.supplies.setVoltage(channel=1, voltage=14)
                self.supplies.setCurrent(channel=1, current=0.2)
                self.supplies.outp_ON(channel=1)

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
        sleep(0.5)
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
            # print(hex(device_data))
            # Write the new value to the device
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg_addr, device_data])
        else:
            print(f'Data is out of width')

    def execute_startup_ref(self):
        startup_procedure = self.procedures['REF_procedure'].loc[0].split('\n')
        for instruction in startup_procedure:
            instruction = instruction.strip().lower()
            if re.match('0x', instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                self.write_device(reg_data)
            if re.match('Force__V5VDRV__5.2V'.lower(), instruction):
                print('Force__V5VDRV__5.2V')
                self.supplies_8.setVoltage(channel=1, voltage=5.2)
                self.supplies_8.setCurrent(channel=1,current=0.2)
                self.supplies_8.outp_ON(channel=1)
            if re.match('Wait'.lower(), instruction):
                waiting_instruction = self.parser.extract_wait_instruction(instruction)
                print(f'Wait : {waiting_instruction}')
                self.waiting_function(waiting_instruction)

    
    def execute_Boost_test_default(self):
        startup_procedure = self.procedures['Test_Boost'].loc[0].split('\n')
        for instruction in startup_procedure:
            instruction = instruction.lower()
            if re.match('0x', instruction):
                reg_data = self.parser.extract_RegisterAddress__Instruction(instruction)
                # print(reg_data)
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
            if re.search('voltage', signal_Unit):
                if re.search('hwmute', signal_Name):
                    self.mcp2317.Switch(device_addr=0x22, row=6, col=1, Enable=True)
                    sleep(0.5)
                    self.trim_values,self.reg_value = self.trim_sweep_voltage(self.reg_trim,self.LSB_trim,self.MSB_trim)
                #     self.trim_OCP(self.reg_trim,self.LSB_trim,self.MSB_trim,self.reg_trim2,self.LSB_trim2,self.MSB_trim2)
                # else: 
                #     self.trim_values,self.reg_value = self.trim_sweep_voltage(self.reg_trim,self.LSB_trim,self.MSB_trim)
            if re.search('current', signal_Unit):
                if re.search('hwmute', signal_Name):
                    self.mcp2317.Switch(device_addr=0x22, row=6, col=2, Enable=True)
                    sleep(0.5)
                    self.pa.emulMode_Ammeter(channel=1)
                    self.pa.outp_ON(channel=1)
                    self.trim_values,self.reg_value = self.trim_sweep_current(self.reg_trim,self.LSB_trim,self.MSB_trim)
                    self.pa.outp_OFF(channel=1)

            if re.search('frequency', signal_Unit):
                self.trim_values,self.reg_value = self.trim_sweep_freq(self.reg_trim,self.LSB_trim,self.MSB_trim, self.best_codes)


    def force_signal(self,force_signal_instruction: {}):
        if force_signal_instruction:
            signal_Unit = force_signal_instruction.get('Unit')
            signal_name = force_signal_instruction.get('Signal')
            # print(signal_Unit)
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
                if re.search('vbso', signal_name):
                    self.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= True)
                    sleep(0.5)
                    self.supplies_8.setVoltage(channel=1,voltage=signal_force)
                    self.supplies_8.setCurrent(channel=1, current=0.2)
                    self.supplies_8.outp_ON(channel=1)
                
            
            if re.search('A', signal_Unit):
                signal_force = force_signal_instruction.get('Value')
                if re.search('sw',signal_name):
                    defval_reg1 = 0x7F 
                    defval_reg2 = 0xD0  
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xFE, 0x01])
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB1, defval_reg1])
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB2, defval_reg2])
                    sleep(0.5)
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
        self.valore_multimetro, self.new_register_val1, self.new_register_val2= self.trim.sweep_trim_bit_freq_two_registers(self.reg_trim,self.LSB_trim,self.MSB_trim,self.reg_trim2,self.LSB_trim2,self.MSB_trim2)
        ref.best_codes.append(ref.new_register_val1)
        ref.best_codes.append(ref.new_register_val2)
        ref.closest_values.append(ref.valore_multimetro)
        return self.valore_multimetro, self.new_register_val1, self.new_register_val2
    
    def trim_sweep_current(self,reg_trim,lsb,msb):
        # self.mcp2317.Switch(device_addr=0x20, row=1, col=1, Enable=True)
        self.trim_values,self.reg_value = self.trim.sweep_trim_bit_current(self.reg_trim,self.LSB_trim,self.MSB_trim)
        return self.trim_values,self.reg_value
    
    def trim_sweep_voltage(self,reg_trim,lsb,msb):
        # self.mcp2317.Switch(device_addr=0x20, row=1, col=1, Enable=True)
        self.trim_values,self.reg_value = self.trim.sweep_trim_bit_voltage(self.reg_trim,self.LSB_trim,self.MSB_trim)
        return self.trim_values,self.reg_value
    
    def trim_sweep_freq(self,reg_trim,lsb,msb, best_codes):
        # input("Remove the wire that connects motherboars with the matrix number 2")
        self.trim_values,self.reg_value = self.trim.sweep_trim_bit_freq(self.reg_trim,self.LSB_trim,self.MSB_trim,self.best_codes)
        return self.trim_values,self.reg_value

    def find_best_code(self, trim_values, reg_value, typical):
        closest_value = self.trim.find_closest_value(trim_values,typical)
        best_code = self.trim.find_best_code(trim_values, reg_value, typical)
        # print(closest_value)
        # print(hex(best_code))
        return closest_value,best_code
    
    def waiting_function(self,waiting_instruction:{}):
        if waiting_instruction:
            waiting_time = waiting_instruction.get('Delay')
            # print(waiting_time)
            sleep(float(waiting_time))
        
    def ref_DFT(self,data=pd.DataFrame({}), test_name=''):
        # # Accedere alla riga 3 e confrontare il test_name
        # if test_name in data.loc[3].values:
        #     # Se il test_name è trovato, estrarre il valore dalla riga 3
        #     instructions = data.loc[3].where(data.loc[3] == test_name).dropna().values[0]
        #     print("Valore trovato nella riga 3:", instructions)
        # else:
        #     print(f"{test_name} non trovato nella riga 3.")

        test = data.loc[3].where(data.loc[3] == test_name).dropna().values[0]
        print(test)
        col_name = data.columns[data.loc[3] == test].values[0]
        instructions = data.loc[4, col_name]
        print("instructions:", instructions)
        typical = data.loc[7, col_name]
        print("typical", typical)
        typical_value, _ = self.value_clean(typical)
        print(typical_value)
        instructions = instructions.split('\n')
        for instruction in instructions:
            instruction = instruction.lower()
            print(instruction)
            
            if re.match('run', instruction):
                if re.findall('startup', instruction):
                    print('Startup Procedure')
                    self.execute_startup()
                if re.findall('REF_procedure'.lower(), instruction):
                    print('Startup_ref procedure')
                    self.execute_startup_ref()
                if re.findall('Test_Boost'.lower(), instruction):
                    print('Enable Boost Test Default Procedure')
                    self.execute_Boost_test_default()

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
            if re.match('trim', instruction):
                reg_instr = self.parser.extract_TrimSweep_Instruction(instruction)
                print(f'Trim instruction : {reg_instr}')
                # print(type(reg_instr))
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
            if re.match('calculate', instruction):
                self.closest_value, self.best_code = self.find_best_code(self.trim_values, self.reg_value, typical_value)
                self.best_codes.append(self.best_code)
                print(self.best_codes)
                self.closest_values.append(self.closest_value)
                if len(self.best_codes) == 1:
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB0, self.best_codes[0]])
                elif len(self.best_codes) == 2:
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB3, self.best_codes[1]])
                elif len(self.best_codes) == 3:
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xEF, self.best_codes[2]])  
                elif len(self.best_codes) == 4:
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB1, self.best_codes[3]])  
                elif len(self.best_codes) == 5:
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB2, self.best_codes[4]])
                # print(best_codes)
                # print(closest_values)
            if re.match('wait', instruction):
                waiting_instruction = self.parser.extract_wait_instruction(instruction)
                print(f'Wait : {waiting_instruction}')
                self.waiting_function(waiting_instruction)

    def power_on(self):
        self.supplies.setVoltage(channel=2, voltage=3.3)
        self.supplies.setCurrent(channel=2, current=0.2)
        self.supplies.outp_ON(channel=2)
        sleep(0.5)
        self.supplies.setVoltage(channel=1, voltage=14)
        self.supplies.setCurrent(channel=1, current=0.2)
        self.supplies.outp_ON(channel=1)
        sleep(0.5)
        self.supplies_8.setVoltage(channel=1,voltage=5.2)
        self.supplies_8.setCurrent(channel=1, current=0.2)
        self.supplies_8.outp_ON(channel=1)
        sleep(0.5)

    def power_off(self):
        self.supplies_8.outp_OFF(channel=2)
        sleep(0.5)
        self.supplies_8.outp_OFF(channel=1)
        sleep(0.5)
        self.supplies.outp_OFF(channel=2)
        sleep(0.5)
        self.supplies.outp_OFF(channel=1)
        sleep(0.5)
        self.pa.outp_OFF(channel=1)
        sleep(0.5)
        self.pa.outp_OFF(channel=2)
        sleep(0.5)
        self.pa.outp_OFF(channel=3)
        sleep(0.5)
        self.pa.outp_OFF(channel=4)

    def load_chip_counter(self,filename="chip_counter.txt"):
        try:
            # Verifica che filename sia una stringa
            if not isinstance(filename, str):
                raise ValueError("Il parametro filename deve essere una stringa.")

            with open(filename, "r") as file:
                return int(file.read().strip())  # Legge e converte il valore
        except (FileNotFoundError, ValueError) as e:
            # Se il file non esiste o il contenuto non è valido, crea il file e restituisci 0
            print(f"Errore: {e}. Creazione del file con valore iniziale 0.")
            try:
                with open(filename, "w") as file:
                    file.write("0")  # Scrive 0 nel file appena creato
                return 0  # Restituisce 0
            except Exception as ex:
                print(f"Errore durante la creazione del file: {ex}")
                return 0  # In caso di errore, restituisce 0


    def save_chip_counter(self, count, filename="chip_counter.txt"):
        with open(filename, "w") as file:
            file.write(str(count))  # Scrive il valore nel file

    def save_to_excel(self, filename="DFT_6201_Result.xlsx", chip_number=None):
        try:
            # Usa direttamente chip_number, senza caricare dal file
            if chip_number is None:
                raise ValueError("Il numero del chip deve essere fornito")

            # Sostituire chip_name con chip_number
            chip_name = f"chip{chip_number}"

            row_names = self.row_names if hasattr(self, 'Trimming') and self.row_names else ["Bandgap voltage", "Bandgap current", "FRO"]
            best_codes = self.best_codes if hasattr(self, 'best_codes') else [None] * len(row_names)
            closest_values = self.closest_values if hasattr(self, 'closest_values') else [None] * len(row_names)

            max_length = max(len(row_names), len(best_codes), len(closest_values))
            row_names.extend([None] * (max_length - len(row_names)))
            best_codes.extend([None] * (max_length - len(best_codes)))
            closest_values.extend([None] * (max_length - len(closest_values)))

            best_codes = [format(x, 'X') if x is not None else None for x in best_codes]

            data_to_save = {
                "Chip": [chip_name] * max_length,  # Aggiunge il numero del chip a ogni riga
                "Trimming": row_names,
                "Best Codes": best_codes,
                "Closest Values": closest_values,
            }
            df_new = pd.DataFrame(data_to_save)

            if os.path.exists(filename):
                existing_df = pd.read_excel(filename, sheet_name="Trimming")
                combined_df = pd.concat([existing_df, pd.DataFrame([[""] * len(data_to_save)], columns=data_to_save.keys()), df_new], ignore_index=True)
            else:
                combined_df = pd.concat([df_new, pd.DataFrame([[""] * len(data_to_save)], columns=data_to_save.keys())], ignore_index=True)

            with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
                combined_df.to_excel(writer, sheet_name="Trimming", index=False)

            print(f"File salvato correttamente come {filename}.")

        except Exception as e:
            print(f"Errore durante il salvataggio: {e}")

    def write_trimming_bit(self, chip_number):
        
        self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xFE, 0x01])
        registers = [0xC0, 0xC1]
        self.best_codes.pop(0)
        print(self.best_codes)
        fro = self.best_codes[1]
        push_reg = self.mcp.mcpRead(SlaveAddress=0x68, data=[0xCA], Nobytes=1)[0]  
        for reg, code in zip(registers, self.best_codes):
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg, code])
        if push_reg == 0xFF:
            self.mcp.mcpWrite(SlaveAddress=0x68, data=[0xC1, fro])
            self.mcp.mcpWrite(SlaveAddress=0x68, data=[0xCA, 0xFE])
            # self.mcp.mcpWrite(SlaveAddress=0x68, data=[reg_trim, new_register_val])
        else:
            self.mcp.mcpWrite(SlaveAddress=0x68, data=[0xC1, fro])
            self.mcp.mcpWrite(SlaveAddress=0x68, data=[0xCA, 0xFF])
        
        print(self.mcp.mcpRead(SlaveAddress=0x68, data=[0xC1], Nobytes=1)[0])  
       
            
        # Scrittura del chip number nel registro 0xAE (se specificato)
        if chip_number is not None:
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xAE, int(chip_number)])

        print(self.mcp.mcpRead(SlaveAddress=0x68, data=[0xAE], Nobytes=1)[0])  

    def burn_procedure(self, chip_number):
        registers = [0xC0, 0xC1]  # Aggiunto registro 0xBB
        names = ["C0", "C1"]

        # Lettura iniziale dei registri
        read_values = [self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg], Nobytes=1)[0] for reg in registers]
        for i, name in enumerate(names):
            # Usa chip_number per BB invece di best_codes[i]
            trimming_value = chip_number if name == "AE" else (self.best_codes[i] if i < len(self.best_codes) else 'N/A')
            print(f"Value read from the register {name}: {read_values[i]}. {name}'s trimming value: {trimming_value}")

        # Confronto tra valori letti e attesi
        for i, (reg_value, best_code) in enumerate(zip(read_values, self.best_codes + [chip_number])):  # Usa chip_number per BB
            if i < len(self.best_codes) and reg_value != best_code:
                print(f"Reg {names[i]} has different value")
                return

        # Alimentazione
        self.supplies_8.setVoltage(channel=2, voltage=12)
        self.supplies_8.setCurrent(channel=2, current=0.3)
        self.supplies_8.outp_ON(channel=2)
        sleep(0.5)
        self.supplies.setVoltage(channel=1, voltage=8)
        self.supplies.setCurrent(channel=1, current=0.3)
        self.supplies.outp_ON(channel=1)
        sleep(0.5)
        ########################Burnign VBGcurrent################
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3E, 0x10])
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3F, 0x80])
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3E, 0x12])
        ########################Burnign VBG&FRO################
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3E, 0x10])
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3F, 0x81])
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3E, 0x12])
        ########################Burnign chipID################
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3E, 0x10])
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3F, 0x6E])
        self.mcp.mcpWrite(SlaveAddress= self.slave_address, data = [0x3E, 0x12])



if __name__ == '__main__':
    chip_number = 1  # Inizializza il numero del chip
    while True:  # Loop infinito
        answer = input("Do you want to insert a new chip? (y/n): ").strip().lower()

        if answer == 'y':
            print(f"\n--- Chip number {chip_number} ---")
            ref = Reference()
            ref.power_on()
            ref_data = pd.read_excel('IVM6021_ATE_TM_web.xlsx', sheet_name='Trimming')
            # print(ref_data)
            tests = ref.read_yaml(path_to_yaml=Path('Trimming.yaml'))
            print(tests)

            try:
                for test in tests.Trim:
                    for i in range(0x20, 0x27):
                        sleep(0.5)
                        ref.mcp2317.Switch_reset(device_addr=i)
                    print(f'............ {test}')     
                    ref.ref_DFT(ref_data, test)
                # ref.save_to_excel("DFT_6201_Result.xlsx", chip_number)

                if ref.burn_var:
                    ref.save_to_excel("DFT_6201_Result.xlsx", chip_number)
                    ref.write_trimming_bit(chip_number)
                    ref.burn_procedure(chip_number)

            except TypeError as e:
                print(f'ZIO Entered in Exception loop :> {e}')
                traceback.print_exc()

            except KeyboardInterrupt:
                for i in range(0x20, 0x27):
                    sleep(0.5)
                    ref.mcp2317.Switch_reset(device_addr=i)
                ref.power_off()

            except Exception as e:
                print(f'PORCO Entered in Exception loop :> {e}')
                traceback.print_exc()
                for i in range(0x20, 0x27):
                    sleep(0.5)
                    ref.mcp2317.Switch_reset(device_addr=i)
                ref.power_off()

            for i in range(0x20, 0x27):
                sleep(0.5)
                ref.mcp2317.Switch_reset(device_addr=i)
            ref.power_off()

            chip_number += 1  # Incrementa automaticamente il numero del chip

        elif answer == 'n':
            print("End of program")
            for i in range(0x20, 0x27):
                sleep(0.5)
                ref.mcp2317.Switch_reset(device_addr=i)
            ref.power_off()
            break  # Esce dal loop e termina il programma

        else:
            print("Risposta non valida. Digita 'si' o 'no'.")




