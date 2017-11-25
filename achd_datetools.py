#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is file to set the date of inspection to be processed


import datetime as dt
from os import environ
from sys import argv

#datetime object
#2017,7,9

#ISO style
#20170709

def date_iso(d):
    "convert a date object to achd formating"
    # datetime.date(2017, 10, 21) -> '20171021' 
    # alternative to '{:%Y%m%d}'.format(date_obj)
    # return d.isoformat().replace('-','')
    return d.strftime("%Y%m%d")

def date_iter(start=dt.date.today(), end=dt.date.today()+dt.timedelta(days=1)):
    "date generator"
    change = dt.timedelta(days=1)
    while start < end:
        yield (start-change) + change
        start = start + change

def date_gen(start=(2017,8,17), end=(2017,8,18)):
    "datetime counter"
    # takes tuples of ints that will be converted to a date object
    start = dt.date(*start)
    end = dt.date(*end)
    while start <= end:
        yield start
        start = start + dt.timedelta(days=1)

if environ.get('ACHD_DATE'):
    achd_today = environ['ACHD_DATE']
else:
    achd_today = date_iso(dt.date.today()) 

#list(map(date_iso,date_iter()))
#(date_iso(x) for x in date_iter())
if __name__ == '__main__':
    print(date_iso(dt.date.today()))
    d = dt.datetime.strptime(argv[1], '%Y%m%d')
    print(d.strftime('%Y%m%d'))
