'''
Created on Nov 21, 2011

@author: JSU
pylint score 9.74/10 as of 18 Jan 2012
'''
import cfg
import smtplib, locale
import numpy as np
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Reporting():
    '''structures and sends email reports for position, P&L, and exposure'''
    
    def __init__(self):
        self.before_abs_ntl = 0
        locale.setlocale(locale.LC_ALL, '')
        
    def check_status(self):
        '''check absolute notional values of each portfolio 
        identify new trades by changes in values
        send email if changes
        '''

        if cfg.BOOK.AbsNotional != self.before_abs_ntl: 
            cfg.IS_READY_TO_EMAIL = True
        if cfg.IS_READY_TO_EMAIL:
            cfg.IS_READY_TO_EMAIL = False
            if cfg.IS_EMAIL_ENABLED:  
                email_report()
            
        self.before_abs_ntl = cfg.BOOK.AbsNotional
        cfg.IS_READY_TO_EMAIL = False
        
def email_report():
    '''calls functions to structure and send report'''
    structure_report()
    
def structure_report():
    '''structures subject and body of report'''
    book = cfg.BOOK
    book.WrapAll()
    subject = "TrdRpt: "     
    if not cfg.IS_LIVE: 
        subject += "Test "
    body = ""
    report = []
            
    for portfolio in book.All:
        if portfolio.Name == "ngxPrompt": 
            continue
        report = []
        
        abs_ntl = portfolio.AbsNotional
        #opnNtl = p.NetNotional
        #clsNtl = p.AbsNotional-np.abs(opnNtl)
        #openStr = "No open positions"
        #for inst in portfolio:                                
        #    if np.abs(inst.Position) > 0.5 :
        #        report.append(inst.show())
        #        openStr = "OPEN POSITIONS FOLLOW:\r\n"
        
        if abs_ntl != 0:
            report.insert(0, "*****PORTFOLIO: %s *****" % portfolio.Name)
            #report.insert(1, "Open PNL: %.2f" % open)
            report.insert(1, "Closed PNL: %s" % locale.currency(
                            portfolio.ClosedPnL, grouping = True))   
            #report.insert(3, "Open Notional: %.0f" % opnNtl)
            #report.insert(4, "Closed Notional: %.0f" % clsNtl)
            report.insert(5, "Total Notional: %.0f" % abs_ntl) 
            #report.insert(6, openStr)
            report.append(' ')
            
            add = '\r\n'.join(report)
            body += add
            body += '\r\n'
            
    portfolio = book.ngxPrompt
    report.insert(0, "*****PORTFOLIO: %s *****" % portfolio.Name)   
    
    open_mmbtu = float(np.round((
               portfolio.t_net_MMBTU / portfolio[3].HedgeSize), 2))
    open_bs = float(np.round((
               portfolio.t_net_BS / portfolio[1].HedgeSize), 2))
    open_cad = float(np.round((
               portfolio.t_net_CAD / portfolio[4].HedgeSize), 2))

    if open_mmbtu == 0: 
        open_mmbtu = "None"
    if open_bs == 0: 
        open_bs = "None"
    if open_cad == 0: 
        open_cad = "None"
    
    report.insert(1, "MMBTU Exposure: %s: %s contracts \n" % (
        locale.currency(portfolio.t_close_MMBTU, grouping=True), open_mmbtu))
    report.insert(2, "Basis Exposure: %s: %s contracts \n" % (
        locale.currency(portfolio.t_close_BS, grouping=True), open_bs))
    report.insert(3, "Currency Exposure: %s: %s contracts \n" % (
        locale.currency(portfolio.t_close_CAD, grouping=True), open_cad))
    report.insert(4, "Hedged PNL if held to end: %s" % locale.currency(
        (portfolio.synthTotalMidPnL), grouping=True))
    report.insert(5, "Close All Now: %s" % locale.currency(
        (portfolio.LongToClose + portfolio.ShortToClose), grouping=True))
    report.append(' ')
    
    add = '\r\n'.join(report)
    body += add
    body += '\r\n'

    send_report(subject, body)
    
    
def send_report(subject, body):
    '''send report via email'''
    #subject += "|Open: %.2f|  |Closed: %.2f|  |Total: %.2f|" % (
                            #0, book.ClosedPnL, (0+book.ClosedPnL))
    msg = MIMEMultipart()        

    sender = ""         #sender address
    if body == "":
        body = "No positions"

    msg['From'] = sender
    msg['To'] = ','.join(cfg.ADDRESS_BOOK)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    #print text
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    smtp_sender = smtplib.SMTP('')      #server address
    smtp_sender.sendmail(sender, cfg.ADDRESS_BOOK, text)
    smtp_sender.quit()     

"""
def email_report(self):
        subject = "TrdRpt: "
        if not cfg.IS_LIVE: subject += "Test "
        body = ""
        report=[]
        allOpen=0
        allClosed=0
        
        pN= cfg.BOOK.ngxPrompt
        if pN.AbsNotional!=0:
            report=[]
            
            open_mmbtu=int(np.round((pN.t_net_MMBTU/pN[3].HedgeSize),0))
            open_bs=int(np.round((pN.t_net_BS/pN[1].HedgeSize),0))
            open_cad=int(np.round((pN.t_net_CAD/pN[4].HedgeSize),0))
    
            if open_mmbtu == 0: open_mmbtu="None"
            if open_bs == 0: open_bs="None"
            if open_cad == 0: open_cad="None"
            
            report.insert(0, "*****NGX EXPOSURE: *****")                    
            report.insert(1, "MMBTU Exposure: %s" % open_mmbtu)
            report.insert(2, "Basis Exposure: %s" % open_bs)            
            report.insert(3, "Currency Exposure: %s" % open_cad)
            report.append(' ')
            
            add='\r\n'.join(report)
            body+=add
            body+='\r\n'
                
        for p in cfg.BOOK.All:
            p.WrapAll()
            report=[]
            openStr="No open positions"
            for inst in p:        
                inst.CalcPosition2()                          
                if np.abs(inst._position-inst._exposed) > 0.5 :
                    report.append(inst.show())
                    openStr="OPEN POSITIONS FOLLOW:\r\n"
            open = p.WrapOpenPnL()
            closed = p.WrapClosedPnL()
            
            allOpen+=open
            allClosed+=closed
            
            
            abs_ntl = p.AbsNotional
            opnNtl = p.NetNotional
            clsNtl = p.AbsNotional-np.abs(opnNtl)
            
            if abs_ntl!=0:
                report.insert(0, "*****PORTFOLIO: %s *****" % p.Name)                    
                report.insert(1, "Open PNL: %.2f" % open)
                report.insert(2, "Closed PNL: %.2f" % closed)   
                report.insert(3, "Open Notional: %.0f" % opnNtl)
                report.insert(4, "Closed Notional: %.0f" % clsNtl)
                report.insert(5, "Total Notional: %.0f" % abs_ntl)
                report.insert(6, openStr)
                report.append(' ')
                
                add='\r\n'.join(report)
                body+=add
                body+='\r\n'


        subject += "|Open: %.2f|  |Closed: %.2f|  |Total: %.2f|" % (allOpen, allClosed, (allOpen+allClosed))
        msg = MIMEMultipart()        
    
        sender = ""             #sender address
        
        if body=="":body="No positions"
    
        msg['From'] = sender
        msg['To'] = ','.join(cfg.ADDRESS_BOOK)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        text=msg.as_string()
        #print text
        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP()          #server address
        s.sendmail(sender,cfg.ADDRESS_BOOK, text)
        s.quit()        
"""
