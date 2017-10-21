#!/usr/bin/jython
# -*- coding: utf-8 -*-
#
from achd_pdfbox1229 import *
from os import path
import datetime as dt

base_project='./'
input_date=dt.datetime.today()
day = '{:%Y%m%d}'.format(input_date)
#day = '{:%Y%m%d}'.format(dt.datetime(2017,7,20))

dir_out=glob.iglob(base_project+day+'/'+day+'*.pdf')
for x in dir_out:
    basename=path.basename(x)
    jsonfile = base_project+'json/'+basename[:-4]+'.json'
    txtfile = base_project+'txt/'+basename[:-4]+'.txt'
    try:
        pdf_obj=achdInspect(x)
        jsonify(jsonfile,pdf_obj.doc_label_ALT())
        base_text(txtfile,pdf_obj)
    except:
        print(pdf_obj.filename)
if __name__ == '__main__':
    from itertools import chain
    days = ['{:%Y%m%d}'.format(dt.datetime(2017,7,y)) for y in range(21,21)]
    dir_out=(glob.iglob(base_project+day+'/'+day+'*.pdf') for day in days)
    for x in chain.from_iterable(dir_out):
        basename=path.basename(x)
        jsonfile = base_project+'json/'+basename[:-4]+'.json'
        txtfile = base_project+'txt/'+basename[:-4]+'.txt'
        try:
           pdf_obj=achdInspect(x)
           jsonify(jsonfile,pdf_obj.doc_label_ALT())
           base_text(txtfile,pdf_obj)
        except:
           print(pdf_obj.filename)

