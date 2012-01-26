'''
Created on 30/set/2011

@author: andreaceccanti
'''
import unittest
import logging
from ws import get_ticket, get_ticket_history
from model import get_ggus_ticket, ticket_su

class Test(unittest.TestCase):
   
    def testTicketAccess(self):
        logging.basicConfig(level=logging.INFO)
#        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        #logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#        logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
        #logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
        
        ticket_no = "78435"
        ## ticket = get_ticket(ticket_no)
        ## print ticket
        
        ticket_history = get_ticket_history(ticket_no)
        print ticket_history
        
        g = get_ggus_ticket(ticket_no)
        g.print_status_history()


#        su = ticket_su(ticket)
#        print su
#        sla_comp_values = g.get_sla_compliance_values()
#        print sla_comp_values

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ## Set the logging to DEBUG if you want to see the XML
    #logging.getLogger('suds.client').setLevel(logging.DEBUG)
    unittest.main()