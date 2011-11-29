'''
Created on 18/ago/2011

@author: andreaceccanti
'''
import unittest
from business import BusinessCalendar
from datetime import datetime, date, timedelta

class BusinessHoursTest(unittest.TestCase):
    
    def testNoOperation(self):
        monday_at_9 = datetime(2011,8,15,9,0,0)
        cal = BusinessCalendar(start_date=monday_at_9)
        
        self.assertEquals(monday_at_9, cal.add_business_days(0))
        self.assertEquals(monday_at_9, cal.add_business_hours(0))
    
    def testAddOneDayMonday(self):
        monday_at_9 = datetime(2011,8,15,9,0,0)
        next_business_day = datetime(2011,8,16,9,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_9)
        self.assertEquals(next_business_day, cal.add_business_days(1))
    
    def testAddOneDayFriday(self):
        friday_at_16 = datetime(2011,8,19,16,0,0)
        next_business_day = datetime(2011,8,22,16,0,0)
        
        cal = BusinessCalendar(start_date=friday_at_16)
        self.assertEquals(next_business_day, cal.add_business_days(1))
    
    def testAddOneDaySunday(self):
        sunday_at_10 = datetime(2011,8,28,10,0)
        next_business_day = datetime(2011,8,30,9,0,0)
        
        cal = BusinessCalendar(start_date=sunday_at_10)
        self.assertEquals(next_business_day, cal.add_business_days(1))
    
        
    def testAddAWeek(self):
        monday_at_9 = datetime(2011,8,15,9,0,0)
        five_bd_after = datetime(2011,8,22,9,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_9)
        self.assertEquals(five_bd_after, cal.add_business_days(5))
    
    def testLateNonWorkingHour(self):
        monday_at_22 = datetime(2011,8,15,22,0,0)
        one_business_day_after = datetime(2011,8,17,9,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_22)
        self.assertEquals(one_business_day_after, cal.add_business_days(1))
    
    def testEarlyNonWorkingHour(self):
        monday_at_4 = datetime(2011,8,15,4,0,0)
        one_business_day_after = datetime(2011,8,16,9,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_4)
        self.assertEquals(one_business_day_after, cal.add_business_days(1))

    
    def testAddHoursInWorkingDay(self):
        monday_at_9 = datetime(2011,8,15,9,0,0)
        monday_at_12 = datetime(2011,8,15,12,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_9)
        self.assertEquals(monday_at_12, cal.add_business_hours(3))
    
    def testAdd10HoursinWorkingDay(self):
        monday_at_9 = datetime(2011,8,15,9,0,0)
        tuesday_at_11 = datetime(2011,8,16,11,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_9)
        self.assertEquals(tuesday_at_11, cal.add_business_hours(10))
    
    def testAddHoursOutsideOfficeHours(self):
        monday_at_4 = datetime(2011,8,15,4,0,0)
        monday_at_12 = datetime(2011,8,15,12,0,0)
        
        cal = BusinessCalendar(start_date=monday_at_4)
        self.assertEquals(monday_at_12, cal.add_business_hours(3))
    
    def testAddHoursFriday(self):
        friday_at_16 = datetime(2011,8,19,16,0,0)
        monday_at_12 = datetime(2011,8,22,12,0,0)
        
        cal = BusinessCalendar(start_date=friday_at_16)
        self.assertEquals(monday_at_12,cal.add_business_hours(4))
    
    def testHolidays1(self):
        ferragsto_at_9 = datetime(2011,8,15,9,0,0)
        nbd = datetime(2011,8,17,9,0,0)
        cal = BusinessCalendar(start_date=ferragsto_at_9, holidays=[date(2011,8,15)])
        self.assertEquals(nbd, cal.add_business_days(1))
    
    def testHolidays2(self):
        sunday_at_10 = datetime(2011,8,28,10,0)
        nbd = datetime(2011,9,2,9,0)
        holidays = [date(2011,8,x) for x in range(29,32)]
        
        cal = BusinessCalendar(start_date=sunday_at_10, holidays=holidays)
        self.assertEquals(nbd, cal.add_business_days(1))
    
    def testAddTimeDelta(self):
        monday_at_9 = datetime(2011,8,15,9,0,0)
        nbd = datetime(2011,8,17,13,0,0)
        
        t = timedelta(days=1, hours=12)
        cal = BusinessCalendar(start_date=monday_at_9)
        
        self.assertEquals(nbd, cal.add_business_time(t))
    
    def test15days(self):
        
        sd = datetime(2011,8,1,9,0)
        nbd = datetime(2011,8,22,9,0)
        cal = BusinessCalendar(start_date=sd)
        self.assertEquals(nbd, cal.add_business_days(15))
    
    def test40days(self):
        sd = datetime(2011,8,1,9,0)
        nbd = datetime(2011,9,26,9,0)
        cal = BusinessCalendar(start_date=sd)
        self.assertEquals(nbd, cal.add_business_days(40))
    
    def testSameDateCount(self):
        sd = datetime(2011,8,1,9,0)
        ed = datetime(2011,8,1,9,0)
        cal = BusinessCalendar(start_date=sd)
        self.assertEquals(0, cal.count_business_days(ed))
    
    def test1DayCount(self):
        sd = datetime(2011,8,1,9,0)
        ed = datetime(2011,8,2,9,0)
        cal = BusinessCalendar(start_date=sd)
        self.assertEquals(1, cal.count_business_days(ed))
        
    def test6DaysCount(self):
        sd = datetime(2011,8,1,9,0)
        ed = datetime(2011,8,9,9,0)
        cal = BusinessCalendar(start_date=sd)
        self.assertEquals(6, cal.count_business_days(ed))
    
    def test15DaysCount(self):
        sd = datetime(2011,8,1,9,0)
        ed = datetime(2011,8,22,9,0)
        cal = BusinessCalendar(start_date=sd)
        self.assertEquals(15, cal.count_business_days(ed))
    
    def testSelfIntegrity(self):
        sd = datetime(2011,8,1,9,0)
        cal = BusinessCalendar(start_date=sd)
        ed = cal.add_business_days(18)
        self.assertEquals(18,cal.count_business_days(ed))
        
if __name__ == "__main__":
    
    unittest.main()