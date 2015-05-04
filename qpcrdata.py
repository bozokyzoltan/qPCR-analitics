#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Under GPL licence.
"""

import numpy as np
import xlrd


class Data(object):
    """
    """
    def __init__(self):
        """
        """
        self.data = {}
        self.order = []
        return None
    def read_datafile(self, filename):
        """
        """
        book = xlrd.open_workbook(filename)
        for sheet_index, sheet_name in enumerate(book.sheet_names()):
            sheet = book.sheet_by_name(sheet_name)
            for row in xrange(1, sheet.nrows):
                for col in xrange(sheet.ncols):
                    if col == 0:
                        self.order.append(sheet.cell_value(row, col))
                    if not self.order[-1] in self.data:
                        self.data[self.order[-1]] = []
                    try:
                        self.data[self.order[-1]].append(float(sheet.cell_value(row, col)))
                    except ValueError:
                        self.data[self.order[-1]].append(str(sheet.cell_value(row, col)))
        #
        return None
    def order(self):
        return self.order
    def data(self):
        return self.data
        
        
