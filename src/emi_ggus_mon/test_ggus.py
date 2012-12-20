'''
Created on 30/set/2011

@author: andreaceccanti
'''
from datetime import date, datetime
from emi_ggus_mon.model import ticket_id, ticket_meta_status, ticket_last_update, \
    ticket_date_of_change, get_ggus_tickets, ticket_status, ticket_eta
from emi_ggus_mon.query import \
    emi_submitted_tickets_in_period_for_unassigned_sus, \
    third_level_submitted_tickets_in_period, third_level_closed_tickets_in_period,\
    emi_third_level_open_tickets, emi_third_level_closed_tickets, open_very_urgent_and_top_priority_tickets
from emi_ggus_mon.ws import get_tickets, init_ggus_client, history_url,\
    help_desk_url
from model import get_ggus_ticket, ticket_su
from query import emi_third_level_assigned_tickets, \
    emi_submitted_tickets_in_period
from suds import WebFault
from ws import get_ticket, get_ticket_history
import csv
import logging
import re
import sys
import unittest
     
    
        
class Test(unittest.TestCase):
   
    def testTicketAccess(self):
        logging.basicConfig(level=logging.INFO)
        #logging.getLogger('suds.client').setLevel(logging.DEBUG)
        #logging.getLogger('suds.transport').setLevel(logging.DEBUG)
        #logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
        #logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
        
#        ticket_no = "78435"
#        ticket = get_ticket(ticket_no)
#        print ticket
#        
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
        
        query = open_very_urgent_and_top_priority_tickets()
        print query
        ggus_client = init_ggus_client(help_desk_url)
        
        tickets = get_tickets(query)
        
        for t in filter(lambda t: ticket_eta(t) is None, tickets):
            print t
            print ticket_id(t), ticket_eta(t)
        
        print len(tickets)
        
     
        
        
        
        
        
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ## Set the logging to DEBUG if you want to see the XML
    #logging.getLogger('suds.client').setLevel(logging.DEBUG)
    unittest.main()