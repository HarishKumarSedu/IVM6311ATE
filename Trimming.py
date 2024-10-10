from SwitchMatrix.mcp2221 import MCP2221
# from SwitchMatrix.mcp2317 import MCP2317
from Instruments.Keysight_34461 import A34461
import pandas as pd
from time import sleep

class Trim:

    def __init__(self,mcp):
        self.meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.mcp = mcp
        # self.mcp2317 = MCP2317(mcp=self.mcp)
        self.slave_address = 0x6c

    def sweep_trim_bit(self, reg_trim, lsb, msb):
        # Leggi il valore del registro (assumendo che mcpRead restituisca una lista con un byte)
        reg_val = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg_trim], Nobytes=1)[0]  # Prendi il primo elemento della lista
        # Define lsb and msb
        lsb = 4  # Least significant bit
        msb = 7  # Most significant bit
        modified_register=[]
        # Calculate the number of iterations
        n_iterations = msb - lsb + 1
        # Create the mask for the range between lsb and msb
        mask = 0
        trim_values = []

        for i in range(lsb, msb + 1):
            mask |= (1 << i)  # Set the bits between lsb and msb to 1

        # Keep the bits outside the range (we save them to restore them later)
        external_bits = reg_val & ~mask  # 'reg_val' is now an integer

        # Loop to increment the internal bits
        for increment in range(1 << n_iterations):  # Loop from 0 to 2^(msb-lsb+1) - 1
            # Operation on the internal bits (increment)
            internal_bits = (increment << lsb) & mask  # Apply the increment and limit it to the mask
            # print(bin(internal_bits))
            # Combine the external bits with the modified internal bits
            modified_register.append( external_bits | internal_bits)
            # Print the results for each iteration
            # print(f"Iteration {increment}: Modified register = {hex(modified_register[-1])}")
            self.mcp.mcpWrite(SlaveAddress=0x6C, data=[0xB0, modified_register[-1]])
            trim_value = self.meter.meas_V()
            trim_values.append(trim_value)

        print(trim_values)
        return trim_values,modified_register
    
    def find_closest_value(self,trim_values, target):
        # Use the min function to find the closest element
        closest_value = min(trim_values, key=lambda x: abs(x - target))
        return closest_value

    def find_best_code(self, trim_values, modified_registers, target):
        # Find the index of the closest trim value
        values = {abs(trim_value - target):i for trim_value,i in zip(trim_values,modified_registers)}
        minimum = min(values.keys())
        # index = min(range(len(trim_values)), key=lambda i: abs(trim_values[i] - target))
        # print(len(trim_values),len(modified_registers))
        best_code = values.get(minimum)
        # print(minimum)
        # print(hex(best_code))
        return  best_code # Return both the closest trim value and its corresponding modified register

if __name__ == '__main__':
    mcp = MCP2221()
    trim = Trim(mcp=mcp)
    trim.mcp2317.Switch(device_addr=0x20,row=1, col=4, Enable=True)
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[00,0x0F])
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0xFE,0x01])
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0x2F,0xAA])
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0x2F,0xBB])
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0x0F,0x88])
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0x10,0x08])
    trim.mcp2317.Switch(device_addr=0x20,row=1, col=4, Enable=False)
    sleep(1)
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0x19,0x81])
    sleep(1)
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0x1A,0x01])
    sleep(1)
    trim.mcp.mcpWrite(SlaveAddress=0x6C,data=[0xB0,0x0E])
    reg_trim = 0xb0
    lsb = 7
    msb = 4
    target = 1.8
    trim_values, modified_registers = trim.sweep_trim_bit(reg_trim,lsb,msb)
    closest_value = trim.find_closest_value(trim_values, target)
    # print(closest_value)
    trim.find_best_code(trim_values,modified_registers, target)

