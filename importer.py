#!/usr/bin/env python
# encoding: utf-8

"""
The core executable for scraping E*Trade statements

USAGE:
    statement-scraper statements PDF...
    statement-scraper directories DIR...
    statement-scraper csv FILE...
"""

import docopt
import os
import scraper
import sys

from etrade import contributions
from etrade import deposits
from etrade import dividends
from etrade import interest
from etrade import trades
from etrade import withdrawals

from etrade.portfolios import Portfolio

def get_transactions(portfolio, statement_string):
    """
    Get all transactions from a text-formatted E*Trade statement. Returns a 
    Portfolio class object
    """
    start = statement_string.find('TRANSACTION HISTORY')
    transaction_block = statement_string[start:]
    
    portfolio.add_trades(trades.get_records(transaction_block))
    portfolio.add_dividends(dividends.get_records(transaction_block))
    portfolio.add_interest(interest.get_records(transaction_block))

    portfolio.add_deposits(deposits.get_records(transaction_block))
    portfolio.add_deposits(contributions.get_records(transaction_block))
    portfolio.add_withdrawals(withdrawals.get_records(transaction_block))

def parse_directory(dir_path):
    """
    Returns a list of statements formatted as strings
    """
    portfolio = Portfolio()
    for pdf in os.listdir(dir_path):
        print >> sys.stderr, "Parsing %s" % pdf
        if pdf[-4:] != '.pdf':
            continue
        pdf = os.path.join(dir_path, pdf)
        statement = scraper.get_pdf_as_string(pdf)
        get_transactions(portfolio, statement)
    return portfolio

DIR = '/Users/jarvis/Google Drive/Fund/Monthly Statements/ROTH/'
DIR = '/Users/jarvis/Google Drive/Fund/Monthly Statements/MAIN/'

def main(args):
    """Main parser"""
    portfolio = Portfolio()
    if args['statements']:
        for pdf in args['PDF']:
            statement = scraper.get_pdf_as_string(pdf)
            get_transactions(portfolio, statement)

    elif args['directories']:
        for directory in args['DIR']:
            portfolio = parse_directory(directory)

    elif args['csv']:
        for filename in args['FILE']:
            csv = open(filename)
            portfolio.parse_from_csv(csv)
        portfolio.build_portfolio()
        #portfolio.get_end_of_month_assets('2013-11-30')
        #portfolio.get_deltas()
        portfolio.get_commissions()


    """
    TRACKING: 
    ROTH DONE [lacking 2013-12]
    MAIN up to 2013-11-31

    Records of portfolio value:
    ROTH:
    2010-12-31: 3,920.45 [-49.95]
    2011-12-31: 3,616.26 [-29.97]
    2012-12-31: 6,922.26 [-29.97]
    2013-11-31: 13,551.97 [-29.97]

    MAIN:
    2009-12-31: 5,999.88
    2010-12-31: 12,115.33
    2011-12-31: 5,227.93
    2012-12-31: 12,560.06
    2013-11-31: 37,841.98

    COMBINED:
    2009-12-31: 5,999.88 [-207.9]
    2010-12-31: 16,035.78 [-339.38]
    2011-12-31: 8,844.19 [-611.5864]
    2012-12-31: 19,482.32 [-283.575]
    2013-11-31: 51,393.95 [-254.129]

    NOTES:
    2008-12-29 WH purchase had a commission of 12.99 that was reimbursed as part of some promo; the reimbursement came on 2009-01-26
    """
    """
    for record in portfolio._sort_activity():
        print record
        """

if __name__ == "__main__":
    main(docopt.docopt(__doc__))
