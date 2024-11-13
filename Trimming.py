# from SwitchMatrix.mcp2221 import MCP2221
# from SwitchMatrix.mcp2317 import MCP2317
from Instruments.Keysight_34461 import A34461
from Instruments.DigitalScope import dpo_2014B
import pandas as pd
from time import sleep

class Trim:

    def __init__(self,mcp,mcp2317):
        self.meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.mcp = mcp
        self.scope = dpo_2014B('USB0::0x0699::0x0456::C014545::INSTR')
        self.mcp2317 = mcp2317
        self.slave_address = 0x6c

    def sweep_trim_bit_voltage(self, reg_trim, lsb, msb):

        self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[0xB1, 0x70]) ####Set default vbg_curve
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
        # print(hex(reg_val))
        self.scope.set_HScale('100E-6')
        sleep(2)
        # self.scope.set_autoSet()
        self.scope.set_trigger__mode(mode='NORM')
        self.scope.set_HScale('4E-6')
        self.scope.set_Channel__VScale(channel=2,scale=1)
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
            sleep(1)
            # input('>>>>>>>>')
            # freq = self.scope.Meas_Mean(channel='CH2', Meas='MEAS1')
            # print(freq)
            for i in range(0,20):
                sleep(0.05)
                freq= freq + self.scope.meas_Freq(Meas='MEAS1')
            trim_values.append(freq/(i+1))

            print(f"Increment: {increment}, Internal bits: {bin(internal_bits)}, Register: {hex(new_register_val)}, freq: {trim_values[-1]}")
        print(trim_values)
        # Return the measured values and the modified registers
        return trim_values, modified_register

    def sweep_trim_bit_freq_two_registers(self, reg1, lsb1, msb1, reg2, lsb2, msb2):
        try:
            defval_reg1 = 0x7F
            defval_reg2 = 0xD0
            # print(reg1)
            # print(lsb1)
            # print(msb1)
            # print(reg2)
            # print(lsb2)
            # print(msb2)
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg1, defval_reg1])
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg2, defval_reg2])

            
            reg_val1 = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg1], Nobytes=1)[0]
            reg_val2 = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg2], Nobytes=1)[0]

            print(f"Registro 1 iniziale: {hex(reg_val1)}, Registro 2 iniziale: {hex(reg_val2)}")

            mask1 = ((1 << (msb1 - lsb1 + 1)) - 1) << lsb1
            mask2 = ((1 << (msb2 - lsb2 + 1)) - 1) << lsb2

            external_bits1 = reg_val1 & ~mask1
            external_bits2 = reg_val2 & ~mask2
            reg_val1_zeroed = reg_val1 & ~mask1
            reg_val2_zeroed = reg_val2 & ~mask2

            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg1, reg_val1_zeroed])
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg2, reg_val2_zeroed])

            print(self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg1], Nobytes=1)[0])
            print(self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg1], Nobytes=1)[0])
            
            for increment2 in [0xD0, 0xF0]:
                internal_bits2 = increment2 & mask2
                new_register_val2 = external_bits2 | internal_bits2
                self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg2, new_register_val2])

                
                if increment2 == 0xD0:
                    increment1 = 0x7F
                    increment_step = -1
                    end_value = 0x70
                else:
                    increment1 = 0x7F
                    increment_step = -1
                    end_value = 0x70

                while (increment_step == -1 and increment1 >= end_value) or (increment_step == 1 and increment1 <= end_value):
                    internal_bits1 = (increment1 << lsb1) & mask1
                    new_register_val1 = external_bits1 | internal_bits1
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg1, new_register_val1])

                    sleep(0.5)  
                    self.mcp2317.Switch(device_addr=0x24, row=2, col=1, Enable=True)
                    sleep(0.5)

                    try:
                        valore_multimetro = self.meter.meas_V()
                        
                        
                        print(f"Increment1: {hex(increment1)}, Increment2: {hex(increment2)}, Valore multimetro: {valore_multimetro}")

                       
                        if 0.45 <= valore_multimetro <= 0.95:
                            # print(valore_multimetro, new_register_val1, new_register_val2)
                            return valore_multimetro, new_register_val1, new_register_val2

                    except Exception as e:
                        print(f"Measurement error: {e}")
                        continue  

                    increment1 += increment_step

            print("Impossible find right value")
            return 0.0, defval_reg1, defval_reg2  

        except Exception as e:
            print(f"Error during the execution: {e}")
            return 0.0, 0, 0  # Valori di default in caso di errore


# if __name__ == '__main__':
#     mcp = MCP2221()
#     trim = Trim(mcp=mcp)
    # reg1 = 0xB1
    # reg2 = 0xB2
    # lsb1 = 0
    # msb1 = 3
    # lsb2 = 5
    # msb2 = 5
    # target = 1.8
    # trim_values, modified_registers = trim.sweep_trim_bit_freq_two_registers(reg1,lsb1,msb1,reg2,lsb2,msb2)
    # closest_value = trim.find_closest_value(trim_values, target)
    # # print(closest_value)
    # trim.find_best_code(trim_values,modified_registers, target)
