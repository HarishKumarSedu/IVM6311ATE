from SwitchMatrix.mcp2221 import MCP2221
from SwitchMatrix.mcp2317 import MCP2317
from Instruments.Keysight_34461 import A34461
from Instruments.DigitalScope import dpo_2014B
from Instruments.Keysight_E3648 import E3648
from Instruments.KeySight_N670x import N670x
import pandas as pd
from time import sleep


class Trimcopy:

    def __init__(self,mcp):
        self.meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        mcp = MCP2221()
        self.mcp = mcp
        self.pa = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
        self.supplies = E3648('GPIB0::7::INSTR')
        self.supplies_8 = E3648('GPIB0::8::INSTR')
        self.scope = dpo_2014B('USB0::0x0699::0x0456::C014545::INSTR')
        self.mcp2317 = MCP2317(mcp=self.mcp)
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
        self.scope.set_HScale('100E-6')
        sleep(1)
        # self.scope.set_autoSet()
        self.scope.set_trigger__mode(mode='NORM')
        self.scope.set_HScale('10E-6')
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
            sleep(1)
            # input('>>>>>>>>')
            # freq = self.scope.Meas_Mean(channel='CH2', Meas='MEAS1')
            # print(freq)
            for i in range(0,20):
                sleep(0.05)
                freq= freq + self.scope.meas_Freq(Meas='MEAS2')
            trim_values.append(freq/(i+1))

            print(f"Increment: {increment}, Internal bits: {bin(internal_bits)}, Register: {hex(new_register_val)}, freq: {trim_values[-1]}")
        print(trim_values)
        # Return the measured values and the modified registers
        return trim_values, modified_register

    def sweep_trim_bit_freq_two_registers(self, reg1, lsb1, msb1, reg2, lsb2, msb2):
        try:

            defval_reg1 = 0x7F
            defval_reg2 = 0xD0
            trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data = [0xB1, defval_reg1])
            trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data = [0xB2, defval_reg2])
            # Leggi i valori iniziali dei registri
            reg_val1 = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg1], Nobytes=1)[0]
            reg_val2 = self.mcp.mcpRead(SlaveAddress=self.slave_address, data=[reg2], Nobytes=1)[0]
            
            print(f"Registro 1 iniziale: {hex(reg_val1)}, Registro 2 iniziale: {hex(reg_val2)}")


            self.scope.single__Trigger__Mode()
            self.scope.set_HScale('100E-6')
            sleep(1)
            self.scope.set_trigger__mode(mode='NORM')
            self.scope.set_HScale('10E-6')
            self.scope.set_Channel__VScale(scale=0.5)

            # Calcola le iterazioni per reg1
            n_iterations1 = (1 << (msb1 - lsb1 + 1))

            # Crea le maschere per entrambi i registri
            mask1 = ((1 << (msb1 - lsb1 + 1)) - 1) << lsb1
            mask2 = ((1 << (msb2 - lsb2 + 1)) - 1) << lsb2
            
            # Conserva i bit esterni per entrambi i registri
            external_bits1 = reg_val1 & ~mask1
            external_bits2 = reg_val2 & ~mask2
            
            # Zero i bit interni prima di iniziare
            reg_val1_zeroed = reg_val1 & ~mask1
            reg_val2_zeroed = reg_val2 & ~mask2

            # Scrivi i registri con i bit azzerati
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg1, reg_val1_zeroed])
            self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg2, reg_val2_zeroed])

            trim_values = []
            modified_registers = []
            Triggered = False

            # Imposta i valori fissi per increment2
            increment2_values = [0xD0, 0xF0]

            for increment2 in increment2_values:
                # Imposta i bit interni per reg2
                internal_bits2 = increment2 & mask2
                new_register_val2 = external_bits2 | internal_bits2

                if increment2 == 0xD0:
                    # Primo ciclo con increment2 = 0xD0, decremento di increment1 da 0x7F a 0x70
                    increment1_range = range(0x7F, 0x6F, -1)
                else:
                    # Secondo ciclo con increment2 = 0xF0, incremento di increment1 da 0x70 a 0x7F
                    increment1_range = range(0x70, 0x80)

                for increment1 in increment1_range:
                    # Modifica i bit interni per reg1
                    internal_bits1 = (increment1 << lsb1) & mask1
                    new_register_val1 = external_bits1 | internal_bits1

                    modified_registers.append((new_register_val1, new_register_val2))

                    # Scrivi i nuovi valori dei registri
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg1, new_register_val1])
                    self.mcp.mcpWrite(SlaveAddress=self.slave_address, data=[reg2, new_register_val2])

                    sleep(1)  # Tempo di stabilizzazione
                    # Stampa i valori attuali dei registri
                    print(f"Registro 1: {hex(new_register_val1)}, Registro 2: {hex(new_register_val2)}")

                    

            return new_register_val1, new_register_val1

        except Exception as e:
            print(f"Errore durante l'esecuzione: {e}")



if __name__ == '__main__':
    mcp = MCP2221()
    mcp.reset()
    sleep(0.5)
    trim = Trimcopy(mcp=mcp)
    for i in range (0x20,0x27):
        sleep(0.5)
        trim.mcp2317.Switch_reset(device_addr=i)
    trim.supplies.outp_OFF(channel=1)
    trim.supplies.outp_OFF(channel=2)
    trim.pa.outp_OFF(channel=4)
    trim.supplies_8.outp_OFF(channel=2)
    trim.supplies_8.outp_OFF(channel=1)

    trim.supplies_8.setVoltage(channel=2, voltage = 5)
    trim.supplies_8.setCurrent(channel=2, current=0.2)
    trim.supplies_8.outp_ON(channel=2)
    trim.supplies_8.setVoltage(channel=1, voltage = 3.6)
    trim.supplies_8.setCurrent(channel=1, current=0.2)
    trim.supplies_8.outp_ON(channel=1)

    trim.supplies.setVoltage(channel=1, voltage=3.6)
    trim.supplies.setCurrent(channel=1, current=0.2)
    trim.supplies.outp_ON(channel=1)
    trim.supplies.setVoltage(channel=2, voltage=1.8)
    trim.supplies.setCurrent(channel=2, current=0.2)
    trim.supplies.outp_ON(channel=2)
    sleep(1)
    trim.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= False)
    sleep(1)
    trim.mcp2317.Switch(device_addr=0x23, row = 7, col = 5, Enable= True)
    sleep(0.5)

    trim.pa.setVoltage(channel=4, voltage=1.8)
    trim.pa.outp_ON(channel=4)
    sleep(1)
    trim.mcp2317.Switch(device_addr=0x20,row = 1, col = 4, Enable=True)
    sleep(2)
    #######################STARTUP
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x00, 0x0F])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x01])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x2F, 0xAA])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x2F, 0xBB])
    # trim.mcp2317.Switch(device_addr=0x23, row=8, col=6, Enable=True)
    # sleep(0.5)
    # trim.pa.emulMode_2Q(channel=3)
    # trim.pa.setVoltage_Priority(channel=3)
    # trim.pa.setVoltage(channel=3,voltage=3.6)
    # sleep(0.2)
    # trim.pa.outp_ON(channel=3)
    #############################RUN_TEST_BOOST_ENABLE
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB0, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB1, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB3, 0x21])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x01])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x18, 0x40])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB1, 0x40])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB2, 0xD5])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB4, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x01])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x17, 0x40])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x16, 0x40])
    #############################RUN_ENABLE_ANA_TEST_POINT
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x01])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x0F, 0x88])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x10, 0x08])
    sleep(1)
    trim.mcp2317.Switch(device_addr=0x20,row = 1, col = 4, Enable=False)
    sleep(0.5)
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x19, 0x80])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x1A, 0x00])
    sleep(0.5)
    ##############################RUN_OCP
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB0, 0x02])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB2, 0xD7])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xC0, 0x03])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x01])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x1A, 0x10])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x03, 0x07])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x04, 0x18])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x00])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB2, 0xD7])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xFE, 0x01])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x0F, 0x80])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0xB0, 0x0E])
    sleep(0.5)
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x15, 0x04])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data=[0x19, 0x82])
    defval_reg1 = 0x7F
    defval_reg2 = 0xD0
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data = [0xB1, defval_reg1])
    trim.mcp.mcpWrite(SlaveAddress=trim.slave_address, data = [0xB2, defval_reg2])
    sleep(1)
    trim.mcp2317.Switch(device_addr=0x23, row=8, col=7, Enable=True)
    sleep(0.5)
    trim.pa.emulMode_2Q(channel=1)
    trim.pa.setCurrent(channel=1,current=0.4)
    trim.pa.outp_ON(channel=1)

    reg1 = 0xB1
    reg2 = 0xB2
    lsb1 = 0
    msb1 = 3
    lsb2 = 5
    msb2 = 5
    target = 1.8
    trim_values, modified_registers = trim.sweep_trim_bit_freq_two_registers(reg1,lsb1,msb1,reg2,lsb2,msb2)
    # closest_value = trim.find_closest_value(trim_values, target)
    # print(closest_value)
    # trim.find_best_code(trim_values,modified_registers, target)
    for i in range (0x20,0x27):
        sleep(0.5)
        trim.mcp2317.Switch_reset(device_addr=i)
    trim.pa.outp_OFF(channel=1)
    trim.pa.outp_OFF(channel=4)
    trim.supplies_8.outp_OFF(channel=1)
    trim.supplies_8.outp_OFF(channel=2)
    trim.supplies.outp_OFF(channel=1)
    trim.supplies.outp_OFF(channel=2)


