'''
Created on Nov 21, 2011

@author: JSU
pylint score 9.13/10 as of 18 Jan 2012
'''
import cfg, sys
import os, time
from twisted.internet.protocol import Factory
from twisted.internet.task import LoopingCall



class FilesysWatcher():
    '''watches file system for changes (new trades) and updates portfolios'''
    loop = None
    directoryState = {}
    
    def __init__(self):
        print 'protocol initialized'
        for file_path in cfg.PATH_REPORT:
            self.directoryState[file_path] = [f for f in os.listdir(file_path)]
        print 'Initial directory set'
        self.loop = LoopingCall(follow_dir, self)
        self.loop.start(cfg.INTERVAL_UPDATE_POS)        
        
def parse_file(filename):
    '''open file, split lines, call trade parser'''
    for line in file(filename, 'rb'):
        trade_line = line.split(',')
        if trade_line[0] == 'Row Number':
            continue
        parse_trade_file(trade_line)
                
def parse_trade_file(trade_line):
    '''parse trade, call function to add to portfolio'''
    print trade_line
    
    contract_desc = trade_line[9]
    if len(contract_desc) > 6:
        try:
            month1 = trade_line[9][0:3]
            month2 = trade_line[9][6:9]
            month1ind = cfg.MONTH_NAME.index(month1)
            month2ind = cfg.MONTH_NAME.index(month2)
            month = cfg.MONTH_CODE[month1ind] + cfg.MONTH_CODE[month2ind]
        except:
            print "TT Trade parse error: ", sys.exc_info()[0]
            return 
    else: month = trade_line[9][0:3]  
    
    year = trade_line[9][3:5]
    
    #TODO: add method to assign contracts owned by more than one portfolio
    
    if cfg.MONTH_NAME.index(month) > 12:        #strip contract
        bullets = cfg.STRIP_MAP[month]            
        for bullet in bullets: 
            contract = cfg.MONTH_NAME[bullet] + year
            book_trade(trade_line, contract)
    else:
        contract = month + year
        book_trade(trade_line, contract)
          
def book_trade(trade_line, contract):
    '''assign trade to portfolio book'''
    product = cfg.NAMES_TT.get_value(trade_line[8])
    if product == '': 
        product = trade_line[8]
    
    side = trade_line[2]
    qty = int(float(trade_line[3]))
    price = float(trade_line[5])     
    trade_id = trade_line[43]
    trader = trade_line[13]
    method = "TT"
    fee = trade_line[35]
    if fee == '': 
        fee = 0 
    fill_time =  trade_line[16]
    
    for portfolio in cfg.BOOK.All:
        inst = None
        for port_inst in portfolio:
            if port_inst.GetProduct() == product and port_inst.GetContract() == contract: 
                inst = port_inst
        if inst == None: 
            continue
        is_last = True
        inst.AddTrade(trade_id, side, qty, price, fill_time,
                      trader, method, is_last, fee)
        print "%s %s %s %s %s %s %s %s %s" % (
                  trade_id, side, qty, price, fill_time, 
                  trader, method, is_last, fee)   
        
            
def follow_dir(fsw):
    '''watch directory for new trade files'''
    if cfg.IS_RELOAD_DATA_TRIGGER: 
        reload_day()
    state = {}
    before = fsw.directoryState
    for filepath in cfg.PATH_REPORT:
        state[filepath] = [f for f in os.listdir(filepath)]
        added = [f for f in state[filepath] if not f in before[filepath]]
        removed = [f for f in before[filepath] if not f in state[filepath]]
        for filename in added:
            file_string = filepath + filename
            parse_file(file_string)
            print "added %s" % filename
        for filename in removed:
            print "removed %s" % filename
    fsw.directoryState = state
    
def reload_day():
    '''search directory for today's fills and reload into portfolio'''
    cfg.IS_RELOAD_DATA_TRIGGER = False
    for filepath in cfg.PATH_REPORT:
        for filename in os.listdir(filepath):
            file_string = os.path.join(filepath, filename)    
            modified_time = time.localtime(os.path.getmtime(file_string))
            now = time.localtime()            
            if modified_time[0:3] == now[0:3]: 
                parse_file(file_string)
                print "added %s" % filename
     
class FillsFactory(Factory):
    '''factory to start and manage FilesysWatcher
    used only in standalone/debug mode    
    '''
    #protocol = FswProtocol
    
    def __init__(self):
        print 'factory initialized'
        #fsw = FilesysWatcher()
        FilesysWatcher()

def start_fills():
    '''start reactor to watch for fills
    used only in standalone/debug mode'''
    #reactor = reactr
    #factory = FillsFactory()
    FillsFactory()
    
if __name__ == '__main__':    
    from twisted.internet import reactor
    #from twisted.internet.task import LoopingCall
    
    #factory=FswFactory()
    
    start_fills()
    
    reactor.run()

    
