#!/usr/bin/jython
# -*- coding: utf-8 -*-
#
from achd_pdfbox1229 import *
from os import path
import datetime as dt

base_project='/home/kenneth/Documents/scripts/achdremix/'
input_date=dt.datetime.today()
day = '{:%Y%m%d}'.format(input_date)
#day = '{:%Y%m%d}'.format(dt.datetime(2016,11,30))

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
