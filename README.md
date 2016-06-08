# The EMI GGUS support monitor

The EMI GGUS support monitor is a python script
that provides insight on the status and performance
of EMI support by contacting the GGUS [0] web services.

## Dependencies

  * python >= 2.4
  * python-suds >= 0.3.9 [1]
  

## Installation instructions

To install this package on your machine, please type (as root):

python setup.py install

## Usage

Type:

ggus.py

in order to generate the support status report.

In order to generate a support status report compliant
with EMI support status record archive [2], use the following
command:

ggus.py --twiki-format 


## Contact & Support

For any information, contact:

andrea.ceccanti@cnaf.infn.it

== References

[0] https://ggus.eu/pages/home.php
[1] https://fedorahosted.org/suds/
[2] https://twiki.cern.ch/twiki/bin/view/EMI/TSA15WeeklyTicketStatus

