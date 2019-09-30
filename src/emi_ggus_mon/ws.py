'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from suds import WebFault
from suds.client import Client
from suds.plugin import MessagePlugin
import re

# This is due to a bug in the GGUS web service:
# https://ggus.eu/ws/ticket_info.php?ticket=77698


class FixRemindOnFieldPlugin(MessagePlugin):
    def received(self, context):
        (reply, num_changes) = re.subn(
            r'<ns0:GHD_Remind_On>.*</ns0:GHD_Remind_On>', '', context.reply)
        context.reply = reply


help_desk_url = "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/GGUS"
history_url = "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/Grid_History"

username = "emiuser"
password = "HpL6xVhu?"


def init_ggus_client(url):
    p = FixRemindOnFieldPlugin()

    c = Client(url, plugins=[p])
    auth_token = c.factory.create("AuthenticationInfo")
    auth_token.userName = username
    auth_token.password = password
    c.set_options(soapheaders=auth_token)
    return c


def get_ticket(ticket_id):
    ggus_client = init_ggus_client(help_desk_url)
    return ggus_client.service.TicketGet(ticket_id)


def get_tickets2(query1, query2):
    retval = []
    ggus_client = init_ggus_client(help_desk_url)

    list_result = ggus_client.service.TicketGetList(query1)

    for t in list_result:
        retval.append(ggus_client.service.TicketGet(t['GHD_Request-ID']))
    list_result = ggus_client.service.TicketGetList(query2)

    for t in list_result:
        retval.append(ggus_client.service.TicketGet(t['GHD_Request-ID']))

    return retval


def get_tickets(query, start=0, limit=-1):
    retval = []
    ggus_client = init_ggus_client(help_desk_url)
    list_result = ggus_client.service.TicketGetList(query,
                                                    startRecord=start,
                                                    maxLimit=limit)
    for t in list_result:
        retval.append(ggus_client.service.TicketGet(t['GHD_Request-ID']))

    return retval


def get_ticket_history(ggus_ticket):
    history_client = init_ggus_client(history_url)
    return history_client.service.OpGetTicketHist(ggus_ticket)


def cnaf_tickets():
    ggus_client = init_ggus_client(help_desk_url)

    all_results = []
    retval = []

    for su in ["VOMS", "VOMS-Admin", "StoRM", "ARGUS"]:
        su_result = []
        try:
            su_result = ggus_client.service.TicketGetList(GHD_Responsible_Unit=su,
                                                          GHD_Meta_Status="Open")
        except WebFault, f:
            # For some absurd reason the ggus web service raises an error when
            # a query has no results, instead of simply returning an
            # empty result
            if not (f.fault is None) and not (u'ERROR (302): Entry does not exist in database; ' in repr(f.fault.faultstring)):
                raise f

        print "%s open tickets : %d" % (su, len(su_result))
        all_results = all_results + su_result

    print "Open tickets found: ", len(all_results)

    for t in all_results:
        ticket = ggus_client.service.TicketGet(t['GHD_Request_ID'])
        retval.append(ticket)

    return retval
