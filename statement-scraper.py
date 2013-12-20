#!/usr/bin/env python
# encoding: utf-8

"""
The core executable for scraping E*Trade statements
"""

import scraper
import sys

from etrade import dividends
from etrade import trades

#from transactions import deposit
#from transactions import withdrawal
#from transactions import dividend

def get_deposit_records(statement_string):
    """
    Parses statement lines for all deposit records
    """
    for line in statement_string.split('\n'):
        if 'Contrib ACH' in line:
            print line
            # TODO; format this somehow

def get_dividend_and_interest_records(text_block):
    """
    Get all the records 
    #TODO: take the formatter function
    """
    text_block = text_block.split('\n')
    for i, line in enumerate(text_block):
        if single_line_transaction(line):
            print line
            #TODO: Format this, too
        elif starts_with_date(line):
            print ' '.join([text_block[i+1], line])
            #TODO: Format this // plug in to larger library

def get_dividends_and_interest(text_block):
    """
    Get all account contributions and distributions
    """
    start = text_block.find('(cid:68)(cid:73)(cid:86)(cid:73)(cid:68)(cid:69)(cid:78)(cid:68)(cid:83)(cid:32)(cid:38)(cid:32)(cid:73)(cid:78)(cid:84)(cid:69)(cid:82)(cid:69)(cid:83)(cid:84)(cid:32)(cid:65)(cid:67)(cid:84)(cid:73)(cid:86)(cid:73)(cid:84)(cid:89) (cid:32)')
    end = text_block.find('TOTAL DIVIDENDS (cid:38) INTEREST ACTIVITY')
    print text_block[start:end]
    get_dividend_and_interest_records(text_block[start:end])

def get_transactions(statement_string, parse_trades=True, parse_dividends=True, contrib_distrib=True):
    start = statement_string.find('TRANSACTION HISTORY')
    end = len(statement_string)
    transaction_block = statement_string[start:end]
    if parse_trades:
        trade_records = trades.get_records(transaction_block)
        for trade_record in trade_records:
            print trade_record

    if parse_dividends:
        dividend_records = dividends.get_records(transaction_block)
        for dividend_record in dividend_records:
            print dividend_record


def main():
    for pdf in sys.argv[1:]:
        statement = scraper.get_pdf_as_string(pdf)

        print "\n\nDEPOSITS\n\n"
        #deposits.get_deposits(statement)
        #print statement

        print "\n\nTRANSACTIONS\n\n"
        get_transactions(statement)


if __name__ == "__main__":
    main()
