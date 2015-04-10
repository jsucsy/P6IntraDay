'''
Created on Nov 18, 2011

@author: JSU
main wx app based on twisted protocol
'''
import time
import wx
import wx.grid as gridlib
import core, cfg, data, fills, report, ArcSql
import numpy as np
from twisted.python import log
from twisted.internet import wxreactor
wxreactor.install()

#import t.i.reactor only after installing wxreactor:
from twisted.internet import reactor
from twisted.internet.task import LoopingCall


ID_EXIT  = 101
ID_EMAILOFF = 201
ID_EMAILON = 202
ID_EMAILREADY = 203
ID_ADDRBOOK = 204
ID_GETTTDATA = 301
ID_GETARCLOGDATA = 302
ID_RELOADDATA = 303
ID_LOADOVERNIGHT = 304
ID_TIME = 1100
ID_TIMEARCDATA = 1101
ID_LINESARCDATA = 1102
ID_ISLIVE = 1103
ID_MAILER = 1104
ID_TTMD = 1105
ID_ARCMD = 1106



class StatusPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        
        self.vSizer = None
        self.grid = None
        self.hSizer = None
        self.fieldLabels = [] 
        self.fields=[]
        self.buttons=[]
        
        # create some sizers
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.fieldLabels.append(wx.StaticText(self,label="Live/Test: "))
        self.fieldLabels.append(wx.StaticText(self,label="Address Book: "))
        self.fieldLabels.append(wx.StaticText(self,label="Update Timestamp: "))
        self.fieldLabels.append(wx.StaticText(self,label="Data Connections: "))

        if cfg.IS_LIVE: 
            self.fields.append(wx.StaticText(self,label="PRODUCTION"))
            self.SetBackgroundColour('#71C671')
        else:
            self.fields.append(wx.StaticText(self,label="TESTING"))
            self.SetBackgroundColour('gray')
        self.Refresh()
        
        self.fields.append(wx.StaticText(self,label=str(cfg.ADDRESS_BOOK)))
        self.testTS = wx.StaticText(self,label=str(time.strftime("%Y-%m-%d %H:%M:%S")))
        self.dataCon=wx.StaticText(self,label=str(cfg.DATA_CONNECTIONS))
        #self.testTS=wx.StaticText(self,label='None')
        self.fields.append(self.testTS)
        self.fields.append(self.dataCon)
        
        self.btnEnableEmail=wx.Button(self,label="Enable Email")
        self.btnEmailReport=wx.Button(self,label="Email Report")
        self.Bind(wx.EVT_BUTTON, self.ToggleEmailEnabled, self.btnEnableEmail)
        self.Bind(wx.EVT_BUTTON, self.OnEmailReport, self.btnEmailReport)
        
        for i in range(0,len(self.fieldLabels)):
            self.grid.Add(self.fieldLabels[i],pos=(i,0))
        
        for i in range(0,len(self.fields)):
            self.grid.Add(self.fields[i],pos=(i,1))
        
        self.grid.Add(self.btnEnableEmail,pos=(0,3))
        self.grid.Add(self.btnEmailReport,pos=(1,3))
        
        self.hSizer.Add(self.grid,0,wx.ALL,5)
        self.vSizer.Add(self.hSizer,0,wx.ALL,5)
        self.SetSizerAndFit(self.vSizer)  

    def Update(self):
        #self.testTS.SetLabel(str(datetime.utcnow()))
        self.testTS.SetLabel(time.strftime("%Y-%m-%d %H:%M:%S"))    
        self.dataCon.SetLabel(str(cfg.DATA_CONNECTIONS))

    def OnEmailReport(self,e):
        cfg.IS_READY_TO_EMAIL=True
        report.email_report()
        
    def ToggleEmailEnabled(self,e):
        cfg.IS_EMAIL_ENABLED=True
        
        
class ManualOrderPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        
        # create some sizers
        vSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.fieldLabels = [] 
        self.fieldLabels.append(wx.StaticText(self,label="Portfolio: "))
        self.fieldLabels.append(wx.StaticText(self,label="Contract: "))
        self.fieldLabels.append(wx.StaticText(self,label="Quantity: "))
        self.fieldLabels.append(wx.StaticText(self,label="Trade Price: "))
        self.fieldLabels.append(wx.StaticText(self,label="Last Price: "))
        
        for i in range(0,len(self.fieldLabels)):
            grid.Add(self.fieldLabels[i],pos=(i,0))
        
        self.cbxPortfolios=wx.ComboBox(self,size=(150,-1),choices=cfg.BOOK.Names,style=wx.CB_READONLY)
        self.cbxInstruments=wx.ComboBox(self,size=(150,-1),style=wx.CB_READONLY)
        self.txtCurr=wx.TextCtrl(self,size=(60,-1),style=wx.TE_READONLY)
        self.txtQty=wx.TextCtrl(self,size=(60,-1))
        self.txtTradePrice=wx.TextCtrl(self,size=(60,-1))
        self.txtLastPrice=wx.TextCtrl(self,size=(60,-1))
        
        self.direction='Buy'
        self.rdoDir=wx.RadioBox(self,label="Direction",choices=['Buy','Sell'])
        
        self.Bind(wx.EVT_COMBOBOX, self.OnPortfolioSelect, self.cbxPortfolios)
        self.Bind(wx.EVT_COMBOBOX, self.OnInstrumentSelect, self.cbxInstruments)
        self.Bind(wx.EVT_TEXT,self.OnTradePrice,self.txtTradePrice)       
        
        grid.Add(self.cbxPortfolios,pos=(0,1))
        grid.Add(self.cbxInstruments,pos=(1,1))
        grid.Add(self.txtCurr,pos=(1,2))
        grid.Add(self.txtQty,pos=(2,1))
        grid.Add(self.txtTradePrice,pos=(3,1))
        grid.Add(self.txtLastPrice,pos=(4,1))
        grid.Add(self.rdoDir,pos=(5,1))
        
        self.btnSaveTrade=wx.Button(self,label="Save Trade")
        self.Bind(wx.EVT_BUTTON, self.OnSaveTrade, self.btnSaveTrade)
        
        grid.Add(self.btnSaveTrade,pos=(len(self.fieldLabels),0))
        
        hSizer.Add(grid,0,wx.ALL,5)
        vSizer.Add(hSizer,0,wx.ALL,5)
        #mainSizer.Add(self.button
        self.SetSizerAndFit(vSizer)          
        
    def OnSaveTrade(self,e):
        headerStr="Row Number,Exchange,B/S/X,Filled Qty,Wrk Qty,Price,Currency,P/F/O,Product,Expiry,Account,Member,Group,Trader,Acct Type,Date Order,Time Order,Date Exch,Time Exch,Instrument,Order Num,Qty Order,TT Order Key,Order Type,Product Type,TIF,Trans ID,Strike,C/P,FFT2,FFT3,Clr Member,Exch Mbr,Exch Grp,Exch Trd,Fee,Give Up,Cntr Firm,Cntr Mbr,Order Price,Exported,Allocation ID,Username,Fill Key\n"
        ts = time.strftime("%Y_%m_%d_%H%M%S")
        name=cfg.PATH_REPORT[0]+"ManualP6_%s.csv" % ts
        dateOrder=time.strftime("%d/%m/%Y")
        timeOrder=time.strftime("%H:%M:%S")        
        prt=self.cbxPortfolios.Value
        curr=self.txtCurr.Value[0:3]
        prodContract=self.cbxInstruments.Value.split(' ')
        prod=prodContract[0]
        contract=prodContract[1]
        tid=str(int(time.time()))
        dir=self.rdoDir.GetStringSelection()
        qty=str(self.txtQty.Value)
        px=str(self.txtTradePrice.Value)
        x=1
        tradeParam=[]
        #inst.AddTrade(tradeID,dir,qty,px,fillTime,trader,method,isLast,fee)
        tradeParam.append(str(x))
        tradeParam.append('ManualEntry')
        tradeParam.append(dir)
        tradeParam.append(qty)
        tradeParam.append('')
        tradeParam.append(px)
        tradeParam.append('')                   #tradeParam.append(curr)
        tradeParam.append('F')
        tradeParam.append(prod)
        tradeParam.append(contract)
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('ManualEntry')        #Trader
        tradeParam.append('')
        tradeParam.append(dateOrder)
        tradeParam.append(timeOrder)
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append(self.cbxInstruments.Value)
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')               #Order type
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')               #FFT2
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')               #Cntr Mbr
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append('')
        tradeParam.append(str(time.time()))

        tradeStr=",".join(tradeParam)
        #print tradeParam
        #print 
        with open(name,'w')as f:
            f.write(headerStr)
            f.write(tradeStr)
                
        #clear all fields
        self.cbxInstruments.Clear()
        #self.txtQty.Clear()
        self.txtCurr.Clear()
        #self.txtTradePrice.Clear()
        #self.txtLastPrice.Clear()
        
    def OnTradePrice(self,e):
        self.txtLastPrice.Value=self.txtTradePrice.Value
        
    def OnPortfolioSelect(self,e):
        self.cbxInstruments.Clear()   
        self.txtQty.Clear()
        self.txtTradePrice.Clear()
        self.txtLastPrice.Clear()     
        for p in cfg.BOOK.All:
            if self.cbxPortfolios.Value == p.Name:
                for i in p:
                    self.cbxInstruments.Append(i.Name)
                return
            
    def OnInstrumentSelect(self,e):
        for p in cfg.BOOK.All:
            if self.cbxPortfolios.Value == p.Name:
                for i in p:
                    if self.cbxInstruments.Value==i.Name:
                        #print i.BaseCurr
                        self.txtCurr.Value=i.BaseCurr
                return
        
        self.txtQty.Clear()
        self.txtTradePrice.Clear()
        self.txtLastPrice.Clear()
        self.Refresh()
        
    def Update(self):
        """periodic GUI update"""
        return          
    
class ReportingPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.portfolio=None
        self.instrument=None
        
        self.fieldLabels = [] 
        self.fieldLabels.append(wx.StaticText(self,label="Portfolio: "))
        self.fieldLabels.append(wx.StaticText(self,label="Contract: "))
        self.fieldLabels.append(wx.StaticText(self,label="Last Price: "))
        
        for i in range(0,len(self.fieldLabels)):
            grid.Add(self.fieldLabels[i],pos=(i,0))
        
        self.cbxPortfolios=wx.ComboBox(self,size=(95,-1),choices=cfg.BOOK.Names,style=wx.CB_READONLY)
        self.cbxInstruments=wx.ComboBox(self,size=(95,-1),style=wx.CB_READONLY)
        self.txtLastPrice=wx.TextCtrl(self,size=(60,-1))
        
        self.btnUpdateLast=wx.Button(self,label="Update Last Price")
        #self.btnEmailReport=wx.Button(self,label="Email Report")
        
        self.Bind(wx.EVT_COMBOBOX, self.OnPortfolioSelect, self.cbxPortfolios)
        self.Bind(wx.EVT_COMBOBOX, self.OnInstrumentSelect, self.cbxInstruments)
        self.Bind(wx.EVT_BUTTON, self.OnUpdateLast, self.btnUpdateLast)
        #self.Bind(wx.EVT_BUTTON, self.OnEmailReport, self.btnEmailReport)
        
        grid.Add(self.cbxPortfolios,pos=(0,1))
        grid.Add(self.cbxInstruments,pos=(1,1))
        grid.Add(self.txtLastPrice,pos=(2,1))

        grid.Add(self.btnUpdateLast,pos=(2,3))
        #grid.Add(self.btnEmailReport,pos=(3,3))
        
        hSizer.Add(grid,0,wx.ALL,5)
        vSizer.Add(hSizer,0,wx.ALL,5)
        #mainSizer.Add(self.button
        self.SetSizerAndFit(vSizer)
        
    def Update(self):
        """periodic GUI update"""
        return          
        
    def OnEmailReport(self,e):
        cfg.IS_READY_TO_EMAIL=True
        
    def OnUpdateLast(self,e):
        px = float(self.txtLastPrice.Value)
        self.instrument.SetLastPrice(px)
        
    def OnPortfolioSelect(self,e):
        self.cbxInstruments.Clear()   
        self.txtLastPrice.Clear()     
        for p in cfg.BOOK.All:
            if self.cbxPortfolios.Value == p.Name:
                self.portfolio=p
                for i in p:
                    self.cbxInstruments.Append(i.Name)
                return
            
    def OnInstrumentSelect(self,e):
        self.txtLastPrice.Clear()
        for i in self.portfolio:
            if i.Name == self.cbxInstruments.Value: self.instrument = i
  
class CurrencyGrid(gridlib.Grid):
    def __init__(self,parent):
        gridlib.Grid.__init__(self,parent)
        self.moveTo=None
        
        numCols=2
        numRows=cfg.BOOK.Count()+1      
        
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.CreateGrid(numRows,numCols)
        self.EnableEditing(False)           #make grid readonly
        
        self.SetColLabelValue(0,"Curr")
        self.SetColLabelValue(1,"Rate")
        self.SetRowLabelSize(25)
        self.SetColSize(0,120)
        self.SetColSize(1,80)
        
        self.SetCellValue(0,0,"Daily Totals")
        for i in range(cfg.BOOK.Count()):
            self.SetCellValue(i+1,0,cfg.BOOK.All[i].Name) 
            
        #test all events
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)
        
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelLeftDClick)
        
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)
        
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        
        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)  
        
    def Update(self):
        cfg.BOOK.WrapAll()
        self.SetCellValue(0,1,str(np.round(cfg.BOOK.OpenPnL,2)))
        self.SetCellValue(0,2,str(np.round(cfg.BOOK.ClosedPnL,2)))
        for i in range(cfg.BOOK.Count()):
            self.SetCellValue(i+1,1,str(np.round(cfg.BOOK.All[i].OpenPnL,2)))
            self.SetCellValue(i+1,2,str(np.round(cfg.BOOK.All[i].ClosedPnL,2))) 
            self.SetCellValue(i+1,3,str(np.round((cfg.BOOK.All[i].ClosedPnL+cfg.BOOK.All[i].OpenPnL),2))) 
            self.SetCellValue(i+1,4,str(np.round(cfg.BOOK.All[i].Volume,0)))
            self.SetCellValue(i+1,5,str(np.round(cfg.BOOK.All[i].AbsNotional,0)))
        
        
    def OnCellLeftClick(self,evt):
        evt.Skip()
        
    def OnCellRightClick(self,evt):
        evt.Skip()
        
    def OnCellLeftDClick(self,evt):
        evt.Skip()
        
    def OnCellRightDClick(self,evt):
        evt.Skip()
        
    def OnLabelLeftClick(self,evt):
        evt.Skip()
        
    def OnLabelRightClick(self,evt):
        evt.Skip()
    
    def OnLabelLeftDClick(self,evt):
        evt.Skip()
    
    def OnLabelRightDClick(self,evt):
        evt.Skip()
    
    def OnRowSize(self,evt):
        evt.Skip()
    
    def OnColSize(self,evt):
        evt.Skip()
    
    def OnRangeSelect(self,evt):
        evt.Skip()
    
    def OnCellChange(self,evt):
        evt.Skip()
    
    def OnIdle(self,evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo=None
            
        evt.Skip()
    
    def OnSelectCell(self,evt):
        evt.Skip()
        
    def OnEditorShown(self,evt):
        evt.Skip()
    
    def OnEditorHidden(self,evt):
        evt.Skip()
    
    def OnEditorCreated(self,evt):
        evt.Skip()     
     
class SummaryGrid(gridlib.Grid):
    def __init__(self,parent):
        gridlib.Grid.__init__(self,parent)
        self.moveTo=None
        
        numCols=6
        numRows=cfg.BOOK.Count()+1      
        
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.CreateGrid(numRows,numCols)
        self.EnableEditing(False)           #make grid readonly
        
        self.SetColLabelValue(0,"Portfolio")
        self.SetColLabelValue(1,"OpenPnL")
        self.SetColLabelValue(2,"ClosedPnL")
        self.SetColLabelValue(3,"Total")
        self.SetColLabelValue(4,"Volume")
        self.SetColLabelValue(5,"Notional")
        self.SetRowLabelSize(25)
        self.SetColSize(0,120)
        self.SetColSize(1,60)
        self.SetColSize(2,60)
        self.SetColSize(3,60)
        self.SetColSize(4,60)
        #self.SetColSize(5,60)
        
        self.SetCellValue(0,0,"Daily Totals")
        for i in range(cfg.BOOK.Count()):
            self.SetCellValue(i+1,0,cfg.BOOK.All[i].Name) 
            
        #test all events
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)
        
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelLeftDClick)
        
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)
        
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        
        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)  
        
    def Update(self):
        cfg.BOOK.WrapAll()
        self.SetCellValue(0,1,str(np.round(cfg.BOOK.OpenPnL,2)))
        self.SetCellValue(0,2,str(np.round(cfg.BOOK.ClosedPnL,2)))
        self.SetCellValue(0,3,str(np.round(cfg.BOOK.OpenPnL+cfg.BOOK.ClosedPnL,2)))
        for i in range(cfg.BOOK.Count()):
            self.SetCellValue(i+1,1,str(np.round(cfg.BOOK.All[i].OpenPnL,2)))
            self.SetCellValue(i+1,2,str(np.round(cfg.BOOK.All[i].ClosedPnL,2))) 
            self.SetCellValue(i+1,3,str(np.round((cfg.BOOK.All[i].ClosedPnL+cfg.BOOK.All[i].OpenPnL),2))) 
            self.SetCellValue(i+1,4,str(np.round(cfg.BOOK.All[i].Volume,0)))
            self.SetCellValue(i+1,5,str(np.round(cfg.BOOK.All[i].AbsNotional,0)))
        
        
    def OnCellLeftClick(self,evt):
        evt.Skip()
        
    def OnCellRightClick(self,evt):
        evt.Skip()
        
    def OnCellLeftDClick(self,evt):
        evt.Skip()
        
    def OnCellRightDClick(self,evt):
        evt.Skip()
        
    def OnLabelLeftClick(self,evt):
        evt.Skip()
        
    def OnLabelRightClick(self,evt):
        evt.Skip()
    
    def OnLabelLeftDClick(self,evt):
        evt.Skip()
    
    def OnLabelRightDClick(self,evt):
        evt.Skip()
    
    def OnRowSize(self,evt):
        evt.Skip()
    
    def OnColSize(self,evt):
        evt.Skip()
    
    def OnRangeSelect(self,evt):
        evt.Skip()
    
    def OnCellChange(self,evt):
        evt.Skip()
    
    def OnIdle(self,evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo=None
            
        evt.Skip()
    
    def OnSelectCell(self,evt):
        evt.Skip()
        
    def OnEditorShown(self,evt):
        evt.Skip()
    
    def OnEditorHidden(self,evt):
        evt.Skip()
    
    def OnEditorCreated(self,evt):
        evt.Skip()     
         
class PortfolioGrid(gridlib.Grid):
    def __init__(self,parent,portfolio):
        gridlib.Grid.__init__(self,parent)
        self.portfolio=portfolio
        self.moveTo=None
        
        numCols=18
        numRows=len(self.portfolio)+1
        
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.CreateGrid(numRows,numCols)
        self.EnableEditing(False)           #make grid readonly
        
        #simple cell formatting
        #self.SetColSize(3,200)        
        #self.SetRowSize(4,45)
        #self.SetCellValue(0,0,"First cell")
        #self.SetReadOnly(3,3,True)
        
        #attribute objects to keep a set of formatting values for reuse
        #attr=gridlib.GridCellAttr()
        #attr.SetTextColour(wx.BLACK)
        #attr.SetBackgroundColour(wx.RED)
        #attr.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.BOLD))
        
        #set cell attributes for whole row(or column)
        #self.SetRowAttr(5,attr)
        self.SetColLabelValue(0,"Contract")
        self.SetColLabelValue(1,"OpenPnL")
        self.SetColLabelValue(2,"ClosedPnL")
        self.SetColLabelValue(3,"Position")
        self.SetColLabelValue(4,"Bid")
        self.SetColLabelValue(5,"Ask")
        self.SetColLabelValue(6,"Last")
        
        self.SetColLabelValue(7,"BotVol")
        self.SetColLabelValue(8,"BWAP")
        self.SetColLabelValue(9,"B To Cl")
        self.SetColLabelValue(10,"B Ntl")
        
        self.SetColLabelValue(11,"SldVol")
        self.SetColLabelValue(12,"SWAP")
        self.SetColLabelValue(13,"S To Cl")
        self.SetColLabelValue(14,"S Ntl")
                
        self.SetColLabelValue(15,"AbsNtl")
        self.SetColLabelValue(16,"ToClose")
        self.SetRowLabelSize(25)
        self.SetColSize(0,120)
        self.SetColSize(1,60)
        self.SetColSize(2,60)
        self.SetColSize(3,60)
        self.SetColSize(4,60)
        self.SetColSize(5,60)
        self.SetColSize(6,60)
        self.SetColSize(7,60)
        self.SetColSize(8,60)
        self.SetColSize(9,60)
        self.SetColSize(10,60)
        self.SetColSize(11,60)
        self.SetColSize(12,60)
        self.SetColSize(13,60)
        self.SetColSize(14,60)
        self.SetColSize(15,60)
        self.SetColSize(16,60)
        self.SetColSize(17,60)
        
        for i in range(len(self.portfolio)):
            self.SetCellValue(i+1,0,self.portfolio[i].Name)            
        
        self.SetColLabelAlignment(wx.ALIGN_LEFT,wx.ALIGN_BOTTOM)
        
        #test all events
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)
        
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelLeftDClick)
        
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)
        
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        
        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)
        
    def Update(self):
        p=self.portfolio
        p.WrapAll()
        #self.SetCellValue(i,1,str(np.round(inst.OpenPnL,2)))               
        self.SetCellValue(0,2,str(np.round(p.ClosedPnL,2)))
        #self.SetCellValue(0,3,str(inst.Position))

        #self.SetCellValue(0,7,str(inst.LongPos))
        self.SetCellValue(0,9,str(np.round(p.LongToClose,0)))
        #self.SetCellValue(0,10,str(np.round(inst.LongNtl,0)))
        
        #self.SetCellValue(0,11,str(inst.ShortPos))
        self.SetCellValue(0,13,str(np.round(p.ShortToClose,0)))
        #self.SetCellValue(0,14,str(np.round(inst.ShortNtl,5)))
        
        #self.SetCellValue(i,15,str(inst.AbsNotional))
        self.SetCellValue(0,16,str(np.round((p.LongToClose+p.ShortToClose),0)))

        i=1        
        for inst in self.portfolio:
            if not np.isnan(inst.Bid):
                self.SetCellValue(i,4,"%s"%inst.Bid)
            if not np.isnan(inst.Ask):
                self.SetCellValue(i,5,"%s"%inst.Ask)
            if not np.isnan(inst.Last): 
                self.SetCellValue(i,6,"%s"%inst.Last)
                
            if inst.AbsNotional != 0:
                #self.SetCellValue(i,1,str(np.round(inst.OpenPnL,2)))               
                self.SetCellValue(i,2,str(np.round(inst.ClosedPnL,2)))
                self.SetCellValue(i,3,str(inst.Position))

                self.SetCellValue(i,7,str(inst.LongPos))
                self.SetCellValue(i,8,str(np.round(inst.BWAP,5)))
                #self.SetCellValue(i,9,str(np.round(inst.LongPnL,0)))
                self.SetCellValue(i,9,str(np.round(inst.LongToClose,0)))
                self.SetCellValue(i,10,str(np.round(inst.LongNtl,0)))
                
                self.SetCellValue(i,11,str(inst.ShortPos))
                self.SetCellValue(i,12,str(np.round(inst.SWAP,5)))
                #self.SetCellValue(i,13,str(np.round(inst.ShortPnL,5)))
                self.SetCellValue(i,13,str(np.round(inst.ShortToClose,5)))
                self.SetCellValue(i,14,str(np.round(inst.ShortNtl,5)))
                
                self.SetCellValue(i,15,str(inst.AbsNotional))
                self.SetCellValue(i,16,str(np.round((inst.LongToClose+inst.ShortToClose),0)))
                
            i+=1    
        
    def OnCellLeftClick(self,evt):
        evt.Skip()
        
    def OnCellRightClick(self,evt):
        evt.Skip()
        
    def OnCellLeftDClick(self,evt):
        evt.Skip()
        
    def OnCellRightDClick(self,evt):
        evt.Skip()
        
    def OnLabelLeftClick(self,evt):
        evt.Skip()
        
    def OnLabelRightClick(self,evt):
        evt.Skip()
    
    def OnLabelLeftDClick(self,evt):
        evt.Skip()
    
    def OnLabelRightDClick(self,evt):
        evt.Skip()
    
    def OnRowSize(self,evt):
        evt.Skip()
    
    def OnColSize(self,evt):
        evt.Skip()
    
    def OnRangeSelect(self,evt):
        evt.Skip()
    
    def OnCellChange(self,evt):
        evt.Skip()
    
    def OnIdle(self,evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo=None
            
        evt.Skip()
    
    def OnSelectCell(self,evt):
        evt.Skip()
        
    def OnEditorShown(self,evt):
        evt.Skip()
    
    def OnEditorHidden(self,evt):
        evt.Skip()
    
    def OnEditorCreated(self,evt):
        evt.Skip()    

class SynthGrid(PortfolioGrid):
    def __init__(self,parent,portfolio):
        gridlib.Grid.__init__(self,parent)
        self.portfolio=portfolio
        self.moveTo=None
        
        numCols=16
        numRows=7
        
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.CreateGrid(numRows,numCols)
        self.EnableEditing(False)           #make grid readonly
        
        self.SetColLabelValue(0,"Type")
        self.SetColLabelValue(1,"Mol Exp")
        self.SetColLabelValue(2,"Mol Hedge")
        self.SetColLabelValue(3,"Net Mol")
        self.SetColLabelValue(4,"")
        self.SetColLabelValue(5,"BS Exp")
        self.SetColLabelValue(6,"BS Hedge")
        self.SetColLabelValue(7,"Net BS")
        self.SetColLabelValue(8,"")
        self.SetColLabelValue(9,"CAD Exp")
        self.SetColLabelValue(10,"CAD Hedge")
        self.SetColLabelValue(11,"Net CAD")
        self.SetColLabelValue(12,"")
        self.SetColLabelValue(13,"+Mid PnL")
        self.SetColLabelValue(14,"-Mid PnL")
        self.SetColLabelValue(15,"T Mid PnL")
        self.SetRowLabelSize(25)
        self.SetColSize(0,63)
        self.SetColSize(1,63)
        self.SetColSize(2,63)
        self.SetColSize(3,63)
        self.SetColSize(4,15)
        self.SetColSize(5,63)
        self.SetColSize(6,63)
        self.SetColSize(7,63)
        self.SetColSize(8,15)
        self.SetColSize(9,63)
        self.SetColSize(10,70)
        self.SetColSize(11,63)
        self.SetColSize(12,15)
        self.SetColSize(13,70)
        self.SetColSize(14,70)
        self.SetColSize(15,70)    
        
        self.SetCellValue(0,0,"Daily")
        self.SetCellValue(1,0,"Contract")
        self.SetCellValue(2,0,"Raw")
        self.SetCellValue(4,0,"Totals")
        self.SetCellValue(5,0,"Contract")
        self.SetCellValue(6,0,"Raw")
        
        self.SetColLabelAlignment(wx.ALIGN_LEFT,wx.ALIGN_BOTTOM)
        
        #test all events
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)
        
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelLeftDClick)
        
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)
        
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        
        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)
        
    def Update(self):
        p=self.portfolio
        
        self.SetCellValue(0,13,str(np.round((p.synthLongMidPnL),2)))
        self.SetCellValue(0,14,str(np.round((p.synthShortMidPnL),2)))
        self.SetCellValue(0,15,str(np.round((p.synthTotalMidPnL),2)))
        
        
        self.SetCellValue(1,1,str(np.round((p.m_exposure_MMBTU/p[3].HedgeSize),2)))
        self.SetCellValue(1,2,str(np.round((p.m_hedge_MMBTU/p[3].HedgeSize),2)))
        self.SetCellValue(1,3,str(np.round((p.m_net_MMBTU/p[3].HedgeSize),2)))
        self.SetCellValue(1,5,str(np.round((p.m_exposure_BS/p[1].HedgeSize),2)))
        self.SetCellValue(1,6,str(np.round((p.m_hedge_BS/p[1].HedgeSize),2)))
        self.SetCellValue(1,7,str(np.round((p.m_net_BS/p[1].HedgeSize),2)))
        self.SetCellValue(1,9,str(np.round((p.m_exposure_CAD/p[4].HedgeSize),2)))
        self.SetCellValue(1,10,str(np.round((p.m_hedge_CAD/p[4].HedgeSize),2)))
        self.SetCellValue(1,11,str(np.round((p.m_net_CAD/p[4].HedgeSize),2))) 
        
        self.SetCellValue(2,1,str(int(np.round(p.m_exposure_MMBTU,0))))
        self.SetCellValue(2,2,str(int(np.round(p.m_hedge_MMBTU,0))))
        self.SetCellValue(2,3,str(int(np.round((p.m_net_MMBTU),0))))
        self.SetCellValue(2,5,str(int(np.round(p.m_exposure_BS,0))))
        self.SetCellValue(2,6,str(int(np.round(p.m_hedge_BS,0))))
        self.SetCellValue(2,7,str(int(np.round((p.m_net_BS),0))))
        self.SetCellValue(2,9,str(int(np.round(p.m_exposure_CAD,0))))
        self.SetCellValue(2,10,str(int(np.round(p.m_hedge_CAD,0))))
        self.SetCellValue(2,11,str(int(np.round((p.m_net_CAD),0))))
        
        self.SetCellValue(5,1,str(np.round((p.t_exposure_MMBTU/p[3].HedgeSize),2)))
        self.SetCellValue(5,2,str(np.round((p.t_hedge_MMBTU/p[3].HedgeSize),2)))
        self.SetCellValue(5,3,str(np.round((p.t_net_MMBTU/p[3].HedgeSize),2)))
        self.SetCellValue(5,5,str(np.round((p.t_exposure_BS/p[1].HedgeSize),2)))
        self.SetCellValue(5,6,str(np.round((p.t_hedge_BS/p[1].HedgeSize),2)))
        self.SetCellValue(5,7,str(np.round((p.t_net_BS/p[1].HedgeSize),2)))
        self.SetCellValue(5,9,str(np.round((p.t_exposure_CAD/p[4].HedgeSize),2)))
        self.SetCellValue(5,10,str(np.round((p.t_hedge_CAD/p[4].HedgeSize),2)))
        self.SetCellValue(5,11,str(np.round((p.t_net_CAD/p[4].HedgeSize),2))) 
        
        self.SetCellValue(6,1,str(int(np.round(p.t_exposure_MMBTU,0))))
        self.SetCellValue(6,2,str(int(np.round(p.t_hedge_MMBTU,0))))
        self.SetCellValue(6,3,str(int(np.round((p.t_net_MMBTU),0))))
        self.SetCellValue(6,5,str(int(np.round(p.t_exposure_BS,0))))
        self.SetCellValue(6,6,str(int(np.round(p.t_hedge_BS,0))))
        self.SetCellValue(6,7,str(int(np.round((p.t_net_BS),0))))
        self.SetCellValue(6,9,str(int(np.round(p.t_exposure_CAD,0))))
        self.SetCellValue(6,10,str(int(np.round(p.t_hedge_CAD,0))))
        self.SetCellValue(6,11,str(int(np.round((p.t_net_CAD),0))))                   


class CustomStatusBar(wx.StatusBar):
    def __init__(self,parent):
        wx.StatusBar.__init__(self,parent)
        
        self.SetFieldsCount(8)
        # Sets the three fields to be relative widths to each other.
        
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        self.statusWidgets=[]
        self.statusTime=wx.StaticText(self,ID_TIME,time.strftime("%H:%M:%S"))
        self.statusWidgets.append(self.statusTime)
        self.statusLogTime=wx.StaticText(self,ID_TIMEARCDATA,"")    #time.strftime("%H:%M:%S",cfg.TIME_ARC_DATA))
        self.statusWidgets.append(self.statusLogTime)
        self.linesArcData =wx.StaticText(self,ID_LINESARCDATA,str(cfg.LINES_ARC_DATA))
        self.statusWidgets.append(self.linesArcData)
        self.statusIsLive=wx.StaticText(self,ID_ISLIVE,"isLive")
        self.statusWidgets.append(self.statusIsLive)
        self.statusMailer=wx.StaticText(self,ID_MAILER,"MAILER")
        self.statusWidgets.append(self.statusMailer)
        self.statusTtPricing=wx.StaticText(self,ID_TTMD,"TT MD")
        self.statusWidgets.append(self.statusTtPricing)
        self.statusArcLog=wx.StaticText(self,ID_ARCMD,"ARC MD")
        self.statusWidgets.append(self.statusArcLog) 
        
        self.Reposition()
        
    def Reposition(self):
        self.Update()
        self.SetStatusWidths([-5,-2,-2,-2, -3, -3,-3,-3])
        
        if cfg.IS_LIVE: 
            self.statusIsLive.SetBackgroundColour('green')
            self.statusIsLive.SetLabel("LIVE")
        else: 
            self.statusIsLive.SetBackgroundColour('#FFC125')
            self.statusIsLive.SetLabel("TESTING")
                
        for i in range(0,len(self.statusWidgets)):
            rect = self.GetFieldRect(1+i)
            self.statusWidgets[i].SetPosition((rect.x+2, rect.y+2))
            self.statusWidgets[i].SetSize((rect.width-4, rect.height-4))
                
        self.sizeChanged = False
        
    def OnSize(self, evt):
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()   
            
    def Update(self):
        
        self.linesArcData.SetLabel(str(cfg.LINES_ARC_DATA))
        self.statusLogTime.SetLabel(time.strftime("%H:%M:%S",cfg.TIME_ARC_DATA))
        
        if cfg.IS_EMAIL_ENABLED: self.statusMailer.SetBackgroundColour('green')
        else: self.statusMailer.SetBackgroundColour('red')
        
        if cfg.DATA_CONNECTIONS.__contains__(12001):self.statusTtPricing.SetBackgroundColour('green')
        else: self.statusTtPricing.SetBackgroundColour('red')
        if cfg.DATA_CONNECTIONS.__contains__(12102):self.statusArcLog.SetBackgroundColour('green')
        elif cfg.DATA_CONNECTIONS.__contains__(12105):self.statusArcLog.SetBackgroundColour('#FFC125')
        else: self.statusArcLog.SetBackgroundColour('red')
                
        self.statusTime.SetLabel(time.strftime("%H:%M:%S"))
        self.Refresh()
        
            
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,title="P6 Proving Ground",size=(1230,425))
        
        self.guiLoop=None
        
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        filemenu=wx.Menu()        
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT,"&About"," Info about this program") 
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")        
        
        reportmenu=wx.Menu()
        menuEmailOn = reportmenu.Append(ID_EMAILON,"&Enable Email","Enable Email Reporting")
        menuEmailOff = reportmenu.Append(ID_EMAILOFF,"&Disable Email","Disable Email Reporting")
        menuEmailReady = reportmenu.Append(ID_EMAILREADY,"&Send Email Now","Force Send New Report")
        reportmenu.AppendSeparator()
        menuShowAddr = reportmenu.Append(ID_ADDRBOOK,"Show Active &Address Book","Display Email Recipient List")
        
        datamenu=wx.Menu()
        menuReconnectTtData=datamenu.Append(ID_GETTTDATA,"Reconnect &TT Data","Reconnect to TT Price Server")
        menuReconnectArcLogData=datamenu.Append(ID_GETARCLOGDATA,"Reconnect &Arc Log","Reconnect to ARC Log")
        datamenu.AppendSeparator()
        menuReloadData=datamenu.Append(ID_RELOADDATA,"&Reload Today's Fills","Reload TT and Manual Fills from File")
        menuLoadOvernight=datamenu.Append(ID_LOADOVERNIGHT,"&Load Overnight Positions","Load Positions Carried Overnight")
        
        menuBar=wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        menuBar.Append(reportmenu,"&Reporting")
        menuBar.Append(datamenu,"&Data")
        self.SetMenuBar(menuBar)    #add the MenuBar to the frame content
        self.sb=CustomStatusBar(self)
        self.SetStatusBar(self.sb)
        
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.DoExit, menuExit)
        
        self.Bind(wx.EVT_MENU, self.OnEmailEnabled, menuEmailOn)
        self.Bind(wx.EVT_MENU, self.OnEmailDisabled, menuEmailOff)
        self.Bind(wx.EVT_MENU, self.OnEmailReady, menuEmailReady)
        self.Bind(wx.EVT_MENU, self.OnShowAddr, menuShowAddr)
        
        self.Bind(wx.EVT_MENU, self.OnReconnectTt, menuReconnectTtData)
        self.Bind(wx.EVT_MENU, self.OnReconnectArcLog, menuReconnectArcLogData)
        self.Bind(wx.EVT_MENU, self.OnReloadData, menuReloadData)
        self.Bind(wx.EVT_MENU, self.OnLoadOvernight, menuLoadOvernight)
        
        wx.EVT_MENU(self, ID_EXIT,  self.DoExit)
        wx.EVT_MENU(self, ID_EMAILON,  self.OnEmailEnabled)
        wx.EVT_MENU(self, ID_EMAILOFF,  self.OnEmailDisabled)
        wx.EVT_MENU(self, ID_EMAILREADY,  self.OnEmailReady)
        wx.EVT_MENU(self, ID_ADDRBOOK,  self.OnShowAddr)
        wx.EVT_MENU(self, ID_GETTTDATA,  self.OnReconnectTt)
        wx.EVT_MENU(self, ID_GETARCLOGDATA,  self.OnReconnectArcLog)
        wx.EVT_MENU(self, ID_RELOADDATA,  self.OnReloadData)
        wx.EVT_MENU(self, ID_LOADOVERNIGHT,  self.OnLoadOvernight)
        
        #create panel and notebook on the panel
        p = wx.Panel(self)
        self.nb = wx.Notebook(p)
        #self.sb = StateBar(p)
        
        #create page windows as children of notebook
        self.pages=[]
        #self.pages.append(StatusPanel(self.nb))
        self.pages.append(SummaryGrid(self.nb))
        self.pages.append(ManualOrderPanel(self.nb))
        self.pages.append(ReportingPanel(self.nb))
        self.pages.append(SynthGrid(self.nb,cfg.BOOK.ngxPrompt))
        for n in cfg.BOOK.All:
            self.pages.append(PortfolioGrid(self.nb,n))          
        
        #add pages to notebook
        self.nb.AddPage(self.pages[0],"Sum")
        self.nb.AddPage(self.pages[1],"OrderEntry")
        self.nb.AddPage(self.pages[2],"Reporting")
        self.nb.AddPage(self.pages[3],"Synth")
        i=self.nb.GetPageCount()
        for n in cfg.BOOK.All:
            self.nb.AddPage(self.pages[i],n.Name)
            i+=1
            
        #put notebook in sizer for panel to manage
        sizer = wx.BoxSizer()
        sizer.Add(self.nb,1,wx.EXPAND)
        p.SetSizer(sizer)
        
        self.guiLoop=LoopingCall(self.OnGuiUpdate)
        self.guiLoop.start(cfg.INTERVAL_UPDATE_GUI)
                
        # make sure reactor.stop() is used to stop event loop:
        wx.EVT_CLOSE(self, lambda evt: reactor.stop())

    def OnReconnectTt(self,event):
        data.reconnect_data(reactor, 12001)

    def OnReconnectArcLog(self, event):
        cfg.LINES_ARC_DATA=0
        cfg.TIME_ARC_DATA=time.localtime()
        if cfg.IS_LIVE: data.reconnect_data(reactor, 12102)
        else: data.reconnect_data(reactor, 12105)

    def OnReloadData(self, event):
        cfg.IS_RELOAD_DATA_TRIGGER=True
        
    def OnLoadOvernight(self, event):
        today = time.strftime("%Y%m%d")
        best = "OvernightPos_19000101.txt"
        dir = cfg.PATH_POSITIONS_OVERNIGHT
        for f in os.listdir(dir):
            if (f[-12:-4]<today) and (f[-12:-4]>best[-12:-4]):
                best = f
                #print "%s %s" % (f[-12:-4], best[-12:-4])
        
        pathname = os.path.join(dir,best)
        #print pathname
        cfg.BOOK.LoadOvernight(pathname)
        

    def OnEmailEnabled(self, event):
        cfg.IS_READY_TO_EMAIL=False
        cfg.IS_EMAIL_ENABLED=True
        
    def OnEmailDisabled(self,event):
        cfg.IS_READY_TO_EMAIL=False        
        cfg.IS_EMAIL_ENABLED=False
    
    def OnEmailReady(self,event):
        cfg.IS_READY_TO_EMAIL=True

    def OnShowAddr(self,event):
        dlg = wx.MessageDialog(self,"%s" % cfg.ADDRESS_BOOK, "Report Recipients", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def DoExit(self, event):
        reactor.stop()
    
    def OnGuiUpdate(self):
        for page in self.pages:
            page.Update()
        self.sb.Update()
                
    def OnAbout(self,e):
        #message dialog box with ok button
        dlg = wx.MessageDialog(self,"Intraday Trading Operations Panel", "About P6", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

class Startup(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self,None,title="Log In to Arcadium Position Database",size=(500,500))
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.fieldLabels = [] 
        self.fieldLabels.append(wx.StaticText(self,label="DB User:"))
        self.fieldLabels.append(wx.StaticText(self,label="DB Pass:"))
        self.fieldLabels.append(wx.StaticText(self,label="Production:"))
        
         
        for i in range(0,len(self.fieldLabels)):
            grid.Add(self.fieldLabels[i],pos=(i,0))
         
        self.tc1 = wx.TextCtrl(self, size=(180,-1))
        self.tc2 = wx.TextCtrl(self, size=(180,-1), style=wx.TE_PASSWORD)
        self.isLive = wx.CheckBox(self, label='PRODUCTION REPORTING')
        
        self.btnConnect=wx.Button(self,label="Connect",id=wx.ID_OK)
        self.btnCancel=wx.Button(self,label="Cancel",id=wx.ID_CANCEL)
        
        self.Bind(wx.EVT_BUTTON, self.OnConnectArcSql, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        grid.Add(self.tc1,pos=(0,1))
        grid.Add(self.tc2,pos=(1,1))
        grid.Add(self.isLive,pos=(2,1))
        self.isLive.Value = cfg.IS_LIVE
        self.isLive.Disable()
                 
        grid.Add(self.btnConnect,pos=(0,3))
        grid.Add(self.btnCancel,pos=(1,3))
        
        hSizer.Add(grid,0,wx.ALL,5)
        vSizer.Add(hSizer,0,wx.ALL,5)
        #mainSizer.Add(self.button
        self.SetSizerAndFit(vSizer)
        
    def OnConnectArcSql(self,e):
        try:
            #cfg.IS_LIVE=self.isLive.GetValue()
            #cfg.setParams()
            self.btnConnect.Disable()
            self.btnCancel.Disable()
            
            today = time.strftime("%Y-%m-%d")
            #today = '2012-01-12'
            SqlEngine=ArcSql.SqlEngine(self.tc1.Value,self.tc2.Value)
            ArcSqlLoop=LoopingCall(SqlEngine.set_call,today)
            ArcSqlLoop.start(cfg.INTERVAL_UPDATE_SQL)
            
        except Exception as ex:
            self.ShowError(str(ex))
            cfg.IS_QUITTING_TIME=True
        self.Destroy()
        
    def OnCancel(self,e):
        cfg.IS_QUITTING_TIME=True
        self.Destroy()
        
    def OnExit(self,e):
        self.OnCancel(e)
        
    def ShowError(self,ex):
        dlg = wx.MessageDialog(None, ex, 'Login Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()

class MainApp(wx.App):
    #ArcSqlLoop=None
    rptLoop=None

    def OnInit(self):
        self.getParams()        
        namePath=cfg.PATH_SYS_LOG+time.strftime("%Y%m%d")
        i = 0
        for infile in glob.glob(namePath+'*'): 
            if int(infile.split('.')[-2]) > i : i = int(infile.split('.')[-2])     
        logName='%s.%0d.log' % (namePath,(int(i)+1))
        log.startLogging(open(logName,'w'))
        
        Startup().ShowModal()
        frame = MainFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        # look, we can use twisted calls!
        data.start_data(reactor)
        fills.FilesysWatcher()
        rpt=report.Reporting()
        rptLoop=LoopingCall(rpt.check_status)
        rptLoop.start(cfg.INTERVAL_UPDATE_EMAIL)
        
        return True

    def getParams(self):
        getLive=wx.MessageDialog(None,'Start In Production Mode?','Mode Selection',
                          wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
        isGetLive=getLive.ShowModal()
        if isGetLive==wx.ID_YES: cfg.IS_LIVE=True
        else: cfg.IS_LIVE=False
        #cfg.IS_LIVE=getLive
        self.setParams()
        #print cfg.IS_LIVE
        #print cfg.PATH_SYS_LOG
        #print cfg.ADDRESS_BOOK
        
    def setParams(self):
        if cfg.IS_LIVE:
            cfg.PATH_REPORT.append("M:\\Reporting\\Trade Reporting\\P6\\DealReports\\ManEntry\\")
            cfg.PATH_REPORT.append("M:\\Reporting\\Trade Reporting\\P6\\DealReports\\TT\\")
            cfg.PATH_POSITIONS_OVERNIGHT=("M:\\Reporting\\Trade Reporting\\P6\\DealReports\\OnPositions\\")
            cfg.PATH_PORTFOLIO_LIST= "M:\\Reporting\\Trade Reporting\\P6\\Cfg\\portfolioList.csv"
            cfg.PATH_CURRENCY_LIST= "M:\\Reporting\\Trade Reporting\\P6\\Cfg\\currList.txt"
            cfg.PATH_SYS_LOG="C:\\TradingSystems\\P6\\logs\\"
            cfg.ADDRESS_BOOK = []
            cfg.INTERVAL_UPDATE_POS=1
            cfg.INTERVAL_UPDATE_SQL=1
            cfg.INTERVAL_UPDATE_GUI=1
            cfg.INTERVAL_UPDATE_EMAIL=60
        else:
            cfg.PATH_REPORT.append("M:\\Reporting\\Trade Reporting\\P6\\DealReports\\Testing\\ManEntry\\")
            cfg.PATH_REPORT.append("M:\\Reporting\\Trade Reporting\\P6\\DealReports\\Testing\\TT\\")    
            cfg.PATH_POSITIONS_OVERNIGHT=("M:\\Reporting\\Trade Reporting\\P6\\DealReports\\Testing\\OnPositions\\")
            cfg.PATH_PORTFOLIO_LIST= "M:\\Reporting\\Trade Reporting\\P6\\Cfg\\portfolioList.csv"
            cfg.PATH_CURRENCY_LIST= "M:\\Reporting\\Trade Reporting\\P6\\Cfg\\currList.txt"
            cfg.PATH_SYS_LOG="C:\\TradingSystems\\P6\\Testing\\logs\\"
            cfg.ADDRESS_BOOK= []
            cfg.INTERVAL_UPDATE_POS=2
            cfg.INTERVAL_UPDATE_SQL=2
            cfg.INTERVAL_UPDATE_GUI=1
            cfg.INTERVAL_UPDATE_EMAIL=3
        
        cfg.BOOK = core.PortfolioAll(cfg.PATH_PORTFOLIO_LIST)
        cfg.CURRENCY=core.currDict(cfg.PATH_CURRENCY_LIST)
        

if __name__ == '__main__':
    #import cfg, core
    import glob, os
    #from twisted.enterprise import adbapi

    # register the App instance with Twisted:
    app = MainApp(0)
    reactor.registerWxApp(app)
        
    # start the event loop:
    if not cfg.IS_QUITTING_TIME:
        reactor.run()
    
    
