from SwitchMatrix import mcp2221,mcp2317
from Instruments.Audio_precision import AP555
from time import sleep, ctime, time
# from usr_lib import xml_lib
# from usr_lib import inv_lib
# from usr_lib.inv_lib import PathLib, Conversion, SaveLib
import pyvisa as visa
import os
import math

AP_file = "Char_6311_AZcomp.approjx"
# libPath = PathLib()
# current_path = libPath.current_path()

# def offset_delited(offset, DC_offset,thrs, step):

#     while abs(AZ_offset) > thrs:
#         if offset > 0:
#             DC_offset += step
#             offset -= step
#         if offset < 0:
#             DC_offset -= step
#             offset += step
#     return DC_offset, offset

path = os.getcwd() + "\\PA_template\\" + AP_file
print(path)
ap = AP555(mode = 'BenchMode', fullpath=path)
AZ_offset = ap.Read_meter(3,1)
print("Comparator's offset is:", AZ_offset)
DC_offset2 = 1.8
ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= 1.8)
ap.Enable_Generator(True)

if abs(AZ_offset) > 0:
    while -0.00025< AZ_offset > 0.00025:
        DC_offset2 = DC_offset2 + 0.00025
        sleep(2)
        ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
        sleep(2)
        AZ_offset = ap.Read_meter(3,1)
        print("Comparator's offset is ***********************************:", AZ_offset)

elif abs(AZ_offset) < 0:
        while -0.00025< AZ_offset > 0.00025:
            DC_offset2 = DC_offset2 - 0.00025
            sleep(2)
            ap.Configure_Generator(False,Level1=-60, Level2=-60  , Freq=1000, Waveform = 'Sine, Var Phase', DC_offset1= 1.8, DC_offset2= DC_offset2)
            sleep(2)
            AZ_offset = ap.Read_meter(3,1)
            print("Comparator's offset is ##############################:", AZ_offset)

# while 





