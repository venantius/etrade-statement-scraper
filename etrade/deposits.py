#!/usr/bin/env python
# encoding: utf-8

"""
Library for deposit record-related functions
"""

from etrade.record import Record

class Deposit(Record):
    """
    A deposit
    """
    def __init__(self):
        super(Deposit, self).__init__()
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
        _, record.amount = single_line_record.rsplit(' ', 1)
        record.amount = float(record.amount.replace(',',''))
        record.transaction_type = 'Deposit'
        return record

    def __repr__(self):
        return ','.join([str(x) for x in [self.date, self.transaction_type,
            self.amount]])

    @staticmethod
    def clean(record):
        x = record.find('DEPOSIT')
        end = record[x+7:]
        end = end.split(' ')
        if end[0][0:5] == "REFID":
            return record
        else:
            return record[:x+7] + end[1] + ' ' + end[0]
        
    @classmethod
    def is_single_line(cls, transaction_record):
        """
        Does this dividend record exist entirely on one line?
        """
        if transaction_record.find('Deposit ACH') != -1 and \
                transaction_record.find('REFID') != -1:
            return True
        else:
            return False

def get_records(text_block):
    """
    Get all the trades from a block of text listing trade records
    """
    #TODO: Refactor all of these into a classmethod for Record, then
    # set arguments for start, end, find, and non-single-line behavior
    start = text_block.find('(cid:87)(cid:73)(cid:84)(cid:72)(cid:68)'\
            '(cid:82)(cid:65)(cid:87)(cid:65)(cid:76)(cid:83)(cid:32)'\
            '(cid:38)(cid:32)(cid:68)(cid:69)(cid:80)(cid:79)(cid:83)'\
            '(cid:73)(cid:84)(cid:83) (cid:32)')
    end = text_block.find('NET WITHDRAWALS (cid:38) DEPOSITS')
    text_block = text_block[start:end]
    deposits = []
    text_block = text_block.split('\n')
    """
    for line in text_block:
        print line
    """
    for i, record in enumerate(text_block):
        if record.find('Deposit ACH') != -1:
            if Deposit.is_single_line(record):
                deposits.append(Deposit.from_record(record))
            elif len(record.split(' ')) < 1:
                continue
            else:
                record = ''.join([text_block[i], text_block[i+1], 
                    ' ', text_block[i-1]])
                record = Deposit.clean(record)
                record = Deposit.from_record(record)
                deposits.append(record)
    return deposits
