import pyvisa
from Instruments.DigitalScope import dpo_2014B

scope = dpo_2014B("USB0::0x0699::0x0401::C020132::INSTR")

scope.write('SAVe:IMAG:FILE PNG')
scope.write('HARDCOPY START')
raw_data = scope.read_raw()

fid = open('my_img.png', 'wb')
fid.write(raw_data)
fid.close()
print('done')
