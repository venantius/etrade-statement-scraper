#!/usr/bin/env python
# encoding: utf-8

"""
Library for dividend record-related functions
"""

from etrade.record import Record

class Dividend(Record):
    """
    A dividend
    """
    def __init__(self):
        super(Dividend, self).__init__()
        self.date = None
        self.symbol = None
        self.transaction_type = None
        self.amount = None

    @classmethod
    def from_record(cls, single_line_record):
        """
        Parse a dividend record from a given PDF record
        """
        record = cls()
        record.date = cls.string_to_datetime(single_line_record[0:8])
        _, record.transaction_type, single_line_record = \
                single_line_record.split(' ', 2)
        _, record.symbol, record.amount = \
                single_line_record.rsplit(' ', 2)
        record.amount = float(record.amount)
        return record

    def __repr__(self):
        return ','.join([str(x) for x in [self.date, self.transaction_type,
            self.symbol, self.amount]])

    @classmethod
    def from_string(cls, csv_record):
        record = cls()
        record.date, record.transaction_type, record.symbol, record.amount = csv_record.split(',')
        return record

    @classmethod
    def is_single_line(cls, transaction_record):
        """
        Does this dividend record exist entirely on one line?
        """
        return False

def get_records(text_block):
    """
    Get all the trades from a block of text listing trade records
    """
    start = text_block.find('(cid:68)(cid:73)(cid:86)(cid:73)(cid:68)(cid:69)'\
            '(cid:78)(cid:68)(cid:83)(cid:32)(cid:38)(cid:32)(cid:73)(cid:78)'\
            '(cid:84)(cid:69)(cid:82)(cid:69)(cid:83)(cid:84)(cid:32)(cid:65)'\
            '(cid:67)(cid:84)(cid:73)(cid:86)(cid:73)(cid:84)(cid:89) (cid:32)')
    end = text_block.find('TOTAL DIVIDENDS (cid:38) INTEREST ACTIVITY')
    text_block = text_block[start:end]
    trades = []
    text_block = text_block.split('\n')
    """
    for line in text_block:
        print line
    print '\n'
    """
    for i, trade_record in enumerate(text_block):
        if trade_record.find('Dividend') != -1:
            try:
                if trade_record.find('PROCESSING FEE') != -1:
                    trade_record = ' '.join([trade_record, text_block[i+1]])
                    record = Dividend.from_record(trade_record)
                    record.amount = -record.amount
                    trades.append(record)
                else:
                    if text_block[i-1][0:4] == "DATE":
                        trade_record = ' '.join([trade_record, text_block[i+1]])
                        trades.append(Dividend.from_record(trade_record))
                    else:
                        trade_record = ' '.join([trade_record, text_block[i-1]])
                        trades.append(Dividend.from_record(trade_record))
            except Exception:
                print trade_record
    return trades
