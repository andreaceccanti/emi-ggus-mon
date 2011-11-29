'''
Created on 30/ago/2011

@author: andreaceccanti
'''

from sys import stderr
from datetime import datetime, timedelta
from string import Template
from suds import WebFault

from emi_ggus_mon.business import BusinessCalendar
from emi_ggus_mon.model import ticket_priority, ticket_status, ticket_su, ticket_id, \
    ticket_short_description, get_ggus_ticket, ticket_creation_time

from emi_ggus_mon.query import emi_third_level_assigned_tickets, open_tickets_for_su, \
    emi_third_level_open_tickets, emi_third_level_open_tickets_in_period, open_tickets_for_su_in_period

from emi_ggus_mon.su import emi_support_units, emi_3rd_level_su
from emi_ggus_mon.ws import get_tickets

report_template = Template("""As of ${now}, there are ${numOpen} open tickets in EMI SUs, of which:
    ${numAssigned} assigned,
    ${numInProgress} in progress,
    ${numOnHold} on hold,
    ${numReopened} reopened,
    ${numWaitingForReply} waiting for reply.

The tickets in assigned include:
    
    ${numTopPriority} top priority,
    ${numVeryUrgent} very urgent,
    ${numUrgent} urgent,
    ${numLessUrgent} less urgent.
""")

statuses = ["assigned", "in progress", "on hold", "reopened", "waiting for reply"]
priorities = ["less urgent", "urgent", "very urgent", "top priority"]

sla_constraints = { "top priority": timedelta(hours=4),
                    "very urgent": timedelta(days=2),
                    "urgent": timedelta(days=5),
                    "less urgent": timedelta(days=15)
                    }

def ticket_resolution_delay(ticket):
    
    ggus_ticket = get_ggus_ticket(ticket_id(ticket))
    
    sla_comp_values = ggus_ticket.get_sla_compliance_values()[ticket_su(ticket)]
    
    bc = BusinessCalendar(sla_comp_values.assigned_time)
    resolution_date = bc.add_business_time(sla_constraints[sla_comp_values.priority_when_assigned])
    
    out_of_assigned_time = sla_comp_values.out_of_assigned_time
    if out_of_assigned_time is None:
        out_of_assigned_time = datetime.now()
    
    if resolution_date >= out_of_assigned_time:
        return timedelta(hours=0)
    else:
        if out_of_assigned_time != resolution_date.day:
            bd_delay = BusinessCalendar(resolution_date).count_business_days(out_of_assigned_time)
            return timedelta(days=bd_delay)
        
        return out_of_assigned_time - resolution_date    


def print_assigned_tickets_report(assigned_priority_classification=None):
    
    now = datetime.now()
    
    if assigned_priority_classification is None:
        assigned_priority_classification = {}
        for i in priorities:
            assigned_priority_classification[i] = []
        
        for t in get_tickets(emi_third_level_assigned_tickets()):
            assigned_priority_classification[ticket_priority(t)].append(t)
    
    for p in priorities:
        if len(assigned_priority_classification[p]) == 0:
            continue
        else:
            print p, ":"
            num_violations = 0
            for t in assigned_priority_classification[p]:
                
                ggus_ticket = get_ggus_ticket(ticket_id(t))
                
                assigned_time = ggus_ticket.get_sla_compliance_values()[ticket_su(t)].assigned_time
                bc = BusinessCalendar(assigned_time)
                
                resolution_date = bc.add_business_time(sla_constraints[p])
                
                if resolution_date >= now:
                    sla_violation_string = "SLA check: OK (Assigned on: %s. To be taken in charge before %s)" % (assigned_time, resolution_date)
                else:
                    if now.day != resolution_date.day:
                        bd_delay = BusinessCalendar(resolution_date).count_business_days(now)
                        delay = "%s work days" % bd_delay
                    else:
                        delay = "%s hours" % (now - resolution_date)
                    
                    sla_violation_string = "SLA VIOLATION: Delay: %s (Assigned on: %s. Had to be taken in charge before %s)" % (delay, assigned_time, resolution_date)
                    num_violations = num_violations + 1
                
                print "\t(%s) \"%s\" https://ggus.eu/tech/ticket_show.php?ticket=%s\n\t%s" % (ticket_su(t),
                                                                                              ticket_short_description(t),
                                                                                              ticket_id(t),
                                                                                              sla_violation_string)
                print
            
            print "Of the %d %s tickets, %d violate the SLA " % (len(assigned_priority_classification[p]), p, num_violations)
            print




def print_sla_stats(start_date, end_date=datetime.now()):
    print >> stderr, "Producing SLA compliance report for period: %s -> %s . Be patient..." % (start_date, end_date)
    try:
        tickets = get_tickets(emi_third_level_open_tickets_in_period(start_date, end_date))
    except WebFault:
        print >> stderr, "No open tickets found in period (%s,%s)" % (start_date, end_date)
        return
    
    print >>stderr, "Found %d matching tickets" % len(tickets)
    accum = timedelta()
    for t in tickets:
        delay = ticket_resolution_delay(t)
        # print  "%s,%s,%s" % (ticket_su(t), ticket_status(t), ticket_resolution_delay(t))
        accum = accum + delay
    
    avg_delay = accum / len(tickets)
    print "start_date,end_date,avg_delay"
    print "%s,%s,%s" % (start_date,end_date,avg_delay)
    

    
def print_sla_report(start_date, end_date=datetime.now(), su_list=None, print_seconds=False):
    print >> stderr, "Print SLA status report for period %s -> %s. " % (start_date, end_date)
    print >> stderr, "The report prints the average SLA violation delay in seconds per SU and ticket priority."
    
    if su_list:
        sus = sorted(su_list, key=str.lower)
    else:
        sus = sorted(emi_3rd_level_su.keys(), key=str.lower)
    
    first_line = "su,%s" % ','.join(priorities)
    template_line = "%s,%s" % ('%s', ','.join(['%s' for i in range(len(priorities))]))
    
    tickets_total = 0
    print first_line
    
    for su in sus:
        tickets = []
        try:
            tickets = get_tickets(open_tickets_for_su_in_period(su, start_date, end_date))
        except WebFault:
            print >> stderr, "No open tickets found for SU %s in period (%s,%s)" % (su, start_date, end_date)
            continue
        
        tickets_total = tickets_total + len(tickets)
        priority_classification = {}
        priority_averages = {}
        
        for i in priorities:
            priority_classification[i] = []
            priority_averages[i] = timedelta(hours=0)       
        
        for t in tickets:
            prio = ticket_priority(t)
            priority_classification[prio].append(ticket_resolution_delay(t))
        
        
        for i in priorities:
            accum = timedelta(hours=0)
            
            for d in priority_classification[prio]:
                accum = accum + d
            
            if len(priority_classification[prio]) > 0:
                accum = accum / len(priority_classification[prio])
            
            priority_averages[prio] = accum
        if print_seconds:
            print template_line % (su,
                                   td_seconds(priority_averages[priorities[0]]),
                                   td_seconds(priority_averages[priorities[1]]),
                                   td_seconds(priority_averages[priorities[2]]),
                                   td_seconds(priority_averages[priorities[3]])
                                   )
        else:
            print template_line % (su,
                                   priority_averages[priorities[0]],
                                   priority_averages[priorities[1]],
                                   priority_averages[priorities[2]],
                                   priority_averages[priorities[3]]
                                   )
           
def td_seconds(timedelta):
    return timedelta.seconds + timedelta.days * 24 * 3600

def print_su_report():
    sus = sorted(emi_support_units.keys(), key=str.lower)
    
    first_line = "su,%s,%s" % (','.join(statuses), ','.join(priorities))
    template_line = "%s,%s" % ('%s', ','.join(['%d' for i in range(len(priorities) + len(statuses))]))
    zero_template = "%s,%s" % ('%s', ','.join(['0' for i in range(len(priorities) + len(statuses))]))
    
    print first_line
    for su in sus:
        tickets = []
        try:
            tickets = get_tickets(open_tickets_for_su(su))
        except WebFault:
            print >> stderr, "No open tickets found for SU %s" % su
            print zero_template % su
            continue
        
        status_classification = {}
        priority_classification = {}
        for i in statuses:
            status_classification[i] = []
        
        for i in priorities:
            priority_classification[i] = []
        
        for t in tickets:
            status = ticket_status(t)
            status_classification[status].append(t)
        
        for t in tickets:
            prio = ticket_priority(t)
            priority_classification[prio].append(t)
        
        print template_line % (su,
                               len(status_classification[statuses[0]]),
                               len(status_classification[statuses[1]]),
                               len(status_classification[statuses[2]]),
                               len(status_classification[statuses[3]]),
                               len(status_classification[statuses[4]]),
                               len(priority_classification[priorities[0]]),
                               len(priority_classification[priorities[1]]),
                               len(priority_classification[priorities[2]]),
                               len(priority_classification[priorities[3]]))
        

def print_overall_report(twiki_format=False):
    
    tickets = get_tickets(emi_third_level_open_tickets())
    
    status_classification = {}
    
    for i in statuses:
        status_classification[i] = []
    
    for t in tickets:
        status = ticket_status(t)
        status_classification[status].append(t)
    
    assigned_priority_classification = {}
    
    for i in priorities:
        assigned_priority_classification[i] = []
    
    for t in status_classification['assigned']:
        prio = ticket_priority(t)
        assigned_priority_classification[prio].append(t)
    
    keys = {'now': datetime.now(),
            'numOpen': len(tickets),
            'numAssigned': len(status_classification['assigned']),
            'numInProgress': len(status_classification['in progress']),
            'numOnHold': len(status_classification['on hold']),
            'numReopened': len(status_classification['reopened']),
            'numWaitingForReply': len(status_classification['waiting for reply']),
            'numTopPriority': len(assigned_priority_classification['top priority']),
            'numVeryUrgent': len(assigned_priority_classification['very urgent']),
            'numUrgent': len(assigned_priority_classification['urgent']),
            'numLessUrgent': len(assigned_priority_classification['less urgent'])
            }
    now = datetime.now()
    
    if twiki_format:
        print "---+ Support status report %d-%d-%d" % (now.day, now.month, now.year)
        print "<verbatim>"
        print
    
    print report_template.safe_substitute(keys)
    print "Assigned ticket detail (per priority):"
    print
    print_assigned_tickets_report(assigned_priority_classification)
    
    if twiki_format:
        print "</verbatim>"

