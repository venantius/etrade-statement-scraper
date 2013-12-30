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

    """
    for record in portfolio._sort_activity():
        print record
        """

if __name__ == "__main__":
    main(docopt.docopt(__doc__))
