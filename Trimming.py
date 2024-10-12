from SwitchMatrix.mcp2221 import MCP2221
# from SwitchMatrix.mcp2317 import MCP2317
from Instruments.Keysight_34461 import A34461
from Instruments.DigitalScope import dpo_2014B
import pandas as pd
from time import sleep

class Trim:

    def __init__(self,mcp):
        self.meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.mcp = mcp
        self.scope = dpo_2014B('USB0::0x0699::0x0456::C014545::INSTR')
        # self.mcp2317 = MCP2317(mcp=self.mcp)
        self.slave_address = 0x6c

    def sweep_trim_bit_voltage(self, reg_trim, lsb, msb):
        # Read the value of the register (assuming mcpRead returns a list with one byte)
        reg_val = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg_trim], Nobytes=1)[0]  # Take the first element of the list

        modified_register = []
        trim_values = []

        # Calculate the number of iterations
        n_iterations = (1 << (msb - lsb + 1))  # This is 2^(msb-lsb+1)

        # Create the mask for the bits between lsb and msb
        mask = ((1 << (msb - lsb + 1)) - 1) << lsb  # Create a mask that has bits 1 between lsb and msb

        # Keep the external bits (we save them to restore later)
        external_bits = reg_val & ~mask  # Preserve the external bits (outside the masked range)

        # Force the internal bits to 0 before starting
        reg_val_zeroed = reg_val & ~mask  # Zero the bits between lsb and msb

        # Write the register with the bits set to zero
        self.mcp.mcpWrite(SlaveAddress=0x6C, data=[reg_trim, reg_val_zeroed])

        # Loop to increment the bits between lsb and msb
        for increment in range(n_iterations):  # Loop from 0 to 2^(msb-lsb+1) - 1
            # Operation on the internal bits (increment)
            internal_bits = (increment << lsb) & mask  # Increment only the bits between lsb and msb
            
            # Combine the external bits with the modified internal bits
            new_register_val = external_bits | internal_bits
            modified_register.append(new_register_val)

            # Write the new register value
            self.mcp.mcpWrite(SlaveAddress=0x6C, data=[reg_trim, new_register_val])
            
            # Measure the trim value and add it to the list
            trim_value = self.meter.meas_V()
            trim_values.append(trim_value)

            print(f"Increment: {increment}, Internal bits: {bin(internal_bits)}, Register: {hex(new_register_val)}")
        
        print(trim_values)
        # Return the measured values and the modified registers
        return trim_values, modified_register
    
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
    
    def sweep_trim_bit_freq(self, reg_trim, lsb, msb):
        # Read the value of the register (assuming mcpRead returns a list with one byte)
        reg_val = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg_trim], Nobytes=1)[0]  # Take the first element of the list
        print(hex(reg_val))
        # self.scope.set_autoSet()
        self.scope.set_trigger__mode(mode='NORM')
        self.scope.set_HScale('2E-6')
        self.scope.set_Channel__VScale(scale=0.5)
        modified_register = []
        trim_values = []

        # Calculate the number of iterations
        n_iterations = (1 << (msb - lsb + 1))  # This is 2^(msb-lsb+1)

        # Create the mask for the bits between lsb and msb
        mask = ((1 << (msb - lsb + 1)) - 1) << lsb  # Create a mask that has bits 1 between lsb and msb

        # Keep the external bits (we save them to restore later)
        external_bits = reg_val & ~mask  # Preserve the external bits (outside the masked range)

        # Force the internal bits to 0 before starting
        reg_val_zeroed = reg_val & ~mask  # Zero the bits between lsb and msb

        # Write the register with the bits set to zero
        self.mcp.mcpWrite(SlaveAddress=0x6C, data=[reg_trim, reg_val_zeroed])

        # Loop to increment the bits between lsb and msb
        for increment in range(n_iterations):  # Loop from 0 to 2^(msb-lsb+1) - 1
            # Operation on the internal bits (increment)
            internal_bits = (increment << lsb) & mask  # Increment only the bits between lsb and msb
            
            # Combine the external bits with the modified internal bits
            new_register_val = external_bits | internal_bits
            modified_register.append(new_register_val)

            # Write the new register value
            self.mcp.mcpWrite(SlaveAddress=0x6C, data=[reg_trim, new_register_val])
            
            # Measure the trim value and add it to the list
            i=0
            freq = 0
            # input('>>>>>>>>')
            for i in range(0,20):
                freq= freq + self.scope.meas_Freq()
                sleep(0.01)
            trim_values.append(freq/(i+1))

            print(f"Increment: {increment}, Internal bits: {bin(internal_bits)}, Register: {hex(new_register_val)}, freq: {trim_values[-1]}")
        print(trim_values)
        # Return the measured values and the modified registers
        return trim_values, modified_register
    


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

