#!/usr/bin/env python
# encoding: utf-8

"""
Library for trading record-related functions
"""

from etrade.record import Record

class Trade(Record):
    """
    A trade
    """
    def __init__(self):
        super(Trade, self).__init__()
        self.trade_date = None
        self.date = None # Settlement date
        self.symbol = None
        self.transaction_type = None
        self.quantity = None
        self.price = None
        self.commission = None

    @classmethod
    def from_record(cls, single_line_record):
        """
        Parse a trade from a given PDF record
        """
        trade = cls()
        trade.trade_date = cls.string_to_datetime(single_line_record[0:8])
        _, trade.date, single_line_record = \
                single_line_record.split(' ', 2)
        trade.date = cls.string_to_datetime(trade.date)
        (_, trade.symbol, trade.transaction_type, trade.quantity, trade.price, 
                amount) = single_line_record.rsplit(' ', 5)
        trade.quantity = float(trade.quantity)
        trade.price = float(trade.price)
        trade.commission = float(amount) - trade.quantity * trade.price
        return trade

    def __repr__(self):
        return ','.join([str(x) for x in [self.date, self.transaction_type,
            self.symbol, self.quantity, self.price, self.commission]])

    @classmethod
    def is_single_line(cls, transaction_record):
        """
        Does this trade record exist entirely on one line?
        """
        if (transaction_record.find('Bought') != -1 or 
                transaction_record.find('Sold') != -1):
            if cls.starts_with_date(transaction_record):
                return True
        else:
            return False

def get_records(text_block):
    """
    Get all the trades from a block of text listing trade records
    """
    start = text_block.find('(cid:83)(cid:69)(cid:67)(cid:85)(cid:82)(cid:73)'\
            '(cid:84)(cid:73)(cid:69)(cid:83)(cid:32)(cid:80)(cid:85)(cid:82)'\
            '(cid:67)(cid:72)(cid:65)(cid:83)(cid:69)(cid:68)(cid:32)(cid:79)'\
            '(cid:82)(cid:32)(cid:83)(cid:79)(cid:76)(cid:68) (cid:32)')
    end = text_block.find('TOTAL SECURITIES ACTIVITY')
    text_block = text_block[start:end].split('\n')
    trades = []
    for i, trade_record in enumerate(text_block):
        if Trade.is_single_line(trade_record):
            trades.append(Trade.from_record(trade_record))
        elif Trade.starts_with_date(trade_record):
            trade_record = ' '.join([trade_record, text_block[i+1]])
            trades.append(Trade.from_record(trade_record))
    return trades
