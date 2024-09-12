import time
import pyautogui
import pywinauto
from pywinauto import Application
from pywinauto.keyboard import send_keys
import pyvisa as visa
from pyvisa.attributes import *
from pyvisa.constants import *
from pywinauto import Application

class dpo_2014B:

    def __init__(self, usb_id):
        rm = visa.ResourceManager()
        # rm.list_resources()
        self.scope = rm.open_resource(usb_id)
        self.scope.read_termination = '\n'
        self.scope.write_termination = '\n'

        # self.reset()

    def get_IDN(self):
        return (self.scope.query('*IDN?'))

    def reset(self):
        self.scope.write('*RST')     

    def get_error(self):
        return self.scope.query('SYST:ERR?')  
    
    def meas_Freq(self,Meas='MEAS1'):
        self.scope.write(f'MEASUrement:{Meas}:TYPE FREQUENCY')
        return float(self.scope.query(f'MEASUrement:{Meas}:VALUE?'))
    
    def imm_meas_Freq(self, channel=1):
        self.scope.write(f'MEASUrement:IMMed:TYPe FREQUENCY')
        self.scope.write(f':MEASUrement:IMMed:SOUrce{str(channel)} CH{str(channel)}')
        self.scope.write(f':MEASUrement:IMMed:VALue?')
        value = self.scope.read()
        return float(value)
    
    def set_trigger__mode(self,mode='AUTO'):
        # TRIGger:MAIn:MODe { AUTO | NORMal }
        self.scope.write(f'TRIGger:MAIn:MODe {mode}')

    def init_scopePosEdge__Trigger(self,channel='CH1'):
        self.scope.write(':TRIG:A:TYP EDG')
        self.scope.write(f':TRIG:A:EDGE:SOU {channel}')
        self.scope.write(':TRIG:A:EDGE:SLO RIS')
        # self.scope.write('ACQUIRE:STOPAFTER SEQUENCE')
        # self.scope.write('ACTONEV:EVENTTYP TRIG')
        # self.scope.write(':ACTONEV:NUMACQ 1')
        # self.scope.write(':ACTONEV:REPEATC 1')
        
    def init_scopeNegEdge__Trigger(self,channel='CH1'):
        self.scope.write(':TRIG:A:TYP EDG')
        self.scope.write(f':TRIG:A:EDGE:SOU {channel}')
        self.scope.write(':TRIG:A:EDGE:SLO FALL')
        self.scope.write('ACQUIRE:STOPAFTER SEQUENCE')
        # self.scope.write('ACTONEV:EVENTTYP TRIG')
        # self.scope.write(':ACTONEV:NUMACQ 1')
        # self.scope.write(':ACTONEV:REPEATC 1')

    def single_Trigger__ON(self):
        self.scope.write('ACQuire:STATE ON')
    def single_Trigger__RUN(self):
        self.scope.write('ACQuire:STATE RUN')
    def set_Channel__VScale(self,channel=1,scale=0.05):
        self.scope.write(f'CH{str(channel)}:SCAle {str(scale)}')
    def get_Channel__VScale(self,channel=1):
        return float(self.scope.query(f'CH{str(channel)}:SCAle?'))
    def set_HScale(self,scale='400E-9'):
        self.scope.write(f'HORizontal:MAIn:SCAle {scale}')
    def get_HScale(self):
        return float(self.scope.query(f'HORizontal:MAIn:SCAle'))
    
    def set_autoSet(self):
        self.scope.write('AUTOSet EXECute')

    @property
    def acquireState(self):
        if float(self.scope.query('ACQuire:STATE?')) == 1.0:
            State = True 
        else :
            State = False 

        return State
    
    def get_trigger__level(self):
        return float(self.scope.query('TRIGger:MAIn:LEVel?')) 
    
    def set_trigger__level(self,level):
        self.scope.write(f'TRIGger:MAIn:LEVel {str(level)}')

    def scopeTrigger_Acquire(self,channel='CH1'):
        self.scope.write('ACQUIRE:STATE OFF')
        self.scope.write(f'SELECT:{channel} ON')
        self.scope.write('ACQUIRE:MODE SAMPLE')
        self.scope.write('ACQUIRE:STOPAFTER SEQUENCE')
        # /* Acquire waveform data */
        self.scope.write('ACQUIRE:STATE ON')
        # /* Set up the measurement parameters */
        self.scope.write('MEASUREMENT:IMMED:TYPE FREQUENCY')
        self.scope.write(f'MEASUREMENT:IMMED:SOURCE {channel}')
        # /* Wait until the acquisition is complete before taking
        # the measurement */
        # While BUSY?
    @property
    def scopeAcquire_BUSY(self):
        return int(float(self.scope.query('BUSY?')))

    def Meas_Amp(self,channel='CH1',Meas='MEAS1'):
        # self.scope.write('MEASUREMENT:IMMED:TYPE AMPLITUDE')
        # self.scope.write(f'MEASUREMENT:IMMED:SOURCE {channel}')
        self.scope.write(f'MEASUrement:{Meas}:TYPE AMPLITUDE')
        return float(self.scope.query(f'MEASUrement:{Meas}:VALUE?'))
    
    def Meas_Mean(self,channel='CH1',Meas='MEAS1'):
        # self.scope.write('MEASUREMENT:IMMED:TYPE AMPLITUDE')
        # self.scope.write(f'MEASUREMENT:IMMED:SOURCE {channel}')
        self.scope.write(f'MEASUrement:{Meas}:TYPE MEAN')
        return float(self.scope.query(f'MEASUrement:{Meas}:VALUE?'))
    

    def openchoice_screenshot(self,file_path=''):
        app = Application(backend='win32').connect(title='OpenChoice Desktop')
        dlg = app.window(title='OpenChoice Desktop')
        dlg.set_focus()
        send_keys('^g') 
        time.sleep(2) 
        send_keys('^s')
        time.sleep(2) 
        send_keys(file_path)
        send_keys('{ENTER}') 
        print("Screenshot saved!")
        time.sleep(2)
        send_keys('{ENTER}')
        time.sleep(2)
        send_keys('{ESC}') 
        #dlg.close()

if __name__ == '__main__':
    scope = dpo_2014B('USB0::0x0699::0x0401::C020132::INSTR')
    scope.openchoice_screenshot('C:\\Users\\invlab\\Documents\\IVM6311ATE\\IVM6311ATE\\screenshot.png')
   
    # # print(scope.meas_Freq())
    # # print(scope.get_error())

    # # scope.set_trigger__mode(mode='AUTO')
    # # scope.scope.write('ACQUIRE:STATE OFF')
    # scope.set_trigger__mode(mode='NORM')
    # # time.sleep(1)
    # scope.init_scopePosEdge__Trigger(channel='CH3')
    # # time.sleep(1)
    # scope.single_Trigger__ON()
    # time.sleep(1)
    # # print('State',scope.acquireState)
    # while scope.acquireState == True :
    #    print('rotate')
    # # time.sleep(1)
    # scope.scope.write('ACQUIRE:STATE OFF')
    # # scope.single_Trigger__RUN()
    # image_data = scope.acquire_screenshot()
    # if image_data:
    #     # Salva l'immagine su disco o visualizzala in altro modo
    #     with open('screenshot.png', 'wb') as f:
    #         f.write(image_data)
    #     print("Immagine salvata come 'screenshot.png'.")
    # else:
    #     print("L'immagine non è stata acquisita correttamente."



