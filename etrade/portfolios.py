#!/usr/bin/env python
# encoding: utf-8

"""
A Portfolio class
"""

from collections import defaultdict

class Portfolio(object):
    def __init__(self):
        # The things that make a portfolio
        self.positions = dict() # {date: [{asset}...]}
        self.cash = int()

        # The history one needs
        self.trades = []
        self.deposits = []
        self.withdrawals = []
        self.dividends = []
        self.interest = []

    def __repr__(self):
        print "Assets:"
        for position in self.positions:
            print position
        print "Cash: %s" % self.cash

    def _sort_activity(self):
        """
        Return a time-sorted list of all activity
        """
        activity = []
        activity.extend(self.trades)
        activity.extend(self.deposits)
        activity.extend(self.withdrawals)
        activity.extend(self.dividends)
        activity.extend(self.interest)
        activity.sort(key=lambda x: x.date)
        return activity

    def add_trades(self, trades):
        """
        Add a list of trades to this portfolio
        """
        self.trades.extend(trades)

    def add_deposits(self, deposits):
        """
        Add a list of deposits to this portfolio
        """
        self.deposits.extend(deposits)

    def add_withdrawals(self, withdrawals):
        """
        Add a list of withdrawals to this portfolio
        """
        self.withdrawals.extend(withdrawals)

    def add_dividends(self, dividends):
        """
        Add a list of dividends to this portfolio
        """
        self.dividends.extend(dividends)

    def add_interest(self, interest):
        """
        Add a list of interest activity to this portfolio
        """
        self.interest.extend(interest)

def parse_record(record, position_dict):
    if record.transaction_type == "Contrib":
        position_dict['Cash'] += record.amount
    elif record.transaction_type == "Dividend":
        position_dict['Cash'] += record.amount
    elif record.transaction_type == "Bought":
        print record.__dict__
    else:
        print record.transaction_type, record.__dict__

def build_portfolio(activities):
    #activities = self._sort_activity()
    current_date = activities[0].date
    position_dict = defaultdict(dict)
    position_dict['Cash'] = 0
    for activity in activities:
        parse_record(activity, position_dict)

    print position_dict
