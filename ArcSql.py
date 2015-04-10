'''
Created on Nov 23, 2011

@author: JSU
pylint score 8.33/10 as of 17 Jan 2012
'''
import cfg
from twisted.enterprise import adbapi

class SqlEngine():
    '''establishes and maintains database connection
    requests and processes trade data'''
    
    pos_before = None
    def __init__(self, usr, pwd):           #,dbPool):
        self.pos_before = []
        self.dbpool = adbapi.ConnectionPool("MySQLdb",
                                   host = 'localhost',
                                   user = usr,
                                   passwd = pwd,
                                   db = 'falcon')
        
    def get_trades(self, fill_date):
        '''send query requesting today's trades'''
        return self.dbpool.runQuery(
                "SELECT * FROM `falcon`.`fills_orders` WHERE fill_date = '%s' " % fill_date)
    
    def get_historical(self, fill_date):
        '''send query requesting trades from any previous day'''
        return self.dbpool.runQuery(
                "SELECT * FROM `falcon`.`fills_orders_all` WHERE fill_date = '%s' " % fill_date)
    
    def process_today(self, result):
        '''process today's trades from self.get_trades'''
        if result: 
            if result != self.pos_before:
                after = [f for f in result if not f in self.pos_before]
                if after: 
                    for row in after: 
                        book_trade_arcsql(row)
                self.pos_before = result
            #else: print "Nothing new"
        #else: print "No trades found"
            
    def set_call(self, fill_date):
        '''set callback for self.get_trades'''
        self.get_trades(fill_date).addCallback(self.process_today)        
    
def book_trade_arcsql(trade_line):
    '''book trade from SQL database into portfolio'''
    #unkTrade = True
    fill_time =  trade_line[1]
    trade_id = trade_line[1]
    qty = int(trade_line[2])
    method = trade_line[7]       
    month = int(float(str(trade_line[12])[4:6]))  
    year = str(trade_line[12])[2:4]
    product = cfg.NAMES_ARC.get_value(trade_line[11])
    contract = str(cfg.MONTH_NAME[month]) + year
    price = trade_line[4] * cfg.NORMALIZE_ARC.get(product, 1)
    side = trade_line[15]        
    trader = 'cif-fx'
    fee = 0

    port = cfg.BOOK.ngxPrompt
    inst = None
    for i in port:
        if i.GetProduct() == product and i.GetContract() == contract: inst = i
    if inst == None: return
    is_last = True
    
    inst.AddTrade(trade_id, side, qty, price, fill_time, 
                  trader, method, is_last, fee)
    print "%s %s %s %s %s %s %s %s %s" % (
            trade_id, side, qty, price, fill_time, trader, method, is_last, fee)
    #unkTrade = False

   
def check_main():
    '''prints 'awake' if module is being run locally'''
    print "awake..."

if __name__ == '__main__':    
    import getpass, time

    from twisted.internet import reactor    
    from twisted.internet.task import LoopingCall
    
    USR = getpass.getpass()
    PWD = getpass.getpass()
    
    SQL_ENGINE = SqlEngine(USR, PWD)
    FILL_DATE = time.strftime("%Y-%m-%d")
    #fillDate = '2011-11-22'

    LOOP = LoopingCall(SQL_ENGINE.set_call, FILL_DATE)
    
    LOOP.start(2)
    MAINLOOP = LoopingCall(check_main)
    MAINLOOP.start(1)
    
    reactor.run()
