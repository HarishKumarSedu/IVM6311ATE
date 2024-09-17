
from typing import Union
import warnings
import time 
# from mcp2221 import MCP2221


class MCP2317:
    def __init__(self, mcp='') -> None:
        self.IODIRA = 0x00 # Bank GPIO congurations :  1 - InPut , 2 - Output ; default all Bank GPIOs are inputs 
        self.IODIRB = 0x01 
        self.GPIOA  = 0x12 # GPIO BANK output set 
        self.GPIOB  = 0x13 # GPIO BANK output set 
       
        self.mcp2221 = mcp
        
        self.AllOUTput = 0x00 # enable all the GPIO as output 
        self.AllINput = 0xFF  # configure all the gpios as inputs 
        self.ResetAllOUTput = 0x00 # open all the switches 
        self.SetAllOUTput = 0xFF   # close all the switches 
        
        self.configure()
        
    def configure(self,):
        # self.mcp.mcp.Reset() # reset the mcp 
        self.mcp2221.mcp2221.GPIO_Init() # initialize the mcp gpios 
        self.mcp2221.mcp2221.GPIO_0_OutputMode() # set the gpio as output 
        self.mcp2221.mcp2221.GPIO_1_OutputMode()
        self.mcp2221.mcp2221.GPIO_2_OutputMode()
        self.mcp2221.mcp2221.GPIO_3_OutputMode()
        self.mcp2221.mcp2221.GPIO_0_Output(1)
        self.mcp2221.mcp2221.GPIO_1_Output(1) # Enable the GPIO output 
        self.mcp2221.mcp2221.GPIO_2_Output(1)
        self.mcp2221.mcp2221.GPIO_3_Output(1)
        # self.mcp2221.mcpWrite(self.slaveAddress, [self.IODIRA, self.AllOUTput]) # configure all the bank A gpios are as outputs 
        # self.mcp2221.mcpWrite(self.slaveAddress, [self.IODIRB, self.AllOUTput]) # configure all the bank B gpios are as outputs 
    
    def reset(self):
        # self.mcp.mcpWrite(self.slaveAddress, [self.GPIOA, self.ResetAllOUTput]) # configure all the bank A gpios are as outputs 
        # self.mcp.mcpWrite(self.slaveAddress, [self.GPIOB, self.ResetAllOUTput]) # configure all the bank B gpios are as outputs 

        # Hard reset the GPIO expanders 
        self.mcp2221.mcp2221.GPIO_0_Output(0) # Disable the GPIO output 
        self.mcp2221.mcp2221.GPIO_0_Output(0) # Disable the GPIO output 
        self.mcp2221.mcp2221.GPIO_0_Output(0) # Disable the GPIO output 
        self.mcp2221.mcp2221.GPIO_0_Output(0) # Disable the GPIO output 
        
        # Reset the MCP
        # self.mcp.mcp.Reset()
        
    
    
    def Switch(self,device_addr=0x20, row=1, col =1, Enable = False):
            self.mcp2221.mcpWrite(device_addr, [self.IODIRA, self.AllOUTput]) # configure all the bank A gpios are as outputs 
            self.mcp2221.mcpWrite(device_addr, [self.IODIRB, self.AllOUTput]) # configure all the bank B gpios are as outputs 
        # if  (0 > row <= 8) and (0 > col <= 8):
            # odd Row 
            if row % 2 :
                RegBank_addr = self.GPIOA
            else:
                RegBank_addr = self.GPIOB
            self.mcp2221.mcpRead(device_addr, [RegBank_addr])
            time.sleep(0.2)
            if Enable:
                data = self.mcp2221.mcpRead(device_addr, [RegBank_addr])[0] # Read the register bank data
                data = data | (1 << col-1)
                self.mcp2221.mcpWrite(device_addr, [RegBank_addr,data])
                # print(hex(RegBank_addr),self.mcp2221.mcpRead(self.slaveAddress, [RegBank_addr]))
            else:
                data = self.mcp2221.mcpRead(device_addr, [RegBank_addr])[0] # Read the register bank data
                data = data & (255 - (1 << col-1))
                self.mcp2221.mcpWrite(device_addr, [RegBank_addr,data])
                # print(hex(RegBank_addr),self.mcp2221.mcpRead(self.slaveAddress, [RegBank_addr]))
        # else:
        #     warnings.warn(f'Signal Matrix Selection Outof  Context of the Matrix row :{row} ; col:{col}')
    def Switch_reset(self,device_addr=0x20):  
            self.mcp2221.mcpWrite(device_addr, [self.GPIOA, 0x00]) # configure all the bank A gpios are as outputs 
            self.mcp2221.mcpWrite(device_addr, [self.GPIOB,0x00]) # configure all the bank B gpios are as outputs 
                
if __name__=='__main__':
    mcp=MCP2221()
    mcp2317 = MCP2317(mcp=mcp)
    time.sleep(1)
    mcp2317.Switch(device_addr=0x20,row=1, col=4, Enable=False)
    mcp2317.Switch(device_addr=0x20,row=1, col=2, Enable=True)
    mcp2317.Switch(device_addr=0x21,row=3, col=3, Enable=True)
    # mcp2317.Switch(device_addr=0x20,row=1, col=4, Enable=False)
    # time.sleep(2)
    # mcp2317.Switch(row=4, col=1, Enable=False)
    # mcp2317.reset()