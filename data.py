'''
Created on Nov 18, 2011

@author: JSU
pylint score 8.37/10 as of 18 Jan 2012
'''

import cfg
import datetime, time
import numpy as np
from twisted.internet.protocol import Protocol, ClientFactory

SOURCE_LIST = []
CONNECTED_LIST = []
class DataProtocol(Protocol):
    '''manages data received from connections'''
    log = ''
    
    task_num = 0
    timeStart = 0
    timeElapsed = 0
    count = 0

    def dataReceived(self, data):
        '''native protocol method for receiving data
        does not meet pylint name spec, exclude'''
        try:
            process_data(data)
        except:
            return
                            
    def connectionLost(self, reason):
        '''called when connection to port is lost
        overrides original protocol method
        does not meet pylint spec for name, exclude'''
        lines = 0
        for line in self.log:
            lines += 1
        self.count = lines
        print '%.0f found in %s' % (self.count, self.timeElapsed)
        self.data_finished(self.log)

    def data_finished(self, log):
        '''callback to finish data processing after connection termination'''
        self.factory.data_finished(self.task_num, log)
        
def book_trade_log(trade_line):
    '''add trade from ARC log to portfolio book'''
    print trade_line
    product = cfg.NAMES_ARC.get_value(trade_line[2])
    if product == '': 
        product = trade_line[2]
    contract = (cfg.MONTH_NAME[int(trade_line[3][4:6])]     #month
                + trade_line[3][2:4])                       #year
    side = trade_line[8]
    qty = int(float(trade_line[10]))
    price = float(trade_line[9])     
    trade_id = trade_line[0]
    trader = "ciffx"
    method = "ARC"
    fee = 0
    #if fee == '': fee = 0 
    fill_time =  trade_line[12]       

    for portfolio in cfg.BOOK.All:
        inst = None
        for port_inst in portfolio:
            if port_inst.GetProduct() == product and port_inst.GetContract() == contract: 
                inst = port_inst
        if inst == None: continue
        is_last = True
        inst.AddTrade(trade_id, side, qty, price, 
                      fill_time, trader, method, is_last, fee)
        
def process_data(data):
    '''callback for processing received data'''
    if len(data) < 2:
        return
    elif data[-1] == '`':   #TT data
        process_tt_data(data)
    else:                   #if data[-1] == '\n':  #ARC data
        process_arc_data(data)
        
def process_tt_data(data):
    '''split market data from TT'''
    #print "TT data: %s" % data
    lines = data.split('`')
    for line in lines:
        mkt_data = line.split(';')
        prod = cfg.NAMES_TT.get_value(mkt_data[0])
        if prod != '':
            update_marketdata_tt(mkt_data, prod)

def process_arc_data(data):
    '''split market data from ARC logs'''
    lines = data.split('~')
    for line in lines:
        try:
            cfg.LINES_ARC_DATA += 1
            mkt_data = line.split(";")
            timestamp = time.localtime(float(mkt_data[1]))
            cfg.TIME_ARC_DATA = timestamp               
            if mkt_data[0] == 'bsMid':
                update_basis_midpoint(mkt_data)
            elif mkt_data[0] == 'chnged':
                update_marketdata_arc(mkt_data, timestamp)
        except:
            return
        
def update_marketdata_tt(mkt_data, prod):
    '''parse and send market data from TT'''
    contract = mkt_data[1]
    currency_product = cfg.NAMES_CURRENCY.get_key(prod)
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    
    try: 
        last = float(mkt_data[2])
    except: 
        last = np.nan
    
    try: 
        bid = float(mkt_data[3])
    except: 
        bid = np.nan
    
    try: 
        ask = float(mkt_data[4])
    except: 
        ask = np.nan
    
    #if currency_product in cfg.CURRENCY: 
    #   if cfg.CURRENCY[currency_product].contract == cont: 
        #cfg.CURRENCY[currency_product].setRate(float(mkt_data[2]))
    for portfolio in cfg.BOOK.All:
        for i in portfolio:
            try:
                if i.GetProduct() == prod and i.GetContract() == contract : 
                    #i.Last=float(mkt_data[2])
                    i.UpdateMarket(bid, ask, last, "TT")
                    if cfg.IS_LIVE: 
                        print "%s %s-%s %s: %f; %f; %f" % (
                            timestamp, "TT", prod, contract, bid, ask, last)
            except Exception as ex:
                print ex                                
                #print "Unknown market data: %s" % mkt_data[2]

def update_marketdata_arc(mkt_data, timestamp):
    '''parse and send market data from ARC'''
    prod = cfg.NAMES_ARC.get_value(mkt_data[3])
    if prod != '':  
        contract = str(cfg.MONTH_NAME[int(str(mkt_data[4])[4:6])]
                     + str(mkt_data[4])[2:4])
        last = np.nan
        try: 
            bid = float(mkt_data[6]) * cfg.NORMALIZE_ARC.get(prod, 1)        
            #default to 1 if no normalization value
        except: 
            bid = np.nan
        try: 
            ask = float(mkt_data[8]) * cfg.NORMALIZE_ARC.get(prod, 1)        
            #default to 1 if no normalization value
        except: 
            ask = np.nan
        #for portfolio in cfg.BOOK.All:
        for i in cfg.BOOK.ngxPrompt:
            try:
                if i.GetProduct() == prod and i.GetContract() == contract: 
                    i.UpdateMarket(bid, ask, last, "ARC", timestamp)
                    if cfg.IS_LIVE: 
                        print "%s %s-%s %s: %f; %f; %f" % (
                            time.strftime("%H:%M:%S",timestamp), "ARC", prod, 
                            contract, bid, ask, last)  
            except Exception as ex:
                print ex
        
def update_basis_midpoint(mkt_data):
    '''special case to update basis market midpoint 
    to allow pricing of basis position in synthetic calc'''
    prod = cfg.NAMES_ARC.get_value(mkt_data[4])
    contract = str(cfg.MONTH_NAME[int(str(mkt_data[4])[4:6])] 
                   + str(mkt_data[4])[2:4])
    if prod != '':
        last = (((float(mkt_data[10]) + float(mkt_data[11])) / 2) * 
            cfg.NORMALIZE_ARC.get(prod,1))
        for i in cfg.BOOK.ngxPrompt:
            try:
                if i.GetProduct()==prod and i.GetContract()==contract: 
                    i.UpdateLast(last)
            except Exception as ex:
                print ex

class DataClientFactory(ClientFactory):
    '''client factory to manage connections and listen for data'''

    task_num = 1
    #print "test"

    protocol = DataProtocol # tell base class what proto to build

    def __init__(self, source_count, reactr):
        self.source_count = source_count
        self.sources = {} # task num -> poem
        self.reactr = reactr

    def buildProtocol(self, address):
        '''set up connection protocol
        override method from ClientFactory.buildProtocol
        does not meet pylint spec for name, exclude'''
        #if address not in SOURCE_LIST: SOURCE_LIST.append(address)
        #if address not in CONNECTED_LIST: CONNECTED_LIST.append(address)
        proto = ClientFactory.buildProtocol(self, address)
        proto.task_num = self.task_num
        self.task_num += 1
        return proto

    def data_finished(self, task_num=None, log=None):
        '''clean up connections after connection closed, data finished'''
        if task_num is not None:
            self.sources[task_num] = log

        self.source_count -= 1

        if self.source_count == 0:
            self.report()
            #from twisted.internet import reactor
            #reactor.stop()

    def report(self):
        '''report connection status'''
        for i in self.sources:
            print 'Task %d: %d bytes of log' % (i, len(self.sources[i]))
            print 'No data connections'

    def attempt_reconnect(self):
        '''force reconnect attempts'''
        for source in SOURCE_LIST not in CONNECTED_LIST:
            self.buildProtocol(source)   

    def clientConnectionLost(self, connector, reason):
        '''required method for Twisted data factory
        handles lost connections
        does not meet pylint spec for name, exclude'''
        dest = connector.getDestination()
        print 'Lost connection to %s, %s' % (dest, reason)
        #CONNECTED_LIST.remove(dest)
        cfg.DATA_CONNECTIONS.remove(dest.port)

    def clientConnectionFailed(self, connector, reason):    
        '''required method for Twisted data factory
        handles failed connection attempts
        does not meet pylint spec for name, exclude'''
        dest = connector.getDestination()
        print 'Failed to connect to %s, %s' % (dest, reason)
        #CONNECTED_LIST.remove(dest)
        cfg.DATA_CONNECTIONS.remove(dest.port)        
        self.data_finished()



def start_data(reactr):
    '''set up connection params and start factory    
    #port 12001 : TT price server
    #port 12102 : nimitz log price server
    #port 12003 : not in use
    #port 12105 : nimitz log price server testing
    '''
    if cfg.IS_LIVE:
        addresses = (12001, 12102)#,12003)
    else: 
        addresses = (12001, 12105)#,12003)

    
    factory = DataClientFactory(len(addresses), reactr)

    host = 'localhost'
    for address in addresses:
        port = address
        reactr.connectTCP(host, port, factory)
        cfg.DATA_CONNECTIONS.append(address)
        
def reconnect_data(reactr, address):
    '''attempt to restart connections    
    called from main.py to restart connections
    '''
    factory = DataClientFactory(1, reactr)

    host = 'localhost'

    port = address
    reactr.connectTCP(host, port, factory)
    cfg.DATA_CONNECTIONS.append(address)


if __name__ == '__main__':    
    from twisted.internet import reactor
    
    START = datetime.datetime.now()
    start_data(reactor)
    
    reactor.run()

    ELAPSED = datetime.datetime.now() - START
    #print 'Data attempted to %d servers for %s' % (len(addresses), elapsed)
