from SwitchMatrix.mcp2221 import MCP2221
from Instruments.Audio_precision import AP555
from Instruments.DigitalScope import dpo_2014B
from time import sleep, ctime, time
from PyMCP2221A import PyMCP2221A
import pyvisa as visa
import os
import math

scope = dpo_2014B("USB0::0x0699::0x0401::C020132::INSTR")
mcp=MCP2221()
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
AZ_offset_array = []


#################################################  deleted intrinsic offset
if abs(AZ_offset) > 0:
    while -0.00025< AZ_offset > 0.00025:
        DC_offset2 = DC_offset2 + 0.00025
        print("DC offset is:", DC_offset2)
        sleep(1)
        ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
        sleep(1)
        AZ_offset = ap.Read_meter(3,1)
        print("Comparator's offset is:", AZ_offset)
DC_offset2_correct1 = DC_offset2
print("DC_offset_correct:", DC_offset2_correct1)
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct1)

if AZ_offset < 0:
    while abs(AZ_offset) > 0.00025:
        DC_offset2 = DC_offset2 + 0.00025
        print("DC offset is:", DC_offset2)
        sleep(1)
        ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
        sleep(1)
        AZ_offset = ap.Read_meter(3,1)
        print("Comparator's offset is:", AZ_offset)
DC_offset2_correct1 = DC_offset2
print("DC_offset_correct:", DC_offset2_correct1)
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct1)

####Setup the device

mcp.mcpWrite(SlaveAddress=0x6C,data=[0xFE,0x01])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0x03,0x05])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0x04,0x72])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE0,0x0C])
mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE1,0x1F])

scope.set_trigger__mode(mode='NORM')
scope.set_HScale()
scope.set_Channel__VScale(scale=0.5)
DC_offset2_correct2 = DC_offset2_correct1
i = 1

while DC_offset2_correct2 < 1.805:
    ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct1)
    i = i+1
    DC_offset2_correct2 = DC_offset2_correct2 + 0.00025
    sleep(2)
    ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
    mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE4,0x01])
    scope.openchoice_screenshot(file_path=r'C:\Users\invlab\Documents\IVM6311ATE\IVM6311ATE\AZ_comp_DFT{i}.png')
    AZ_offset = ap.Read_meter(3,1)
    AZ_offset_array.append(AZ_offset)
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct1)
DC_offset2_correct2 = DC_offset2_correct1

while DC_offset2_correct2 > 1.795:
    ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct1)
    i = i+1
    DC_offset2_correct2 = DC_offset2_correct2 - 0.00025
    sleep(2)
    ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
    mcp.mcpWrite(SlaveAddress=0x6C,data=[0xE4,0x01])
    scope.openchoice_screenshot(file_path=r'C:\Users\invlab\Documents\IVM6311ATE\IVM6311ATE\AZ_comp_DFT{i}.png')
    AZ_offset = ap.Read_meter(3,1)
    AZ_offset_array.append(AZ_offset)
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2_correct1)











