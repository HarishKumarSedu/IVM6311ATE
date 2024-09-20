# from IvmDriver.mcp2221 import MCP2221
from mcp2221 import MCP2221
from procedures.startup import Startup
from procedures.Enable_Ana_Testpoint import EnableAnalogTestPoint
from IvmDriver.logger import log
from KeySight_N670x import N670x
from Instruments.multimeter import mul_34401A
from Instruments.Keysight_E362x import E362X
from time import sleep 
from common import Instruments
import pandas as pd 
from tqdm import tqdm
import os 
from pathlib import Path

class BandgapTrim:
    
    def __init__(self,mcp) -> None:
        # self.supply = N670x(Instruments().ID.PowerSupply)
        self.multimeter = mul_34401A(Instruments().ID.Multimeter1)
        # sleep(2)
        log.info('........... BandGap ........')
        self.mcp = mcp 
        # input('>')
        EnableAnalogTestPoint(mcp=self.mcp)
        self.trimregister = 0xB0
        BandGapInstructions = [ 
            [0xFE,0x01],
            # [0x19,0x81],
            [0x1A,0x01],
            [0xB1,0xff],
            [self.trimregister,0x0E],
        ]
        for instruction in BandGapInstructions:
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=instruction)
            sleep(0.3)
        # input('>')
        if self.mcp.mcpRead(SlaveAddress=0x6c, data=[0x1A]):
            log.info('BandGap Brought in SWDN pin ....!')
            log.warning(self.mcp.mcpRead(SlaveAddress=0x6c, data=[self.trimregister]))
            self.measure_BandGap()
        else:
            log.error('BandGap Brought Signal error re-run procedure ....!')
        
    
    def measure_BandGap(self):
        setCode = []
        BandGapValue = []
        erro_percentage = []
        for i in tqdm(range(8)):
            value = self.mcp.mcpRead(SlaveAddress=0x6c, data=[self.trimregister])[0]
            # log.warning(hex(value))
            value = ((value & 0x0f)| (i<<4))
            log.warning(hex(value))
            sleep(0.1)
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=[self.trimregister,value])
            sleep(0.3)
            setCode.append(i)
            BandGapValue.append(self.multimeter.meas_V(count=1))
            # BandGapValue.append(self.multimeter.read_value(cnt=1))
        for i in tqdm(range(15,7,-1)):
            value = self.mcp.mcpRead(SlaveAddress=0x6c, data=[self.trimregister])[0]
            log.warning(hex(value))
            value = ((value & 0x0f)| (i<<4))
            log.warning(hex(value))
            sleep(0.1)
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=[self.trimregister,value])
            sleep(0.3)
            setCode.append(i)
            BandGapValue.append(self.multimeter.meas_V(count=1))
            # BandGapValue.append(self.multimeter.read_value(cnt=1))
            erro_percentage.append((abs(BandGapValue[-1]) - 1.799)/BandGapValue[-1] *100)

        data = pd.DataFrame({'SetCode':setCode,'BandGapValue':BandGapValue})
        data['error_percentage']  = data['BandGapValue'].apply(lambda x : abs(x-1.8))
        # print(data['BandGapValue'], data['SetCode'])
        trimmingCode_index = data[['error_percentage']].idxmin()
        optimal_value = data.loc[trimmingCode_index,"BandGapValue"].to_list()[-1]
        data.to_csv('bandgap.csv')
        if  1.793 < optimal_value <1.804:
            log.info(f'Optimal value : {optimal_value}V')
            self.trimcode = data.loc[trimmingCode_index,"SetCode"].to_list()[-1]
            log.info(f'Trim Code : {self.trimcode}')
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=[self.trimregister,self.trimcode << 4 | 0xE])
            self.trim_codeValue()
        else:
            log.error(f'Trimming failed measured value : {optimal_value} ')
    def trim_codeValue(self):
        
        # log.warning(hex(self.trimcode << 4 | 0xE))
        return [self.trimregister,self.mcp.mcpRead(SlaveAddress=0x6c, data=[self.trimregister])[-1]]
    
    def burn_value(self, trimcode):
        # self.supply.setVoltage(channel=2,voltage=8)
        # self.supply.setVoltage(channel=4,voltage=14)
        # self.supply.outp_ON(channel=2)
        # self.supply.outp_ON(channel=4)
        sleep(4)
        BandgapBurn_Instruction = [
        [0xFE,0x0],
        [0xB0,0xFE],
        [0xFE,0x1],
        [self.trimregister,0xFE],
        [self.trimregister,(trimcode << 4 | 0xE)],
        [0xAF,0x80],
        [0xAE,0x02],
        [0xAE,0x00],
        ]
        for instruction in BandgapBurn_Instruction:
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=instruction)
            sleep(1)
        BandgapValue =self.mcp.mcpRead(SlaveAddress=0x6c,data=[self.trimregister], Nobytes=1)[-1]
        if BandgapValue == (trimcode << 4 | 0xE):
            log.info(f'Band Trim Value {hex(BandgapValue)} burned Successfully ...!')
        else:
            log.critical(f'Bandgap Trim vlaue not able to burn ...!')
        sleep(1)
        self.mcp.GPIO0(True)
        sleep(3)
        # self.supply.setVoltage(channel=2,voltage=0)
        # self.supply.setVoltage(channel=4,voltage=0)

if __name__ == '__main__':
    BandgapTrim()