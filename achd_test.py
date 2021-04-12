#!/usr/bin/jython
# -*- coding: utf-8 -*-
#
from achd_datetools import achd_today
from achd_pdfbox1229 import *
import datetime as dt
from glob import iglob
from os import path
from sys import argv

#base_dir="/home/kenneth7/rebuild/achd_remix/"
base_dir="/home/kdurril/Development/rebuild/rebuild/rebuild/achd_remix/"

def process_file(x,base_dir="/mnt/"):
    "process the given file"
    basename=path.basename(x)
    jsonfile = base_dir+'json/'+basename[:-4]+'.json'
    txtfile = base_dir+'txt/'+basename[:-4]+'.txt'
    try:
        pdf_obj=achdInspect(x)
        jsonify(jsonfile,pdf_obj.doc_label_ALT())
        base_text(txtfile,pdf_obj)
        pdf_obj.doc.close()
        del pdf_obj
    except:
        print("C")


def current_dir(base_dir="/mnt/", directory="20171010/"):
    if len(argv) > 1:
        print(argv[1])
        process_file(argv[1],base_dir=base_dir)
    else:
        dir_out=list(iglob(base_dir+directory+"*.pdf"))
        for x in dir_out:
            process_file(x, base_dir=base_dir)
if __name__ == '__main__':
    #d = dt.datetime.strptime(argv[1], '%Y%m%d')
    current_dir(base_dir=base_dir, directory=argv[2]+"/")
