from SwitchMatrix import mcp2221,mcp2317
from Instruments.Audio_precision import AP555
from Instruments.DigitalScope import dpo_2014B
from time import sleep, ctime, time
from PyMCP2221A import PyMCP2221A
import pyvisa as visa
import os
import math

scope = dpo_2014B("USB0::0x0699::0x0401::C020132::INSTR")
mcp=mcp2221()
AP_file = "Char_6311_AZcomp.approjx"

path = os.getcwd() + "\\PA_template\\" + AP_file
print(path)
ap = AP555(mode = 'BenchMode', fullpath=path)
AZ_offset = ap.Read_meter(3,1)
print("Comparator's offset is:", AZ_offset)
print(type(AZ_offset))
DC_offset2 = 1.8
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= 1.8)
ap.Enable_Generator(True)

if abs(AZ_offset) > 0:
    print("AAAAAAAAAAAAAAAAAAAAAAAAA",AZ_offset)
    while -0.00025< AZ_offset > 0.00025:
        DC_offset2 = DC_offset2 + 0.00025
        print("DC offset is:", DC_offset2)
        sleep(2)
        ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
        sleep(2)
        AZ_offset = ap.Read_meter(3,1)
        print("Comparator's offset is ***********************************:", AZ_offset)
DC_offset2_correct = DC_offset2
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct)

if AZ_offset < 0:
    print("AAAAAAAAAAAAAAAAAAAAAAAAA", abs(AZ_offset))
    while abs(AZ_offset) > 0.00025:
        DC_offset2 = DC_offset2 - 0.00025
        print("DC offset is:", DC_offset2)
        sleep(2)
        ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
        sleep(2)
        AZ_offset = ap.Read_meter(3,1)
        print("Comparator's offset is ##############################:", AZ_offset)
DC_offset2_correct = DC_offset2
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct)

####Setup the device

mcp.mcpWrite(SlaveAddress=0x6C,data=[0xFE,0x01])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0x03,0x05])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0x04,0x72])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE0,0x0C])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE1,0x1F])

scope.set_trigger__mode(mode='NORM')
scope.set_HScale()
scope.set_Channel__VScale(scale=0.5)

while DC_offset2 < 1.810:
    DC_offset2 = DC_offset2 = DC_offset2 + 0.00025
    sleep(2)
    ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
    mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE4,0x01])
    scope.acquireImage()
    AZ_offset = ap.Read_meter(3,1)









