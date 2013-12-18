#!/usr/bin/env python
# encoding: utf-8

"""
The core executable for scraping E*Trade statements
"""

from datetime import datetime

import re
import scraper
import sys

#from transactions import deposit
#from transactions import withdrawal
#from transactions import dividend

def get_deposits(statement_string):
    for line in statement_string.split('\n'):
        if 'Contrib ACH' in line:
            print line
            # TODO; format this somehow

def starts_with_date(record_line):
    try:
        datetime.strptime(record_line[0:8], '%m/%d/%y')
        return True
    except Exception:
        return False

def single_line_transaction(transaction_record):
    if transaction_record.find('Bought') != -1 and starts_with_date(transaction_record):
        return True
    else:
        return False

def get_transactions(statement_string):
    start = statement_string.find('TRANSACTION HISTORY')
    end = statement_string.find('TOTAL SECURITIES ACTIVITY')
    transaction_block = statement_string[start:end]
    print transaction_block + '\n\n\n'
    transaction_records = transaction_block.split('\n')[3:] # skip the header fields for the table
    for i, line in enumerate(transaction_records):
        if single_line_transaction(line):
            print line
            #TODO: Format this, too
        elif starts_with_date(line):
            print ' '.join([line,transaction_records[i+1]])
            #TODO: Format this // plug in to larger library

def main():
    for pdf in sys.argv[1:]:
        statement = scraper.get_pdf_as_string(pdf)
        #get_deposits(statement)
        #print statement

        get_transactions(statement)


if __name__ == "__main__":
    main()
