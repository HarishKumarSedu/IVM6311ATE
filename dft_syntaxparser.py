
import re 
from typing import List

class Parser:
    
    def __init__(self) -> None:
        pass
    
    def extract_RegisterAddress__Instruction(self,instruction: str):
        pattern1 = re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+\[(.*?)\]+[_]+(0[xX]+[0-9a-fA-F]+)\b") # sample data 0x00[1:2]_0x0
        pattern2 = re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+[_]+(0[xX]+[0-9a-fA-F]+)\b") # sample data 0x00_0x0
        pattern3 = re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+\[(.*?)\]") # sample data 0x00[1:2]
        # parse the data for the bit information and the register information 
        def register_format(instruction):
            instruction_length = len(instruction)
            register = {}
            # there is no bit field it is the default size
            if instruction_length == 2:
                if ":" in instruction[1]:
                    bits = instruction[1].split(':')
                    register={
                    "RegAddr" : hex(int(instruction[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : None,
                    }
                else:
                    register={
                        "RegAddr" : hex(int(instruction[0],16)),
                        "MSB" : 7,
                        "LSB" : 0,
                        "Data" : hex(int(instruction[1],16)),
                    }
            # check for the bit field 
            elif instruction_length == 3:
                #check for the single bit or bit field 
                if ":" in instruction[1]:
                    bits = instruction[1].split(':')
                    register={
                    "RegAddr" : hex(int(instruction[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : hex(int(instruction[2],16)),
                    }

                else:
                    register={
                    "RegAddr" : hex(int(instruction[0],16)),
                    "MSB" :hex(int(instruction[1],16)),
                    "LSB" : hex(int(instruction[1],16)),
                    "Data" : hex(int(instruction[2],16)),
                    }
            return register
        # Remove the comments from the register
        if re.search(r"\"(.*?)\"",instruction):
            instruction = re.sub(r"\"(.*?)\"",'',instruction)
        if  re.match(pattern1, instruction):
            # register = register_format(value)
            register = register_format(re.findall(pattern1, instruction)[0])
            # parse only register information and the register value 
        elif re.match(pattern2, instruction): 
            register = register_format(re.findall(pattern2, instruction)[0])
        elif re.match(pattern3, instruction): 
            register = register_format(re.findall(pattern3, instruction)[0])
        else: 
            register = {}

        return register
    
    # # extract_TrimSweep__Instruction('TrimSweep - 0xB0[7:4] "Select code which sets ATEST voltage as close as possible to target"')
    def extract_TrimSweep__Instruction(self,instruction: str):
       def register_format(instruction):
           instruction_length = len(instruction)
           register = {}
           # there is no bit field it is the default size
           if instruction_length == 2:
               if ":" in instruction[1]:
                   bits = instruction[1].split(':')
                   register={
                   "RegAddr" : hex(int(instruction[0],16)),
                   "MSB" :int(bits[0],16),
                   "LSB" : int(bits[1],16),
                   "Data" : None,
                   }
               else:
                   register={
                       "RegAddr" : hex(int(instruction[0],16)),
                       "MSB" : 7,
                       "LSB" : 0,
                       "Data" : hex(int(instruction[1],16)),
                   }
           # check for the bit field 
           elif instruction_length == 3:
               #check for the single bit or bit field 
               if ":" in instruction[1]:
                   bits = instruction[1].split(':')
                   register={
                   "RegAddr" : hex(int(instruction[0],16)),
                   "MSB" :hex(int(bits[1],16)),
                   "LSB" : hex(int(bits[0],16)),
                   "Data" : hex(int(instruction[2],16)),
                   }
    
               else:
                   register={
                   "RegAddr" : hex(int(instruction[0],16)),
                   "MSB" :hex(int(instruction[1],16)),
                   "LSB" : hex(int(instruction[1],16)),
                   "Data" : hex(int(instruction[2],16)),
                   }
           return register
       # extract the trim sweep pattren 
       pattern = re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+\[(.*?)\]")
       instruction = re.findall(pattern, instruction)[0]
       return register_format(instruction=instruction)
   
    def extract_Trim__Instruction(self,instruction: str):
        return self.extract_TrimSweep__Instruction(instruction)

    def extract_CopyRegister__Instruction(self,instruction: str)->dict:
        pattern1=re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+\[(.*?)\]")
        register ={}
        def register_format(instruction):
            instruction_length = len(instruction)
            register = {}
            # there is no bit field it is the default size
            if instruction_length == 2:
                if ":" in instruction[1]:
                    bits = instruction[1].split(':')
                    register={
                    "RegAddr" : hex(int(instruction[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : None,
                    }
                else:
                    register={
                        "RegAddr" : hex(int(instruction[0],16)),
                        "MSB" : 7,
                        "LSB" : 0,
                        "Data" : hex(int(instruction[1],16)),
                    }
            # check for the bit field 
            elif instruction_length == 3:
                #check for the single bit or bit field 
                if ":" in instruction[1]:
                    bits = instruction[1].split(':')
                    register={
                    "RegAddr" : hex(int(instruction[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : hex(int(instruction[2],16)),
                    }

                else:
                    register={
                    "RegAddr" : hex(int(instruction[0],16)),
                    "MSB" :hex(int(instruction[1],16)),
                    "LSB" : hex(int(instruction[1],16)),
                    "Data" : hex(int(instruction[2],16)),
                    }
            return register

        if 'copy__' in instruction.lower():
            if len(regs := [re.findall(pattern1, i)[0] for i in instruction.split('__')[1:] if re.match(pattern1, i)]) == 2:
                if copyReg := register_format(regs[0]):
                    if pasteReg := register_format(regs[1]):
                        register={
                            "copyReg":copyReg,
                            "pasteReg":pasteReg,
                        }
            else:
                register =register
        else:
            register = register

        return register
    # extract_CopyRegister__Instruction('Copy__0xCB[7:4]__0xCC[3:0]')
    def extract_RestoreRegister__Instruction(self,instruction: str)->dict:
        # Remove the comments from the register
        if re.search(r"\"(.*?)\"",instruction):
            instruction = re.sub(r"\"(.*?)\"",'',instruction)

        pattern1=re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+\[(.*?)\]")
        register ={}
        def register_format(reg:List):
            instruction_length = len(reg)
            register = {}
            # there is no bit field it is the default size
            if instruction_length == 2:
                if ":" in reg[1]:
                    bits = reg[1].split(':')
                    register={
                    "RegAddr" : hex(int(reg[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : None,
                    }
                else:
                    register={
                        "RegAddr" : hex(int(reg[0],16)),
                        "MSB" : 7,
                        "LSB" : 0,
                        "Data" : hex(int(reg[1],16)),
                    }
            # check for the bit field 
            elif instruction_length == 3:
                #check for the single bit or bit field 
                if ":" in reg[1]:
                    bits = reg[1].split(':')
                    register={
                    "RegAddr" : hex(int(reg[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : hex(int(reg[2],16)),
                    }
            else :
                #check for the single bit or bit field 
                register={
                "RegAddr" : hex(int(reg[0],16)),
                "MSB" :'0x7',
                "LSB" : '0x1',
                "Data" : None,
                }
            return register

        if 'restore__' in instruction.lower():
            if len(regs := [ re.findall(pattern1, i)[0] if re.match(pattern1, i) else i for i in instruction.split('__')[1:]  ] ) == 2:
                if restoreReg := register_format(regs[1]):
                    register={
                            "restoreReg":restoreReg,
                            "var":regs[0],
                        }
            else:
                register =register
        else:
            register = register

        return register
    # extract_RestoreRegister__Instruction('Restore__varCB__0xCB "int offset idle"')

    def extract_SaveRegister__Instruction(self,instruction: str)->dict:
        # Remove the comments from the register
        if re.search(r"\"(.*?)\"",instruction):
            instruction = re.sub(r"\"(.*?)\"",'',instruction)

        pattern1=re.compile(r"\b(0[xX]+[0-9a-fA-F]+)+\[(.*?)\]")
        register ={}
        def register_format(reg:List):
            instruction_length = len(reg)
            register = {}
            # there is no bit field it is the default size
            if instruction_length == 2:
                if ":" in reg[1]:
                    bits = reg[1].split(':')
                    register={
                    "RegAddr" : hex(int(reg[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : None,
                    }
                else:
                    register={
                        "RegAddr" : hex(int(reg[0],16)),
                        "MSB" : 7,
                        "LSB" : 0,
                        "Data" : hex(int(reg[1],16)),
                    }
            # check for the bit field 
            elif instruction_length == 3:
                #check for the single bit or bit field 
                if ":" in reg[1]:
                    bits = reg[1].split(':')
                    register={
                    "RegAddr" : hex(int(reg[0],16)),
                    "MSB" :hex(int(bits[1],16)),
                    "LSB" : hex(int(bits[0],16)),
                    "Data" : hex(int(reg[2],16)),
                    }
            else :
                #check for the single bit or bit field 
                register={
                "RegAddr" : hex(int(reg[0],16)),
                "MSB" :'0x7',
                "LSB" : '0x1',
                "Data" : None,
                }
            return register

        if 'save__' in instruction.lower():
            if len(regs := [ re.findall(pattern1, i)[0] if re.match(pattern1, i) else i for i in instruction.split('__')[1:]  ] ) == 2:
                if saveReg := register_format(regs[0]):
                    register={
                            "saveReg":saveReg,
                            "var":regs[1],
                        }
            else:
                register =register
        else:
            register = register

        return register
    #extract_SaveRegister__Instruction('Save__0xCB__varCB "int offset idle"')
    
    def extract_Force__Instruction(self,instruction: str):
        force_signal = {}
        def delist(x:List):
            if isinstance(x,List) and len(x) != 0 :
                x=x[-1]
            elif len(x) == 0:
                x = 0
            else:
                x = x
            return x 

        def value_unit(value, unit):
            if 'm' in unit:
                value = value*10**-3
                unit = unit.strip('m').capitalize()

            elif 'u' in unit:
                value = value*10**-6
                unit = unit.strip('u').capitalize()

            elif 'n' in unit:
                value = value*10**-9
                unit = unit.strip('n').capitalize()

            elif 'k' in unit:
                value = value*10**3
                unit = unit.strip('k').capitalize()

            else :
                value = value
                unit = unit.capitalize()

            return value, unit

        # match the small or capital letter force key word
        if re.match('[Force]|[force]', instruction) and re.search('__', instruction) :
            signal = instruction
            # signal = re.findall(re.compile('([A-Za-z0-9\.\-]+)'), Instruction)[1:] # find the force signal and with the value 
            #remove the comments if there are any comments 
            if re.search(r"\"(.*?)\"",signal):
                signal = re.sub(r"\"(.*?)\"",'',signal)

            signal = signal.split('__')[1:] # find the force signal and with the value 
            #check the signal and value, array length 
            # if the instruction has signal and the value array length must the 2 
            signal_length = len(signal)
            if signal_length == 2:
                ########################
                # for force instruction length 2 
                # @pattren 'Force_Current__SW__400mA'
                ########################

                signal_name = signal[0]
                    #check the signal unit and extract the number 
                unit = delist(re.findall('[A-Za-z]+', signal[1].lower()))
                if  value := float(delist(re.findall('[0-9\.\-]+', signal[1]))) :
                    # check the volatage or current 
                    value, unit = value_unit(value,unit)
                # else check for the open or close 

                elif value := delist(re.findall('OPEN', signal[1])):
                    unit = None 
                elif value := delist(re.findall('CLOSE', signal[1])):
                        unit = None

                force_signal = {
                'Signal' : signal_name,
                'Value'  : value ,
                'Unit'   : unit
                }

            elif signal_length == 3:
                ########################
                # for force instruction length 2 
                # @pattren 'Force_Current__SW__400mA'
                ########################
                signal_name = signal[1]
                #check the signal unit and extract the number 
                unit = delist(re.findall('[A-Za-z]+', signal[2].lower()))
                if  value := float(delist(re.findall('[0-9\.\-]+', signal[2]))) :
                    # check the volatage or current 
                    value, unit = value_unit(value,unit)

                # else check for the open or close 
                elif value := delist(re.findall('OPEN', signal[1])):
                    unit = None 
                elif value := delist(re.findall('CLOSE', signal[1])):
                    unit = None 

                force_signal = {
                    'Signal' : signal_name,
                    'Value'  : value ,
                    'Unit'   : unit
                }


        return force_signal    
        # extract_Force__Instruction(Instruction = 'Force_Current__SW__400mA')
        # extract_Force__Instruction(Instruction = 'Force_Current__VBSO__-400mA')
        # extract_Force__Instruction(Instruction = 'Force_Current__SW__400mA "chiedere comando corrente"')
        # extract_Force__Instruction(Instruction = 'Force__SDWN__OPEN')
        # extract_Force__Instruction(Instruction = 'Force__SDWN__1.8V')

    def extract_Force_Instruction_AP(self,instruction: str):
        
        force_signal = {}
        def delist(x:List):
            if isinstance(x,List) and len(x) != 0 :
                x=x[-1]
            elif len(x) == 0:
                x = 0
            else:
                x = x
            return x 

        def value_unit(value, unit):
            if 'm' in unit:
                value = value*10**-3
                unit = unit.strip('m').capitalize()

            elif 'u' in unit:
                value = value*10**-6
                unit = unit.strip('u').capitalize()

            elif 'n' in unit:
                value = value*10**-9
                unit = unit.strip('n').capitalize()

            elif 'k' in unit:
                value = value*10**3
                unit = unit.strip('k').capitalize()

            else :
                value = value
                unit = unit.capitalize()

            return value, unit

        # match the small or capital letter force key word
        if re.match('[ForceAP]|[forceAP]', instruction) and re.search('__', instruction) :
            signal = instruction
            # signal = re.findall(re.compile('([A-Za-z0-9\.\-]+)'), Instruction)[1:] # find the force signal and with the value 
            #remove the comments if there are any comments 
            if re.search(r"\"(.*?)\"",signal):
                signal = re.sub(r"\"(.*?)\"",'',signal)

            signal = signal.split('__')[1:] # find the force signal and with the value 
            #check the signal and value, array length 
            # if the instruction has signal and the value array length must the 2 
            signal_length = len(signal)
            if signal_length == 2:
                ########################
                # for force instruction length 2 
                # @pattren 'Force_Current__SW__400mA'
                ########################

                AP_mode = signal[0]
                signal_name = signal[1]
                    #check the signal unit and extract the number 
                unit = delist(re.findall('[A-Za-z]+', signal[1].lower()))
                if  value := float(delist(re.findall('[0-9\.\-]+', signal[1]))) :
                    # check the volatage or current 
                    value, unit = value_unit(value,unit)
                # else check for the open or close 

                elif value := delist(re.findall('OPEN', signal[1])):
                    unit = None 
                elif value := delist(re.findall('CLOSE', signal[1])):
                        unit = None

                force_signal = {
                'AP_mode': AP_mode,
                'Signal' : signal_name,
                'Value'  : value ,
                'Unit'   : unit
                }


            elif signal_length == 3:
                ########################
                # for force instruction length 2 
                # @pattren 'Force_Current__SW__400mA'
                ########################
                AP_mode = signal[0]
                signal_name = signal[1]
                #check the signal unit and extract the number 
                unit = delist(re.findall('[A-Za-z]+', signal[2].lower()))
                if  value := float(delist(re.findall('[0-9\.\-]+', signal[2]))) :
                    # check the volatage or current 
                    value, unit = value_unit(value,unit)

                # else check for the open or close 
                elif value := delist(re.findall('OPEN', signal[1])):
                    unit = None 
                elif value := delist(re.findall('CLOSE', signal[1])):
                    unit = None 

                force_signal = {
                    'AP_mode': AP_mode,
                    'Signal' : signal_name,
                    'Value'  : value ,
                    'Unit'   : unit
                }


            print(force_signal)

        return force_signal    
    
    def extract_Sweep_Instruction_AP(self,instruction: str):
        
        force_signal = {}
        def delist(x:List):
            if isinstance(x,List) and len(x) != 0 :
                x=x[-1]
            elif len(x) == 0:
                x = 0
            else:
                x = x
            return x 

        def value_unit(value, unit):
            if 'm' in unit:
                value = value*10**-3
                unit = unit.strip('m').capitalize()

            elif 'u' in unit:
                value = value*10**-6
                unit = unit.strip('u').capitalize()

            elif 'n' in unit:
                value = value*10**-9
                unit = unit.strip('n').capitalize()

            elif 'k' in unit:
                value = value*10**3
                unit = unit.strip('k').capitalize()

            else :
                value = value
                unit = unit.capitalize()

            return value, unit

        # match the small or capital letter force key word
        if re.match('[CompSweepAP]|[compsweepAP]', instruction) and re.search('__', instruction) :
            signal = instruction
            # signal = re.findall(re.compile('([A-Za-z0-9\.\-]+)'), Instruction)[1:] # find the force signal and with the value 
            #remove the comments if there are any comments 
            if re.search(r"\"(.*?)\"",signal):
                signal = re.sub(r"\"(.*?)\"",'',signal)

            signal = signal.split('__')[1:] # find the force signal and with the value 
            #check the signal and value, array length 
            # if the instruction has signal and the value array length must the 2 
            signal_length = len(signal)
            print(signal_length)
            if signal_length == 3:
                ########################
                # for force instruction length 2 
                # @pattren 'Force_Current__SW__400mA'
                ########################

                AP_mode = signal[0]
                signal_name = signal[1]
                    #check the signal unit and extract the number 
                unit = delist(re.findall('[A-Za-z]+', signal[1].lower()))
                if  value := float(delist(re.findall('[0-9\.\-]+', signal[1]))) :
                    # check the volatage or current 
                    value, unit = value_unit(value,unit)
                # else check for the open or close 

                elif value := delist(re.findall('OPEN', signal[1])):
                    unit = None 
                elif value := delist(re.findall('CLOSE', signal[1])):
                        unit = None

                force_signal = {
                'Signal' : signal_name,
                'Value'  : value ,
                'Unit'   : unit
                }

                print(force_signal)

            elif signal_length == 4:
                ########################
                # for force instruction length 2 
                # @pattren 'Force_Current__SW__400mA'
                ########################
                signal_name = signal[0]
                startin_value = signal[1]
                end_value = signal[2]
                step_value = signal[3]
                #check the signal unit and extract the number 
                unit = delist(re.findall('[A-Za-z]+', signal[2].lower()))
                if  value := float(delist(re.findall('[0-9\.\-]+', signal[2]))) :
                    # check the volatage or current 
                    value, unit = value_unit(value,unit)

                # else check for the open or close 
                elif value := delist(re.findall('OPEN', signal[1])):
                    unit = None 
                elif value := delist(re.findall('CLOSE', signal[1])):
                    unit = None 

                force_signal = {
                    'Signal' : signal_name,
                    'Start_Value'  : startin_value,
                    'End_Value'   : end_value,
                    'Step_value': step_value,
                }


            print(force_signal)
        

        return force_signal    
    
    def extract_Delay__Instruction(self,instruction: str):
        delay = 0
        # meath the measure signal
        Instruction = instruction.lower()
        if re.match('wait', Instruction):
            signal = re.findall('[A-Za-z0-9\.]+', Instruction)[1:] # find the measure signal and with the value 
            #check the signal and value, array length 
            # if the instruction has signal and the value array length must the 2 
            if len(signal) >= 2:
                print()
                delay = float( (lambda x :  float(*x) if isinstance(x,List) else float(*x))(re.findall('[0-9\.]+', signal[1])))
                # check for the milli seconds 
                if 'ms' in signal[1]:
                    delay  = delay* 10**-3
                # check for the micro seconds 
                elif 'us' in signal[1]:
                    delay  = delay* 10**-6
        return delay    
    # extract_Delay__Instruction(Instruction = 'Wait__delay__0.1ms')
    
    def extract_Measure__Instruction(self,instruction: str):
        measure_signal = {}
        signal = instruction

        if re.search(r"\"(.*?)\"",signal):
            signal = re.sub(r"\"(.*?)\"",'',signal)

        if re.match('meas', signal.lower()):
            signal = re.findall('[A-Za-z0-9\.]+', signal)[1:] # find the measure signal and with the value 
            #check the signal and value, array length 
            # if the instruction has signal and the value array length must the 2 
            if len(signal) >= 2:
                signal_name = signal[1]
                unit = signal[0]

                measure_signal = {
                    'Signal' : signal_name,
                    'Unit'   : unit
                }

        return measure_signal    
    # extract_Measure__Instruction(Instruction = 'Measure__Current__SDWN')
    
    #procedure signal extraction 
    # instruction = 'Run_DACPA_tourn_on_wo_calibration'
    def extract_Procedure(self,instruction: str):
        pattern = re.compile(r'Run_+([0-9a-zA-Z-_]+)') # extract the signal and the signal value 
        if re.search(pattern, instruction):
            signal = re.findall(pattern, instruction)[0]
            instruction = signal
            # print(signal)
        return instruction
    # Procedure__extract(instruction)

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

if __name__ == '__main__':
    parser = Parser()
    # print(parser.extract_TrimSweep__Instruction('trimsweep - 0xb0[7:4] "select code which sets atest voltage as close as possible to target"'))
    print(parser.value_clean('2ma'))
    