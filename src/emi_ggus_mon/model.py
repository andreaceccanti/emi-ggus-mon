'''
Created on 17/ago/2011

@author: andreaceccanti
'''
from suds.sudsobject import asdict
from operator import attrgetter

from su import emi_support_units
from ws import get_ticket, get_ticket_history, get_tickets



    
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

def ticket_creation_time(ggus_ticket):
    return ggus_ticket['GHD_Date_Time_Of_Problem'][0]

def ticket_id(ggus_ticket):
    return ggus_ticket['GHD_Request-ID'][0]

def ticket_priority(ggus_ticket):
    return ggus_ticket['GHD_Priority'][0]

def ticket_status(ggus_ticket):
    return ggus_ticket['GHD_Status'][0]

def ticket_su(ggus_ticket):
    return ggus_ticket['GHD_Responsible_Unit'][0]

def ticket_short_description(ggus_ticket):
    return ggus_ticket['GHD_Short_Description'][0]

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
            
            if item_dict.has_key('GHI_Status'):
                sc = StatusChange(time=item_dict['GHI_Creation_Date'], 
                                  status=item_dict['GHI_Status'], 
                                  su=item_dict['GHI_Support_Unit'],
                                  modifier=item_dict['GHI_Last_Modifier'])
                self.status_history.append(sc)
            
            elif item_dict.has_key('GHI_Priority'):
                
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
                
    
    def get_sla_compliance_values(self):
        
        priority_when_assigned = None
        retval = {}
        
        for sc in self.status_history:
            if sc.su in emi_support_units.keys():
                if sc.status == 'assigned':
                    priority_when_assigned = self.__priority_at_time(sc.time)
                    retval[sc.su] = SLAComplianceValue(sc.su,priority_when_assigned, sc.time, None, None, None)
                elif sc.status == 'in progress':
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