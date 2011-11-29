'''
Created on 30/set/2011

@author: andreaceccanti
'''
import unittest
import logging
from ws import get_ticket, get_ticket_history

from su import emi_1st_level_su, emi_3rd_level_su

class Test(unittest.TestCase):
    
    def testSuDifference(self):
        print emi_3rd_level_su

    def testTicketAccess(self):
        
        ticket_no = "72982"
        ticket = get_ticket(ticket_no)
        print ticket
        
        ticket_history = get_ticket_history(ticket_no)
        print ticket_history

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.FATAL)
    unittest.main()