#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a daily file for downloading achd inspections

from achd_datetools import *
import datetime as dt
from functools import wraps
from glob import glob
from itertools import chain
from os import mkdir, path
from os.path import basename
import sys
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

def url_direct(date):
    "Create iterator of urls from supplied date"
    url_stem = "http://appsrv.achd.net/reports/rwservlet?food_rep_insp&P_ENCOUNTER="
    day = date_iso(date)
    base_stem = url_stem+day
    zfil = (str(x).zfill(4) for x in range(1, 86))
    encounters = (base_stem+x for x in zfil)
    return encounters

def grab_pdf(inspection):
    "Takes inspection from url_prep, download pdf"
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent',\
        '''Mozilla/5.0 
        (X11; Ubuntu; Linux x86_64; rv:54.0) 
        Gecko/20170613 Firefox/54.0'''),\
        ('Accept-encoding', 'gzip')]
    folder = "./"+inspection[-12:-4]
    pdffile = inspection[-12:]
    
    if path.isdir(folder) == False:
                mkdir(folder)
    with opener.open(inspection) as viewout:
        if viewout.getheader('Content-Type') == 'application/pdf':  
            outputfolder = folder+'/'+pdffile+'.pdf'
            with open(outputfolder, "wb") as pdfout:
                    pdfout.write(viewout.read())
            return outputfolder
        else:
            print(viewout.getheader('Content-Type'))

def absolute(start=None, end=None):
    "get files based on specific date range"
    "start and end must be tuples: YYYY,MM,DD"
    if start == None and end == None:
        start = dt.date.today()
        end = dt.date.today() + dt.timedelta(days=1)
    else:
        start = dt.date(*start)
        end = dt.date(*end)
    lastweek = date_iter(start, end)
    for date in lastweek:
        encounters = url_direct(date)
        for inspection in encounters:
            try: 
                grab_pdf(inspection)
            finally:
                with open('inspection.log','a') as ins_log:
                    ins_log.write(inspection)

def relative():
    "get files based on relative date range"
    
    encounters = url_prep(delta=0, count=90)

    for inspection in encounters:
        #try:
        grab_pdf(inspection)
        #except urllib.error.HTTPError as e:
        #    print("fail, {}".format(e.code))

if __name__ == '__main__':
    absolute()
    #absolute((2017,10,5),(2017,10,7))
