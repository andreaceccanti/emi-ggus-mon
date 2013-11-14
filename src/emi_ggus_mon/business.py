'''
Created on 18/ago/2011

@author: andreaceccanti
'''
from datetime import datetime, timedelta
from copy import copy


def build_date(date, hour, minute):
    return datetime(date.year, date.month, date.day, hour, minute)

def seconds_to_hour(sec):
    return sec/3600

class BusinessCalendar(object):
    def __init__(self, start_date=datetime.now(), 
                 office_hours=[9,17], 
                 office_days=[0,1,2,3,4],
                 weekend_days=[5,6],
                 holidays=[]):
        
        self.office_hours = office_hours
        self.office_days = office_days
        self.holidays = holidays
        self.start_date=start_date
        self.weekend_days = weekend_days
        
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
              
    def add_business_time(self, timedelta):
        if timedelta is None:
            return self.start_date
        
        self.start_date = self.add_business_days(timedelta.days)
        self.start_date = self.add_business_hours(seconds_to_hour(timedelta.seconds))
        
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
    
    def business_time_difference_in_minutes(self,d):
        
        if d <= self.start_date:
            return None
        
        hours_in_a_day = self.office_hours[1] - self.office_hours[0]
        day_count = self.count_business_days(d) - 2 # remove last and first days
        
        if day_count > 0:
            hours = day_count * hours_in_a_day
        else:
            hours = 0
        
        if self.start_date.hour < self.office_hours[0]:
            minutes_first_day = hours_in_a_day * 60
        elif self.start_date.hour >= self.office_hours[1]:
            minutes_first_day = 0
        else:    
            d2 = datetime(year=self.start_date.year,
                          month=self.start_date.month,
                          day=self.start_date.day,
                          hour=self.office_hours[1])
            
            minutes_first_day = (d2 - self.start_date).seconds // 60
            
        if d.hour >= self.office_hours[1]:
            minutes_last_day = hours_in_a_day * 60
        elif d.hour < self.office_hours[0]:
            minutes_last_day = 0
        else:
            d2 = datetime(year=d.year,
                          month=d.month,
                          day=d.day,
                          hour=self.office_hours[0])
            
            minutes_last_day = (d - d2).seconds // 60
            
        total_delay_in_minutes = hours * 60 + minutes_first_day + minutes_last_day  
        return total_delay_in_minutes
        
                    
    def count_business_days(self, date):
        if date <= self.start_date:
            return 0
        
        bd_counter = 0
        temp_date = self.start_date
        
        while temp_date < date:
            temp_date = self.__next_business_day(temp_date)
            bd_counter = bd_counter + 1
         
        return bd_counter