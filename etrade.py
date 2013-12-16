#!/usr/bin/env python
# encoding: utf-8

"""
A script to scrape PDFs of monthly E*Trade account statements.

Should output data in the following format:

date,deposit,amount
date,withdrawal,amount
date,purchase,security,amount,commission
date,sale,security,amount,commission
date,dividend,security,amount,commission
"""

import PyPDF2 as pypdf2 # Functional, but sucks.

def main():
    reader = pypdf2.PdfFileReader('/Users/jarvis/Google Drive/Fund/Monthly Statements/ROTH/ROTH-2013-11.pdf')
    print reader.getDocumentInfo()
    print reader.documentInfo
    print reader.getNamedDestinations() # There are none
    print reader.getNumPages() # probably self-explanatory
    print reader.getOutlines() # Empty
    page_0 = reader.getPage(0) # Gets an insance of PageObject class
    x = page_0.__dict__['indirectRef']


if __name__ == "__main__":
    main()
