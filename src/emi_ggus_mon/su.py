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

cnaf_sus = {
    "ARGUS" : SupportUnit("ARGUS"),
    "StoRM" : SupportUnit("StoRM"),
    "VOMS" : SupportUnit("VOMS"),
    "VOMS-Admin" : SupportUnit("VOMS-Admin")
}

emi_1st_level_su = { 
                     "EMI QA" : SupportUnit("EMI QA"),
                     "EMI Release Management" : SupportUnit("EMI Release Management"),
                     "EMI Testbeds" : SupportUnit("EMI Testbeds")
                    }

emi_3rd_level_su = {
                     ## EMI SUs as sorted in GGUS report generator
                     "AMGA" : SupportUnit("AMGA"),
                     "APEL-EMI" : SupportUnit("APEL-EMI"),
                     "ARC" : SupportUnit("ARC"),
                     "ARGUS" : SupportUnit("ARGUS"),
                     "CREAM-BLAH" : SupportUnit("CREAM-BLAH"),
                     "DGAS" : SupportUnit("DGAS"),
                     "DPM Development" : SupportUnit("DPM Development"),
                     "EMI" : SupportUnit("EMI"),
                     "EMI Common": SupportUnit("EMI Common"),
                     "EMI Common Data Library": SupportUnit("EMI Common Data Library"),
                     "EMI UI": SupportUnit("EMI UI"),
                     "EMI WN": SupportUnit("EMI WN"),
                     "EMIR" : SupportUnit("EMIR"),
                     "FTS Development" : SupportUnit("FTS Development"),
                     "Gridsite" : SupportUnit("Gridsite"),
                     "Information System Development" : SupportUnit("Information System Development"),
                     "LFC Development" : SupportUnit("LFC Development"),
                     "MPI" : SupportUnit("MPI"),
                     "Proxyrenewal" : SupportUnit("Proxyrenewal"),
                     "SAGA-SD" : SupportUnit("SAGA-SD"),
                     "StoRM" : SupportUnit("StoRM"),
                     "UNICORE-Client" : SupportUnit("UNICORE-Client"),
                     "UNICORE-Server" : SupportUnit("UNICORE-Server"),
                     "VOMS" : SupportUnit("VOMS"),
                     "VOMS-Admin" : SupportUnit("VOMS-Admin"),
                     "WNodes" : SupportUnit("WNodes"),
                     "caNL" : SupportUnit("caNL"),
                     "dCache Support" : SupportUnit("dCache Support"),
                     "gLite Hydra" : SupportUnit("gLite Hydra"),
                     "gLite Identity Security" : SupportUnit("gLite Identity Security"),
                     "gLite Java Security" : SupportUnit("gLite Java Security"),
                     "gLite L&B" : SupportUnit("gLite L&B"),
                     "gLite Security" : SupportUnit("gLite Security"),
                     "gLite WMS" : SupportUnit("gLite WMS"),
                     "gLite Yaim Core" : SupportUnit("gLite Yaim Core"),
                     "lcg_util Development" : SupportUnit("lcg_util Development"),
                     
                     ## Middleware clients 
                     "gLite UI" : SupportUnit("gLite UI"),
                     "gLite WN" : SupportUnit("gLite WN"),
                     
                     ## Batch systems
                     "gLite LSF Utils" : SupportUnit("gLite LSF Utils"),
                     "gLite SGE Utils" : SupportUnit("gLite SGE Utils"),
                     "gLite Torque Utils" : SupportUnit("gLite Torque Utils"),
                     
                     }

emi_support_units = dict(emi_1st_level_su.items()+emi_3rd_level_su.items())
                     
still_unassigned_emi_su = ["gLite SGE Utils", "gLite LSF Utils", "gLite Torque Utils"]              
wrongly_assigned_emi_su = ["EGI Software Provisioning",
                           "EGI Software Provisioning Support"]
