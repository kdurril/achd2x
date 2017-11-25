#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a daily file for downloading achd inspections

# url_direct

from achd_datetools import achd_today, date_iter, date_iso
import datetime as dt
from functools import wraps
from itertools import chain
from os import mkdir, path
from os.path import basename
import urllib.request
import urllib.error

def parse(pdf_file=None):
        'convert to a decorator'
        out = basename(pdf_file).split('.')[0]+'.txt'
        with open(out, 'w') as f:
            parsed = parser.from_file(pdf_file)
            txt_out = parsed['content']
            f.write(txt_out)
            return txt_out

def url_direct(date):
    "Create iterator of urls from supplied date"
    url_stem = "http://appsrv.achd.net/reports/rwservlet?food_rep_insp&P_ENCOUNTER="
    day = date_iso(date)
    base_stem = url_stem+day
    zfil = (str(x).zfill(4) for x in range(1, 100))
    encounters = (base_stem+x for x in zfil)
    return encounters

def grab_pdf(inspection):
    "Takes inspection from url_direct, download pdf"
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent',\
        '''Mozilla/5.0 
        (X11; Ubuntu; Linux x86_64; rv:55.0) 
        Gecko/20171026 Firefox/55.0'''),\
        ('Accept-encoding', 'gzip')]
    folder = "./"+inspection[-12:-4]
    pdffile = inspection[-12:]
    
    if path.isdir(folder) == False:
                mkdir(folder)
    with opener.open(inspection) as viewout:
        while viewout.getheader('Content-Type') == 'application/pdf':  
            outputfolder = folder+'/'+pdffile+'.pdf'
            with open(outputfolder, "wb") as pdfout:
                    pdfout.write(viewout.read())
            return outputfolder
        #else:
        #    print(viewout.getheader('Content-Type'))
        #    print(pdffile)
        #    break

#Date input helper functions
#date_tuple and date_str allows human input that converts to datetime obj

def date_tuple(start=None, end=None):
    'helper function for date_input start:tuple'
    start = dt.date(*start)
    if end:
        end = dt.date(*end)
    if not end:
        end = start + dt.timedelta(days=1)
    return (start, end)

def date_str(start=None, end=None):
    'helper function for date_input start:str'
    format = "%Y%m%d"
    t_start = dt.datetime.strptime(start, format)
    if end:
        t_end = dt.datetime.strptime(end, format)
    if not end:
        t_end = t_start + dt.timedelta(days=1)
    start = dt.date(t_start.year,t_start.month,t_start.day)
    end = dt.date(t_end.year, t_end.month, t_end.day)
    return (start, end)

def date_input(start=None, end=None):
    "allow multiple input types for creating date objects"
    #default
    if start == None:
        start = dt.date.today()
        end = dt.date.today() + dt.timedelta(days=1)
        return (start, end)
    #tuple - (2017,5,8)
    elif isinstance(start, tuple):
        return date_tuple(start,end)
    #string - '20170508'
    elif isinstance(start, str):
        return date_str(start,end)

def absolute(start=None, end=None):
    "get files based on specific date range"
    start, end = date_input(start, end)
    lastweek = date_iter(start, end)
    for date in lastweek:
        encounters = url_direct(date)
        for inspection in encounters:
            try: 
                grab_pdf(inspection)
            finally:
                with open('inspection.log','a') as ins_log:
                    ins_log.write(inspection)

if __name__ == '__main__':
    absolute(achd_today)
