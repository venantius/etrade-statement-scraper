#!/usr/bin/env python

"""
A collection of functions used by all of the record types
"""

from datetime import datetime

class Record(object):
    """
    Parent record class. Includes some defaults methods that may be overwritten
    in the various subclasses
    """
    def __init__(self):
        pass

    @staticmethod
    def starts_with_date(record_line):
        """
        Boolean check to see if this record starts with a date.
        """
        try:
            datetime.strptime(record_line[0:8], '%m/%d/%y')
            return True
        except ValueError:
            return False

    @staticmethod
    def string_to_datetime(date_string):
        """
        Parse a string formatted %m/%d/%y into a datetime object
        """
        return datetime.strptime(date_string, '%m/%d/%y').date()

    def is_single_line(self, record):
        raise NotImplementedError
