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

    def is_option(self):
        """
        Look at the symbol to see if this is an option
        """
        if self.symbol[0:4] == "CALL" or self.symbol[0:3] == "PUT":
            return True
        else:
            return False

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
                trade.amount) = single_line_record.strip().rsplit(' ', 5)
        trade.amount = float(trade.amount.replace(',', ''))
        trade.quantity = float(trade.quantity)
        trade.price = float(trade.price)
        if trade.transaction_type == "Bought":
            trade.commission = float(trade.amount) - \
                    trade.quantity * trade.price
        else:
            trade.commission = float(trade.amount) + \
                    trade.quantity * trade.price
        if trade.symbol == "CONTRACT":
            print record
            raise Exception
        return trade

    @classmethod
    def option_from_record(cls, single_line_record):
        """
        Parse an option trade from a given PDF record
        """
        trade = cls()
        record = single_line_record
        trade.trade_date = cls.string_to_datetime(single_line_record[0:8])
        _, trade.date, single_line_record = \
                single_line_record.split(' ', 2)
        trade.date = cls.string_to_datetime(trade.date)
        _temp = single_line_record.split()
        option_type = _temp[0]
        symbol = _temp[1]
        exercise_date = _temp[2]
        trade.symbol = '-'.join([option_type, symbol, exercise_date])
        (_, trade.transaction_type, trade.quantity, trade.price, 
                trade.amount) = single_line_record.strip().rsplit(' ', 4)
        trade.amount = float(trade.amount.replace(',', ''))
        trade.quantity = float(trade.quantity)
        trade.price = float(trade.price)
        if trade.transaction_type == "Bought":
            trade.commission = float(trade.amount) - \
                    (100 * trade.quantity) * trade.price
        else:
            trade.commission = float(trade.amount) + \
                    (100 * trade.quantity) * trade.price
        return trade

    def __repr__(self):
        return ','.join([str(x) for x in [self.date, self.transaction_type,
            self.symbol, self.quantity, self.price, self.commission]])

    @classmethod
    def from_string(cls, csv_record):
        """
        Parse a trade from a given CSV record
        """
        trade = cls()
        trade.date, trade.transaction_type, trade.symbol, trade.quantity, \
                trade.price, trade.commission = csv_record.split(',')
        trade.date = cls.string_to_datetime(trade.date, '%Y-%m-%d')
        trade.quantity = float(trade.quantity)
        trade.price = float(trade.price)
        trade.commission = float(trade.commission)
        return trade

    @staticmethod
    def record_is_option(transaction_record):
        """
        Is this trade record an options contract
        """
        if transaction_record.find("CONTRACT") != -1:
            return True
        else:
            return False

    @classmethod
    def is_single_line(cls, transaction_record):
        """
        Does this trade record exist entirely on one line?
        """
        if (transaction_record.find('Bought') != -1 or 
                transaction_record.find('Sold') != -1):
            if cls.starts_with_date(transaction_record) and \
                    cls.starts_with_date(' '.join(
                        transaction_record.split(' ')[1:])):
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
        try:
            if Trade.record_is_option(trade_record):

                    if not Trade.starts_with_date(trade_record):
                        j = i
                        while not Trade.starts_with_date(trade_record) and not \
                                Trade.is_single_line(trade_record):
                            trade_record = ' '.join([text_block[i-1], trade_record])
                            i -= 1
                        if not Trade.starts_with_date(' '.join(
                                trade_record.split(' ')[1:])):
                            trade_record = ' '.join([text_block[i], trade_record])
                        i = j
                
                    j = i
                    while not Trade.is_single_line(trade_record):
                        try:
                            if text_block[i+1].find("PAGE") != -1:
                                trade_record = ' '.join([trade_record, text_block[j-1]])
                                j -= 1
                            else:
                                try:
                                    trade_record = ' '.join([trade_record, text_block[i+1]])
                                    i += 1
                                except Exception:
                                    break
                        except IndexError:
                            try:
                                trade_record = ' '.join([trade_record, text_block[i+1]])
                                i += 1
                            except Exception:
                                break
                    if Trade.starts_with_date(' '.join(
                        trade_record.split(' ')[1:])):
                        
                        trades.append(Trade.option_from_record(trade_record))
            else:
                if Trade.is_single_line(trade_record):
                    trades.append(Trade.from_record(trade_record))
                elif Trade.starts_with_date(trade_record):
                    if Trade.starts_with_date(' '.join(trade_record.split(' ')[1:])):
                        trade_record = ' '.join([trade_record, text_block[i+1]])
                        trades.append(Trade.from_record(trade_record))
                    else:
                        while not Trade.is_single_line(trade_record):
                            try:
                                trade_record = ' '.join([trade_record, text_block[i+1]])
                                i += 1
                            except Exception:
                                break
                        if Trade.starts_with_date(' '.join(
                            trade_record.split(' ')[1:])):
                            trades.append(Trade.from_record(trade_record))
        except Exception:
            print trade_record
    return trades
