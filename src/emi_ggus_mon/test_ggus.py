'''
Created on 30/set/2011

@author: andreaceccanti
'''
from datetime import date, datetime
from emi_ggus_mon.model import ticket_id, ticket_meta_status, ticket_last_update,\
    ticket_date_of_change, get_ggus_tickets
from emi_ggus_mon.query import \
    emi_submitted_tickets_in_period_for_unassigned_sus,\
    third_level_submitted_tickets_in_period,\
    third_level_closed_tickets_in_period
from emi_ggus_mon.ws import get_tickets
from model import get_ggus_ticket, ticket_su
from query import emi_third_level_assigned_tickets, \
    emi_submitted_tickets_in_period
from suds import WebFault
from ws import get_ticket, get_ticket_history
import logging
import sys
import unittest


class Test(unittest.TestCase):
   
#    def testTicketAccess(self):
#        logging.basicConfig(level=logging.INFO)
#        logging.getLogger('suds.client').setLevel(logging.DEBUG)
#        logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#        logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
#        logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
#        
#        ticket_no = "78435"
#        ticket = get_ticket(ticket_no)
#        print ticket
#        
#        ticket_history = get_ticket_history(ticket_no)
#        print ticket_history
#        
#        g = get_ggus_ticket(ticket_no)
#        g.print_status_history()
#
#
#        su = ticket_su(ticket)
#        print su
#        sla_comp_values = g.get_sla_compliance_values()
#        print sla_comp_values


    def testThirdLevelQuery(self):
        
        start_date = date(2011,11,1)
        end_date = date(2011,11,7)
        
        query_str = third_level_closed_tickets_in_period(start_date,end_date)
        print query_str
        tickets = get_tickets(query_str)
        for t in tickets:
            print t
            ggus_t = get_ggus_ticket(ticket_id(t))
            
            print ticket_id(t)+"(%s) %s %s %s %s" % (ticket_su(t),ticket_meta_status(t),ticket_last_update(t),ggus_t.assigned_time(), ggus_t.solution_time().seconds / 3600 )
        
        
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ## Set the logging to DEBUG if you want to see the XML
    #logging.getLogger('suds.client').setLevel(logging.DEBUG)
    unittest.main()