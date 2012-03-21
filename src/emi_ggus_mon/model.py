'''
Created on 17/ago/2011

@author: andreaceccanti
'''
from datetime import datetime
from operator import attrgetter
from su import emi_support_units
from suds.sudsobject import asdict
from ws import get_ticket, get_ticket_history, get_tickets
import sys


def get_ggus_tickets(query):
    
    ggus_tickets = []
    tickets = get_tickets(query)
    
    for t in tickets:
        ggus_tickets.append(get_ggus_ticket(ticket_id(t)))
    
    return ggus_tickets

def get_ggus_ticket(ticket_id):
    ggus_ticket = get_ticket(ticket_id)
    t = GGUSTicket(ggus_ticket)
    history = get_ticket_history(ticket_id)
    t.create_history(history)
    return t

def safe_get_item(l, index):
    if l:
        if index < len(l):
            return l[index]
    
    return None

def ticket_creation_time(ggus_ticket):
    return ggus_ticket['GHD_Date_Time_Of_Problem']

def ticket_url(ggus_ticket):
    return "https://ggus.eu/ws/ticket_info.php?ticket=%s" % ticket_id(ggus_ticket)

def ticket_id(ggus_ticket):
    return ggus_ticket['GHD_Request-ID']

def ticket_priority(ggus_ticket):
    return ggus_ticket['GHD_Priority']

def ticket_status(ggus_ticket):
    return ggus_ticket['GHD_Status']

def ticket_meta_status(ggus_ticket):
    return ggus_ticket['GHD_Meta_Status']

def ticket_su(ggus_ticket):
    return ggus_ticket['GHD_Responsible_Unit']

def ticket_short_description(ggus_ticket):
    return ggus_ticket['GHD_Short_Description']

def ticket_last_update(ggus_ticket):
    return ggus_ticket['GHD_Last_Update']

def ticket_date_of_change(ggus_ticket):
    return ggus_ticket['GHD_Date_Of_Change']

def ticket_internal_creation_time(ggus_ticket):
    return ggus_ticket['GHD_Date_Of_Creation']

class GGUSTicket:
    def __init__(self, ggus_ticket):
        self.ticket = ggus_ticket
        self.status_history = []
        self.priority_history = []
    
    def __repr__(self):
        
        if not self.ticket:
            return "undef"
    
        return ticket_id(self.ticket)
    
    def __priority_at_time(self, time):
        
        last_priority = ticket_priority(self.ticket)
        
        for i in self.priority_history:
            if i.time <= time:
                last_priority = i.priority
            else:
                break
        
        return last_priority
        
    def __cleanup_priority_history(self):
                
        last_prio = None
        to_be_removed = []
        
        for ele in self.priority_history:
            if not last_prio or (ele.priority != last_prio):
                last_prio = ele.priority
            else:
                to_be_removed.append(ele)
        
        for i in to_be_removed:
            self.priority_history.remove(i)
                
        
    def create_history(self, ggus_history):
        
        for item in ggus_history:
            item_dict = asdict(item)
            
            if not item_dict.has_key('GHI_Last_Modifier'):
                ## Ignore entries without the last modifier field
                ## as are not useful for us to calculate SLA status 
                continue
            
            if item_dict.has_key('GHI_Status') and item_dict['GHI_Status'] != None: 
                sc = StatusChange(time=item_dict['GHI_Creation_Date'], 
                                  status=item_dict['GHI_Status'], 
                                  su=item_dict['GHI_Support_Unit'],
                                  modifier=item_dict['GHI_Last_Modifier'])
                self.status_history.append(sc)
            
            elif item_dict.has_key('GHI_Priority') and len(item_dict['GHI_Priority']) > 0:
                
                pc = PriorityChange(time=item_dict['GHI_Creation_Date'],
                                    priority=item_dict['GHI_Priority'],
                                    su=None,
                                    modifier=item_dict['GHI_Last_Modifier'])
                self.priority_history.append(pc)
        
        self.status_history = sorted(self.status_history, key=attrgetter('time'))
        self.priority_history = sorted(self.priority_history, key=attrgetter('time'))
        self.__cleanup_priority_history()
        
        
    def print_status_history(self):
        self.__print_history(self.status_history)
    
    def print_priority_history(self):
        for pi in self.priority_history:
            print pi
    
    def __print_history(self, history):
        if not history or len(history) == 0:
            print 'empty history'
            return
        
        last_date = None
        for c in history:
            if last_date is None:
                last_date = c.time
                print c 
            else:
                time_diff = c.time - last_date
                print c, "(%s)" % time_diff
                last_date = c.time
    
    def solution_time(self):
        
        
        last_solution_time = None
        
        for sc in self.status_history:
            if sc.status == 'solved' or sc.status == 'unsolved':
                last_solution_time = sc.time
        
         
        if last_solution_time:
            time_to_solution = last_solution_time - self.assigned_time()
            
#            print >>sys.stderr, "(%s) %s - %s [assigned: %s,lst: %s,tts: %s]" % (ticket_su(self.ticket),
#                                                                                 ticket_url(self.ticket),
#                                                                                 ticket_priority(self.ticket),
#                                                                                 self.assigned_time(),
#                                                                                 last_solution_time,
#                                                                                 time_to_solution)
            return time_to_solution 
        
        return None
    
    def new_time(self):
        for sc in self.status_history:
            if sc.status == 'new':
                return sc.time
        
        return ticket_internal_creation_time(self.ticket)
        
    def assigned_time(self):
        
        last_assigned_time = None
        for sc in self.status_history:
            if sc.su in emi_support_units.keys():
                if sc.status == 'assigned':
                    last_assigned_time = sc.time
        
        return last_assigned_time
        
    def get_sla_compliance_values(self):
        
        priority_when_assigned = None
        last_status_seen = None
        retval = {}
        
        for sc in self.status_history:
            if sc.su in emi_support_units.keys():
                if sc.status == 'assigned':
                    priority_when_assigned = self.__priority_at_time(sc.time)
                    retval[sc.su] = SLAComplianceValue(sc.su,priority_when_assigned, sc.time, None, None, None)
                elif sc.status == 'in progress':
                    
                    if last_status_seen == 'in progress':
                        continue
                    
                    if retval.has_key(sc.su):
                        retval[sc.su].in_progress_time = sc.time
                        retval[sc.su].out_of_assigned_time = sc.time
                        retval[sc.su].out_of_assigned_status = sc.status
                    else:
                        raise Exception, "Found in progress transition before a ticket was assigned to the %s SU." % sc.su
                else:
                    if retval.has_key(sc.su):
                        if retval[sc.su].assigned_time:
                            retval[sc.su].out_of_assigned_time = sc.time
                            retval[sc.su].out_of_assigned_status = sc.status
                
                last_status_seen = sc.status
        
        return retval
    

class SLAComplianceValue(object):
    def __init__(self, su, prio, assigned_time, in_progress_time, ooa_time, ooa_status):
        self.su = su
        self.priority_when_assigned = prio
        self.assigned_time = assigned_time
        self.in_progress_time = in_progress_time
        self.out_of_assigned_time = ooa_time
        self.out_of_assigned_status = ooa_status
    
    def __repr__(self):
        return "%s - %s (assigned: %s, in_progress: %s, out_of_assigned: %s, out_of_assign_status: %s)" % (self.su,
                                                                                                       self.priority_when_assigned,
                                                                                                       self.assigned_time,
                                                                                                       self.in_progress_time,
                                                                                                       self.out_of_assigned_time,
                                                                                                       self.out_of_assigned_status)
class StatusChange(object):
    def __init__(self, time, status, su, modifier):
        self.time = time
        self.status = status
        self.su = su
        self.modifier = modifier
        
    def __repr__(self):
        return "%s - %s, %s - (%s)" % (self.time, self.su, self.status, self.modifier)

class PriorityChange(StatusChange):
    def __init__(self, time, priority, su, modifier):
        super(PriorityChange, self).__init__(time, None, su, modifier)
        self.priority = priority
    
    def __repr__(self):
        return "%s - Priority: %s - (%s)" % (self.time, self.priority, self.modifier)