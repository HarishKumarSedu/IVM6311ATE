
import json
from switch_matrix.mcp2317 import MCP2317
from time import sleep

class Switch:

    def __init__(self,mcp='' ,Test_name = "VBG_TRM" ,root_file = 'signalroot.json', matrix_signals='matrixsignals.json') -> None:
        self.mcp2317 = MCP2317(mcp)
        with open(root_file, 'r') as file :
            self.signal_data = json.load(file)

        with open(matrix_signals, 'r') as file :
            self.matrix_data = json.load(file)

        signal_root = self.matrix_data.get(Test_name)
        for _, matrix in self.signal_data.items() :
            for root in matrix.keys():
                if root == str(signal_root):
                    matrix_rely = matrix.get(str(signal_root))
                    self.device_addr = int(matrix_rely.get('deviceAddr'), 16)
                    self.row = matrix_rely.get('relay').get('row')
                    self.col = matrix_rely.get('relay').get('col')

    def Force(self,status=False):
        self.mcp2317.Switch(device_addr=self.device_addr, row=self.row,col=self.col, Enable=status)

