
from time import sleep
import pandas as pd
import re 
from tqdm import tqdm

class VBGR_ADJ_TRIM:

    def __init__(self) -> None:
        pass

if __name__ == '__main__':
    data = pd.read_excel('IVM6311_Testing_scripts.xlsx', sheet_name='Reference')
    # data.rename(columns={ str(i):data[str(i)].loc['Symbol in PGM'] for i in range(1,10)}, inplace=True)
    print(data.columns)
    # mcp = MCP2221()
    # vbg = VBG_TRIM(mcp=mcp, data=data)
    # vbg.setup()
    # print(vbg.log_trims)