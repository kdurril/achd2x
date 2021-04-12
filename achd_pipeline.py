#!/home/kenneth7/rebuild/rmx2/bin/python
#ACHDREMIX Pipeline
from achd_daily3 import absolute, grab_pdf
from achd_datetools import achd_today
from achd_jsondb import json2db, pdftxt, pdfjson, txt2db, \
                        tsvectorize, update_jsonalt
import achd_jsonify
import datetime as dt
import glob
import os
import subprocess
import sys
import time

'''
1) Get data from achd.net
  - Cpython3.5 or greater
  - achd_daily3.py

2) Transform pdf into json
  - jython2.7
  - achd_test.py

3) Place text and json documents into database
  - Cpython3.5 or greater
  - achd_jsondb.py

4) Transform json
  - Cpython3.5
  
  - grid
    - achd_json_parse.py

  - comments
    - achd_comment_parse.py

5) Analysis
  - achd_descriptive_stats.py

6) Display
'''

#Date comes from achd_today in datetools
#  - useful as global
#  - see datetools
#Output
#  - paths relative or absolute
#  - achd_daily - to file
#  - achd_test - to file
#  - achd_jsondb - to db

#review design to see that scripts are built with callables that can take outputs and dates
base_project='./'

#"achd_daily3.py"
#absolute(achd_today)

#This calls to achd_jsonify that calls to jython
#This processes one doc at a time for the small digital ocean instance
for document in achd_jsonify.dir_out:
    achd_jsonify.jython_process_pdf(base_dir=achd_jsonify.base_dir,document=document)
    print(document + " jsonifyied")
    time.sleep(2)
#DB credentials
DB=os.environ.get('ACHD_DB')
USER=os.environ.get('ACHD_DBUSER')
PASSWORD=os.environ.get('ACHD_DBPWD')
HOST=os.environ.get('ACHD_DBHOST')
PORT=os.environ.get('ACHD_DBPORT')

#"achd_jsondb.py"
#Files to send to db
txt=pdftxt(in_path=base_project+'txt/'+achd_today+'*.txt') 
json_data=pdfjson(in_path=base_project+'json/'+achd_today+'*.json')

#Database calls
#
txt2db(thelist=txt,database=DB,host=HOST,port=PORT,user=USER,password=PASSWORD)
json2db(thelist=json_data,database=DB,host=HOST,port=PORT,user=USER,password=PASSWORD)
tsvectorize(database=DB,user=USER,host=HOST,port=PORT,password=PASSWORD)
update_jsonalt(database=DB,user=USER,host=HOST,port=PORT,password=PASSWORD)
