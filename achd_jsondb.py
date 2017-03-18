#!/usr/bin/env python
import psycopg2
import re
import glob
import json
import os
from collections import OrderedDict
from achd_comment_parse import Inspection


def pdftxt(in_path='/home/kenneth/Documents/scripts/achdremix_2017/txt/*.txt'):
    for pdffile in glob.glob(in_path):
        inspect_id=os.path.basename(pdffile)[:-4]
        with open(pdffile,'r') as pdfopen:
            yield {'ins_name':inspect_id, 'ins_text': pdfopen.read()}

def pdfjson(in_path='/home/kenneth/Documents/scripts/achdremix_2017/json/*.json'):
    for pdfjob in glob.glob(in_path):
        inspect_id=os.path.basename(pdfjob)[:-5]
        with open(pdfjob,'r') as pdfopen:
            yield {'ins_name':inspect_id, 'ins_text': pdfopen.read()}
    

def txt2db(thelist=pdftxt(), database='postgres', user='kenneth', password=None):
    "Add text from initial pdf to text parsing - this loses its structure"
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
    "Add json from initial pdf parsing"
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

def update_jsonalt(database='postgres', user='kenneth', password=None):
    "Add parsed json doc to postgres"
    con = psycopg2.connect(database=database, user=user, password=password)
    cur = con.cursor()
    qry_json = '''SELECT inspect_id, docjson FROM achd2016 
                  WHERE inspect_id > 201703070001
                  AND docjson IS NOT NULL;'''
    cur.execute(qry_json)
    docs=cur.fetchall()
    jsondocs=({'ins_name':x[0], 
               'doc_json':Inspection(x).to_json()} 
               for x in docs if x[1].get('comments_a48'))
    for doc in jsondocs:
        try:
            cur.execute("UPDATE achd2016 SET docjsonalt = %(doc_json)s WHERE inspect_id = %(ins_name)s;", doc)
        except:
            pass
        finally:
            print(doc['ins_name'])

    con.commit()
    con.close()


def tsvectorize(database='postgres', user='kenneth', password=None):
    "Make full-text searchable with normalization, stemming"
    con = psycopg2.connect(database=database, user=user, password=password)
    cur = con.cursor()
    'Concert text to ts_vector'
    qry_updatedb = "UPDATE achd2016 SET docvector = to_tsvector(doctxt) WHERE docvector IS NULL;"
    cur.execute(qry_updatedb)
    con.commit()

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
    update_jsonalt()
