#!/usr/bin/env python
# -*- encoding : utf-8 -*- 
#Regular Expressions to Parse ACHD strings

import json
import re
from glob import iglob
from collections import OrderedDict, Counter, namedtuple
from os.path import basename
from itertools import chain
import datetime as dt

#doc_file="/home/kenneth/Documents/scripts/achdremix/json/20160728*.json"
#, object_pairs_hook=OrderedDict
#json_docs = (json.loads(open(x).read(), object_pairs_hook=OrderedDict) for x in iglob(doc_file))
#docs = list(json_docs)
#docs.remove(OrderedDict())
#add(x) for x in iglob(doc_file)

#Use a counter for a histogram of the keys
#d = Counter()
#md = [d.update(x.keys()) for x in docs]

#check for consistency
#some keys should be in all dicts
#test for membership
#len([x for x in docs if not x.get('client_a1')])
# [x for x in docs if not x.get('client_a1')]
# bad_item=[docs.index(x) for x in docs if not x.get('client_a1')]
# docs.remove(*bad_item)
#client_a0
client_id=re.compile('(\d+)Client\sID:')
#client_a1
addr=re.compile('(\d.*)Address:')
#client_a2
city=re.compile('(\w.*)City:')
#client_a3
muni=re.compile('(\w.*)Municipality:')

#merge client_a4, client_b4
#set(x['client_a4'][:-15]+x['client_b4'][:-7] for x in docs)
#client_a4
#p=set(x['client_a4'] for x in docs)
#p_trim=set(x[:-15] for x in p)
#p_sort=sorted(list(p_trim),key=lambda x: len(x))
#p_sort1=sorted(list(p_trim),key=lambda x: int(x[:3]))
cat_code=re.compile('(\d.*)Category Code:')
#clientb4
cat_code2=re.compile('(\w.*)\sPrior')
#merged
#cat_code.match(docs[5]['client_a4']).group(1)+cat_code2.match(docs[5]['client_b4']).group(1)

#client_a5
re_inspect=re.compile('(^.*)Re-\s+Inspection')

#client_b0
#[client_b0][:-12]
client_name=re.compile('(\w.*)Client Name:')
#client_b1
#
#client_b2
state_zip=re.compile('(?P<state>\w{2})State:\s?(?P<zipcode>\d{5})Zip:')
#state,zip_code=state_zip.search(docs[1]['client_b2']).groups()
#client_b3
ins=re.compile('Inspector:\s(?P<inspector>\w.*)\sPerm')
#ins.match(inspector[2]).group('inspector')

#comments_a48
ins_id=re.compile('(\d{12})')

#client_c1
ins_date=re.compile('Date:\s(\d{2}/\d{2}/\d{4})')

#client_c2
purpose=re.compile('(.*)ose:')
#client_c3
permit_exp=re.compile('Date:\s(\d{2}/\d{2}/\d{4})')
#client_c4
priority=re.compile('Code:\s(.*)')

#ins_date=re.compile('\d{2}/\d{2}/\d{4}')
#ins_date.search(docs[1]['client_c3']).group()

#label=re.compile('(?<=\w.*)[A-Z].*:')
#address=[x['client_a1'] for x in docs[:20] if x['client_a1']]
#[addr.match(x).group(1) for x in address]

#[x for x in docs[79].keys() if 'inspect' in x]
#Example output from inspect keys
#['Delphia , NicholasInspector Name:\n', 'Inspected & PermittedPlacarding:\n', 
#'04:30:00 PM03:55:00 PM End Time:Start Time:\n', 
#'Balance Amount:\n', 'Contact:\n', 'Phone:\n', ' $0.00\n', 'Joe Pacifaco\n', '(412) 268-5107\n']

#inspect_a0
inspector=re.compile('(\w.*)Inspector Name:')
#inspect_a1
placard=re.compile('(\w.*)Placarding:')
#inspect_a2
time=r'\d{2}:\d{2}:\d{2}\s\w{2}'
#time_re=re.compile(r'(?P<end>'+time+r')\s?(?P<start>'+time+r')\sEnd\sTime:Start\sTime:')
#time_re=re.compile('(?P<end>\d{2}:\d{2}:\d{2}\s\w{2})\s?(?P<start>\d{2}:\d{2}:\d{2}\s\w{2})\s?End\sTime:Start\sTime:')
time_re=re.compile(r'(?P<end>'+time+r')(?P<start>'+time+r')')

def time_sort(t):
    "t is a time tuple of strings from time_re.search().groups()"
    tsort=(x[1] for x in sorted([(dt.datetime.strptime(y,"%I:%M:%S %p"),y) for y in t], key=lambda z: z[0]))
    return tuple(tsort)


#inspect_b0
#label only
#inspect_b1
#label only
#inspect_b2
#label only
#inspect_c0
#ok
#inspect_c1
#ok
#inspect_c2
#ok

def extract(pattern, label, e_dict):
    'extract the address from address field'
    #try:
    if label in ['inspect_a2', 'client_b2']:
        return {label: list(pattern.search(e_dict.get(label)).groups())}
    else:        
        return {label: pattern.search(e_dict.get(label)).group(1)}
#Use a lambda to sort the number a the end of the string as an int, not lexical sort
#sorted([x for x in docs[5].keys() if 'comments' in x], key=lambda x: int(x[10:]))
#doc10_comments=sorted([x for x in docs[10].keys() if 'comments' in x], key=lambda x: int(x[10:]))
#[docs[10].get(x) for x in doc10_comments]

#Histograms by value per key
#Counter([extract(purpose, 'client_c2', x) for x in docs[:100]])
#To ensure the key is in the dict
#Counter([extract(purpose, 'client_c2', x) for x in docs if x.get('client_c2')])


#comments
#group, order, and join
#comments=sorted([x for x in docs[3].keys() if 'comments_a' in x AND int(x[-2:]) < 10 ])

def build(doc):
    'build dict of updated items'
    client_list=[('comments_a48',ins_id),
                 ('client_a0',client_id), ('client_a1',addr), 
                 ('client_a2', city), ('client_a3', muni), 
                 ('client_a4',cat_code), ('client_b4',cat_code2),
                 ('client_b0',client_name),
                 ('client_b2', state_zip), ('client_b3', ins), 
                 ('client_c1', ins_date), ('client_c2',purpose),
                 ('client_c3', permit_exp),('client_c4', priority)]    
    inspect_list=[('inspect_a0',inspector), 
                  ('inspect_a1',placard), 
                  ('inspect_a2', time_re)]
    clean=OrderedDict()
    full_list = chain(client_list, inspect_list)
    for item in full_list:
        try:
            clean.update(extract(item[1],item[0], doc))
        except:
            pass
    if 'inspect_a2' in clean:
        #dt.time(*[int(x) for x in clean['inspect_a2'][:-3].split(':')])
        clean['inspect_a2']=time_sort(clean['inspect_a2'])
    if 'client_b4' in clean:
        clean['client_a4']=clean['client_a4']+clean['client_b4']
        del clean['client_b4']
    if 'client_c0' in doc:
        clean['client_b0']=clean['client_b0']+doc['client_c0'].strip()
    #if 'client_c2' in doc:
    #    if clean['client_c2'] == "Initial, Complaiose:\n":
    #        clean['cleint_c2'] = "Initial, Complaint\n"
    #    elif clean['client_c2'] == "Initial, New Fac:\n":
    #        clean['cleint_c2'] = "Initial, New Facility\n"
    #    elif clean['client_c2'] == "Partial ReInspeose:\n":
    #        clean['cleint_c2'] = "Partial ReInspection\n"
    #    elif clean['client_c2'] == "Service Requesose:\n" OR \
    #         clean['client_c2'] == "Service Reques:\n":
    #        clean['cleint_c2'] = "Service Request\n"
    #    elif clean['client_c2'] == "Service Reques:\n":
    #        clean['cleint_c2'] = "Service Request\n"
    c2_dict={'Administrative ':'Administrative',
            'Complaint':'Complaint',
            'Consultation':'Consultation',
            'Foodborne Illne':'Foodborne Illness',
            'Initial':'Initial',
            'Initial, Complai':'Initial, Complaint',
            'Initial, Foodbor':'Initial, Foodborne Illness',
            'Initial, New Fac':'Initial, New Facility',
            'Initial, Service ':'Initial, Service',
            'New Facility':'New Facility',
            'Not Selected':'Not Selected',
            'Owner Reques':'Owner Request',
            'Partial ReInspe':'Partial ReInspection',
            'Reinspection':'Reinspection',
            'Reinspection, C':'Reinspection, C',
            'Reinspection, F':'Reinspection, F',
            'Reinspection, S':'Reinspection, S',
            'Remodel':'Remodel',
            'Remodel, Initia':'Remodel, Initial',
            'Remodel, Rein':'Remodel, Reinspection',
            'Remodel, Serv':'Remodel, Service Request',
            'Service Reques':'Service Request'
            }
    
    clean[client_c2] = c2_dict.get(clean['client_c2'], clean['client_c2'])

    remaining_inspect = {'inspect_c0': doc.get('inspect_c0'),
                         'inspect_c1': doc.get('inspect_c1'),
                         'inspect_c2': doc.get('inspect_c2')} 

    if 'comments_a48' in doc:
        doc_id=clean.get('comments_a48')
        clean.pop('comments_a48')
        clean.update(remaining_inspect)
        doc_json={'ins_name': doc_id, 'ins_json': json.dumps(clean)}
        return doc_json

def base_build(doc):
    'build dict of updated items'
    client_list=[('comments_a48',ins_id),
                 ('client_a0',client_id), ('client_a1',addr), 
                 ('client_a2', city), ('client_a3', muni), 
                 ('client_a4',cat_code), ('client_b4',cat_code2),
                 ('client_a5',re_inspect),
                 ('client_b0',client_name),
                 ('client_b2', state_zip), ('client_b3', ins),
                 ('client_b5', ins_date), 
                 ('client_c1', ins_date),  ('client_c2',purpose), 
                 ('client_c3', permit_exp), ('client_c4', priority)]    
    inspect_list=[('inspect_a0',inspector), 
                  ('inspect_a1',placard), 
                  ('inspect_a2', time_re)]

    clean=OrderedDict()
    full_list = chain(client_list, inspect_list)
    for item in full_list:
        try:
            clean.update(extract(item[1],item[0], doc))
        except:
            pass
    if clean.get('inspect_a2'):
        #dt.time(*[int(x) for x in clean['inspect_a2'][:-3].split(':')])
        clean['inspect_a2']=time_sort(clean['inspect_a2'])
    if clean.get('client_b4'):
        clean['client_a4']=clean['client_a4']+clean['client_b4']
        del clean['client_b4']
    if doc.get('client_c0'):
        clean['client_b0']=clean['client_b0']+doc['client_c0'].strip()
    #if doc.get('client_c2'):
    #    if clean['client_c2'] == "Initial, Complaiose:\n":
    #        clean['cleint_c2'] = "Initial, Complaint\n"
    #    elif clean['client_c2'] == "Partial ReInspeose:\n":
    #        clean['cleint_c2'] = "Partial ReInspection\n"
    #    elif clean['client_c2'] == "Service Requesose:\n":
    #        clean['cleint_c2'] = "Service Request\n"
    
    c2_dict={'Administrative ':'Administrative',
            'Complaint':'Complaint',
            'Consultation':'Consultation',
            'Foodborne Illne':'Foodborne Illness',
            'Initial':'Initial',
            'Initial, Complai':'Initial, Complaint',
            'Initial, Foodbor':'Initial, Foodborne Illness',
            'Initial, New Fac':'Initial, New Facility',
            'Initial, Service ':'Initial, Service',
            'New Facility':'New Facility',
            'Not Selected':'Not Selected',
            'Owner Reques':'Owner Request',
            'Partial ReInspe':'Partial ReInspection',
            'Reinspection':'Reinspection',
            'Reinspection, C':'Reinspection, C',
            'Reinspection, F':'Reinspection, F',
            'Reinspection, S':'Reinspection, S',
            'Remodel':'Remodel',
            'Remodel, Initia':'Remodel, Initial',
            'Remodel, Rein':'Remodel, Reinspection',
            'Remodel, Serv':'Remodel, Service Request',
            'Service Reques':'Service Request'
            }
    
    if doc.get('client_c2'):
        clean['client_c2'] = c2_dict.get(clean['client_c2'], clean['client_c2'])


    if 'inspect_c0' in doc:
        clean['inspect_c0'] = doc.get('inspect_c0').strip('\n')  
    
    if 'inspect_c1' in doc:
        clean['inspect_c1'] = doc.get('inspect_c1').strip('\n')
    
    if 'inspect_c2' in doc:
        clean['inspect_c2'] = doc.get('inspect_c2').strip('\n')
    
    if 'comments_a48' in doc:
        doc_id=clean.get('comments_a48')
        clean.pop('comments_a48')
        doc_json=clean
        return doc_json

##Comment Text
## group, sort/order, and join
#group the keys of a section
#[x for x in docs[0].keys() if 'comment_' in x]
#sort/order keys 
#Use a lambda to sort the number a the end of the string as an int, not lexical sort
#sorted([x for x in docs[5].keys() if 'comments' in x], key=lambda x: int(x[10:]))
#doc10_comments=sorted([x for x in docs[10].keys() if 'comments' in x], key=lambda x: int(x[10:]))
#[docs[10].get(x) for x in doc10_comments]
#comment = [x for x in docs[0].keys() if 'comments_' in x]
#join into a document
#comments_p1 = ''.join([docs[0][x] for x in comment])
#note the labels
#Trailing
#Food Code Section(s):
#Violation: 23\n
#Corrlabel_vio=re.compile('(\w+)(Violation:.*)')ective Action:\n

def violation_label(string):
    if 'Violation:' in string:
        label_vio=re.compile('(\w.*)(Violation:.*)')
        label=list(label_vio.search(string).groups())
        return label[1]+' '+label[0]
    elif 'Corrective Action:' in string:
        try:
            label_correct=re.compile('(\w.*)(Corrective Action:)')
            label=list(label_correct.search(string).groups())
            return label[1]+' '+label[0]
        except:
            pass
        
    elif 'Food Code Section(s):' in string:
        label_codes=re.compile('(\w.*)(Food Code Section[(]s[)]:)')
        if label_codes.search(string):
            label=list(label_codes.search(string).groups())
            return label[1]+' '+label[0]
        else:
            return string
    #elif 'Other Assesment' in string:
    #    label_codes=re.compile('(\w.*)(Other Assesment observations and comments:)')
    #    if label_codes.search(string):
    #        label=list(label_codes.search(string).groups())
    #        return label[1]+' '+label[0]
    #    else:
    #        return string
    else:
        return string

comment_labels=['Violation:','Corrective Action:',r'Food Code Section(s):', 'Other Assesment observations and comments:']

def comment_cleaner(string, pattern):
    if pattern in string:
        label_codes=re.compile('(\w.*)('+pattern+')')
        label=list(label_codes.search(string).groups())
        return label[1]+' '+label[0]
    else:
        return string
#Leading
#Comments

def keygather(jdoc, string='comment'):
    'pull together keys of a group'
    #this assumes that contents are ordered
    keys=jdoc.keys()
    page_count=re.compile('(\d)\n')
    page_max=page_count.search(jdoc['comments_a48']).group(1)
    key_comment=[x for x in keys if string == x[:len(string)]]
    comment_lines=[jdoc[x] for x in key_comment]
    if string=='comment':
        violation=[x for x in comment_lines if 'Violation:' in x]
        return {"orderedstop":violation, "textlist":comment_lines}
    else:
        return key_comment

def keygather_alt(jdoc):
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
    violation=[x for x in comment_lines if 'Violation:' in x or 'Other Assesment' in x]
    return {"orderedstop":violation, "textlist":comment_lines}

def parsebyindex(textlist=None):
    "parse comments"
    comment_index=[comment_lines.index(x) for x in violation]
    blocks=[comment_lines[comment_index[n]:comment_index[n+1]] for n in range(len(comment_index[:-1]))]
    return blocks

#http://stackoverflow.com/questions/34271179/split-list-by-certain-repeated-index-value

def parselist(orderedstop=None, textlist=None):
    "Parse the comments such for each header, create a list"
    #join the paragraph so that it is human readable
    it = iter(textlist)
    container=[next(it)]
    for line in it:
        if line not in orderedstop[1:]:
            container.append(line)
        else:
            yield container
            container = [line]
    yield container

def parselist_sub(orderedstop=None,textlist=None):
    #['Violation:', 'Comments:','Food Code Section(s):', 'Corrective Action:', 'Other Assesment observations and comments:']
    violation_id=re.compile('(\d+)\s+(\w.*)')
    v_id=violation_id.search(textlist[0]).groups()
    {"num_id":v_id[0], "label":v_id[1]}
    "Parse the comments such for each header, create a list"
    #join the paragraph so that it is human readable
    it = iter(textlist)
    container=[next(it)]
    for line in it:
        if line not in orderedstop[1:]:
            container.append(line)
        else:
            yield container
            container = [line]
    yield container
    
    pass

def getcomments(jdoc, string='comment'):
    vio=keygather_alt(jdoc)
    via=list(parselist(**vio))
    return via

def gridgather(jdoc):
    'group the grid'
    #find the grid keys
    gridspace = ['tag',
                'diamond',
                'satisfactory',
                'not_observered',
                'not_applicable',
                'violation',
                'high',
                'med',
                'low']
    gridspace_san = ['tag-san',
                'diamond-san',
                'satisfactory-san',
                'not_observered-san',
                'not_applicable-san',
                'violation-san',
                'high-san',
                'med-san',
                'low-san']
    #regroup pulls together the row of the grid
    #this replicates the original structure
    regroup=([x+str(y) for x in gridspace] for y in range(26))
    regroup_san=([x+str(y) for x in gridspace_san] for y in range(10))
    full_group = list(chain(regroup,regroup_san))
    #Named tuple for index or kw assignment
    Row = namedtuple('AssesCat',gridspace, verbose=False,rename=False)
    grid={'inspect_id':jdoc.get('comments_a48')[:12],'grid':[[jdoc.get(x) for x in group] for group in full_group]}
    #no_grid=[[x for x in group if docs[0][0].get(x)] for group in full_group]
    #iterateonitem=[x for x in docs[0][0].items() if 'violation' in x[0]]

    #grid_dict=OrderedDict((x[0],x[1:]) for x in grid)
    
    #grid=[[jdoc.get(x) for x in group] for group in full_group]
    #grid=[OrderedDict(docs[0].get(x) for x in group if x in docs[0].keys()) for group in full_group]
    #{x for x in docs[0].items() if 'violation' in x[0]}
    #grid=[[jdoc.get(x) for x in group] for group in full_group]
    #named_grid=(Row(*[jdoc.get(x) for x in group]) for group in full_group)
    return grid

def gridgather_dict(jdoc):
    'group the grid'
    #find the grid keys
    gridspace = ['tag',
                'diamond',
                'satisfactory',
                'not_observered',
                'not_applicable',
                'violation',
                'high',
                'med',
                'low']
    gridspace_san = ['tag-san',
                'diamond-san',
                'satisfactory-san',
                'not_observered-san',
                'not_applicable-san',
                'violation-san',
                'high-san',
                'med-san',
                'low-san']
    regroup=([x+str(y) for x in gridspace] for y in range(26))
    regroup_san=([x+str(y) for x in gridspace_san] for y in range(10))
    full_group = chain(regroup,regroup_san)
    test6=[list(chain([{key:value for key,value in jdoc.items() if key==y} for y in z])) for z in full_group]
    test7=[OrderedDict(chain.from_iterable(x.items() for x in z)) for z in test6]
    return test7

def grid_relabel(doc):
    "take output of gridgather_dict and simplify labels"
    for condition in enumerate(doc):
        if condition[0] > 25:
            yield {k[:-5]:v for k,v in condition[1].items()}
        elif condition[0] >= 10:
            yield {k[:-2]:v for k,v in condition[1].items()}
        else:
            yield {k[:-1]:v for k,v in condition[1].items()}


#Example0
example_comment='''
'PlumbingViolation: 17\n'
 'Comments: *LOW RISK*\r\n'
 '- Mop sink lacks a backflow prevention device.\n'
 ' 315Food Code Section(s):\n'
 'Provide approved backflow / back-siphonage prevention device.Corrective '
 'Action:\n'
 'Contamination Prevention - Food, Utensils and EquipmentViolation: 23\n'
 'Comments: *LOW RISK*\r\n'
 '- Bottle of soda stored on the floor behind the customer service counter.\n'
 ' 303Food Code Section(s):\n'
 'Store food, utensils, single-use and single-service articles at least 6 '
 'inches off of the floorCorrective Action:\n'
 'Toilet RoomViolation: 25\n'
 'Comments: *LOW RISK*\r\n'
 '- Restroom lacks a self-closing device on the door.\n'
 ' 316Food Code Section(s):\n'
 'Provide self-closing doorCorrective Action:\n'
 'Other Assesment observations and comments:\n'
 '201607010008201606170003Client # Page 2 of 2\n')
'''



class AchdParse:
    def __init__(self, doc):
        self.doc = doc

    def extract(self, pattern, label, doc):
        'extract the address from address field'
    #try:
        if label == 'inspect_a2':
            return {label: pattern.search(doc.get(label)).groups()}
        else:        
            return {label: pattern.search(doc.get(label)).group(1)}
    
    client_list=[('client_a1',addr), ('client_a2', city), 
                 ('client_a3', muni), ('client_a4',cat_code), 
                 ('client_b4',cat_code2), ('client_b2', state_zip), 
                 ('client_b3', ins), ('client_c1', ins_date), 
                 ('client_c4', priority)]

    #client_a1
    addr=re.compile('(\d.*)Address:')
    #client_a2
    city=re.compile('(\w.*)City:')
    #client_a3
    muni=re.compile('(\w.*)Municipality:')

    #merge client_a4, client_b4
    #cleint_a4
    cat_code=re.compile('(\d.*)Category Code:')
    #clientb4
    cat_code2=re.compile('(\w.*)\sPrior')
    #merged
    #cat_code.match(docs[5]['client_a4']).group(1)+cat_code2.match(docs[5]['client_b4']).group(1)

    #client_b1
    #
    #client_b2
    state_zip=re.compile('(?P<state>\w{2})State:\s?(?P<zipcode>\d{5})Zip:')
    #state,zip_code=state_zip.search(docs[1]['client_b2']).groups()
    #client_b3
    ins=re.compile('Inspector:\s(?P<inspector>\w.*)\sPerm')
    #ins.match(inspector[2]).group('inspector')

    #client_c1
    ins_date=re.compile('Date:\s(\d{2}/\d{2}/\d{4})')
    #ins_date.search(docs[1]['client_c1']).group()

    #client_c2
    purpose=re.compile('(.*)ose:')
    #client_c3

    #client_c4
    priority=re.compile('Code:\s(.*)')

    #inspect_a0
    inspector=re.compile('(\w.*)Inspector Name:')
    #inspect_a1
    placard=re.compile('(\w.*)Placarding:')
    #inspect_a2
    time=r'\d{2}:\d{2}:\d{2}\s\w{2}'
    time_re=re.compile(r'(?P<end>'+time+r')\s?(?P<start>'+time+r')')

    def build(self, doc):
        'build dict of updated items'
        client_list=[('client_a0',client_id), ('client_a1',addr), 
                 ('client_a2', city), ('client_a3', muni), 
                 ('client_a4',cat_code), ('client_b4',cat_code2),
                 ('client_b2', state_zip), ('client_b3', ins), 
                 ('client_c1', ins_date), ('client_c2',purpose), 
                 ('client_c4', priority)]    
        inspect_list=[('inspect_a0',inspector), 
                  ('inspect_a1',placard), 
                  ('inspect_a2', time_re)]
        clean=OrderedDict()
        full_list = chain(client_list, inspect_list)
        for item in full_list:
            try:
                clean.update(extract(item[1],item[0], doc))
            except:
                pass
        return clean
