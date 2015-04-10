'''
Created on Jul 11, 2011

@author: jsu
library of RegEx to use for parsing logs
pylint score 7.86/10 as of 18 Jan 2012
'''

import re
#import numpy as np
#import cfg
#import subprocess

class Teml_RE:
    '''TradingEngineMessagingLanguage_RegularExpressions'''
    
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
    
    msgOrdStat = re.compile(r'''
        ^                     #start at the beginning
        (?P<timestamp>\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        (onOrderStatusChange):             #msgType, any number of alphanumeric & :
        \s                    #space
        sym=                  #symbol tag in FIX message        
        (\w+):                #contract, any number alphanum
        (\d{6})               #expiry, 6 digits
        (\[\d,\-?\d+\])?:     #optional array-type reference for strategy and contract relationship, '[' & 1 digit & ',' & opt '-' & 1 or more digits & ']'        
        oid=(\d+):            #order ID
        tid=(\d+):            #trade ID
        dst=(\w+):            #destination
        dir=(\w+):            #direction
        px=(\-?\d+.\d+):      #order price
        rsz=(\d+):            #order size
        tif=TIF_(\w+):        #time in force
        itim=(\d{10}.\d{6}):  #itim timestamp
        ost=(\w+):            #order status
        lotim=(\d{10}.\d{6})  #lotim timestamp
        #dnr=(\w+)            #order status        
        ''', re.VERBOSE)
    
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

    msgArbDone = re.compile(r'''
        ^                     #start at the beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        onLegFill:            #msgType, any number of alphanumeric & :
        \s                    #space
        [*]+\s
        ARB\(?(\d+)?\)?             #synth trade number
        \s                    #space
        IS\s
        DONE!\s
        [*]+
        ''', re.VERBOSE)

    msgBasic = re.compile(r'''
        ^                     #start at the beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        (\w+:)                #msgType, any number of alphanumeric & :
        \s                    #space
        #\w{3}\=              #symbol tag in FIX message
        (\w+:\d{6})           #contract and expiry, any number alphanum & ':' & 6 digits
        (\[\d,\d+\])?         #optional array-type reference for strategy and contract relationship, '[' & 1 digit & ',' & 1 or more digits & ']'
        
        
        ''', re.VERBOSE)
    
    acct = re.compile(r'''
        ^                     #start at the beginning        
        \s+                    #leading spaces
        acct
        \s 
        =                    #acct tag
        \s
        (\w+)                #msgType, any number of alphanumeric & :
        ''', re.VERBOSE)
    
    marginAll = re.compile(r'''
        ^                     #start at the beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        handleUserMessage:
        \s
        BID
        \s
        &
        \s
        ASK
        \s
        MARGIN
        \[(\d+)\]
        \s
        set
        \s
        to
        \s
        (\-?\d+.\d+)    #bid margin & ask margin        
        ''', re.VERBOSE)
    
    marginBid = re.compile(r'''
        ^                     #start at the beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        handleUserMessage:
        \sBID\sMARGIN
        \[(\d+)\]
        \sset\sto\s
        (\-?\d+.\d+)    #bid margin & ask margin        
        ''', re.VERBOSE)
     
    marginAsk = re.compile(r'''
        ^                     #start at the beginning
        (\d{10}.\d{6})        #timestamp, 10 digits & '.' & 6 digits
        \s                    #space
        handleUserMessage:
        \sASK\sMARGIN
        \[(\d+)\]
        \sset\sto\s
        (\-?\d+.\d+)    #bid margin & ask margin        
        ''', re.VERBOSE)
    
    lineEnd = re.compile(r'''
        \n
        ''', re.VERBOSE)
