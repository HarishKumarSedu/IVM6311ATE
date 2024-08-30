
import time 
from IvmDriver.logger import log 

class EnableAnalogTestPoint:
    
    def __init__(self,mcp):
        self.mcp = mcp
        EnableAnalogTestPointInstructions = [ 
            [0xFE,0x01],
            # [0x0F,0x88],
            # [0x10,0x08],
            [0x19,0x81],
            [0x1A,0x00],
        ]
        for instruction in EnableAnalogTestPointInstructions:
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=instruction)
            time.sleep(0.3)
        log.info('Enable Analog TestPoint Procedure applied ....!')