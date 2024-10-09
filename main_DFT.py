# main.py
import traceback
from AZ_comp_class import AZ_comp
from Instruments.Keysight_E3648 import E3648
from Instruments.KeySight_N670x import N670x
import pandas as pd
from time import sleep
from SwitchMatrix.mcp2317 import MCP2317
from SwitchMatrix.mcp2221 import MCP2221
from pathlib import Path

def main():
    try:
        az_comp = AZ_comp()
        mcp = MCP2221()
        mcp_matrix = MCP2317(mcp=mcp)
        pa = N670x('USB0::0x0957::0x0F07::MY50002157::INSTR')
        supplies = E3648('GPIB0::7::INSTR')
        output_control = E3648.OutputControl(port='GPIB0::7::INSTR')
        output_control.output_on(channel1=1, channel2=2 , voltage1=4.0, voltage2=1.8, current1=0.2, current2=0.2)
        pa.setVoltage(channel=4,voltage=1.8)
        pa.outp_ON(channel=4)
        AZ_COMP_data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='AZ_COMP')
        tests = az_comp.read_yaml(path_to_yaml=Path('Tests.yaml'))
        print(tests)
        print('************** AZ_COMP DFT ************** ')
        
        for test in tests.AZ_COMP:
            print(f'............ {test}')
            az_comp.AZcomp_DFT(AZ_COMP_data, test)
    
    except  TypeError as e:
        print(f'Entered in Exception loop :> {e}')
        traceback.print_exc()
        pass
    except  KeyboardInterrupt:
        for i in range (0x20,0x28):
            mcp_matrix.Switch_reset(device_addr=i)
            supplies.outp_OFF(channel=1)
            sleep(0.5)
            supplies.outp_OFF(channel=2)
    except  Exception as e:
        print(f'Entered in Exception loop :> {e}')
        traceback.print_exc()
        for i in range (0x20,0x28):
            mcp_matrix.Switch_reset(device_addr=i)
            supplies.outp_OFF(channel=1)
            sleep(0.5)
            supplies.outp_OFF(channel=2)

if __name__ == '__main__':
    main()
