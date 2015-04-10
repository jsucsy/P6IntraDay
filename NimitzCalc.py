'''
Created on Nov 25, 2011

@author: JSU
pylint score 10.00/10 17 Jan 2012
'''
from DualDict import DualDict as dualDict

MMBTU_PER_GJ = 1.0 / 1.055056
GJ_PER_MMBTU = 1.055056

LEG_TYPE = dualDict({0:'NG_ICE',
                    1:'NG_CME',
                    2:'NG_ICE_LOTS',
                    3:'FX_6C',
                    4:'FX_MCD',
                    5:'PH_BS',
                    6:'FI_BS',
                    7:'ID_7A_US',
                    8:'ID_7A_CA'})

SYNTH_LEG_TYPE = dualDict({0:'NG_BEST',
                         1:'BS_BEST', 
                         2:'PH_BS_ID_7A_US',
                         3:'PH_BS_ID_7A_CA'})

BEST_PATH_LEGS = dualDict({0:'BEST_PATH_NG',
                         1:'BEST_PATH_BS'})

BEST_PATH_NG = dualDict({0:'NG_ICE',
                        1:'NG_CME',
                        255:'NONE'})

BEST_PATH_BS = dualDict({0:'PH_BS',
                        1:'ID_7A_US',
                        2:'ID_7A_CA',
                        255:'NONE'})

SIDE = dualDict({-1:'OPPOSITE',
                 1:'SAME'})




class Exposure():
    '''calculate exposure of NGX hedge based on FP position'''
    
    def __init__(self):
        self.m_delta_synth = 0.0
        self.m_exposure = 0.0
        self.m_flat = True
        self.m_is_ok = True
        
    def exposure(self):
        '''returns exposure characteristics'''
        return self.m_exposure
    
    def flat(self):
        '''returns boolean flat status'''
        return self.m_flat
    
    def is_ok(self):
        '''returns boolean correctness status'''
        return self.m_is_ok
    
    def check(self, side, max_hedge):
        '''this is the check to make sure we are not OUT OF HEDGE'''
        #not yet implemented
        

class ExposureNgIce(Exposure):
    '''calculate ICE NG exposure related to FP'''
    
    def __init__(self):             #, synthNimitz):
        Exposure.__init__(self)
        self.m_delta_ng_ice = 0.0
        self.m_delta_ng_ice_lots = 0.0
        

    

if __name__ == '__main__':    
    print [v for v in LEG_TYPE.values()]
    print [v for v in SYNTH_LEG_TYPE.values()]
    print [v for v in BEST_PATH_LEGS.values()]
    print [v for v in BEST_PATH_NG.values()]
    print [v for v in BEST_PATH_BS.values()]
    print [v for v in SIDE.values()]

