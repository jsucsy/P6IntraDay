'''
Created on Oct 18, 2011

@author: JSU
pylint score -0.09/10 as of 18 Jan 2012
project put on hold as of 18 Jan 2012
'''
import numpy as np
import time
#from DualDict import DualDict as dualDict
#import cfg

MMBTU_PER_GJ = 1.0 / 1.055056
GJ_PER_MMBTU = 1.055056

class PortfolioAll:
    
    def __init__(self, portfolioListPath):
        self.All = []
        #self.cif_ngx = NGXportfolio("cif_ngx",True)
        self.ngxPrompt = synthNgx("ngxPrompt", True)
        self.cif_ngx = portfolio("cif_ngx", True)
        self.cif_ukng = portfolio("cif_ukng", True)                                  
        self.cif_clhf = portfolio("cif_clhf", True)
        self.cif_east = portfolio("cif_east", True)
        self.cif_west = portfolio("cif_west", True)
        self.cif_nghf = portfolio("cif_nghf", True)                
        #self.All["cif_ngx"]=self.cif_ngx
        self.All.append(self.ngxPrompt)
        self.All.append(self.cif_ngx)
        self.All.append(self.cif_ukng)
        self.All.append(self.cif_clhf)
        self.All.append(self.cif_east)
        self.All.append(self.cif_west)
        self.All.append(self.cif_nghf)
        'ngxPrompt'
        
        self.Names = self._getNames()
        self.AbsNotional = 0
        self.OpenPnL = 0
        self.ClosedPnL = 0 
        self.Volume = 0
          
        self._getPortfolios(portfolioListPath)      

    def _getPortfolios(self, portfolioListPath):
        for line in file(portfolioListPath, "rb"):                        
            inst = line.split(";")            
            tempInst = instrument(inst)
            getattr(self, inst[0]).append(tempInst)
            
    def _getNames(self):
        _names = []
        for x in self.All:
            _names.append(x.Name)
        return _names
    
    def Count(self):
        return len(self.All)
    
    def LoadOvernight(self, pathOvernight):
        for line in file(pathOvernight):
            position = line.split(";")
            portfolio = getattr(self, position[0])
            for i in portfolio:
                if i.Name == (" ").join((position[1], position[2])):
                    i.SetOvernightPosition(position[3], position[4])
    
    def WrapAll(self):
        _absNotional = 0
        _openPnL = 0
        _closedPnL = 0
        _volume = 0
        for p in self.All:
            p.WrapAll()
            _absNotional += p.AbsNotional
            #_openPnL+=p.OpenPnL
            _closedPnL += p.ClosedPnL
            #_volume+=p.Volume
            
        self.AbsNotional = _absNotional
        #self.OpenPnL=_openPnL
        self.ClosedPnL = _closedPnL
        #self.Volume=_volume
    
    def WrapOpenPnLByName(self, portfolio):
        _openPnL = 0
        _book = getattr(self, portfolio)         
        for i in _book:
            _openPnL += i._openPnL        
        return _openPnL   
    
    def WrapClosedPnLByName(self, portfolio):
        _closedPnL = 0
        _book = getattr(self, portfolio)         
        for i in _book:
            _closedPnL += i._closedPnL        
        return _closedPnL   
    
    def WrapNetNotionalByName(self, portfolio):
        _netNtl = 0
        _book = getattr(self, portfolio)
        for i in _book:
            _netNtl += i._notional        
        return _netNtl
    
    def WrapAbsNotionalByName(self, portfolio):
        _absNtl = 0
        _book = getattr(self, portfolio)
        for i in _book:
            _absNtl += i._absNotional        
        return _absNtl

class portfolio(list):
    def __init__(self, name, active = True):
        self.Name = name
        self.Active = active
        self.AbsNotional = 0
        self.NetNotional = 0
        self.OpenNotional = 0
        self.ClosedNotional = 0
        self.OpenPnL = 0
        self.ClosedPnL = 0
        self.Volume = 0
        
        self.LongToClose = 0
        self.ShortToClose = 0
        
    def WrapAll(self):
        self.WrapAbsNotional()
        self.WrapClosedPnL()
        self.WrapToClose()
        #self.WrapNetNotional()
        #self.WrapOpenPnL()
        #self.WrapVolume()
        
    def WrapToClose(self):
        _longToClose = 0
        _shortToClose = 0
        for i in self:
            _longToClose += i.LongToClose
            _shortToClose += i.ShortToClose
        self.LongToClose = _longToClose
        self.ShortToClose = _shortToClose
        
    def WrapVolume(self):
        _volume = 0
        for i in self:
            _volume += i._positionLong
            _volume += i._positionShort
        self.Volume = _volume
        return _volume
        
    def WrapOpenPnL(self):
        _openPnL = 0     
        for i in self:
            _openPnL += (i.OpenPnL)        
        self.OpenPnL = _openPnL
        return _openPnL   
    
    def WrapClosedPnL(self):
        _closedPnL = 0       
        for i in self:
            _closedPnL += i.ClosedPnL        
        self.ClosedPnL = _closedPnL
        return _closedPnL   
    
    def WrapNetNotional(self):
        _netNtl = 0
        for i in self:
            _netNtl += i._notional  
        self.NetNotional = _netNtl      
        return _netNtl
    
    def WrapOpenNotional(self):
        _opnNtl = 0
        for i in self:
            _opnNtl += i._openNtl
            
    
    def WrapAbsNotional(self):
        _absNtl = 0
        for i in self:
            _absNtl += i.AbsNotional 
        self.AbsNotional = _absNtl       
        return _absNtl

#class synth(np.array()):
#    break

class synthNgx(portfolio):
    def __init__(self, name, active = True):
        '''INSTRUMENT ORDER IS CRITICAL!!!
        inst[0] = FP
        inst[1] = BS
        inst[2] = HH
        inst[3] = HHIL
        inst[4] = 6C'''
        
        self.Name = name
        self.Active = active
        self.AbsNotional = 0
        self.NetNotional = 0
        self.OpenPnL = 0
        self.ClosedPnL = 0
        self.Volume = 0
        
        self.LongToClose = 0
        self.ShortToClose = 0
        
        self.m_exposure_MMBTU = 0.0           #today
        self.m_exposure_CAD = 0.0
        self.m_exposure_BS = 0.0
        self.m_hedge_MMBTU = 0.0
        self.m_hedge_CAD = 0.0
        self.m_hedge_BS = 0.0
        self.m_net_MMBTU = 0.0
        self.m_net_CAD = 0.0
        self.m_net_BS = 0.0      

        self.t_exposure_MMBTU = 0.0           #total
        self.t_exposure_CAD = 0.0
        self.t_exposure_BS = 0.0
        self.t_hedge_MMBTU = 0.0
        self.t_hedge_CAD = 0.0
        self.t_hedge_BS = 0.0
        self.t_net_MMBTU = 0.0
        self.t_net_CAD = 0.0
        self.t_net_BS = 0.0    
        self.t_close_MMBTU = 0.0
        self.t_close_CAD = 0.0
        self.t_close_BS = 0.0
        
        self.synthBid = 0.0
        self.synthAsk = 0.0
        self.synthMid = 0.0
        self.synthLongMidPnL = 0.0        
        self.synthShortMidPnL = 0.0
        self.synthTotalMidPnL = 0.0
                
    def WrapAll(self):
        #self.WrapAbsNotional()
        self.WrapClosedPnL()
        self.WrapToClose()
        #self.WrapNetNotional()
        #self.WrapOpenPnL()
        #self.WrapVolume()
        self.WrapMMBTU()
        self.WrapBS()
        self.WrapCAD()
        self.WrapSynthMid()
        self.WrapMMBTUTotal()
        self.WrapBSTotal()
        self.WrapCADTotal()
        
    def WrapSynthMid(self):
        _synthLongPnL = 0.0
        _synthShortPnL = 0.0
        
        '''
        BSBid=self[1].Bid
        BSAsk=self[1].Ask
        HHBid=self[2].Bid
        HHAsk=self[2].Ask
        CADBid=self[4].Bid
        CADAsk=self[4].Ask
        '''
        if self[1].BWAP == 0 or np.isnan(self[1].BWAP): 
            bsBWAP = self[1].Last
        else:
            bsBWAP = self[1].BWAP
        if self[1].SWAP == 0 or np.isnan(self[1].SWAP):
            bsSWAP = self[1].Last
        else:
            bsSWAP = self[1].SWAP
        hhBWAP = self[2].BWAP
        hhSWAP = self[2].SWAP
        cadBWAP = self[4].BWAP
        cadSWAP = self[4].SWAP
        
        try: 
            synthBWAP = (hhBWAP + bsBWAP) / (cadSWAP / 10000) / GJ_PER_MMBTU
        except: 
            synthBWAP = 0
        try: 
            synthSWAP = (hhSWAP + bsSWAP) / (cadBWAP / 10000) / GJ_PER_MMBTU
        except: 
            synthSWAP = 0
        
        _synthLongPnL = self[0].LongPos * (
                       synthSWAP - self[0].BWAP) * self[0]._tickVal
        _synthShortPnL = self[0].ShortPos * (
                         self[0].SWAP - synthBWAP) * self[0]._tickVal
        
        if np.isnan(_synthLongPnL): 
            self.synthLongMidPnL = 0
        else: 
            self.synthLongMidPnL = _synthLongPnL
        if np.isnan(_synthShortPnL): 
            self.synthShortMidPnL = 0
        else: 
            self.synthShortMidPnL = _synthShortPnL
        self.synthTotalMidPnL = (self.synthLongMidPnL + self.synthShortMidPnL)
        
        return (_synthLongPnL + _synthShortPnL)
        
    def WrapToClose(self):
        _longToClose = 0
        _shortToClose = 0
        for i in self:
            _longToClose += i.LongToClose
            _shortToClose += i.ShortToClose
        self.LongToClose = _longToClose
        self.ShortToClose = _shortToClose
        
    def WrapMMBTU(self):
        _expMMBTU = 0.0
        _hdgMMBTU = 0.0
        _expMMBTU = (float(self[0].Position) * 
                     float(self[0].HedgeSize) * MMBTU_PER_GJ)
        _hdgMMBTU = ((float(self[2].Position) * float(self[2].HedgeSize))
                    + (float(self[3].Position) * float(self[3].HedgeSize)))
        self.m_exposure_MMBTU = _expMMBTU
        self.m_hedge_MMBTU = _hdgMMBTU
        self.m_net_MMBTU = _expMMBTU + _hdgMMBTU
        
    def WrapMMBTUTotal(self):
        
        self.t_exposure_MMBTU = self.m_exposure_MMBTU
        self.t_hedge_MMBTU = self.m_hedge_MMBTU
        self.t_net_MMBTU = self.m_net_MMBTU
        
        
        if self.t_net_MMBTU > 0:
            self.t_close_MMBTU = ((((self[2].Ask - self[2].SWAP) 
                                 * self.t_net_MMBTU) / self[3].HedgeSize)
                                 * self[3]._tickVal)
        elif self.t_net_MMBTU < 0:
            self.t_close_MMBTU = ((((self[2].BWAP - self[2].Bid)
                                 * self.t_net_MMBTU) / self[3].HedgeSize)
                                 * self[3]._tickVal)
        else: 
            self.t_close_MMBTU = 0
        
        '''
        needs to be updated for overnight position
        _expMMBTU=0.0
        _hdgMMBTU=0.0
        _expMMBTU=float(self[0].Position+self[0].PositionOvernight)*float(self[0].HedgeSize)*MMBTU_PER_GJ
        _hdgMMBTU=(float(self[2].Position+self[2].PositionOvernight)*float(self[2].HedgeSize))+(float(self[3].Position+self[3].PositionOvernight)*float(self[3].HedgeSize))
        self.t_exposure_MMBTU=_expMMBTU
        self.t_hedge_MMBTU=_hdgMMBTU
        self.t_net_MMBTU=_expMMBTU + _hdgMMBTU
        '''
        
    def WrapCAD(self):
        _expCAD = 0.0
        _hdgCAD = 0.0
        #self.WrapNetNotional()
        _expCAD = float(self[0].ShortNtl - self[0].LongNtl) * 1.05
        _hdgCAD = float(self[4].Position) * float(self[4].HedgeSize)
        self.m_exposure_CAD = _expCAD
        self.m_hedge_CAD = _hdgCAD
        self.m_net_CAD = _expCAD + _hdgCAD
        
    def WrapCADTotal(self):
        _expCAD = 0.0
        _hdgCAD = 0.0
        #self.WrapNetNotional()
        
        self.t_exposure_CAD = self.m_exposure_CAD
        self.t_hedge_CAD = self.m_hedge_CAD
        self.t_net_CAD = self.m_net_CAD
        
        if self[4].BWAP == 0:
            cadBWAP = self[4].Last
        else:
            cadBWAP = self[4].BWAP
        if self[4].SWAP == 0:
            cadSWAP = self[4].Last
        else:
            cadSWAP = self[4].SWAP
        
        if self.t_net_CAD > 0:
            self.t_close_CAD = ((((self[4].Ask - cadSWAP)
                               * self.t_net_CAD) / self[4].HedgeSize)
                               * self[4]._tickVal)
        elif self.t_net_CAD < 0:
            self.t_close_CAD = ((((cadBWAP - self[4].Bid) 
                               * self.t_net_CAD) / self[4].HedgeSize)
                               * self[4]._tickVal)
        else: self.t_close_CAD = 0
        
        '''
        _onNotional = (self[0].PositionOvernight*self[0]._tickVal*self[0].VWAPOvernight)*(-1)
        _expCAD=float(self[0].NetNotional+_onNotional)*1.05
        _hdgCAD=float(self[4].Position+self[4].PositionOvernight)*float(self[4].HedgeSize)
        self.t_exposure_CAD=_expCAD
        self.t_hedge_CAD=_hdgCAD
        self.t_net_CAD=_expCAD + _hdgCAD
        '''
        
    def WrapBS(self):
        _expBS = 0.0
        _hdgBS = 0.0
        _expBS = float(self[0].Position) * float(self[0].HedgeSize) * MMBTU_PER_GJ
        _hdgBS = float(self[1].Position) * float(self[0].HedgeSize)
        self.m_exposure_BS = _expBS
        self.m_hedge_BS = _hdgBS
        self.m_net_BS = _hdgBS + _expBS
        
    def WrapBSTotal(self):
        
        self.t_exposure_BS = self.m_exposure_BS
        self.t_hedge_BS = self.m_hedge_BS
        self.t_net_BS = self.m_net_BS
        
        if self[1].BWAP == 0: 
            bsBWAP = self[1].Last
        else : 
            bsBWAP = self[1].BWAP
        if self[1].SWAP == 0:
            bsSWAP = self[1].Last
        else:
            bsSWAP = self[1].SWAP
        
        if self.t_net_BS > 0:
            self.t_close_BS = ((((self[1].Ask - bsSWAP) * self.t_net_BS)
                              / self[1].HedgeSize) * self[1]._tickVal)
        elif self.t_net_BS<0:
            self.t_close_BS=(((bsBWAP-self[1].Bid)*self.t_net_BS)/self[1].HedgeSize)*self[1]._tickVal
        else: self.t_close_BS=0
        
        '''
        needs to be updated for overnight position
        _expBS=0.0
        _hdgBS=0.0
        _expBS=float(self[0].Position+self[0].PositionOvernight)*float(self[0].HedgeSize)*MMBTU_PER_GJ
        _hdgBS=float(self[1].Position+self[1].PositionOvernight)*float(self[0].HedgeSize)
        self.t_exposure_BS=_expBS
        self.t_hedge_BS=_hdgBS
        self.t_net_BS=_hdgBS + _expBS
        '''

class tradeObj:
    
    def __init__(self,dir,fillQty,px,time,trader,method,isLastPx,fee,notes,tickVal):
        self._timestamp=time
        self._fillQty = float(fillQty)
        self._px = float(px)
        self._trader = trader
        self._method = method
        self._fee = float(fee)
        self._notes = notes
        self._isLastPx = isLastPx
        self._tickVal = int(tickVal)
        
        #try:
        if (dir.upper() == 'B' or dir.upper() == 'BUY' or dir.upper() == 'BOT'):
            self._dir = 'B'
            self._volume = np.abs(fillQty)              # positive for both buys and sells
            self._notional = self._tickVal*self._volume*self._px*(-1)
            self._absNotional = np.abs(self._notional)
        elif (dir.upper() == 'S' or dir.upper() == 'SELL' or dir.upper() == 'SOLD'):
            self._dir = 'S'
            self._volume = np.abs(fillQty)              #positive for both buys and sells
            self._notional = self._tickVal*self._volume*self._px
            self._absNotional = np.abs(self._notional)
        else:
            self._exception = "Unknown trade direction"
        #except Exception as ex:
        #    print "Trade booking error with %s %.0f at %.4f: %s" % (dir,fillQty,px,ex)

class currDict(dict):
    def __init__(self,currListPath):
        dict.__init__(self)
        for line in file(currListPath,"rb"):                        
            params = line.split(";")            
            if len(params)>2:
                tempInst = currency(params)
                self[tempInst._index]=tempInst

class currency:
    def __init__(self,params):
        self._index=params[0]
        self.product=params[1]
        self.name=params[0]
        self.contract=params[2]
        self.rate=0.0
        
    def setRate(self,rate):
        self.rate=rate
    
    def getRate(self):
        return self.rate

class instrument:
    
    def __init__(self,params):
        #portfolio,product,contract,tickVal,baseCurr='USD',hedgeSize=1
        self._portfolio = params[0]
        self._product = params[1]
        self._contract = params[2]
        self._tickVal=int(params[3])        
        if len(params)>5:self._baseCurr=params[4]
        else: self._baseCurr='USD'        
        if len(params)>6:self._hedgeSize=params[5]
        else: self._hedgeSize=1    
        
        self._trades = {}
        
        self.Name = '%s %s' %(self._product,self._contract)
        self.BaseCurr=self._baseCurr
        self.HedgeSize=float(self._hedgeSize)
        self.Bid=np.nan
        self.Ask=np.nan
        self.Last=np.nan 
        
        self.BWAP=0
        self.LongPos=0
        self.LongNtl=0
        self.LongPnL=0
        self.LongToClose=0
                
        self.SWAP=0
        self.ShortPos=0
        self.ShortNtl=0
        self.ShortPnL=0
        self.ShortToClose=0
        
        self.Position=0
        self.ClosedPnL=0
        self.AbsNotional = 0
        
    def CalcPosition3(self):
        #uses positive volumes for buys and sells
        _position = 0
        _positionLong=0
        _positionShort=0
        _vwap = 0
        _bwap=0
        _swap=0
        _closedPnL = 0
        _openPnL = 0
        _notional = 0
        _absNotional = 0
        
        for i in self._trades.values():
            #if np.isnan(self.Last): self.Last = i._px # or i._isLastPx: self.Last=i._px
            _notional+=i._notional
            _absNotional+=i._absNotional
            if i._dir == 'B':
                _bwap=((_bwap*_positionLong)+(i._px*i._volume))/(_positionLong+i._volume)
                _positionLong+=i._volume
            elif i._dir == 'S':
                _swap=((_swap*_positionShort)+(i._px*i._volume))/(_positionShort+i._volume)
                _positionShort+=i._volume
            else:
                print "Unknown trade %s" % i
        
        if _positionLong==_positionShort:
            _closedPnL = np.minimum(_positionLong,_positionShort)*(_swap-_bwap)*self._tickVal

            
        longNtl=_bwap*_positionLong*self._tickVal
        shortNtl=_swap*_positionShort*self._tickVal
        longVal=((self.Last-_bwap)*_positionLong)*self._tickVal
        shortVal=((_swap-self.Last)*_positionShort)*self._tickVal
        #_openPnL = longVal+ shortVal - _closedPnL
        if np.isnan(_openPnL): _openPnL=0
                        
        _position = _positionLong-_positionShort
        
        #self.OpenPnL=_openPnL
        self.ClosedPnL=_closedPnL
        #self.VWAP=self.GetVWAP()
        self.BWAP=_bwap
        self.SWAP=_swap
        #self.NetNotional=_notional
        self.AbsNotional=_absNotional
        self.Position=_position
        
        self.LongPos=_positionLong
        self.LongNtl=longNtl
        
        self.ShortPos=_positionShort
        self.ShortNtl=shortNtl
        
        
        
        
    def AddTrade(self,tradeID,dir,size,px,time,trader,method,isLastPx,fee=0,notes=""):
        _trade = tradeObj(dir,size,px,time,trader,method,isLastPx,fee,notes,self._tickVal)
        self._trades[tradeID] = _trade
        self.CalcPosition3()
        
    def UpdateMarket(self,bid,ask,last,source="",ts=0):
        self.Bid=bid
        self.Ask=ask
        if np.isnan(last): 
            self.Last=self.Last                        
        else: self.Last=last
        if ts==0: 
            timestamp = time.strftime("%H:%M:%S ",time.localtime())
        else : timestamp = time.strftime("%H:%M:%S",ts)
        
        if self.LongPos==self.ShortPos:
            self.LongToClose=0
            self.ShortToClose=0
        elif self.LongPos>self.ShortPos:
            self.LongToClose=((self.LongPos-self.ShortPos)*(self.Bid-self.BWAP)*self._tickVal)
            self.ShortToClose=0
        elif self.LongPos<self.ShortPos:
            self.LongToClose=0
            self.ShortToClose=((self.ShortPos-self.LongPos)*(self.SWAP-self.Ask)*self._tickVal)
        
          
    
    def UpdateLast(self,last):
        ''' only use for mid basis market value on stat arb basis trades'''
        self.Last=last
        
    
    def show(self):
        details =[] 
        if self.Position < 0:
            vwap=self.SWAP
        elif self.Position > 0:
            vwap=self.BWAP
        else: vwap = 0
        details.append("---%s: %.0f at %.4f--- " % (self.Name,self.Position,vwap)) 
        #details.append("Open PNL: %.2f " % self._openPnL)
        #details.append("Closed PNL: %.2f " % self._closedPnL)
        #details.append("Open Notional: %.2f " % self.Notional)
        #details.append("Closed Notional: %.2f" %  (self._absNotional-np.abs(self._notional)))
        details.append(' ')    
    
    def GetProduct(self):
        return self._product
    def GetContract(self):
        return self._contract
        """
        self._position = 0
        self._positionLong=0
        self._positionShort=0
        #self._exposed = 0               #exposure for hedgeable positions
        self._vwap = 0
        self._bwap=0
        self._swap=0
        self._closedPnL = 0
        self._openPnL = 0
        self._notional = 0
        self._openNotional = 0
        self._closedNotional = 0
        self._absNotional=0
        
        
        self.VWAP=0
        
        
        self.PosShort=0
                
        self.SWAP=0
        
        self.NetNotional=0
        
        self.Position=0   
        self.PositionOvernight=0 
        self.VWAPOvernight=0    
        
        
          
                
    def AddTrade(self,tradeID,dir,size,px,time,trader,method,isLastPx,fee=0,notes=""):
        _trade = tradeObj(dir,size,px,time,trader,method,isLastPx,fee,notes,self._tickVal)
        self._trades[tradeID] = _trade
    
    def SetOvernightPosition(self,position,price):
        self.PositionOvernight = np.int(position)
        self.VWAPOvernight=np.float(price)
    
    def CalcPosition2(self):
        #uses positive volumes for buys and sells
        self._position = 0
        self._positionLong=0
        self._positionShort=0
        self._vwap = 0
        self._bwap=0
        self._swap=0
        #self._closedPnL = 0
        self._openPnL = 0
        self._notional = 0
        self._absNotional = 0
        
        for i in self._trades.values():
            if np.isnan(self.Last): self.Last = i._px # or i._isLastPx: self.Last=i._px
            self._notional+=i._notional
            self._absNotional+=i._absNotional
            if i._dir == 'B':
                self._bwap=((self._bwap*self._positionLong)+(i._px*i._volume))/(self._positionLong+i._volume)
                self._positionLong+=i._volume
            elif i._dir == 'S':
                self._swap=((self._swap*self._positionShort)+(i._px*i._volume))/(self._positionShort+i._volume)
                self._positionShort+=i._volume
            else:
                print "Unknown trade %s" % i
        
        if self._positionLong==self._positionShort:
            self._closedPnL = np.minimum(self._positionLong,self._positionShort)*(self._swap-self._bwap)*self._tickVal
        longVal=((self.Last-self._bwap)*self._positionLong)*self._tickVal
        shortVal=((self._swap-self.Last)*self._positionShort)*self._tickVal
        self._openPnL = longVal+ shortVal - self._closedPnL
        if np.isnan(self._openPnL): self._openPnL=0
                        
        self._position = self._positionLong-self._positionShort
        self.Wrap()
              
    
    
    def show(self):
        details =[] 
        if self._position < 0:
            vwap=self._swap
        elif self._position > 0:
            vwap=self._bwap
        else: vwap = 0
        details.append("---%s: %.0f at %.4f--- " % (self.Name,self._position,vwap)) 
        details.append("Open PNL: %.2f " % self._openPnL)
        details.append("Closed PNL: %.2f " % self._closedPnL)
        details.append("Open Notional: %.2f " % self._notional)
        details.append("Closed Notional: %.2f" %  (self._absNotional-np.abs(self._notional)))
        details.append(' ')                       
        
        '''
        details = 
        "%s: %.0f at %.4f -- Cl PnL %.2f, Op PnL %.2f, %.2f ntl, %.2f absNtl" % (self._contract,
                                                          self._position, 
                                                          self._vwap, 
                                                          self._closedPnL,
                                                          self._openPnL, 
                                                          self._notional,
                                                          self._absNotional)
        '''
        return "\r\n".join(details)
    
    
    def showTrades(self):
        for i in self._trades.values():
            print "%s: %s %.0f at %.3f by %s via %s" % (i._timestamp,
                                                        i._dir,
                                                        i._fillQty,
                                                        i._px,
                                                        i._trader,
                                                        i._method)
    
    def Wrap(self):
        self.OpenPnL=self.GetOpenPNL()
        self.ClosedPnL=self.GetClosedPNL()
        self.VWAP=self.GetVWAP()
        self.BWAP=self.GetBWAP()
        self.SWAP=self.GetSWAP()
        self.NetNotional=self.GetNotional()
        self.AbsNotional=self.GetAbsNotional()
        self.Position=self.GetPosition()
        self.PosLong=self.GetPosLong()
        self.PosShort=self.GetPosShort()
     
    
    def GetPortfolio(self):
        return self._portfolio    
    def GetTickVal(self):
        return self._tickVal    
    def GetPosition(self):
        return self._position    
    def GetPosLong(self):
        return self._positionLong
    def GetPosShort(self):
        return self._positionShort
    def GetVWAP(self):
        return self._vwap
    def GetBWAP(self):
        return self._bwap 
    def GetSWAP(self):
        return self._swap     
    def GetClosedPNL(self):
        return self._closedPnL    
    def GetOpenPNL(self):
        return self._openPnL    
    def GetNotional(self):
        return self._notional    
    def GetAbsNotional(self):
        return self._absNotional    
    def GetLastPrice(self):
        return self.Last   
    #def SetLastPrice(self,last):
    #    self.Last=last
    def ReCalcOpenPnL(self):
        if self.Position== 0:
            self._openPnL=0
            self.OpenPnL=0
        else:
            #self._closedPnL = np.minimum(self._positionLong,self._positionShort)*(self._swap-self._bwap)*self._tickVal
            longVal=((self.Last-self._bwap)*self._positionLong)*self._tickVal
            shortVal=((self._swap-self.Last)*self._positionShort)*self._tickVal
            self._openPnL = longVal+ shortVal - self._closedPnL
            self.GetOpenPNL()
            
    """
            
class PnLException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    
    
#if __name__ == '__main__':
    #unit tests
    

