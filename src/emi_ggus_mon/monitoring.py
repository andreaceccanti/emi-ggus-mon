'''
Created on 13/giu/2013

@author: andreaceccanti
'''
from model import GGUS_PRIORITIES
import os
import time
import sys
from datetime import datetime
from emi_ggus_mon.ws import cnaf_tickets
from suds import WebFault
from emi_ggus_mon.model import GGUS_ALL_STATES, get_ggus_ticket, ticket_id, \
    GGUS_PRIORITY_MAP, ticket_priority, ticket_short_description, ticket_su, \
    ticket_url, ticket_status
from emi_ggus_mon.report import classify_priority
import StringIO
from string import Template

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

    template_str = """
        <tr>
        <td>${su}</td>
        <td><a href="https://ggus.eu/ws/ticket_info.php?ticket=${id}">${id}</a></td>
        <td>${status}</td>
        <td class="prio_${prio_class}">${prio}</td>
        <td><h5>${desc}</h5></td>
        <td><span class=\"badge\">${age}</span></td>
        </tr>"""

    ggus_t = get_ggus_ticket(ticket_id(t))
    assigned_time = ggus_t.assigned_time()
    age = (datetime.now() - assigned_time).days


    template = Template(template_str)
    ticket_str = template.substitute({"id":ticket_id(t),
                         "desc": ticket_short_description(t),
                         "su": ticket_su(t),
                         "prio_class" : ticket_priority(t).replace(' ','_'),
                         "prio": ticket_priority(t),
                         "age": age,
                         "related": None,
                         "status": ticket_status(t)
                         })

    return ticket_str

def ticket_needs_attention(t):
    val = (ticket_status(t) in ["assigned", "in progress", "reopened"])
    return  val

def waiting_for_reply_tickes(t):
    return  ticket_status(t) == "waiting for reply"

def on_hold_tickets(t):
    return ticket_status(t) == "on hold"

def format_ticket(t):

    ggus_t = get_ggus_ticket(ticket_id(t))
    assigned_time = ggus_t.assigned_time()
    age = (datetime.now() - assigned_time).days

    warning = ""

    # if ticket_status(t) == 'on hold' and ticket_related_issue(t) is None:
    #    warning = "on hold ticket without related issue!".upper()

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
                         "related": None })

    if len(warning) > 0:
        ticket_str = ticket_str + "\n\t\t\tWARNING: %s" % warning

    return ticket_str

def get_html_report(tickets):
    urgent_tickets = filter(ticket_needs_attention, tickets)
    wfr_tickets = filter(waiting_for_reply_tickes, tickets)
    other_tickets = filter(on_hold_tickets, tickets)

    current_time = time.strftime("%Y-%m-%d %H:%M")

    report_template="""<!DOCTYPE html><html><head>
    <title>GGUS ticket report - ${date}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <!-- This page style -->
    <link href="style.css" rel="stylesheet">
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h3 class="text-muted">GGUS ticket report</h3>
            <h5>${date}</h5>
        </div>
        <hr/>
        ${content}
    </div>
    </body>"""

    panel_template="""<div class=\"panel ${panel_class}\">
            <div class=\"panel-heading\">
                <div class=\"panel_title\">
                    ${panel_title}
                </div>
            </div>
            ${content}
            </div><!-- panel -->"""

    table_template="""
            <table class=\"table table-striped\">
                <thead>
                <tr>
                    <th>SU</th>
                    <th>Ticket</th>
                    <th>Status</th>
                    <th>Prio</th>
                    <th>Desc.</th>
                    <th>Age</th>
                </tr>
                </thead>
                <tbody>
                ${content}
                </tbody>
            </table>"""

    table = Template(table_template)
    panel = Template(panel_template)
    report = Template(report_template)

    tickets_content = StringIO.StringIO()
    urgent_tickets_content = StringIO.StringIO()
    wfr_tickets_content = StringIO.StringIO()
    other_tickets_content =  StringIO.StringIO()

    if len(urgent_tickets) > 0:
        priority_classification = classify_priority(urgent_tickets)

        for p in sorted(priority_classification.keys(),
                        key=lambda t: GGUS_PRIORITY_MAP[t],
                        reverse=True):
            for t in priority_classification[p]:
                print >> urgent_tickets_content, format_ticket_html(t)
        table_content = table.substitute({"content": urgent_tickets_content.getvalue()})
        panel_title = "Tickets that need immediate attention <span class=\"badge badge-title\">%d</span>" % len(urgent_tickets)

        print >> tickets_content, panel.substitute({"panel_class": "panel-primary",
                                                    "panel_title": panel_title,
                                                    "content" : table_content})

    if len(wfr_tickets) > 0:
        priority_classification = classify_priority(wfr_tickets)
        for p in sorted(priority_classification.keys(),
                        key=lambda t: GGUS_PRIORITY_MAP[t],
                        reverse=True):
            for t in priority_classification[p]:
                print >> wfr_tickets_content, format_ticket_html(t)
        panel_title = "Waiting for reply tickets <span class=\"badge badge-title\">%d</span>" % len(wfr_tickets)
        print >> tickets_content, panel.substitute({"panel_class": "panel-primary",
                                                    "panel_title": panel_title,
                                                    "content": table.substitute({"content": wfr_tickets_content.getvalue()})})
    if len(other_tickets) > 0:
        priority_classification = classify_priority(other_tickets)
        for p in sorted(priority_classification.keys(),
                        key=lambda t: GGUS_PRIORITY_MAP[t],
                        reverse=True):
            for t in priority_classification[p]:
                print >> other_tickets_content, format_ticket_html(t)
        panel_title = "Other open tickets <span class=\"badge badge-title\">%d</span>" % len(other_tickets)
        print >> tickets_content, panel.substitute({"panel_class": "panel-primary",
                                                    "panel_title": panel_title,
                                                    "content": table.substitute({"content": other_tickets_content.getvalue()})})


    return (report.substitute({"content":tickets_content.getvalue(), "date": current_time}),"report.html")


def report_dir_sanity_checks(report_dir):

    if not os.path.exists(report_dir):
        raise RuntimeError("%s does not exist." % report_dir)

    if not os.path.isdir(report_dir):
        raise RuntimeError("%s is not a directory." % report_dir)

def check_ticket_status(report_dir):
    report_dir_sanity_checks(report_dir)

    print "Generating CNAF GGUS html report"
    try:
        tickets = cnaf_tickets()
    except WebFault, f:
        print >> sys.stderr, "Error fetching open tickets for CNAF SUs. %s" % f

    (report, filename) = get_html_report(tickets)
    try:
        report_file = open(os.path.join(report_dir, filename), "w")
        report_file.write(report)
        report_file.close()

        print "Report written to %s." % os.path.join(report_dir, filename)

    except IOError as e:
        print >>sys.stderr, "IOError: %s " % e
        sys.exit(1)
