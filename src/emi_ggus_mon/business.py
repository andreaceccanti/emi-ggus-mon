'''
Created on 18/ago/2011

@author: andreaceccanti
'''
from datetime import datetime, timedelta

def build_date(date, hour, minute):
    return datetime(date.year, date.month, date.day, hour, minute)

def seconds_to_hour(sec):
    return sec/3600

class BusinessCalendar(object):
    def __init__(self, start_date=datetime.now(), office_hours=[9,17], office_days=[0,1,2,3,4], holidays=[]):
        
        self.office_hours = office_hours
        self.office_days = office_days
        self.holidays = holidays
        self.start_date=start_date
        
        ## Remove duplicates from holidays
        if len(holidays) > 0:
            self.holidays = list(set(holidays))
        
        ## Adjust start date so that it falls in a business day
        if not self.__is_business_day(self.start_date):
            self.start_date = build_date(self.__next_business_day(self.start_date),
                                           self.office_hours[0],
                                           0)
        
        ## Adjust start date so that office hours are considered
        if self.start_date.hour < self.office_hours[0]:
            self.start_date = build_date(self.start_date, 
                                         self.office_hours[0],
                                         0)
        
        if self.start_date.hour > self.office_hours[1]:
            nb_day = self.__next_business_day(self.start_date)
            self.start_date = build_date(nb_day, 
                                         self.office_hours[0],
                                         0)
        
    
    def __next_business_day(self, d):
        if d is None:
            return None
        
        d = d + timedelta(days=1)
        
        if not d.weekday() in self.office_days:
            d = d + timedelta(days=(7 - d.weekday()))
            
        while d.date() in self.holidays:
            d = d + timedelta(days=1)
        
        return d
    
    def __in_office_hours(self, d):
        if d is None:
            return None
        if d.hour < self.office_hours[0] or d.hour > self.office_hours[1]:
            return False
        return True
        
    def __is_business_day(self, d):
        
        if d is None:
            return None
        
        if d.date() in self.holidays or (d.weekday() not in self.office_days):
            return False
        
        return True
              
    def add_business_time(self, t):
        if t is None:
            return self.start_date
        
        self.start_date = self.add_business_days(t.days)
        self.start_date = self.add_business_hours(seconds_to_hour(t.seconds))
        
        return self.start_date
        
    def add_business_days(self,days):
        if days == 0:
            return self.start_date
        
        temp_date = self.start_date
        
        for d in range(days):
            temp_date =  self.__next_business_day(temp_date)
            
        return temp_date
    
    def add_business_hours(self, hours):
        if hours == 0:
            return self.start_date
        
        temp_date = self.start_date + timedelta(hours=hours)
        
        if temp_date.hour > self.office_hours[1]:
            hour_diff = temp_date.hour - self.office_hours[1]
            temp_date = build_date(self.__next_business_day(temp_date),
                                   self.office_hours[0]+hour_diff,
                                   0)
        
        return temp_date 
            
        
    def count_business_days(self, date):
        if date <= self.start_date:
            return 0
        
        bd_counter = 0
        temp_date = self.start_date
        
        while temp_date < date:
            temp_date = self.__next_business_day(temp_date)
            bd_counter = bd_counter + 1
         
        return bd_counter