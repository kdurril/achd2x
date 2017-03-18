#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a daily file for downloading achd inspections

import time
import urllib.request
import urllib.error
import datetime as dt
import sys
from itertools import chain
from functools import wraps
from os import mkdir, path, stat

from glob import glob
from os.path import basename

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
    d = dt.date.today()
    d1 = dt.timedelta(days=delta)
    day = '{:%Y%m%d}'.format(d-d1)
    base_stem = url_stem+day+'00'
    zfil = (str(x).zfill(2) for x in range(1, count))
    encounters = (base_stem+x for x in zfil)
    return encounters

def date_iter(start, end=dt.date.today()):
    "date generator"
    change = dt.timedelta(days=1)
    while start < end:
        yield (start-change) + change
        start = start + change

def url_direct(date):
    "Create iterator of urls from supplied date"
    url_stem = "http://appsrv.achd.net/reports/rwservlet?food_rep_insp&P_ENCOUNTER="
    day = '{:%Y%m%d}'.format(date)
    base_stem = url_stem+day+'00'
    zfil = (str(x).zfill(2) for x in range(1, 86))
    encounters = (base_stem+x for x in zfil)
    return encounters

   
def grab_pdf(inspection):
    "Takes inspection from url_prep, download pdf"
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent',\
        '''Mozilla/5.0 
        (X11; Ubuntu; Linux x86_64; rv:46.0) 
        Gecko/2016101 Firefox/46.0'''),\
        ('Accept-encoding', 'gzip')]
    folder = "/home/kenneth/Documents/scripts/achdremix_2017/"+inspection[-12:-4]
    pdffile = inspection[-12:]
    
    if path.isdir(folder) == False:
                mkdir(folder)
    with opener.open(inspection) as viewout:
        if viewout.getheader('Content-Type') == 'application/pdf':  
            outputfolder = folder+'/'+pdffile+'.pdf'
            with open(outputfolder, "wb") as pdfout:
                    pdfout.write(viewout.read())
            return outputfolder
                    #time.sleep(1)
        else:
            print(viewout.getheader('Content-Type'))
            

def absolute(start=None, end=dt.datetime.today()):
    "get files based on specific date range"
    "start and end must be tuples: YYYY,MM,DD"
    start = dt.datetime(*start)
    end = dt.datetime(*end)
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
    relative()
    #absolute((2016,9,27),(2016,9,28))
