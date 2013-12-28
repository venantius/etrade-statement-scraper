#!/usr/bin/env python
# encoding: utf-8

"""
Mostly stuff I stole from the PDFminer site, modified a little to work with E*Trade stuff (at least, as well as it can be expected to).
"""

import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LTPage 
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage
# viable, but complicated. looking into pdftables as a more accessible library
# import pdftables # Definitely much better than pdfminer alone. Viable contender.

def with_pdf (pdf_doc, pdf_pwd, fn, *args):
    """Open the pdf document, and apply the function, returning the results"""
    result = None
    try:
        # open the pdf file
        fp = open(pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser)
        # connect the parser and document objects
        parser.set_document(doc)
        # supply the password for initialization
        doc.initialize(pdf_pwd)

        if doc.is_extractable:
            # apply the function and return the result
            result = fn(doc, *args)

        # close the pdf file
        fp.close()
    except IOError, e:
        # the file doesn't exist or similar problem
        print e
        pass
    return result

def parse_lt_objs (lt_objs, page_number, images_folder='/tmp', text=[]):
    """Iterate through the list of LT* objects and capture the text or image data contained in each"""
    text_content = [] 

    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBox):
            if lt_obj.get_text():
                text_content.append(lt_obj.get_text())
        elif isinstance(lt_obj, LTTextLine):
            # text
            continue
            if lt_obj.get_text():
                text_content.append(lt_obj.get_text())
        elif isinstance(lt_obj, LTFigure):
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            if parse_lt_objs(lt_obj._objs, page_number, images_folder, text_content):
                text_content.append(parse_lt_objs(lt_obj._objs, page_number, images_folder, text_content))

    return '\n'.join(text_content)

def _parse_pages (doc):
    """With an open PDFDocument object, get the pages and parse each one
    [this is a higher-order function to be passed to with_pdf()]"""
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(
            line_overlap = 0.0001,
            char_margin = 120.0,
            line_margin = 10000000.5,
            word_margin = 0.08,
            boxes_flow = 1.5,
            detect_vertical = False
            )
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    text_content = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_content.append(parse_lt_objs(layout._objs, (i+1)))
    return text_content

def get_pdf_as_string(pdf_doc, pdf_pwd='', images_folder='/tmp'):
    """Process each of the pages in this pdf file and print the entire text to stdout"""
    array = with_pdf(pdf_doc, pdf_pwd, _parse_pages)
    return '\n\n'.join(array)
