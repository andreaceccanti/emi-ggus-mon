# -*- coding: utf-8 -*- 
'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from datetime import timedelta
from operator import attrgetter
from su import emi_support_units
from suds.sudsobject import asdict
from ws import get_ticket, get_ticket_history, get_tickets
from emi_ggus_mon.business import BusinessCalendar


GGUS_PRIORITY_MAP = {"less urgent":0,
                     "urgent":1,
                     "very urgent":2,
                     "top priority": 3}

GGUS_PRIORITIES = ("less urgent", 
                   "urgent", 
                   "very urgent", 
                   "top priority")

GGUS_TERMINAL_STATES = ('solved',
                        'unsolved',
                        'closed',
                        'verified')

GGUS_OPEN_STATES = ('new', 
                    'assigned', 
                    'in progress',
                    'reopened',
                    'waiting for reply', 
                    'on hold')

GGUS_NEED_WORK_STATES = ('assigned',
                         'in progress',
                         'reopened' )

GGUS_ALL_STATES = GGUS_OPEN_STATES + GGUS_TERMINAL_STATES

SLA_CONSTRAINTS = { "top priority": timedelta(hours=4),
                    "very urgent": timedelta(days=2),
                    "urgent": timedelta(days=5),
                    "less urgent": timedelta(days=15)
                    }


def same_day(dt1,dt2):
    if dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day:
        return True
    return False

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
    return ggus_ticket['GHD_Request_ID']

def ticket_priority_index(ggus_ticket):
    return GGUS_PRIORITY_MAP[ticket_priority(ggus_ticket)]

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

def ticket_category(ggus_ticket):
    return ggus_ticket['GHD_Category']

def ticket_eta(ggus_ticket):
    return ggus_ticket['GHD_ETA']

def ticket_related_issue(ggus_ticket):
    return ggus_ticket['GHD_Related_Issue']

class GGUSTicket:
    def __init__(self, ggus_ticket):
        self.ticket = ggus_ticket
        self.status_history = []
        self.priority_history = []
        self.status_transitions = []
    
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
                
    
    def __expected_takeover_time(self, assigned_time):
        priority_when_assigned = self.__priority_at_time(assigned_time)
        bc = BusinessCalendar(assigned_time)
        return bc.add_business_time(SLA_CONSTRAINTS[priority_when_assigned])
    
    def create_history(self, ggus_history):
        
        for item in reversed(ggus_history):
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
            
            if item_dict.has_key('GHI_Priority') and len(item_dict['GHI_Priority']) > 0:
                if item_dict.has_key('GHI_Support_Unit'):
                    prio_su = item_dict['GHI_Support_Unit']
                else:
                    prio_su = None
                
                pc = PriorityChange(time=item_dict['GHI_Creation_Date'],
                                    priority=item_dict['GHI_Priority'],
                                    su=prio_su,
                                    modifier=item_dict['GHI_Last_Modifier'])
                self.priority_history.append(pc)
        
        self.status_history = sorted(self.status_history, key=attrgetter('time'))
        self.priority_history = sorted(self.priority_history, key=attrgetter('time'))
        self.__cleanup_priority_history()
        self.__create_status_transition()
    
    def closest_su_or_status_change_transition(self, t, dest_status_list=[]):
        for tt in self.status_transitions:
            if tt.end_time < t.end_time:
                continue
            
            if t == tt:
                continue
            
            if len(dest_status_list) > 0:
                if tt.end_state in dest_status_list:
                    return tt
            else:
                if tt.start_state == t.end_state:
                    if tt.end_state != t.end_state: 
                        return tt
                    if tt.end_su != tt.start_su:
                        return tt
        
        return None
    
    def emi_sus_assigned_transitions(self):
        
        def is_assigned(t):
            val = (t.start_su != t.end_su and t.end_su in emi_support_units and 
                   t.end_state == "assigned")
            return val
        
        return filter(is_assigned, self.status_transitions)
        
    def assigned_transitions(self, su):
        
        def is_assigned(t):
            val = (t.start_su != t.end_su and t.end_su == su and 
                   t.end_state == "assigned")
            return val
        
        return filter(is_assigned, self.status_transitions)
    
    
    def final_transitions(self,su):
        
        def is_final(t):
            val = (t.end_su == su and t.end_state != t.start_state and t.end_state in ['solved', 'unsolved', 'closed'])
            return val
        
        return filter(is_final, self.status_transitions)
    
    def out_of_assigned_transitions(self, su):
        
        def is_out_of_assigned(t):
            val = (t.start_su == t.end_su) and (t.end_su == su) and (t.start_state == "assigned" and t.end_state != "assigned")
            return val
         
        return filter(is_out_of_assigned, self.status_transitions)
        
    def __create_status_transition(self):
        
        if len(self.status_history) > 2:
            i = 0
            while (i+1 < len(self.status_history)):
                st = transtion_from_status_changes(self.status_history[i],
                                                   self.status_history[i+1])
                self.status_transitions.append(st)
                i = i+1

    def print_status_transitions(self):
        for t in self.status_transitions:
            print t
    
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
                ## In python 2.x __repr__ string must be ascii-only
                ## and not a unicode string, this changes with python 3.x
                print c.utf8repr(), "(%s)" % time_diff
                last_date = c.time    
        
    def last_solution_time(self):
        last_solution_time = None
        
        if ticket_status(self.ticket) in GGUS_TERMINAL_STATES:
            for sc in self.status_history:
                if sc.status == 'solved' or sc.status == 'unsolved':
                    last_solution_time = sc.time
        
        return last_solution_time
        
    def solution_time(self):
        
        last_solution_time = self.last_solution_time()        
         
        if last_solution_time:
            if self.assigned_time():
                time_to_solution = last_solution_time - self.assigned_time()
            else:
                raise RuntimeError('Assigned time not set for ticket %s' % ticket_url(self.ticket))
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
        
        if last_assigned_time is None:
            ## if no assigned time is set but there are
            ## in progress or on hold transitions for the ticket
            ## for the EMI su, we take those transitions as assigned
            ## time. This can happen for old tickets
            for sc in self.status_history:
                if sc.su in emi_support_units.keys() and sc.status in ['new','in progress', 'on hold']:
                    last_assigned_time = sc.time
                    
        return last_assigned_time
    
    def __bd_delay(self, expected_date, actual_date):
        if actual_date <= expected_date:
            return None
        
        return BusinessCalendar(expected_date).business_time_difference_in_minutes(actual_date)
    
    def get_sla_compliance_values2(self, check_su=None):
        
        compliance_values = []
        
        if check_su is None:
            transitions = self.emi_sus_assigned_transitions()
        else:
            su = ticket_su(self.ticket)
            transitions = self.assigned_transitions(su)
        
        for t in transitions:
            
            priority_when_assigned = self.__priority_at_time(t.end_time)
            expected_takeover_time = self.__expected_takeover_time(t.end_time)
            
            val = SLAComplianceValue(t.end_su, 
                                     priority_when_assigned,
                                     t.end_time)
            
            val.expected_takeover_time = expected_takeover_time
            
            out_of_assigned_transition = self.closest_su_or_status_change_transition(t)
            
            if out_of_assigned_transition:
                val.out_of_assigned_status = out_of_assigned_transition.end_state
                val.out_of_assigned_time = out_of_assigned_transition.end_time
            
                if out_of_assigned_transition.end_state == 'in progress':
                    val.in_progress_time = out_of_assigned_transition.end_time
                
                if out_of_assigned_transition.end_time > expected_takeover_time:
                    val.sla_delay = self.__bd_delay(expected_takeover_time, 
                                                    out_of_assigned_transition.end_time)
            
            compliance_values.append(val)
        
        return compliance_values

class StateTransition(object):
    
    def __init__(self,
                 start_su=None,
                 end_su=None,
                 start_state=None, 
                 end_state=None, 
                 time=None, 
                 priority=None, 
                 modifier=None):
        
        self.start_su = start_su
        self.end_su = end_su
        self.start_state = start_state
        self.end_state = end_state
        self.start_time = time
        self.end_time = None
        self.priority = priority
        self.modifier = modifier
        self.time_since_last_transition = None
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return " %s -> %s (start_time: %s, end_time: %s modifier: %s, su: %s -> %s, time delta: %s)" % (self.start_state,
                                                                    self.end_state,
                                                                    self.start_time,
                                                                    self.end_time,
                                                                    self.modifier,
                                                                    self.start_su,
                                                                    self.end_su,
                                                                    self.time_since_last_transition)
    
def transtion_from_status_changes(start_sc, end_sc):
    st = StateTransition()
    
    st.start_time = start_sc.time
    st.end_time = end_sc.time
    
    st.start_su = start_sc.su
    st.end_su = end_sc.su
    
    st.modifier = end_sc.modifier
    st.end_state = end_sc.status
    
    st.start_state = start_sc.status
    st.time_since_last_transition = end_sc.time - start_sc.time
    
    return st
    
class SLAComplianceValue(object):
    def __init__(self, su, prio, assigned_time, 
                 in_progress_time=None, 
                 ooa_time=None, 
                 ooa_status=None):
        self.su = su
        self.priority_when_assigned = prio
        self.assigned_time = assigned_time
        self.in_progress_time = in_progress_time
        self.out_of_assigned_time = ooa_time
        self.out_of_assigned_status = ooa_status
        self.expected_takeover_time = None
        self.sla_delay = None
    
    def __repr__(self):
        return "%s - %s (assigned: %s, expected_takeover: %s, in_progress: %s, out_of_assigned: %s, out_of_assign_status: %s, delay: %s)" % (self.su,
                                                                                                                                             self.priority_when_assigned,
                                                                                                                                             self.assigned_time,
                                                                                                                                             self.expected_takeover_time,
                                                                                                                                             self.in_progress_time,
                                                                                                                                             self.out_of_assigned_time,
                                                                                                                                             self.out_of_assigned_status,
                                                                                                                                             self.sla_delay)
class StatusChange(object):
    def __init__(self, time, status, su, modifier):
        self.time = time
        self.status = status
        self.su = su
        self.modifier = modifier
        
    def __repr__(self):
        return "%s - %s, %s - (%s)" % (self.time, self.su, self.status, self.modifier)
    
    
    def utf8repr(self):
        return u"%s - %s, %s - (%s)" % (self.time, self.su, self.status, self.modifier)

class PriorityChange(StatusChange):
    def __init__(self, time, priority, su, modifier):
        super(PriorityChange, self).__init__(time, None, su, modifier)
        self.priority = priority
    
    def __repr__(self):
        
        return "%s - %s  Priority: %s - (%s)" % (self.time, self.su, 
                                                 self.priority,
                                                 self.modifier)
