# from IvmDriver.mcp2221 import MCP2221
from SwitchMatrix.mcp2221 import MCP2221
from SwitchMatrix.mcp2317 import MCP2317
from procedures.startup import Startup
from procedures.Enable_Ana_Testpoint import EnableAnalogTestPoint
from Instruments.Keysight_34461 import A34461
from TempChamber import su_241
# power supply id 
# USB0::0x0957::0x0F07::MY50000622::INSTR
from time import sleep 
import pandas as pd 
from tqdm import tqdm
import os 
from pathlib import Path
from Instruments.Keysight_E3648 import E3648
from Instruments.Keysight_34461 import A34461

class BandGapCurve:
    
    def __init__(self) -> None:
        self.supply = E3648(port='GPIB0::7::INSTR')
        self.chamber = su_241('GPIB0::1::INSTR')
        self.multimeter = A34461('USB0::0x2A8D::0x1401::MY57229870::INSTR')
        # reset power supply Vbat, VDDIO, and Realy VCC
        sleep(2)
        self.mcp = MCP2221()
        self.matrix = MCP2317(mcp=self.mcp)
        self.matrix.Switch(device_addr=0x20,row=2, col=2, Enable=True)
        sleep(1)
        Startup(mcp=self.mcp)
        self.matrix.Switch(device_addr=0x20,row=2, col=2, Enable=False)
        sleep(0.5)
        self.matrix.Switch(device_addr=0x21,row=1, col=1, Enable=True)
        print('Remove the SDWN reset : > ')
        EnableAnalogTestPoint(mcp=self.mcp)
        bandgap_Instructions = [ 
            [0xFE,0x01],
            [0x19,0x81],
            [0x1A,0x01],
            [0xB0,0x0E],
        ]
        for instruction in bandgap_Instructions:
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=instruction)
            sleep(0.3)
        print(f' Band gap voltage {self.multimeter.meas_V(count=1)}')
        input('>')
        # let the Analog Voltage settle down for while 
        # sleep(0.5)
        if self.mcp.mcpRead(SlaveAddress=0x6c, data=[0x1A]):
            print('BandGap Brought in SWDN pin ....!')
            print(self.mcp.mcpRead(SlaveAddress=0x6c, data=[0xB0]))
            self.measure_BandGap()
        else:
            print('BandGap Brought Signal error re-run procedure ....!')
        
    
    def measure_BandGap(self):
        try:
            for temp in tqdm([20,40,60,80]):
                setCode = []
                BandGapValue = []
                self.chamber.set_temp(temp=temp)
                while (temperature:=self.chamber.read_temp()) != temp:
                    print(f'Chamber Temperature {temperature}')
                    sleep(200)

                for i in tqdm(range(0,16,1)):
                    value = self.mcp.mcpRead(SlaveAddress=0x6c, data=[0xB1])[0]
                    print(hex(value))
                    value = ((value & 0x0f)| (i<<4))
                    print(hex(value))
                    self.mcp.mcpWrite(SlaveAddress=0x6c, data=[0xB1,value])
                    sleep(0.3)
                    setCode.append(i)
                    BandGapValue.append(self.bandgap_values())
                #Reset the Chip and Vddio powersupply
                if not os.path.exists(Path('measurements/BandGapCurve2/Device2')):
                    os.makedirs(Path('measurements/BandGapCurve2/Device2'))
                data = pd.DataFrame({'CurveSetCode':setCode,'BandGapValue':BandGapValue})
                data.to_csv(f'measurements/BandGapCurve2/Device2/BandgapCurve_{temp}C.csv')
        except KeyboardInterrupt:
            pass


    def bandgap_values(self):
        BandGapValue={}
        for i in tqdm(range(8)):
            value = self.mcp.mcpRead(SlaveAddress=0x6c, data=[0xB0])[0]
            # print(hex(value))
            value = ((value & 0x0f)| (i<<4))
            print(hex(value))
            sleep(0.1)
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=[0xB0,value])
            sleep(0.3)
            BandGapValue.update({
                i:self.multimeter.meas_V(count=1)
            })
        for i in tqdm(range(15,7,-1)):
            value = self.mcp.mcpRead(SlaveAddress=0x6c, data=[0xB0])[0]
            value = ((value & 0x0f)| (i<<4))
            sleep(0.1)
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=[0xB0,value])
            sleep(0.3)
            BandGapValue.update({
                i:self.multimeter.meas_V(count=1)
            })
        return BandGapValue

BandGapCurve()