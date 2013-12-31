#!/usr/bin/env python
# encoding: utf-8

"""
Library for promotion record-related functions
"""

from etrade.record import Record

class Promotion(Record):
    """
    E*Trade promotions
    """
    def __init__(self):
        super(Promotion, self).__init__()
        self.date = None
        self.transaction_type = None
        self.amount = None

    def __repr__(self):
        return ','.join([str(x) for x in [self.date, self.transaction_type,
            self.amount]])

    @classmethod
    def from_string(cls, csv_record):
        record = cls()
        record.date, record.transaction_type, record.amount = csv_record.split(',')
        record.date = cls.string_to_datetime(record.date, '%Y-%m-%d')
        record.amount = float(record.amount)
        return record

    @staticmethod
    def is_single_line(transaction_record):
        """
        Does this interest record exist entirely on one line?
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
    interest = []
    text_block = text_block.split('\n')
    for i, record in enumerate(text_block):
        if record.find('Interest') != -1:
            if record.find('FROM') != -1: # Implies margin interest
                record = record + ' ' + text_block[i+1]
                try:
                    record = Interest.from_record(record)
                except ValueError:
                    record = record + ' ' + text_block[i+2]
                    record = Interest.from_record(record)
                record.amount = -record.amount
                interest.append(record)
            else:
                interest.append(Interest.from_record(record))
    return interest
