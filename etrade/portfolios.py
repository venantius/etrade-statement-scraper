#!/usr/bin/env python
# encoding: utf-8

"""
A Portfolio class
"""

import copy

from collections import defaultdict
from datetime import timedelta
    
from etrade.contributions import Contribution
from etrade.deposits import Deposit
from etrade.dividends import Dividend
from etrade.interest import Interest
from etrade.promotions import Promotion
from etrade.principal import Principal
from etrade.record import Record
from etrade.trades import Trade
from etrade.withdrawals import Withdrawal

class Portfolio(object):
    def __init__(self):
        # The things that make a portfolio
        self.portfolio = {}

        # The history one needs
        self.trades = []
        self.deposits = []
        self.withdrawals = []
        self.dividends = []
        self.interest = []
        self.principal = []
        self.promotions = []
        self.splits = []

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
        activity.extend(self.principal)
        activity.extend(self.promotions)
        activity.extend(self.splits)
        activity.sort(key=lambda x: x.date)
        return activity

    def get_commissions(self):
        """
        Return a list of commissions
        """
        trades = self.trades
        trades.sort(key=lambda x: x.date)
        commissions = defaultdict(float)
        for trade in trades:
            commissions[trade.date.year] += trade.commission
            print trade.date.year, trade.commission
        print commissions
    
    def get_deltas(self):
        """
        Return a list of deposits and withdrawals
        """
        deposits = self.deposits
        deposits.extend(self.withdrawals)
        deposits.sort(key=lambda x: x.date)
        for delta in deposits:
            if delta.transaction_type == "Withdrawal":
                print str(delta.date) + ',-' + str(delta.amount)
            elif delta.transaction_type == "Contrib" or \
                    delta.transaction_type == "Deposit":
                print str(delta.date) + ',' + str(delta.amount)
            else:
                print delta
                raise Exception

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
            elif transaction_type == "Deposit":
                csv_record = Deposit.from_string(csv_record)
                self.deposits.append(csv_record)
            elif transaction_type == "Withdrawal":
                csv_record = Withdrawal.from_string(csv_record)
                self.withdrawals.append(csv_record)
            elif transaction_type == "Principal":
                csv_record = Principal.from_string(csv_record)
                self.principal.append(csv_record)
            elif transaction_type == "Promotion":
                csv_record = Promotion.from_string(csv_record)
                self.promotions.append(csv_record)
            elif transaction_type == "Split":
                record = Record()
                record.transaction_type = "Split"
                csv_record = csv_record.split(',')
                record.date = Record.string_to_datetime(csv_record[0], '%Y-%m-%d')
                #record.date = csv_record[0]
                record.symbol = csv_record[2]
                record.split_from = int(csv_record[3])
                record.split_to = int(csv_record[4])
                self.splits.append(record)
            else:
                print csv_record
                raise Exception

    def parse_record(self, record, debug=False):
        """
        Updates the portfolio dictionary with a new record
        """
        if record.transaction_type == "Contrib" or \
                record.transaction_type == "Deposit":
            self.portfolio[record.date]['Cash'] += record.amount
        elif record.transaction_type == "Withdrawal":
            self.portfolio[record.date]['Cash'] -= record.amount
        elif record.transaction_type == "Dividend":
            self.portfolio[record.date]['Cash'] += record.amount
        elif record.transaction_type == "Principal":
            self.portfolio[record.date]['Cash'] += record.amount
        elif record.transaction_type == "Interest":
            self.portfolio[record.date]['Cash'] += record.amount
        elif record.transaction_type == "Bought":
            if record.is_option():
                self.portfolio[record.date]['Cash'] -= 100 * record.quantity * record.price + record.commission
                if debug:
                    print "BOUGHT", record.date, record.symbol, 100 * record.quantity * record.price + record.commission
            else:
                self.portfolio[record.date]['Cash'] -= record.quantity * record.price + record.commission
                if debug:
                    print "BOUGHT", record.date, record.symbol, record.quantity * record.price + record.commission
            self.portfolio[record.date][record.symbol] += record.quantity   
        elif record.transaction_type == "Sold":
            if record.is_option():
                if debug:
                    print "SOLD", record.date, record.symbol, 100 * record.quantity * record.price + record.commission
                self.portfolio[record.date]['Cash'] -= 100 * record.quantity * record.price + record.commission
            else:
                self.portfolio[record.date]['Cash'] -= record.quantity * record.price + record.commission
                if debug:
                    print "SOLD", record.date, record.symbol, record.quantity * record.price + record.commission
            self.portfolio[record.date][record.symbol] += record.quantity
            if self.portfolio[record.date][record.symbol] == 0:
                del(self.portfolio[record.date][record.symbol])
        elif record.transaction_type == "Promotion":
            self.portfolio[record.date]['Cash'] += record.amount
        elif record.transaction_type == "Split":
            self.portfolio[record.date][record.symbol] = \
                self.portfolio[record.date][record.symbol] / (record.split_from / record.split_to)
        else:
            print record.transaction_type, record.__dict__
            raise Exception

    def build_portfolio(self):
        """
        Builds the portfolio dictionary into a date: assets mapping.
        
        Assets are a defaultdict(float)
        """
        activities = self._sort_activity()
        current_date = activities[0].date
        self.portfolio[current_date] = defaultdict(float)
        self.portfolio[current_date]['Cash'] = 0.0
        for activity in activities:
            day_portfolio = defaultdict(float)
            while current_date != activity.date:
                current_date += timedelta(1)
                self.portfolio[current_date] = copy.copy(self.portfolio[current_date - timedelta(1)])
            self.parse_record(activity)
        while current_date.month == activity.date.month:
            current_date += timedelta(1)
            self.portfolio[current_date] = copy.copy(self.portfolio[current_date - timedelta(1)])

    def get_end_of_month_assets(self, final_date):
        """
        Gets the end of month asset map for each month
        """
        dates = sorted(self.portfolio.keys())
        final_date = Trade.string_to_datetime(final_date, '%Y-%m-%d')
        prior_date = dates[0]
        for date in dates:
            if date == final_date:
                print date, self.portfolio[date]
                break
            if date.month != prior_date.month:
                print prior_date, self.portfolio[prior_date]
            prior_date = date
        
