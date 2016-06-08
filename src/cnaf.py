#!/usr/bin/env python
# -*- coding: utf-8 -*-
from emi_ggus_mon import __version__
from optparse import OptionParser
import logging
import sys
import codecs
from emi_ggus_mon.monitoring import check_ticket_status

def main():

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.FATAL)

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    parser = OptionParser()

    parser.add_option("",
                      "--target_dir",
                      dest="target_dir",
                      help="HTML report target directory. The script will place the cnaf ggus report in the given directory.")


    (options, args) = parser.parse_args()

    print "cnaf-mon v. %s. " % __version__

    if options.target_dir is None:
        print >> sys.stderr, "Please set the --target_dir option!"
        sys.exit(2)

    check_ticket_status(report_dir=options.target_dir)

if __name__ == '__main__':
    main()
