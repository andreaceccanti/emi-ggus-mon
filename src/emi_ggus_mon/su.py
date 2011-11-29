'''
Created on 17/ago/2011

@author: andreaceccanti
'''

default_timezone=None
default_holidays=[]

class SupportUnit(object):
    
    def __init__(self, name, contact=None, timezone=default_timezone, holidays=default_holidays, office_hours=[9,17]):
        self.name = name
        self.contact = contact
        self.tz = timezone
        self.holidays = holidays
        self.office_hours = office_hours
    
    def timezone(self, tz=None):
        if not tz:
            return self.timezone
        self.tz=tz
    
    def office_hours(self, hours=None):
        if not hours:
            return self.office_hours
        self.office_hours = hours
        
    def holidays(self, holidays=None):
        if not holidays:
            return self.holidays
        self.holidays = holidays
    
emi_1st_level_su = { "EMI" : SupportUnit("EMI"),
                     "EMI QA" : SupportUnit("EMI QA"),
                     "EMI Release Management" : SupportUnit("EMI Release Management"),
                     "EMI Testbed" : SupportUnit("EMI Testbed")
                    }

emi_3rd_level_su = {"AMGA" : SupportUnit("AMGA"),
                     "APEL-EMI" : SupportUnit("APEL-EMI"),
                     "ARC" : SupportUnit("ARC"),
                     "ARGUS" : SupportUnit("ARGUS"),
                     "CREAM-BLAH" : SupportUnit("CREAM-BLAH"),
                     "dCache Support" : SupportUnit("dCache Support"),
                     "DGAS" : SupportUnit("DGAS"),
                     "DPM Development" : SupportUnit("DPM Development"),
                     "FTS Development" : SupportUnit("FTS Development"),
                     "gLite Hydra" : SupportUnit("gLite Hydra"),
                     "gLite Identity Security" : SupportUnit("gLite Identity Security"),
                     "gLite Java Security" : SupportUnit("gLite Java Security"),
                     "gLite L&B" : SupportUnit("gLite L&B"),
                     "gLite Security" : SupportUnit("gLite Security"),
                     "gLite WMS" : SupportUnit("gLite WMS"),
                     "gLite Yaim Core" : SupportUnit("gLite Yaim Core"),
                     "Gridsite" : SupportUnit("Gridsite"),
                     "Information System Development" : SupportUnit("Information System Development"),
                     "lcg_util Development" : SupportUnit("lcg_util Development"),
                     "LFC Development" : SupportUnit("LFC Development"),
                     "MPI" : SupportUnit("MPI"),
                     "Proxyrenewal" : SupportUnit("Proxyrenewal"),
                     "SAGA-SD" : SupportUnit("SAGA-SD"),
                     "StoRM" : SupportUnit("StoRM"),
                     "UNICORE-Client" : SupportUnit("UNICORE-Client"),
                     "UNICORE-Server" : SupportUnit("UNICORE-Server"),
                     "VOMS" : SupportUnit("VOMS"),
                     "VOMS-Admin" : SupportUnit("VOMS-Admin")}

emi_support_units = dict(emi_1st_level_su.items()+emi_3rd_level_su.items())
                     
                     
wrongly_assigned_emi_su = ["EGI Software Provisioning",
                           "EGI Software Provisioning Support"]
                           
       
