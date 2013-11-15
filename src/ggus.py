#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from datetime import datetime
from emi_ggus_mon import __version__
from emi_ggus_mon.report import print_assigned_ticket_status_report, \
    print_su_report, print_sla_report, print_sla_stats, \
    print_submitted_tickets_report, print_ksa_1_2, print_ksa_1_1,\
    print_eta_status_report, print_on_hold_report, print_ticket_history,\
    print_all_tickets_report
from optparse import OptionParser
from string import split
import logging
import sys
import codecs
from emi_ggus_mon.monitoring import check_ticket_status

SLA_START_DATE = datetime(2011,4,12,9,0,0)
SLA_START_MONITORING_DATE = datetime(2011,8,26,9,0,0)

def parse_period(period_str):
    dates = split(period_str,'-')
    return (datetime.strptime(dates[0],'%d/%m/%Y'),datetime.strptime(dates[1],'%d/%m/%Y'))
    
def main():
    
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.FATAL)
    
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
    
    parser = OptionParser()
    parser.add_option("-t", 
                      "--twiki-format", 
                      dest="twiki", 
                      help="Prepares output conforming to the EMI weekly ticket status report",
                      action="store_true", 
                      default=False)
    
    parser.add_option("-p", 
                      "--period", 
                      dest="period", 
                      help="Period for which the stats should be computed. It's a string in the format dd/mm/yyyy-dd/mm/yyyy Example: 01/01/2011-31/01/2011.")
    
    parser.add_option("-s",
                     "--su",
                     dest="su",
                     help="List of SUs for which the stats should be computed.")
    
    parser.add_option("", 
                      "--start", 
                      dest="start", 
                      help="Record start.")
    
    parser.add_option("", 
                      "--limit", 
                      dest="limit", 
                      help="Record limit.")
    
    parser.add_option("",
                      "--target_dir",
                      dest="target_dir",
                      help="HTML report target directory. The script will place the cnaf ggus report in the given directory.")
    
    parser.add_option("",
                      "--report_url",
                      dest="report_url",
                      help="URL where generated report can be accessed.")
    parser.add_option("",
                      "--recipients",
                      dest="recipients",
                      help="List of comma separated email addresses that will be notified of report generation.")
    
    parser.add_option("",
                      "--skip_notification",
                      dest="skip_notification",
                      action="store_true",
                      help="Generates the report but doesn't send out the notification",
                      default=False)
    
    
    (options, args) = parser.parse_args()
    
    print "emi-ggus-mon v. %s. " % __version__
    
    if len(args) == 0:
        print 
        print "Producing EMI support status report, please be patient..." 
        print 
        print_assigned_ticket_status_report(options.twiki)
    else:
        cmd = args[0]
        if cmd == "eta":
            print_eta_status_report()
          
        elif cmd == "on-hold":
            
            print_on_hold_report()
              
        elif cmd == 'su':
            print_su_report()
        
        elif cmd == 'sla':    
            start_date = SLA_START_DATE
            end_date = datetime.now()
            
            if options.period:
                (start_date,end_date) = parse_period(options.period)
            
            print_sla_stats(start_date, end_date)
        
        elif cmd == 'sla-su':
            start_date = SLA_START_DATE
            end_date = datetime.now()
            
            if options.period:
                (start_date,end_date) = parse_period(options.period)
            
            sus = None
            if options.su:
                sus = split(options.su,',')
            
            print_sla_report(start_date, end_date, sus)
            
        elif cmd == 'submitted-tickets':
            start_date = SLA_START_DATE
            end_date = datetime.now()
            
            if options.period:
                (start_date,end_date) = parse_period(options.period)
            
            print_submitted_tickets_report(start_date,end_date)
        
        elif cmd == 'ksa1.1':
            start_date = SLA_START_DATE
            end_date = datetime.now()
            
            if options.period:
                (start_date,end_date) = parse_period(options.period)
            
            print_ksa_1_1(start_date,end_date)
            
        elif cmd == 'ksa1.2':
            start_date = SLA_START_DATE
            end_date = datetime.now()
            if options.period:
                (start_date,end_date) = parse_period(options.period)
            
            print_ksa_1_2(start_date,end_date)
        
        elif cmd == "ticket-history":
            print_ticket_history(args[1:])
            
        elif cmd == "all-tickets":
            start = 0
            limit = -1
            
            if options.limit:
                limit = options.limit
            if options.start:
                start = options.start
            
            print_all_tickets_report(start,limit)
        
        elif cmd == 'cnaf':
            if options.target_dir is None:
                print >> sys.stderr, "Please set the --target_dir option!"
                sys.exit(2)
            
            if options.report_url is None:
                print >> sys.stderr, "Please set the --report_url option!"
                sys.exit(2)
            
            if not options.skip_notification and options.recipients is None:
                print >> sys.stderr, "Please set the --recipients option!"
                sys.exit(2)
            
            check_ticket_status(report_dir=options.target_dir, 
                                report_url=options.report_url,
                                recipients=options.recipients,
                                skip_notification=options.skip_notification)
        else:
            print >>sys.stderr, "Unknown command ", cmd
            sys.exit(1)

if __name__ == '__main__':
    main()
