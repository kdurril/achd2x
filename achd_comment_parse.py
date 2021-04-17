#!/usr/bin/env python
# -*- encoding : utf-8 -*- 
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
#json_docs = (json.loads(open(x).read(), object_pairs_hook=OrderedDict) for x in iglob(doc_file))
#docs2 = list(json_docs)
#docs[11]['comments_a48']
#label=['Violation:', 'Comments','Food Code Section', 'Corrective Action']

def keygather(jdoc):
    "Gather comment keys specifically for each doc page"
    keys=jdoc.keys()
    page_count=re.compile('(\d)\n')
    page_max=int(page_count.search(jdoc['comments_a48']).group(1))
    if page_max > 2:
        comment_mas=['p'+str(x+1) for x in range(1,page_max-1)]
        pagelist=['comments_a'] + comment_mas
        page_dict=OrderedDict((x,[]) for x in pagelist)
        [[page_dict[y].append(x) for x in keys if y in x] for y in page_dict.keys()]
        page_dict['comments_a'].sort(key=lambda x: int(x[10:]))
        [page_dict[page].sort(key=lambda x: int(x[11:])) for page in comment_mas]
        page_sorted=chain.from_iterable(page_dict.values())
    else:
        comment_mas=[]
        pagelist=['comments_a']
        page_dict=OrderedDict((x,[]) for x in pagelist)
        [[page_dict[y].append(x) for x in keys if y in x] for y in page_dict.keys()]
        page_dict['comments_a'].sort(key=lambda x: int(x[10:]))
        page_sorted=page_dict['comments_a']
    comment_lines=[jdoc[x] for x in page_sorted]
    violation=[x for x in comment_lines if 'Violation:' in x or 'Other Assesment observations and comments:' in x]
    return {"orderedstop":violation, "textlist":comment_lines}

def getcomments(jdoc, string='comment'):
    vio=keygather(jdoc)
    via=list(parselist(**vio))
    return via

def dict_parse(textlist):
    code_label=[]
    comments=[]
    food_code=[]
    corrective_action=[]
    other_assesment=[]
    for line in textlist:
        if line != None:
            if 'Violation' in line:
                code_label.append(line.replace('Violation: ',''))
            elif 'Corrective Action:' in line:
                corrective_action.append(line.replace('Corrective Action: ',''))
            elif 'Food Code' in line:
                food_code.append(line.replace('Food Code Section(s): ',''))
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
            else:
                comments.append(line)
    if code_label != []:
        return {
            "code_label":code_label[0],
            "food_code":food_code,
            "corrective_action": corrective_action,
            "comments": comments}

def other_parse(list_of_text):
    "parser for other assesment section"
    dict_group = {"code_label":"", "comments":""}
    category=re.compile('^\d{1,2}[.]?\s[A-Z]')
    stop_lines=[line for line in list_of_text if category.match(line[:6])]

    prep=list(parselist(orderedstop=stop_lines, textlist=list_of_text[1:]))
    container=[]
    footer = re.compile('\d{3,12}.*Client')
    for assesment in prep:
        if footer.match(assesment[0]) == None:
            prep_dict={"code_label":assesment[0],"comments":assesment[1:]}
            status = ['Diamond', 'Satisfactory','Not Applicable','Not Observed', 'Exceptional']
            if status[0] in prep_dict['code_label']:
                prep_dict['code_label']=prep_dict['code_label'][:-len(status[0])-1]
                prep_dict['status']=status[0]
            elif status[1] in prep_dict['code_label']:
                prep_dict['code_label']=prep_dict['code_label'][:-len(status[1])-1]
                prep_dict['status']=status[1]
            elif status[2] in prep_dict['code_label']:
                prep_dict['code_label']=prep_dict['code_label'][:-len(status[2])-1]
                prep_dict['status']=status[2]
            elif status[3] in prep_dict['code_label']:
                prep_dict['code_label']=prep_dict['code_label'][:-len(status[3])-1]
                prep_dict['status']=status[3]
            elif status[4] in prep_dict['code_label']:
                prep_dict['code_label']=prep_dict['code_label'][:-len(status[4])-1]
                prep_dict['status']=status[4]
            if prep_dict['comments'] and footer.match(prep_dict['comments'][-1]):
                prep_dict['comments'].pop()
            prep_dict['comments'] = ''.join(prep_dict['comments'])
            container.append(prep_dict)
    return container

def severity_parse(list_of_text):
    
    high=re.compile('HIGH RISK')
    medium=re.compile('MEDIUM RISK')
    low=re.compile('LOW RISK')

    dict_group={}
    #'high':[],'med': [],'low':[]
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
    
    page_footer = re.compile('\d{3,12}.*Client')
    comments=list(getcomments(doc))
    
    r_group=[[violation_label(y) for y in comment] for comment in comments]
    for violation in r_group:
        try:
            if violation != None:
                comment_iso=dict_parse(violation)
                if comment_iso == None:
                    break
                stopline=[x for x in comment_iso['comments'] if 'RISK*' in x]
                comment_parse=parselist(stopline, comment_iso)
                risk_iso=severity_parse(list(parselist(stopline, comment_iso['comments'])))
                comment_iso['comments']=risk_iso
                yield comment_iso
            else:
                yield comment_iso
        except:
            pass
    if "Other Assesment observations and comments:\n" == comments[-1][0]:
        other_asses=comments.pop()
        assessment=other_parse(other_asses)
        if assessment != []:
            yield {'other_assesment': assessment}

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
        return json.dumps({'inspect_id':self.inspect_id,
        'client':self.client,
        'grid': self.grid,
        'comments':self.comments})
         

#comments_iso=dict_parse(r_group)['comments']
#stopline=[x for x in comment_iso['comments'] if 'RISK' in x]
#comment_iso=dict_parse(r_group)
#severity_parse(list(parselist(stopline, comment_iso['comments'])))
#http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
