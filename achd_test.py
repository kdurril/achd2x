#!/usr/bin/jython
# -*- coding: utf-8 -*-
#
from achd_datetools import achd_today
from achd_pdfbox1229 import *
import datetime as dt
from glob import iglob
from os import path
from sys import argv

def current_dir(base_dir="/mnt/", directory="20171010/"):
#    if directory[-1] != '/':
#        directory + '/'
    dir_out=list(iglob(base_dir+directory+"*.pdf"))
    for x in dir_out:
        basename=path.basename(x)
        jsonfile = base_dir+'json/'+basename[:-4]+'.json'
        txtfile = base_dir+'txt/'+basename[:-4]+'.txt'
        try:
            pdf_obj=achdInspect(x)
            jsonify(jsonfile,pdf_obj.doc_label_ALT())
            base_text(txtfile,pdf_obj)
        except:
            print("C")
if __name__ == '__main__':
    #d = dt.datetime.strptime(argv[1], '%Y%m%d')
    current_dir(base_dir="", directory=achd_today+"/")
