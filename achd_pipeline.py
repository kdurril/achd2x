#!/home/kenneth/Documents/scripts/achdremix/remix/bin/python3
#ACHDREMIX Pipeline
import subprocess
from achd_daily3 import url_prep, absolute, grab_pdf
from achd_jsondb import pdftxt, pdfjson, txt2db, json2db
from achd_jsondb import tsvectorize, update_jsonalt
import datetime as dt
import glob
import os
import sys

'''
1) Get data from achd.net
  - Cpython3.5
  - achd_daily3.py

2) Transform pdf into json
  - jython2.7
  - achd_test.py

3) Place text and json documents into database
  - Cpython3.5
  - achd_jsondb.py

4) Transform json
  - Cpython3.5
  
  - client and inspection info
    - achd_jsontxtalt.py
  
  - grid
    - achd_json_parse.py

  - comments
    - achd_comment_parse.py
    - achd_comments_db.py

5) Analysis
  - achd_descriptive_stats.py

6) Display
'''
#Set date range
#  - are dates relative or absolute
#Set output
#  - are paths relative or absolute

#review design to see that scripts are built with callables that can take outputs and dates
base_project='./'
day = '{:%Y%m%d}'.format(dt.datetime.today())
#day = '{:%Y%m%d}'.format(dt.datetime(2017,7,20))

#dir_out = glob.iglob(base_project+day+'/'+day+'*.pdf')

#"achd_daily3.py"

encounters = url_prep(delta=0, count=83)
for inspection in encounters:
    try:
        grab_pdf(inspection)
    except:
        print(str(inspection))

#"jython -Dpython.path=/home/kenneth/Development/pdfbox-2.0.2/app/target/pdfbox-app-2.0.2.jar achd_test.py"
subprocess.run("./achd_jsonify.sh")

#"achd_jsondb.py"
#password isn't sensative for this
#all data is publicly available
#password is in place because I'd rather keep the habit than not
PASSWORD='achd282' #sys.argv[1]
txt=pdftxt(in_path=base_project+'txt/'+day+'*.txt') 
#txt=pdftxt(in_path=base_project+'txt/201706*.txt') 
json=pdfjson(in_path=base_project+'json/'+day+'*.json')
#json=pdfjson(in_path=base_project+'json/201706*.json')

txt2db(thelist=txt,database='postgres',user='kenneth',password=PASSWORD)
json2db(thelist=json,database='postgres',user='kenneth',password=PASSWORD)
tsvectorize(database='postgres',user='kenneth',password=PASSWORD)
update_jsonalt(database='postgres',user='kenneth',password=PASSWORD)
#"achd_jsontxtalt"
