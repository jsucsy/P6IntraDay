'''
Created on Jan 6, 2012

@author: JSU
read trading log file and serve to front end client
'''
import os, sys, time, datetime, re
from twisted.internet.protocol import ServerFactory, Protocol
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

class LogProtocol(Protocol):
    #loop=None
    #def __init__(self):
    
    def connectionMade(self):
        time.sleep(2)
        self.loop = LoopingCall(follow, open(self.factory.log), self._sendLogLine)
        delay = float(self.factory.delay)
        print "Connected:  %s" % time.strftime("%H:%M:%S")
        if delay > 0: self.loop.start(delay)
        else:self.loop.start(0)
        #for line in self.follow():
        #   self.transport.write(line)
        #self.transport.loseConnection()

    def _sendLogLine(self, line):
        
        self.transport.write("%s" % line)

    def connectionLost(self, reason):
        self.loop.stop()

def follow(fObj, gotLine):
    line = fObj.readline()
    try: 
        bsMid =re.search(msgBsMid, line)
        chnged =re.search(msgBookChanged, line)   
        if bsMid:
            lineOut = "bsMid;%s~" % ";".join(bsMid.groups())
            gotLine(lineOut)
        if chnged:
            lineOut = "chnged;%s~" % ";".join(chnged.groups())
            gotLine(lineOut)     
    except:
        return
    
    #gotLine(line)
    #if re.search(msgBookShort, line):
    #   gotLine(line)
    #elif re.search(msgFill, line):
    #   gotLine(line)

    #if line:
    #   gotLine(line)
    #testDiff
        
msgBookChanged = re.compile(r'''
        ^                     #start at the beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        (onBookChanged):      #msgType, any number of alphanumeric & :
        \s                    #space
        (?:\w+:)?             #optional contract type to accomodate ARC change 2011/08/12
        (\w+):                #contract, any number alphanum
        (\d{6})               #expiry, 6 digits
        (\[\d,\-?\d+\])?      #optional array-type reference for strategy and contract relationship, '[' & 1 digit & ',' & opt '-' & 1 or more digits & ']'   
        \s                    #space
        \*?
        b=(-?\d+.\d+)           #bid
        x(\d+)                #bid qty
        \s
        \*?
        a=(-?\d+.\d+)            #ask
        x(\d+)                 #ask qty
        \s
        otim=(\d{10}.\d{6})    #otim timestamp
        \s
        btim=(\d{10}.\d{6})    #lotim timestamp
        ''', re.VERBOSE)

msgBsMid = re.compile(r'''
        ^                     #start at the beginning
        (?P<timestamp>\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        (?P<msgType>showQtys):             #msgType, any number of alphanumeric & :
        \s                    #space                
        \((\d+)\)\s                #synth number
        \*--\s
        (?:\w+:)?                  #optional contract type to accomodate ARC change 2011/08/12
        (?P<contract>ICE_NGX_BS_LD1_US_AB_NIT):                #contract, any number alphanum
        (?P<expiry>\d{6})               #expiry, 6 digits
        (?P<relRef>\[\d,\-?\d+\])\s      #optional array-type reference for strategy and contract relationship, '[' & 1 digit & ',' & opt '-' & 1 or more digits & ']'        
        ->\s
        opnQty=(?P<opnQty>\-?\d+)\s        #open quantity
        exeQty=(?P<exeQty>\-?\d+)\s        #executed quantity
        toOpnQty=(?P<toOpnQty>\-?\d+)\s--\s    #to open quantity
        db=(?P<db>\-?\d+.\d+)\s            #dBid
        da=(?P<da>\-?\d+.\d+)                #dAsk        
        ''', re.VERBOSE)

class LogFactory(ServerFactory):
    protocol = LogProtocol
    
    def __init__(self,log,delay):
        self.log = log
        self.delay = delay

def spin(inputLog, port=12102, delay=0):
    factory = LogFactory(inputLog, delay)
   
   
    listen  = reactor.listenTCP(port, factory)   
    print "serving %s on %s" %(inputLog, listen.getHost())
   
    reactor.run()   

if __name__ == '__main__':
    today = datetime.date.today()
    logName = "C:\TradingSystems\Enterprise_3_0\TailedLogs\log%s.txt" % today
    #spin(logName,12105)
    spin(logName)


"""
Original copy written on ARC server
#! /usr/bin/python

import optparse, os, sys, time, re
from twisted.internet.protocol import ServerFactory, Protocol
from twisted.internet.task import LoopingCall

def parse_args():
    usage = ''' usage: %prog [options]'''

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port"
    parser.add_option('-p', type='int', help=help, default=12002, dest="port")

    help = "The logfile to tail and write"
    parser.add_option('-f', help=help, default='log/logfull.log',dest="logfile")

    help = "Delay to simulate live log"
    parser.add_option('-d', help=help, default=0, dest="delay")
    #parser.add_option('--file', help=help, default='log/logsnippet.log',dest="logfile")

    options = parser.parse_args()
    return options

class LogProtocol(Protocol):
    #loop=None
    #def __init__(self):

    def connectionMade(self):
        time.sleep(2)
        self.loop = LoopingCall(follow, open(self.factory.log), self._sendLogLine)
        delay = float(self.factory.delay)
        print delay
        if delay > 0: self.loop.start(delay)
        else:self.loop.start(0)
        #for line in self.follow():
        #   self.transport.write(line)
        #self.transport.loseConnection()

    def _sendLogLine(self, line):
        self.transport.write(line)

    def connectionLost(self, reason):
        self.loop.stop()

def follow(fObj, gotLine):
    line = fObj.readline()
    gotLine(line)
    #if re.search(msgBookShort, line):
    #   gotLine(line)
    #elif re.search(msgFill, line):
    #   gotLine(line)

    #if line:
    #   gotLine(line)
    #testDiff


msgShots = re.compile(r'''
        ^                       #start at the beginning
        (?P<timestamp>\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        ''')
        
msgFill = re.compile(r'''
        ^                     #start at the beginning
        (?P<timestamp>\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        (?P<msgType>onFill):             #msgType, any number of alphanumeric & :
        \s                    #space
        sym=                  #symbol tag in FIX message
        (?:\w+:)?                  #optional contract type to accomodate ARC change 2011/08/12
        (?P<contract>\w+):                #contract, any number alphanum
        (?P<expiry>\d{6})               #expiry, 6 digits
        (?P<relRef>\[\d,\-?\d+\])?:      #optional array-type reference for strategy and contract relationship, '[' & 1 digit & ',' & opt '-' & 1 or more digits & ']'
        oid=(?P<oid>\d+):            #order ID
        tid=(?P<tid>\d+):            #trade ID
        dst=(?P<dst>\w+):            #destination
        dir=(?P<dir>\w+):            #direction
        fpx=(?P<fpx>\-?\d+.\d+):        #fill price
        fsz=(?P<fsz>\d+):            #fill size
        tif=TIF_(?P<tif>\w+):            #time in force
        itim=(?P<itim>\d{10}.\d{6}):  #itim timestamp
        lftim=(?P<lftim>\d{10}.\d{6}) #lftim timestamp
        ''', re.VERBOSE)

msgTest = re.compile(r'''
        ^                   #start at beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        ''', re.VERBOSE)

msgBookShort = re.compile(r'''
        ^
        (\d{10}.\d{6})\s      #timestamp, 10 digits & '.' & 6 digits
        (onBookChanged):      #msgType, any number of alphanumeric & :
        ''', re.VERBOSE)




class LogFactory(ServerFactory):
    protocol = LogProtocol

    def __init__(self,log,delay):
        self.log = log
        self.delay = delay

def main():
    options, log_file = parse_args()
    log = options.logfile
    factory = LogFactory(log,options.delay)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory)    #,interface=options.iface)

    print 'Serving %s on %s.' % (options.logfile, port.getHost())

    reactor.run()


if __name__ == '__main__':
    main()
             

"""
