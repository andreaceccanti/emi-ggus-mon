'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from suds.client import Client
from suds.plugin import MessagePlugin
import re

## This is due to a bug in the GGUS web service:
## https://ggus.eu/ws/ticket_info.php?ticket=77698
class FixRemindOnFieldPlugin(MessagePlugin):
    def received(self,context):
        (reply, num_changes) = re.subn(r'<ns0:GHD_Remind_On>.*</ns0:GHD_Remind_On>', '', context.reply)
        context.reply = reply

help_desk_url = "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/Grid_HelpDesk"
history_url = "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/Grid_History"

username = "emiuser"
password = "HpL6xVhu?"

def init_ggus_client(url):
    p = FixRemindOnFieldPlugin()
    
    c = Client(url, plugins=[p])
    auth_token = c.factory.create("AuthenticationInfo")
    auth_token.userName=username
    auth_token.password=password
    c.set_options(soapheaders=auth_token)
    return c

def get_ticket(ticket_id):
    ggus_client = init_ggus_client(help_desk_url)
    return ggus_client.service.TicketGet(ticket_id)

def get_tickets(query):
    retval = []
    ggus_client = init_ggus_client(help_desk_url)
    list_result = ggus_client.service.TicketGetList(query)
    for t in list_result:
        retval.append(ggus_client.service.TicketGet(t['GHD_Request-ID']))
     
    return retval

def get_ticket_history(ggus_ticket):
    history_client = init_ggus_client(history_url)
    return history_client.service.OpGetTicketHist(None,ggus_ticket)

