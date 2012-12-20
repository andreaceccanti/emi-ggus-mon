'''
Created on 17/ago/2011

@author: andreaceccanti
'''

from su import wrongly_assigned_emi_su, emi_1st_level_su
from datetime import datetime, date
from emi_ggus_mon.su import still_unassigned_emi_su, emi_3rd_level_su,\
    emi_support_units

def build_third_level_query_str(str):
    excluded_su = wrongly_assigned_emi_su + emi_1st_level_su.keys()  
    exclusion_str = "".join(["AND 'GHD_Responsible Unit' != \"%s\" " % i for i in excluded_su])
    return str+" "+ exclusion_str

def emi_open_tickets():
    return "'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Responsible Unit'!=\"%s\"" % "EGI Software Provisioning"

def emi_third_level_closed_tickets():
    query_str = "'GHD_Meta Status'=\"Closed\" AND ("
    emi_third_level_su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_3rd_level_su])[0:-3] + ")"
    return query_str+ emi_third_level_su_str

def emi_third_level_open_tickets():
    query_str = "'GHD_Meta Status'=\"Open\" AND ("
    emi_third_level_su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_3rd_level_su])[0:-3] + ")"
    return query_str+ emi_third_level_su_str
    

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
                                                                                                                                                              start_date.isoformat(' '),                                                                                                                                                           end_date.isoformat(' '))
def closed_tickets_for_su(su):
    return "'GHD_Meta Status'=\"Closed\" AND 'GHD_Responsible Unit'=\"%s\"" % su

def emi_open_tickets_for_priority(priority):
    return "'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Priority'=\"%s\" AND 'GHD_Responsible Unit'!=\"%s\"" % ("EGI Software Provisioning",priority)

def emi_third_level_assigned_tickets():
    return build_third_level_query_str("'GHD_EMI Ticket'=\"Yes\" AND 'GHD_Meta Status'=\"Open\" AND 'GHD_Status'=\"assigned\"")

def open_on_hold_tickets():
    query_str = "'GHD_Meta Status'=\"Open\" AND ("
    su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_support_units])[0:-3] + ") "
    on_hold_str = "AND 'GHD_Status' =\"on hold\""
    return query_str+su_str+on_hold_str

def open_very_urgent_and_top_priority_tickets():
    query_str = "'GHD_Meta Status'=\"Open\" AND ("
    su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_support_units])[0:-3] + ") "
    priority_str = "AND (('GHD_Priority' =\"very urgent\" or 'GHD_Priority'=\"top priority\"))" 
    return query_str+su_str+priority_str

def emi_submitted_tickets_in_period(start_date,end_date):
    query_str = "'GHD_Date/Time Of Problem' >= \"%s\" AND 'GHD_Date/Time Of Problem' <= \"%s\" AND 'GHD_Ticket Category' != \"Test\" AND 'GHD_Ticket Category' != \"Spam\" AND (" % (start_date, end_date)
    su_str = "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_support_units])[0:-3] + ")"
    return query_str+su_str

def emi_submitted_tickets_in_period_for_unassigned_sus(start_date,end_date):
    query_str = "'GHD_Date/Time Of Problem' >= \"%s\" AND 'GHD_Date/Time Of Problem' <= \"%s\" AND (" % (start_date, end_date)
    unassigned_sus_str ="".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in still_unassigned_emi_su])[0:-3] + ")"
    return query_str+unassigned_sus_str

def third_level_submitted_tickets_in_period(start_date,end_date):
    query_str = "'GHD_Date/Time Of Problem' >= \"%s\" AND 'GHD_Date/Time Of Problem' <= \"%s\" AND (" % (start_date, end_date)
    emi_third_level_su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_3rd_level_su])[0:-3] + ")"
    return query_str+ emi_third_level_su_str

def third_level_closed_tickets():
    query_str = "'GHD_Meta Status'=\"Closed\" AND ("
    emi_third_level_su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_3rd_level_su])[0:-3] + ")"
    return query_str+ emi_third_level_su_str

def third_level_closed_tickets_in_period(start_date,end_date):
    #query_str = "'GHD_Meta Status'=\"Closed\" AND 'GHD_Last_Update' >= \"%s\" AND 'GHD_Last_Update' < \"%s\" AND (" % (start_date, end_date)
    query_str = "'GHD_Meta Status'=\"Closed\" AND 'GHD_Last Update' >= \"%s\" AND 'GHD_Last Update' <= \"%s\" AND (" % (start_date.strftime("%s"),end_date.strftime("%s")) 
    emi_third_level_su_str= "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_3rd_level_su])[0:-3] + ")"
    return query_str+ emi_third_level_su_str

def emi_closed_tickets_in_period(start_date,end_date):
    query_str = "'GHD_Meta Status'=\"Closed\" AND 'GHD_Last Update' >= \"%s\" AND 'GHD_Last Update' <= \"%s\" AND (" % (start_date.strftime("%s"),end_date.strftime("%s"))
    su_str = "".join(["'GHD_Responsible Unit' = \"%s\" OR " % i for i in emi_support_units])[0:-3] + ")"
    return query_str+su_str
    
    