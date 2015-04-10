'''
Created on Oct 18, 2011

@author: JSU
pylint score 9.43/10 as of 17 Jan 2012
'''

import time
from DualDict import DualDict as DualDict

#class config():
#    __shared_state = {}         #implement Borg design pattern, see: 
#http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/
    
IS_LIVE = True

CONN = None
BOOK = None
CURRENCY = None
IS_READY_TO_EMAIL = False
IS_EMAIL_ENABLED = False         #disable at start to allow full startup process
IS_RELOAD_DATA_TRIGGER = False
IS_PORT_READY = False
IS_QUITTING_TIME = False          #program is done, terminate threads

PATH_REPORT = []
PATH_PORTFOLIO_LIST = ""
PATH_SYS_LOG = ""
PATH_CURRENCY_LIST = ""
PATH_POSITIONS_OVERNIGHT = ""
ADDRESS_BOOK = []
DATA_CONNECTIONS = []
INTERVAL_UPDATE_POS = 0
INTERVAL_UPDATE_SQL = 0
INTERVAL_UPDATE_GUI = 0
INTERVAL_UPDATE_EMAIL = 0
LINES_ARC_DATA = 0
TIME_ARC_DATA = time.localtime()
        
#fpHedgeMap = DualDict({})        #deprecated during cleanup 17 Jan 2012
MONTH_CODE = ['zerofill', 'F', 'G', 'H', 'J', 'K',
              'M', 'N', 'Q', 'U', 'V', 'X', 'Z',
             'Q1 ', 'Q2 ', 'Q3 ', 'Q4 ', 'FG', 'HJ', 'NQ']
MONTH_NAME = ['zerofill', 'Jan', 'Feb', 'Mar', 'Apr', 'May',
              'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
             'Q1 ', 'Q2 ', 'Q3' , 'Q4 ', 'FG', 'HJ', 'NQ']  
NAMES_CURRENCY = DualDict({'GBP':'6B',
                      'CAD':'6C',
                      'EUR':'6E',
                      'JPY':'6J',
                      'CHF':'6S'})                      
NAMES_TT = DualDict({'IPE Nat Gas': 'UKNG',
                     'Henry Nat Gas': 'Henry',
                     'HH ICE Lots': 'HenryIceLots',
                     'MCD': 'MCD',
                     '6C': '6C',
                     'M6B': 'M6B',
                     'CL': 'CL',
                     'NG': 'NG',
                     'PJM Western Hub': 'PJM',
                     'Nepool': 'Nepool',
                     'SP-15': 'SP-15',
                     'NP-15': 'NP-15',
                     'Mid-C': 'Mid-C'})
NAMES_ARC = DualDict({'CME_MCD': 'MCD',
                      'FUT_CME_6C': '6C',
                      'ICE_NG_FP_LD1_HENRY': 'Henry',
                      'ICE_NG_FP_LD1_ICELOTS_HENRY': 'HenryIceLots',
                      'FUT_CME_NG': 'NG',
                      'ICE_NGX_FP_CA_AB_NIT': 'AecoPhysFP',
                      'ICE_NGX_BS_LD1_US_AB_NIT': 'AecoPhysBS',
                      'ICE_NG_BS_LD1_7A_AB_NIT': 'AecoFinBS',
                      'ICE_NGX_ID_7A_US_AB_NIT': 'AecoIdUS',
                      'ICE_NGX_ID_7A_CA_AB_NIT': 'AecoIdCA'})
NORMALIZE_TT = {}
NORMALIZE_ARC = {'6C': 10000,
              'MCD': 1}
STRIP_MAP = DualDict({'Q1 ': [1, 2, 3],
                      'Q2 ': [4, 5, 6],
                      'Q3 ': [7, 8, 9],
                      'Q4 ': [10, 11, 12],
                      'FG' : [1, 2],
                      'HJ' : [3, 4],
                      'NQ' : [7, 8]})


        
"""   
if __name__ == '__main__':
    #unit tests
    #import core
    
    print book.Count()
    for x in book.All:
        print x.Name
        
    print MONTH_CODE[1]
    print MONTH_CODE.index('K')
    print str(MONTH_CODE.index('K')).zfill(2)
    print str(MONTH_CODE.index('Z')).zfill(2)
    
    print MONTH_NAME[7]
    print MONTH_NAME[MONTH_CODE.index('V')]
    
    for i in book.cif_ukng:
        print i.show()        
    print book.cif_ukng[1].show()
    
    #print namesIce.get_value('UK Natural Gas Futures')
    #print namesIce.get_key('NGX Phys BS')
    print NAMES_TT.get_key('UKNG')
    
    a = STRIP_MAP['Q1 ']
    for i in a: print i 
"""
