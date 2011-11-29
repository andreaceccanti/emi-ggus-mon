'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from su import wrongly_assigned_emi_su, emi_1st_level_su
from datetime import datetime, date

def build_third_level_query_str(str):
    excluded_su = wrongly_assigned_emi_su + emi_1st_level_su.keys()  
    exclusion_str = "".join(["AND 'GHD_Responsible Unit' != \"%s\" " % i for i in excluded_su])
    return str+" "+ exclusion_str

def emi_open_tickets():
    return "'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Responsible Unit'!=\"%s\"" % "EGI Software Provisioning"

def emi_third_level_open_tickets():    
    return build_third_level_query_str("'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\"")

def emi_third_level_in_progress_tickets():
    return build_third_level_query_str("'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Status'!=\"assigned\"")

def emi_third_level_open_tickets_in_period(start_date,end_date):
    query_str = "'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Date/Time Of Problem' >= \"%s\" AND 'GHD_Date/Time Of Problem' < \"%s\"" % (start_date, end_date)
    return build_third_level_query_str(query_str)
    
def emi_closed_tickets():
    return "'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Closed\" AND 'GHD_Responsible Unit'!=\"%s\"" % "EGI Software Provisioning"

def all_tickets_for_su(su):
    return "GHD_Responsible Unit'=\"%s\"" % su

def open_tickets_for_su(su):
    return "'GHD_Meta Status'=\"Open\" AND 'GHD_Responsible Unit'=\"%s\"" % su

def open_tickets_for_su_in_period(su, start_date, end_date):
    
    return "'GHD_Meta Status'=\"Open\" AND 'GHD_Responsible Unit'=\"%s\" AND 'GHD_Date/Time Of Problem' >= \"%s\" AND 'GHD_Date/Time Of Problem' < \"%s\"" % (su, 
                                                                                                                                                              start_date.isoformat(' '),
                                                                                                                                                              end_date.isoformat(' '))

def closed_tickets_for_su(su):
    return "'GHD_Meta Status'=\"Closed\" AND 'GHD_Responsible Unit'=\"%s\"" % su

def emi_open_tickets_for_priority(priority):
    return "'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Priority'=\"%s\" AND 'GHD_Responsible Unit'!=\"%s\"" % ("EGI Software Provisioning",priority)

def emi_third_level_assigned_tickets():
    return build_third_level_query_str("'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Status'=\"assigned\"")