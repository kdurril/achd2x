#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from achd_daily3 import date_input, date_tuple, date_str
import datetime

class TestDateParse(unittest.TestCase):
    
    def setUp(self):
        self.date_obj =  (datetime.date(2011,11,1), datetime.date(2011,11,2))
        self.input_str_start = '20171101'
        self.input_str_end = '20171102'
        self.input_tuple_start = (2017,11,1)
        self.input_tuple_end = (2017,11,2)

    def test_default(self):
        self.assertEqual(date_input(), (datetime.date.today(), 
                                      datetime.date.today()+datetime.timedelta(days=1)))

    def test_tuple(self):
        self.assertEqual(date_input((2011,11,1),(2011,11,2)),
                                  self.date_obj)
    def test_str(self):
        self.assertEqual(date_input('20111101','20111102'),
                                  self.date_obj)
    def test_compare(self):
        "the tuple output and string output should be equal"
        self.assertEqual(date_input((2011,11,1),(2011,11,2)),date_input('20111101','20111102'))

    def test_startonly(self):
        "if only start value, implicit end of next day"
        self.assertEqual(date_input((2011,11,1)), self.date_obj)

class TestDateHelper(unittest.TestCase):
    def setUp(self):
        self.date_obj =  (datetime.date(2017,11,1), datetime.date(2017,11,2))
        self.input_str_start = '20171101'
        self.input_str_end = '20171102'
        self.input_tuple_start = (2017,11,1)
        self.input_tuple_end = (2017,11,2)

    def test_str(self):
        "str -> datetime.date"
        self.assertEqual(date_str(self.input_str_start,self.input_str_end), self.date_obj)

    def test_tuple(self):
        "tuple -> datetime.date"
        self.assertEqual(date_tuple(self.input_tuple_start), self.date_obj)

if __name__ == '__main__':
    unittest.main()
