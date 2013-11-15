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
from emi_ggus_mon.model import GGUS_ALL_STATES, get_ggus_ticket, ticket_id, \
    GGUS_PRIORITY_MAP, ticket_priority, ticket_short_description, ticket_su, \
    ticket_url, ticket_eta, ticket_related_issue, GGUS_NEED_WORK_STATES, \
    ticket_priority_index, ticket_status
from emi_ggus_mon.report import classify_status, classify_priority
import StringIO
from string import Template
from timeit import itertools

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

def format_ticket_html(t):
    
    def decorate_priority_html(prio):
        label = "label label-default"
        if prio == "urgent" or prio == "very urgent":
            label = "label label-warning"
        elif prio == "top priority":
            label = "label label-danger"
        
        return "<span class=\"%s\">%s</span>" % (label, prio)
    
    def decorate_status_html(status):
        label = "label label-default"
        if status == "assigned" or status == "in progress" or status == "reopened":
            label = "label label-danger"
        return  "<span class=\"%s\">%s</span>" % (label, status)
    
    template_str = """
        <tr>
        <td>${su}</td>
        <td><a href="https://ggus.eu/ws/ticket_info.php?ticket=${id}">${id}</a></td>
        <td>${status}</td>
        <td>${prio}</td>
        <td>${desc}</td>
        </tr>"""
    
    ggus_t = get_ggus_ticket(ticket_id(t))
    assigned_time = ggus_t.assigned_time()
    age = (datetime.now() - assigned_time).days
    
    
    template = Template(template_str)
    ticket_str = template.substitute({"id":ticket_id(t),
                         "desc": ticket_short_description(t),
                         "su": ticket_su(t),
                         "prio": ticket_priority(t),
                         "age": "%d days old" % age,
                         "related": ticket_related_issue(t),
                         "status": ticket_status(t)
                         })
    
    return ticket_str
    
def ticket_needs_attention(t):
    val = (ticket_status(t) in ["assigned", "in progress", "reopened"] or 
        (ticket_status(t) == "on hold" and ticket_related_issue(t) is None))
    return  val
         
        
def format_ticket(t):
    
    ggus_t = get_ggus_ticket(ticket_id(t))
    assigned_time = ggus_t.assigned_time()
    age = (datetime.now() - assigned_time).days
    
    warning = ""
    if ticket_status(t) == 'on hold' and ticket_related_issue(t) is None:
        warning = "on hold ticket without related issue!".upper()
        
    template=Template("""${url} \"${desc}\"
                SU: ${su}
                Prio: ${prio}
                Age: ${age}
                Related issue: ${related}""")
    
    ticket_str = template.substitute({"url":ticket_url(t),
                         "desc": ticket_short_description(t),
                         "su": ticket_su(t),
                         "prio": ticket_priority(t),
                         "age": "%d days old" % age,
                         "related": ticket_related_issue(t)})
    
    if len(warning) > 0:
        ticket_str = ticket_str + "\n\t\t\tWARNING: %s" % warning
    
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
    
    s = smtplib.SMTP(smtp_server)
    s.sendmail(sender,
               recipients,
               msg.as_string())
    s.quit()


def print_html_report(tickets):
    urgent_tickets = filter(ticket_needs_attention, tickets) 
    other_tickets = filter(lambda t: not ticket_needs_attention(t), tickets)
    
    status_classification = classify_status(tickets)
        
    fragment_str="""
            <table class="table table-striped table-bordered">
                <tr>
                    <th>SU</th>
                    <th>Ticket</th>
                    <th>Status</th>
                    <th>Prio</th>
                    <th>Desc.</th>
                </tr>
                ${tickets}
            </table>"""
    
    fragment  = Template(fragment_str)
    tickets_str = StringIO.StringIO()
    
    
    
    ## urgent
    if len(urgent_tickets) > 0:
        print >> tickets_str, "<tr><th colspan=\"5\">Tickets that need immediate attention</th></tr>"
        priority_classification = classify_priority(urgent_tickets)
    
        for p in sorted(priority_classification.keys(),
                        key=lambda t: GGUS_PRIORITY_MAP[t],
                        reverse=True):
            for t in priority_classification[p]:
                print >> tickets_str, format_ticket_html(t)
    
    if len(other_tickets) > 0:
        print >> tickets_str, "<tr><th colspan=\"5\">Other tickets</th></tr>"
        priority_classification = classify_priority(other_tickets)
        for p in sorted(priority_classification.keys(),
                        key=lambda t: GGUS_PRIORITY_MAP[t],
                        reverse=True):
            for t in priority_classification[p]:
                print >> tickets_str, format_ticket_html(t)
             
    print fragment.substitute({"tickets": tickets_str.getvalue()})
    
def send_tickets_reminder(tickets):
    status_classification = classify_status(tickets)
    
    msg = StringIO.StringIO()
    print >> msg, "Tickets status report for %s" % (", ".join(sorted(cnaf_sus)))
    print >> msg
    print >> msg, "Date: %s" % datetime.now()
    print >> msg, "Open tickets: %d" % len(tickets)
    print >> msg
    print >> msg
    for s in GGUS_OPEN_STATES:
        if len(status_classification[s]) > 0:
            print >> msg, "%s:\n" % s.upper() 
            priority_classification = classify_priority(status_classification[s])
            for p in sorted(priority_classification.keys(),
                            key=lambda t: GGUS_PRIORITY_MAP[t],
                            reverse=True):
                if len(priority_classification[p]) > 0:
                    for t in priority_classification[p]:
                        print >> msg, "\t" + format_ticket(t)
                        print >> msg 
            print >> msg
    
    msg_str = msg.getvalue()
    msg.close()
    
    print msg_str
    send_notification("[ggus-monitor] GGUS ticket status report",
                      msg_str)
    
    print "Status report sent"        

    
def check_ticket_status():
    
    try:
        tickets = get_tickets(cnaf_open_tickets())
    except WebFault, f:
        print >> sys.stderr, "Error fetching open tickets for CNAF SUs. %s" % f
    
    print_html_report(tickets)
    # send_tickets_reminder(tickets)
    
    
    
    
    
    
    
    
                                                      
                                                      
            
        
        
    
    
    
    
    
