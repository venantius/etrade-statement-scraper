#!/usr/bin/env python
# encoding: utf-8

"""
A Portfolio class
"""

from collections import defaultdict
from etrade.dividends import Dividend
from etrade.trades import Trade
from etrade.interest import Interest
from etrade.contributions import Contribution


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

    def parse_from_csv(self, csv):
        for csv_record in csv:
            csv_record = csv_record.strip()
            transaction_type = csv_record.split(',')[1]
            if transaction_type == "Bought" or transaction_type == "Sold":
                csv_record = Trade.from_string(csv_record)
                self.trades.append(csv_record)
            elif transaction_type == "Dividend":
                csv_record = Dividend.from_string(csv_record)
                self.dividends.append(csv_record)
            elif transaction_type == "Contrib":
                csv_record = Contribution.from_string(csv_record)
                self.deposits.append(csv_record)
            elif transaction_type == "Interest":
                csv_record = Interest.from_string(csv_record)
                self.interest.append(csv_record)
            else:
                raise Exception

    def parse_record(record, position_dict):
        if record.transaction_type == "Contrib":
            portfolio += record.amount
        elif record.transaction_type == "Dividend":
            position_dict['Cash'] += record.amount
        elif record.transaction_type == "Interest":
            position_dict['Cash'] += record.amount
        elif record.transaction_type == "Bought":
            position_dict['Cash'] -= record.amount
            position_dict[record.symbol] += record.quantity    
        else:
            print record.transaction_type, record.__dict__

    def build_portfolio(self):
        activities = self._sort_activity()
        current_date = activities[0].date
        for activity in activities:
            self.parse_record(activity)
