'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from suds.client import Client
from suds.plugin import MessagePlugin
import re
import socket
import httplib
from httplib import HTTPConnection, HTTPS_PORT
import ssl

class HTTPSConnection(HTTPConnection):
    "This class allows communication via SSL."
    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None):
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
            # this is the only line we modified from the httplib.py file
            # we added the ssl_version variable
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)

httplib.HTTPSConnection = HTTPSConnection

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

