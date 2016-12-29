#!/usr/bin/env python
import psycopg2
import re
import glob
import json
import os
from collections import OrderedDict

#con = psycopg2.connect(database="postgres", user="kenneth", password="achd282")
#cur = con.cursor()

#cur.execute('''CREATE TABLE achdjson (ID SERIAL PRIMARY KEY,
#                         inspect_id BIGINT, 
#                         doc JSONB);''')
#con.commit()

#f_list = ['json/achd_match.json', 'json/achd_unmatch.json']

#with open('json/achd_match.json') as match:
#    match_docs = json.loads(match.read())
#for doc in match_docs:
#    cur.execute("INSERT INTO achdjson (inspect_id, doc) VALUES(%s, %s)", (doc['inspect_id'],json.dumps(doc)))
#con.commit()

#with open('json/achd_unmatch.json') as unmatch:
#    unmatch_docs = json.loads(unmatch.read())
#for doc in unmatch_docs:
#    cur.execute("INSERT INTO achdjson (inspect_id, doc) VALUES(%s, %s)", (doc['inspect_id'],json.dumps(doc)))
#con.commit()


#text_file '/home/kenneth/Documents/scripts/achdremix/txt/2016071*.txt'
#text_insert="INSERT INTO achdjson (inspect_id, doc) VALUES (%(ins_name)s,%(ins_text)s)", doc
#json_file '/home/kenneth/Documents/scripts/achdremix/json/2016071*.json'
#json_update='''UPDATE achd2016 SET docjson = %s WHERE inspect_id = %s'''

def pdftxt(in_path='/home/kenneth/Documents/scripts/achdremix/txt/2016082*.txt'):
    for pdffile in glob.glob(in_path):
        inspect_id=os.path.basename(pdffile)[:-4]
        with open(pdffile,'r') as pdfopen:
            yield {'ins_name':inspect_id, 'ins_text': pdfopen.read()}

def pdfjson(in_path='/home/kenneth/Documents/scripts/achdremix/json/2016082*.json'):
    for pdfjob in glob.glob(in_path):
        inspect_id=os.path.basename(pdfjob)[:-5]
        with open(pdfjob,'r') as pdfopen:
            yield {'ins_name':inspect_id, 'ins_text': pdfopen.read()}
    

def txt2db(thelist=pdftxt(), database='postgres', user='kenneth', password=None):
    con = psycopg2.connect(database=database, user=user, password=password)
    cur = con.cursor()
    
    the_text=thelist
    
    for doc in the_text:
        if len(doc['ins_name']) == 12:
            try:
                cur.execute("INSERT INTO achd2016 (inspect_id, doctxt) VALUES (%s,%s)", 
                (doc['ins_name'], doc['ins_text']))
            except:
                pass
            finally:
                print(doc['ins_name'])
    
    con.commit()
    con.close()

def json2db(thelist=pdfjson(), database='postgres', user='kenneth', password=None):
    con = psycopg2.connect(database=database, user=user, password=password)
    cur = con.cursor()

    the_json=thelist
    
    jsontoo=({'ins_name':x['ins_name'],
              'ins_text':json.loads(x['ins_text'],
               object_pairs_hook=OrderedDict)} for x in the_json)    
    for doc in jsontoo:
        if len(doc['ins_name']) == 12:
            try:
                cur.execute('''UPDATE achd2016 SET docjson = %s 
                       WHERE inspect_id = %s''', (json.dumps(doc['ins_text']), int(doc['ins_name'])))
            except:
                pass
            finally:
                print(doc['ins_name'])
    
    con.commit()
    con.close()

def tsvectorize(database='postgres', user='kenneth', password=None):
    con = psycopg2.connect(database=database, user=user, password=password)
    cur = con.cursor()
    'Concert text to ts_vector'
    qry_updatedb = "UPDATE achd2016 SET docvector = to_tsvector(doctxt) WHERE docvector IS NULL;"
    cur.execute(qry_updatedb)
    con.commit()

#for doc in the_text:

#        cur.execute("INSERT INTO achdjson (inspect_id, doc) VALUES (%s,%s)", (doc['ins_name'], doc['ins_text']))

#for doc in the_text:
#    if len(doc['ins_name']) == 12:
#        cur.execute("INSERT INTO achd2016 (inspect_id, doctxt) VALUES (%s,%s);", (doc['ins_name'], doc['ins_text']))
      
#and doc['ins_text'][-1] == '}'
#CREATE TABLE achd2016 (inspect_id bigint NOT NULL, doctxt varchar NOT NULL, docjson jsonb);


#def jsondb(base_file):
#    with open(base_file) as match:
#        match_docs = json.loads(match.read())
#    for doc in match_docs:
#        cur.execute("INSERT INTO achdjson (inspect_id, doc) VALUES(%s, %s)", (doc['inspect_id'],json.dumps(doc)))
#    con.commit()

#def jsondb(base_file):
#    with open(base_file) as match:
#        match_docs = json.loads(match.read())
#        inpsect_id = os.path.basename(match.name).split('.')[0]
#        match_docs['inspect_id'] = inpsect_id
    
#    cur.execute("INSERT INTO achdjson (inspect_id, doc) VALUES(%s, %s)", (doc['inspect_id'],json.dumps(doc)))
#    con.commit()

def jsonalso():
    the_json=pdfjson()
    for x in the_json:
        if x['ins_name'] > '20150413001':
            try:
                instext=json.loads(x['ins_text'])
                yield {'ins_name':x['ins_name'], 'ins_text':instext}
            except:
                pass
            finally:
                print(x['ins_name'])

if __name__ == '__main__':
    txt2db()
    json2db()
    tsvectorize()