'''
Created on 13/giu/2013

@author: andreaceccanti
'''
from datetime import datetime, timedelta
from emi_ggus_mon.business import BusinessCalendar
from query import cnaf_open_tickets
from su import cnaf_sus
from model import GGUS_PRIORITIES, GGUS_OPEN_STATES, GGUS_TERMINAL_STATES

import smtplib
import sys
from email.mime.text import MIMEText
from emi_ggus_mon.ws import get_tickets
from suds import WebFault
from emi_ggus_mon.model import GGUS_ALL_STATES, get_ggus_ticket, ticket_id,\
    GGUS_PRIORITY_MAP, ticket_priority, ticket_short_description, ticket_su,\
    ticket_url, ticket_eta, ticket_related_issue, GGUS_NEED_WORK_STATES,\
    ticket_priority_index
from emi_ggus_mon.report import classify_status, classify_priority
import StringIO

URGENT_PRIORITIES = ('top priority', 'very urgent')

def init_status_classification():
    c = {}
    for s in GGUS_ALL_STATES:
        c[s] = []
    return c

def init_priority_classification():
    c = {}
    for p in GGUS_PRIORITIES:
        c[p] = []
    return c

def format_ticket(t):
    
    ggus_t = get_ggus_ticket(ticket_id(t))
    assigned_time = ggus_t.assigned_time()
    age = (datetime.now() - assigned_time).days
    ticket_str = "(%-3d days old) %s: %s - \"%s\"  %s" % (age,
                                                          ticket_priority(t).ljust(12),
                                                          ticket_su(t).ljust(6),
                                                          ticket_short_description(t),
                                                          ticket_url(t))
    return ticket_str


def send_notification(subject,
                      msg_body,
                      sender="GGUS ticket monitor <andrea.ceccanti@cnaf.infn.it>",
                      smtp_server="postino.cnaf.infn.it",
                      recipients=['andrea.ceccanti@cnaf.infn.it']):
    
    msg = MIMEText(msg_body, _charset='utf-8')
    msg['From'] = sender
    msg['To'] = ",".join(recipients)
    msg['Subject'] = subject
    
    s=smtplib.SMTP(smtp_server)
    s.sendmail(sender,
               recipients,
               msg.as_string())
    s.quit()


def send_tickets_reminder(tickets):
    status_classification = classify_status(tickets)
    
    msg = StringIO.StringIO()
    print >> msg, "Open tickets status report for sus %s" % (",".join(sorted(cnaf_sus)))
    print >> msg, "Date: %s" % datetime.now()
    
    for s in GGUS_OPEN_STATES:
        if len(status_classification[s]) > 0:
            print >> msg, "%s:" % s.upper() 
            priority_classification = classify_priority(status_classification[s])
            for p in sorted(priority_classification.keys(), 
                            key=lambda t: GGUS_PRIORITY_MAP[t],
                            reverse=True):
                if len(priority_classification[p]) > 0:
                    for t in priority_classification[p]:
                        print >> msg, "\t" + format_ticket(t)
                    print >> msg
            print >>msg
    
    print msg.getvalue()
    msg.close()
#     if len(msg) > 0:
#         send_notification("There are tickets that must be handled!",
#                           msg)
#         print "Reminder sent."
#     else:
#         print "No ticket in NEED WORK state found."
    
    
            
    
def check_tickets_in_assigned(tickets):
    
    status_classification = classify_status(tickets)
    print "Checking assigned tickets status"
    msg = ""
    if len(status_classification['assigned']) > 0:
        
        print "Tickets in assigned status found..."
        msg = msg +"# Tickets in ASSIGNED status as of %s\n\n" % (datetime.now())
        assigned_tickets = sorted(status_classification['assigned'],
                                lambda t: GGUS_PRIORITY_MAP[ticket_priority(t)]) 
        
        for t in assigned_tickets:
            msg = msg + format_ticket(t)
    
        send_notification('There are tickets in ASSIGNED status that must be handled!', 
                          msg)
        
        print "Tickets in assigned notification email sent."
    

def check_ticket_etas(tickets):
    priority_classification = classify_priority(tickets)
    
    for p in GGUS_PRIORITIES:
        for t in priority_classification[p]:
            # print t
            eta = ticket_eta(t)
            print ticket_priority(t), ticket_url(t), eta
                
            
            
def check_on_hold_tickets(tickets):
    status_classification = classify_status(tickets)
    
    tickets_without_related_issue = []
    for t in status_classification['on hold']:
        related_issue = ticket_related_issue(t)
        if related_issue is None:
            tickets_without_related_issue.append(t)
    
    if len(tickets_without_related_issue) > 0:
        msg = "# Ticket in on-hold status without related issue as of %s\n\n" % datetime.now()
        for t in tickets_without_related_issue:
            pass
    
def check_ticket_status():
    
    try:
        tickets = get_tickets(cnaf_open_tickets())
    except WebFault, f:
        print >> sys.stderr, "Error fetching open tickets for CNAF SUs. %s" % f
    
    send_tickets_reminder(tickets)
    
    
    
    
    
    
    
    
                                                      
                                                      
            
        
        
    
    
    
    
    