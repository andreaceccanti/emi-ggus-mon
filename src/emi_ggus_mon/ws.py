'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from suds.client import Client

help_desk_url = "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/Grid_HelpDesk"
history_url = "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/Grid_History"

username = "emiuser"
password = "HpL6xVhu?"

def init_ggus_client(url):
    c = Client(url)
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

