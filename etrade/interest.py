#!/usr/bin/env python
# encoding: utf-8

"""
Library for interest record-related functions
"""

from etrade.record import Record

class Interest(Record):
    """
    Interest gained.
    """
    def __init__(self):
        super(Interest, self).__init__()
        self.date = None
        self.transaction_type = None
        self.amount = None

    @classmethod
    def from_record(cls, single_line_record):
        """
        Parse an interest record from a given PDF record
        """
        record = cls()
        record.date = cls.string_to_datetime(single_line_record[0:8])
        _, record.transaction_type, single_line_record = \
                single_line_record.split(' ', 2)
        _, record.amount = \
                single_line_record.rsplit(' ', 1)
        record.amount = float(record.amount)
        return record

    def __repr__(self):
        return ','.join([str(x) for x in [self.date, self.transaction_type,
            self.amount]])

    @classmethod
    def is_single_line(cls, transaction_record):
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
    for record in text_block:
        if record.find('Interest') != -1:
            interest.append(Interest.from_record(record))
    return interest
