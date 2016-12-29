#!/usr/bin/env python
#Comment Parser
import json
import re
from glob import iglob
import datetime as dt
from collections import OrderedDict, Counter, namedtuple
from os.path import basename
from itertools import chain
from achd_json_parse import violation_label, keygather, getcomments, gridgather, base_build
from achd_json_parse import gridgather_dict, grid_relabel
from achd_json_parse import parselist
#doc_file="/home/kenneth/Documents/scripts/achdremix/json/20160812*.json"
#json_docs = (json.loads(open(x).read(), object_pairs_hook=OrderedDict) for x in iglob(doc_file))
#docs2 = list(json_docs)
#docs[11]['comments_a48']
#label=['Violation:', 'Comments','Food Code Section', 'Corrective Action']

def dict_parse(textlist):
    #v_id=re.compile('(\d+)\s(\w.*)')
    #violation_number
    #violation_tag
    code_label=[]
    comments=[]
    food_code=[]
    corrective_action=[]
    other_assesment=[]
    for line in textlist:
        if line != None:
            if 'Violation' in line:
                code_label.append(line)
            elif 'Corrective Action:' in line:
                corrective_action.append(line)
            elif 'Food Code' in line:
                food_code.append(line)
            #elif 'Other Assesment observations and comments:':
            #    other_assesment.append(line)
            else:
                comments.append(line)
        else:
            line = 'Violation'
            if 'Violation' in line:
                code_label.append(line)
            elif 'Corrective Action' in line:
                corrective_action.append(line)
            elif 'Food Code' in line:
                food_code.append(line)
            #elif 'Other Assesment' in line:
            #    other_assessment.append(line)
            else:
                comments.append(line)

    if code_label != []:
        return {
            "code_label":code_label[0],
            "food_code":food_code,
            "corrective_action": corrective_action,
            "comments": comments,
            "other_assesments": other_assesment
        }
    else:
        return {
            "code_label":code_label,
            "food_code":food_code,
            "corrective_action": corrective_action,
            "comments": comments,
            "other_assesments": other_assesment
        }


def severity_parse(list_of_text):
    
    high=re.compile('HIGH RISK')
    medium=re.compile('MEDIUM RISK')
    low=re.compile('LOW RISK')

    dict_group={'high':[],'med': [],'low':[]}
    for line in list_of_text:
        #if 'HIGH' in line[0]:
        if high.search(line[0]):
           dict_group['high']=''.join(line[1:])
        #elif 'MEDIUM' in line[0]:
        elif medium.search(line[0]):
            dict_group['med']=''.join(line[1:])
        #elif 'LOW' in line[0]:
        elif low.search(line[0]):
            dict_group['low']=''.join(line[1:])
        else:
            pass
    return dict_group

def final_comments(doc):
    "reparse and group comments"
    comments=list(getcomments(doc))
    r_group=[[violation_label(y) for y in comment] for comment in comments]
    for violation in r_group:
        #try:
        if violation != None:
            comment_iso=dict_parse(violation)
            stopline=[x for x in comment_iso['comments'] if 'RISK*' in x]
            comment_parse=parselist(stopline, comment_iso)
            risk_iso=severity_parse(list(parselist(stopline, comment_iso['comments'])))
            comment_iso['comments']=risk_iso
            yield comment_iso
        #except:

        else:
            violation=['Violation:']
            comment_iso=dict_parse(violation)
            stopline=[x for x in comment_iso['comments'] if 'RISK*' in x]
            comment_parse=parselist(stopline, comment_iso)
            risk_iso=severity_parse(list(parselist(stopline, comment_iso['comments'])))
            comment_iso['comments']=risk_iso
            yield comment_iso

class Inspection(object):
    "expect a tuple with the inspection id and base json"
    def __init__(self,doc):
        self.doc = doc[1]
        self.inspect_id = doc[0]
        #self.original_pdf
        #self.doc_basic_text
        #self.doc_json
        self.client=base_build(doc[1])
        self.grid=tuple(grid_relabel(gridgather_dict(doc[1])))
        self.comments=tuple(final_comments(doc[1]))
        #self.time = to_date()
    
    def __repl__(self):
        return self.inspect_id
    
    #Use DefaultDict
    def desparse(self, assessment):
        "Add keys for missing values."
        key_set = {'diamond', 'satisfactory','not_applicable','not_observed',
                   'violation', 'tag','high','med','low'}
        desparse= key_set.difference(set(assessment.keys()))
        [assessment.update({z:''}) for z in desparse]
        return assessment

    @property
    def grid_desparse(self):
        for x in self.grid:
            yield self.desparse(x)

    @property
    def achd_uri(self):
        '''string or number'''
        base_url="http://appsrv.achd.net/reports/rwservlet?food_rep_insp&P_ENCOUNTER="
        return "{}{}".format(base_url,self.inspect_id)
    
    @property
    def to_date(self):
        datestring=str(self.inspect_id)
        year = int(datestring[:4]) 
        month = int(datestring[4:6]) 
        day = int(datestring[6:8])
        start, end = tuple(dt.datetime.strptime(y,"%I:%M:%S %p").time() for y in self.client['inspect_a2'])
        date_start = dt.datetime.combine(dt.datetime(year, month, day),start)
        date_end = dt.datetime.combine(dt.datetime(year, month, day),end)
        self.period = (date_start, date_end)
        return self.period
    
    @property
    def to_time(self):
        start, end = self.to_date
        self.duration = end - start
        return self.duration

    def violation_weight(self):
        "a weighted summary of violations"
        vio_count=("high25","med25","low25")
        wieght=(2,1.5,1)
        base_count=tuple(int(self.doc.get(x)[0]) for x in vio_count)
        return sum(x*y for x,y in zip(base_count, weight))

    def to_json(self):
        "serialize object to json"
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
         

#comments_iso=dict_parse(r_group)['comments']
#stopline=[x for x in comment_iso['comments'] if 'RISK' in x]
#comment_iso=dict_parse(r_group)
#severity_parse(list(parselist(stopline, comment_iso['comments'])))
#http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable