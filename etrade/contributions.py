#!/usr/bin/env python
# encoding: utf-8

"""
Library for contribution record-related functions
"""

from etrade.record import Record

class Contribution(Record):
    """
    A contribution
    """
    def __init__(self):
        super(Contribution, self).__init__()
        self.date = None
        self.transaction_type = None
        self.amount = None

    @classmethod
    def from_record(cls, single_line_record):
        """
        Parse a dividend record from a given PDF record
        """
        record = cls()
        record.date = cls.string_to_datetime(single_line_record[0:8])
        _, _, record.transaction_type, single_line_record = \
                single_line_record.split(' ', 3)
        _, record.amount = single_line_record.rsplit(' ', 1)
        record.amount = float(record.amount)
        return record

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

    @classmethod
    def is_single_line(cls, transaction_record):
        """
        Does this dividend record exist entirely on one line?
        """
        if len(transaction_record.split(' ')) == 6:
            return True
        else:
            return False

def get_records(text_block):
    """
    Get all the trades from a block of text listing trade records
    """
    start = text_block.find('(cid:67)(cid:79)(cid:78)(cid:84)(cid:82)(cid:73)'\
            '(cid:66)(cid:85)(cid:84)(cid:73)(cid:79)(cid:78)(cid:83)(cid:32)'\
            '(cid:38)(cid:32)(cid:68)(cid:73)(cid:83)(cid:84)(cid:82)(cid:73)'\
            '(cid:66)(cid:85)(cid:84)(cid:73)(cid:79)(cid:78)(cid:83)(cid:32)'\
            '(cid:65)(cid:67)(cid:84)(cid:73)(cid:86)(cid:73)(cid:84)(cid:89)'\
            ' (cid:32)')
    end = text_block.find('TOTAL CONTRIBUTIONS')
    text_block = text_block[start:end]
    contributions = []
    text_block = text_block.split('\n')
    for i, record in enumerate(text_block):
        if record.find('Contrib ACH') != -1:
            if Contribution.is_single_line(record):
                contributions.append(Contribution.from_record(record))
            else:
                record = ''.join([record, text_block[i+1]])
                record = ' '.join([record, text_block[i-1]])
                contributions.append(Contribution.from_record(record))
    return contributions
