from PyMCP2221A import PyMCP2221A
from time import sleep

class MCP2221:

    def __init__(self) :
        # self.mcp = PyMCP2221A.PyMCP2221A()
        # self.mcp.Reset()
        self.mcp2221 = PyMCP2221A.PyMCP2221A()
        self.mcp2221.I2C_Init()
        self.mcp2221.GPIO_Init() # initialize the mcp gpios 
    
    def ConfigGPIO0(self,outp=True):
        if outp:
            self.mcp2221.GPIO_0_OutputMode() # set the gpio as output 
        else:
            self.mcp2221.GPIO_0_InputMode() # set the gpio as output 
    def ConfigGPIO1(self,outp=True):
        if outp:
            self.mcp2221.GPIO_1_OutputMode() # set the gpio as output 
        else:
            self.mcp2221.GPIO_1_InputMode() # set the gpio as output 
    def ConfigGPIO2(self,outp=True):
        if outp:
            self.mcp2221.GPIO_2_OutputMode() # set the gpio as output 
        else:
            self.mcp2221.GPIO_2_InputMode() # set the gpio as output 
    def ConfigGPIO3(self,outp=True):
        if outp:
            self.mcp2221.GPIO_3_OutputMode() # set the gpio as output 
        else:
            self.mcp2221.GPIO_3_InputMode() # set the gpio as output 
    def GPIO0(self,outp=True):
        if outp:
            self.mcp2221.GPIO_0_Output(1) # set the gpio as output 
        else:
            self.mcp2221.GPIO_0_Output(0) # set the gpio as output 
    def GPIO1(self,outp=True):
        if outp:
            self.mcp2221.GPIO_1_Output(1) # set the gpio as output 
        else:
            self.mcp2221.GPIO_1_Output(0) # set the gpio as output 
    def GPIO2(self,outp=True):
        if outp:
            self.mcp2221.GPIO_2_Output(1) # set the gpio as output 
        else:
            self.mcp2221.GPIO_2_Output(0) # set the gpio as output 
    def GPIO3(self,outp=True):
        if outp:
            self.mcp2221.GPIO_3_Output(1) # set the gpio as output 
        else:
            self.mcp2221.GPIO_3_Output(0) # set the gpio as output 
    def reset(self):
        self.mcp2221.Reset()
    def mcpWrite(self,SlaveAddress,data:list):
        # slaveAdddress = data.pop(0)
        # senddata = data
        # senddata = []
        # for i in range(0,len(data)):
        #     senddata.append(data[i])
        # print(senddata)
        self.mcp2221.I2C_Write(SlaveAddress,data)


    def mcpRead(self,SlaveAddress,data:list,Nobytes=1):
        # slaveAddress = data[0]
        self.mcpWrite(SlaveAddress=SlaveAddress,data=data)
        data = self.mcp2221.I2C_Read(SlaveAddress, Nobytes)
        return data

if __name__ == '__main__':

    mcp=MCP2221()
    mcp.mcpWrite(SlaveAddress=0x6C,data=[00,0x0F])
    print(mcp.mcpRead(SlaveAddress=0x6C,data=[00],Nobytes=1))