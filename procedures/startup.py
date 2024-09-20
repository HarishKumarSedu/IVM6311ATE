
import time 

class Startup:
    
    def __init__(self,mcp):
        self.mcp = mcp
        startupInstructions = [
            [0xFE,0x00],
            [0x00,0x0f], 
            [0x00,0x01], 
            [0xFE,0x01],
            [0x2F,0xAA],
            [0x2F,0xBB],
            [0x0F,0x88],
            [0x10,0x08],
            # [0xEE,0x00],
            # [0xFE,0x00],
        ]
        for instruction in startupInstructions:
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=instruction)
            time.sleep(0.3)
        print('Startup Procedure applied ....!')
        print(self.mcp.mcpRead(SlaveAddress=0x6c, data=[0x2F]))
        
class StartupAzComp:
   
    def __init__(self,mcp):
        self.mcp = mcp
        startupInstructions = [
            [0xFE,0x00],
            [0x00,0x0F],
            [0xFE,0x01],
            [0x2F,0xAA],
            [0x2F,0xBB],
            [0x17,0x02],
            [0x18,0x02],
            [0x0F,0xC8],
            [0x10,0x08],
 
        ]
        for instruction in startupInstructions:
            self.mcp.mcpWrite(SlaveAddress=0x6c, data=instruction)
            time.sleep(0.3)
        print('StartupAzComp Procedure applied ....!')
        print(self.mcp.mcpRead(SlaveAddress=0x6c, data=[0x2F]))
        
        