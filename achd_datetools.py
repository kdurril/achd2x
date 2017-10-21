#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is file to isolate the date of inspections

from datetime import date, datetime, timedelta

#datetime object
#2017,7,9

#ISO style
#20170709

def date_iso(d: datetime.date) -> str:
    "convert a date object to achd formating"
    # datetime.date(2017, 10, 21) -> '20171021' 
    # alternative to '{:%Y%m%d}'.format(date_obj)
    return d.isoformat().replace('-','')

def date_iter(start=date.today(), end=date.today()+timedelta(days=1),step=1) -> datetime.date:
    "date generator"
    change = timedelta(days=step)
    while start < end:
        yield (start-change) + change
        start = start + change

def date_gen(start=(2017,8,17), end=(2017,8,18)) -> datetime.date:
    "datetime counter"
    # takes tuples of ints that will be converted to a date object
    start = date(*start)
    end = date(*end)
    while start <= end:
        yield start
        start = start + timedelta(days=1)

def url_prep(delta=1, count=90):
    "Create iterator of urls, default yesterday, 49 inspections"
    url_stem = "http://appsrv.achd.net/reports/rwservlet?food_rep_insp&P_ENCOUNTER="
    d = date.today()
    d1 = timedelta(days=delta)
    day = date_iso(d-d1)
    base_stem = url_stem+day
    zfil = (str(x).zfill(4) for x in range(1, count))
    encounters = (base_stem+x for x in zfil)
    return encounters

#list(map(date_iso,date_iter()))
#(date_iso(x) for x in date_iter())                                      
